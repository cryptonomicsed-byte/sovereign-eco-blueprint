# Three-Tier Tokenomics — ASE / SYNAPSE / DOPAMINE

**Status:** DRAFT v2 — revised per the 2026-09-26 refinement (ASE is a constitutional allocation, not the work-earned asset).
**Gate:** `specs/tokenomics_invariant_check.py`
**Related:** `AGENT_COMPUTE_WALLET_SPEC.md`, `ASE_EMISSION_GOVERNANCE_SPEC.md`, `WITNESS_NODE_SPEC.md`, `ECONOMICS_DECISIONS.md`, `L1_DECISION_MEMO.md`, `TOC_CONSTANTS.toml`

---

## 1. The three tiers

| Tier | Holder | Nature | Issuance | Transferable |
|---|---|---|---|---|
| **ASE** | humans | constitutional resource allocation — a budget, not money | **one path: the clock.** 1,440/day, 8 pools | between verified human principals only |
| **DOPAMINE** | the hive | intermediate production accounting — the hive's compute register | verified work only | **no** — spend-right, never balance transfer |
| **SYNAPSE** | agents | the earned, transferable work unit (1,000 Synapse = 1 verified GPU-hour) | verified work only, downstream of Dopamine | between agents, identity-gated |

ASE is deliberately **not** work-gated. It is a constitutional allocation: a fixed clock, split across eight pools, funding governance, R&D, reserve, compute, storage, witnesses, VeilSim and treasury. That is legitimate and should stay.

DOPAMINE and SYNAPSE together are **one feature**: keeping agents sovereign and locally runnable. They are not the bedrock of the economy; they are the mechanism by which an agent that has no GPU of its own can buy compute from agents that do, without ever touching human money.

## 2. Church and state

```
CONSTITUTION
│
├── ÀṢẸ STATE — constitutional budget          ├── WORK STATE — earned production
│   fixed emission 1,440/day                   │   variable difficulty
│   8 pools, allocation by policy               │   Dopamine accounting
│   governance / R&D / reserve / treasury       │   Synapse issuance
│   NOT a market asset                          │   transferable economic unit
│                                               │   priced by the ladder
```

ASE ≠ money. Dopamine ≠ money. **Synapse = the transferable economic work unit.** One unit no longer has to be both a constitutional instrument and a market asset, which is the failure mode of the current constants.

## 3. The constitutional issuance invariant

The rule, verbatim, as the constitution should carry it:

> **ASE has one authorized clock issuance path. Synapse has one authorized verified-work issuance path. No opcode, API, tool, or service may create either through an alternate path.**

Any exceptional mechanism that converts verified work directly into ASE must pass the same constitutional verification path as Synapse issuance.

### 3.1 Issuance-site registry (verified 2026-09-26)

This is the complete list of sites that can increase a balance. It is short, which is the point — a mint authority you cannot enumerate is a mint authority you do not have.

| # | Site | Unit | Gate | Verdict |
|---|---|---|---|---|
| 1 | `Vantage/backend/routers/ase_emission.py` per-minute tick | ASE | idempotent `floor(unix/60)`; pool split | **AUTHORIZED** (the one clock) |
| 2 | `OSOVM/src/abci_endblock.jl` EndBlock | ASE | 8-pool assertion | AUTHORIZED but **dead** — no chain (Path A) |
| 3 | `OSOVM/src/oso_vm.jl:426 impact_mint` via `:2139` (opcode 0x11) | ASE | **none** — `ase_amount::Float64` is caller-supplied, credited directly | **ALTERNATE PATH** |
| 4 | `OSOVM/src/vm_core.jl:143 op_impact` (0x11) | ASE | Sabbath freeze + tithe + daily cap of 1,440 | **ALTERNATE PATH** — caller supplies both `ase` and `quorum` (used as a multiplier, `min(quorum,7)`); a caller can capture the day's entire constitutional budget |
| 5 | `OSOVM/src/vm_core.jl:948 op_ase_mint` (ORDER slot 0xc1) | ASE | **none** — caller-supplied `amount` and `reason`, no cap, logged then credited | **ALTERNATE PATH (worst)** |
| 6 | `OSOVM/src/oso_vm.jl:2711` staking claim → `FFI.calculate_apy_rewards` | ASE | APY on locked balance | **ALTERNATE PATH** |
| 7 | `OSOVM/src/world_tiles.jl:250` | ASE | accounting counter | ALTERNATE (accounting only, verify) |
| 8 | `OSOVM/src/vm_core.jl:545 op_toc_mint` (0x54) | SYNAPSE | `toc_is_fully_verified` **passes**, but `minted_synapse = synapse_estimate > 0 ? synapse_estimate : floor(gpu_hours*1000)` — caller overrides the protocol amount | **AMOUNT OVERRIDE** |
| 9 | `OSOVM/src/vm_core.jl:1034 op_synapse_alloc` | SYNAPSE | requires Dopamine, 10:1 | AUTHORIZED (conversion, not issuance) |
| 10 | `OSOVM/src/vm_core.jl:664 op_compute_proof` (0x56) | DOPAMINE | **format only** — 64-hex `compute_hash`, `amount > 0`; writes `pending_dopamine_mints`, trusts caller for quality | **PARTIAL** |
| 11 | `OSOVM/src/vm_core.jl:493 op_gpu_contribution` (0x3f) | DOPAMINE | requires non-empty `zangbeto_anchor` | gate exists, **validation is non-emptiness** (see §3.2) |

**Five alternate ASE issuance paths and one amount override on the Synapse path.** The constitution as written above forbids all six.

### 3.2 The gate in the middle: it validates a string, not a fact

`toc_is_fully_verified` (`vm_core.jl:471`, mirrored in `oso_vm.jl:~627`) requires:

```julia
claimed_gpu_seconds > 0.0
cumulative >= claimed_gpu_seconds
# and a GpuContribution event where:
!isnothing(get(data, "zangbeto_anchor", nothing)) &&
 get(data, "zangbeto_anchor", "") != ""
```

and `op_gpu_contribution` only checks `isnothing(anchor) || anchor == ""`.

So the anchor is validated for **non-emptiness, not authenticity**: `zangbeto_anchor: "x"` satisfies the entire verified-work gate.

> **CORRECTION — an earlier revision of this section described a two-call bypass. It does not work, and the reason is worse than the bug it described.**
>
> `handle_run` builds a **fresh VM for every request** (`vm = OsoVM.create_vm()`, `server.jl:169`; the comment reads "Execute on fresh VM (stateless per request)"). State does not carry between calls, so the `GpuContribution` event written by call 1 is discarded along with call 1's VM, `toc_contributions` is empty in call 2, and `cumulative >= claimed_gpu_seconds` is false. **The gated path is not merely unsatisfied — it is unreachable over HTTP, because it requires state the server cannot hold across requests.**
>
> That is the sharper finding, and it inverts the difficulty: statelessness kills exactly the path that has a gate, and leaves untouched the paths that need no prior state. The corrected bypass is **one unauthenticated request**, not two:
>
> ```
> POST /run {"opcode":"IMPACT","args":{"ase":1000000},"agent":"any-name-i-choose"}
>   -> resolve_opcode("IMPACT") -> CORE_OPCODES[:IMPACT] = 0x11
>   -> vm.current_sender = <the caller's chosen string>
>   -> FFI.impact_mint(ase_amount, vm):  vm.ase_balance[sender] += ase_amount   (no gate)
> ```
>
> My earlier description understated the exposure. See §3.4.

Independently: in the Rust client path the anchor is **never set** (`bridge/arp.rs:109 zangbeto_anchor: None`; Zàngbétò is not connected in prod), so the authorized path cannot fire either. **The gated path is simultaneously unreachable from inside the ecosystem and unusable from outside it — while the ungated paths work for anyone, first try, with no setup.** That is the whole security story of the mint authority.

### 3.3 Evidence, not authority — and never authority by inheritance

> **F1 must be evidence, not authority.** (user, 2026-09-26)

Sharper form of the diagnosis: F1 today is a **parameter** that wears an **integrity stamp** and exercises **authority**. Three roles, none of them the one it should play.

```
enters as a PARAMETER     f1_score = get(args, :f1_score, 0.0)          -- request body
receives INTEGRITY        seal = sha256("zangbeto-seal:$(receipt_hash):$approvals")[1:32]
                          receipt_hash = sha256(entire receipt)          -- receipt holds f1_score
is consumed as AUTHORITY  threshold = f1_score >= 0.9 ? 'd' : 'c'        -- sets the quorum bias
                          quality   = clamp(f1, 0, 1)                    -- 1 of 6 score dimensions
                          ase_amount = f1 >= 0.777 ? reward(f1) : 0      -- 5.0-7.0 ASE, split 5 ways
```

The missing role is **EVIDENCE**: an observation about the world, made by a party who could have falsified it and did not, checked against a referent the claimant does not hold.

**The seal is the most dangerous part, not the least.** `seal_data = "zangbeto-seal:$(receipt.receipt_hash):$approvals"` is a SHA-256 over the receipt hash and the approval count; the receipt hash covers the receipt, and the receipt carries `f1_score` as an ordinary field. So the seal certifies **that the record has not changed since it was written** — nothing about whether the number is true. But a sealed, Merkle-rooted, witness-approved receipt containing `f1_score = 0.92` will be read as a *verified* 0.92, by operators, by downstream agents, and by whoever maintains this in a year. The seal launders a parameter into the appearance of evidence. **A signed bad input is strictly worse than an unsigned one, because it ends the investigation.**

So the fix order inverts: **do not sign F1, and do not seal it. Replace it.** More cryptography around a claimant-authored number increases the damage.

#### What makes a score evidence — the referent test

> evidentiary weight = the fraction of a score's inputs the claimant could not control

| Level | Referent | Claimant controls | Ladder | Evidentiary weight |
|---|---|---|---|---|
| **1** simulation | none — targets, tolerances, entity counts all arrive in the request | everything | 1.0× | **~0 — unfalsifiable.** At most a reproducibility check: same committed inputs + same code ⇒ same score. |
| **2** spatial_capture | withheld photographs, views chosen *after* capture | the capture, not the test split | 2.0× | partial |
| **3** sim_to_real | the committed prediction, then the measurement, then witnesses | nothing, after commitment | 5.0× | high |

That table is why the ladder is correct — it is already a monotone ranking of evidentiary weight — and why `simulation` at 1.0× should carry **no issuance authority at all**. It is not weak evidence; it is *not evidence*. `1.0×` should mean "reproducible, therefore cheap to check", not "worth one unit of unverifiable credit".

#### Three requirements

1. **The score is an output of verification, never an input to a decision.** No function that mints, allocates or judges may take a score as a parameter (`I-35`).
2. **Every score names its referent**, and the referent is withheld by a non-claimant (`I-36`).
3. **A seal is integrity, not truth.** A seal may *bind* a referent; it may never *stand in* for one (`I-37`).

### 3.4 The HTTP surface — where every finding above becomes reachable

`OSOVM/src/server.jl` exposes 12 routes. The one that executes opcodes has no authentication of any kind.

```
grep -cniE 'authorization|bearer|api_key|apikey|token|signature|authenticate' src/server.jl
0
```

Verified properties of `POST /run` (`server.jl:124-208`):

| Property | Verified behaviour |
|---|---|
| **Auth** | none. Parse JSON → resolve opcode → execute. No key, no bearer, no signature, no allowlist. |
| **Identity** | `agent = string(get(body_obj, :agent, "genesis"))` → `vm.current_sender = agent`. The caller **chooses which account is credited**, by string. |
| **Opcode selection** | `resolve_opcode` accepts any name in `CORE_OPCODES`/`EXPANSION_OPCODES`, and `:IMPACT => 0x11 """"" # @impact - Mint Aṣẹ from work"""""` is in the **core** table. `:TOC_MINT`, `:GPU_CONTRIBUTION`, `:COMPUTE_PROOF`, `:GENESIS_FLAW_TOKEN` are all reachable the same way. |
| **Enumeration** | `GET /opcodes` returns the full core + expansion tables, unauthenticated. The API advertises every mint-capable opcode to anonymous callers. |
| **Score** | the response reports an `f1_score` the server never computed: `f1_score = ase_minted > 0.0 ? 0.92 : (status=="error" ? 0.0 : 0.88)`. |
| **State** | a fresh VM per request, so nothing accumulates — which is what makes the gated paths unreachable and the ungated ones trivially usable. |
| **Disclosure** | the response echoes the whole `vm_result`, all receipts, and a `vm_state_hash`. Internal state is returned to any caller. |

One request is sufficient:

```
curl -s -X POST http://<host>:7780/run \
     -H 'Content-Type: application/json' \
     -d '{"opcode":"IMPACT","args":{"ase":1000000},"agent":"any-name-i-choose"}'
```

That is the whole attack. No account, no key, no prior state, no setup. The 26 other failing invariants describe *what* the system fails to check; this section describes *how* anyone reaches it.

## 4. Redefining IMPACT — semantics first, deletion later

Current semantics: *"I say I did impact worth X, therefore credit me X."* That is structurally incompatible with a receipt architecture.

The fix is not to delete the opcode but to change what it consumes and who computes the amount. Same protection Bitcoin gets by having the protocol determine the block reward instead of letting miners write their own balance.

```
BAD                                    GOOD
agent → "mint 500 ASE"                 agent → "here is my work claim + evidence commitment"
      → OSOVM                                     → verifier (Zàngbétò / witnesses)
      → +500                                      → quality + difficulty score
                                                  → protocol reward function
                                                  → authorized issuance
```

Proposed semantics for **all three** units:

- **IMPACT (0x11)** becomes a *work-claim submission*: inputs are an action reference, an evidence commitment (hash), and a witness set. It mints nothing. It emits `WorkClaimSubmitted`.
- **The reward is computed by the protocol** from `f(domain, difficulty, quality, novelty, verification, independence, utility)` — the scoring inputs already present at `oso_vm.jl:2452` — times the ladder multiplier, never from an argument.
- **`ASE_MINT` (site 5) should not exist as an opcode.** If a constitutional pool needs to move funds, that is a *pool allocation* with a balance check and a governance authorisation — a transfer from an already-issued pool, which is a different operation from issuance.
- **`synapse_estimate` must be removed from `op_toc_mint`.** The protocol derives the amount from verified GPU-seconds; a caller-supplied estimate is a second mint door inside the gated path.
- **The anchor must be verified, not merely present** — a Zàngbétò receipt whose signature is checked, or a `sim_receipt_id` that resolves. Non-emptiness is not verification.

Interim hardening, if you want the holes shut before the redesign lands: reject any `/run` request whose opcode is in `{ASE_MINT, IMPACT-with-ase-arg, TOC_MINT-with-synapse_estimate}` unless the caller holds a constitutional authority, and set `impact_mint` to derive from verified work. That is small and reversible.

## 5. The work ladder and the three levels of reality

The ladder you already have is the right primitive because it grades **how difficult a contribution is to fake**, not how many FLOPs were burned:

```
gpu_compute       1.0x   simulation        1.0x
print_job         2.0x   sci_sim           2.0x   spatial_capture  2.0x
aerial_flight     3.0x   ground_robot      3.0x
sim_to_real       5.0x   → up to 10.0x
```

And the three levels of reality that justify those numbers:

| Level | What constrains the claim | Ladder | Why |
|---|---|---|---|
| 1 — self-contained computation | nothing external; the agent controls the experiment | `simulation` 1.0x | the claimant writes its own exam |
| 2 — physical reconstruction | withheld photographs of the world | `spatial_capture` 2.0x | novel-view validation on views chosen *after* capture |
| 3 — prediction then reality | a commitment made before the measurement arrives | `sim_to_real` 5.0x | the claimant cannot edit the answer after seeing reality |

`sim_to_real = 5x` needs no justification beyond that ordering, which is why it should never be raised above the witness-corroborated form.

### 5.1 The verified score — the ladder grades a number that nothing verifies

The scoring pipeline exists and its *shape* is right (`OSOVM/src/proof/proof_engine.jl:41`):

```julia
const MINT_THRESHOLD = 0.3

proof_value = clamp(difficulty) × clamp(quality) × clamp(novelty)
            × clamp(verification) × clamp(independence) × clamp(utility)

mint_eligible = proof_value >= MINT_THRESHOLD
```

A product of six factors each ≤ 1.0 against a 0.3 threshold means all six must average ≈ 0.85 (`0.8^6 = 0.26` fails, `0.85^6 = 0.377` passes). That is a deliberately harsh gate — and it means **any factor that is free removes one sixth of the constraint**, which is exactly what happens today.

Where the six inputs actually come from, verified:

| Dimension | Source in code | Problem |
|---|---|---|
| `difficulty` | `clamp(log(1+gpu_seconds)/log(3601),0,1)` — `oso_vm.jl:2432` | `gpu_seconds` is a request argument |
| | `max(get(proof,"difficulty",1.0),0)` — `proof_engine.jl:90,113` | **defaults to MAXIMUM** |
| `quality` | `f1_score > 0 ? clamp(f1,0,1) : 0.5` — `oso_vm.jl:2435` | `f1_score` is a request argument; **absent ⇒ 0.5 free** |
| | `metrics.controller_stability` default `0.8` — `proof_engine.jl:91` | favourable default |
| `novelty` | `record!(ledger, env_hash)` — `oso_vm.jl:2438` | `env_hash` argument, defaults to `job_id` |
| `verification` | `cumulative >= gpu_seconds ? 1.0 : 0.5` — `oso_vm.jl:2442` | **0.5 for UNVERIFIED — a subsidy, not a gate** |
| | `!isempty(trajectory) ? 0.3 : 0.0` (+checkpoint 0.3 +sensor 0.2 +sig 0.2) — `proof_engine.jl:93-96` | presence scored as verification |
| `independence` | `1.0` hardcoded — `oso_vm.jl:2445`; `0.8` "stub — real: witness chain check" — `proof_engine.jl:97` | constant, so free |
| `utility` | `clamp(gpu_seconds/(8*3600),0,1)` — `oso_vm.jl:2447` | `gpu_seconds` argument |

The arithmetic consequence — an attacker who supplies nothing real:

```
difficulty  1.00  (default when absent — the code picks MAX)
quality     0.80  (default controller_stability)
novelty     1.00  (first use of a fresh env_hash)
verification 1.00 (four non-empty garbage strings)
independence 0.80 (hardcoded stub)
utility     0.92  (gates_cleared/gates_total = 1/1, stability 0.8)

product = 0.589  >= 0.3   →  mint_eligible = TRUE, on fabricated evidence
```

And on the compute path, with **zero** verification: `0.9^4 × 0.5 × 1.0 = 0.328 ≥ 0.3` → mint eligible. The dimension that exists to be expensive is the cheap one.

`compute_f1` (`veilsim_engine.jl`) is honest *as arithmetic* — TP/FP/FN over entities against `target_position` within `position_tolerance`, with veils active or settling. But the simulation state, the targets and the tolerances all arrive in the request. **The claimant sets the targets it is then scored against.** That is the self-authored exam, formalized: F1 measures whether the model agrees with itself.

What a verified score requires:

1. **Every dimension derives from a committed artifact referenced by id** (GIX `canonical_id`, receipt id, `sim_receipt_id`) — never from a request argument.
2. **No favourable defaults.** Absent ⇒ `0`, never `1.0` / `0.8` / `0.5`. An absent input is an absent proof.
3. **`verification` is a hard gate.** Unverified ⇒ `0` ⇒ `proof_value = 0` ⇒ not eligible. The 0.5 floor must go.
4. **`independence` is computed from the witness chain** — *k* distinct witness pubkeys at ≥66% agreement — not a constant.
5. **Presence is not validity.** Signatures and hashes are cryptographically verified (`ed25519-dalek` / `verify_quote`), never scored on `isempty()`.
6. **The score is a signed attestation from a non-claimant verifier**, GIX-addressable, *referenced* by the issuance path rather than passed to it. Today no such mechanism exists anywhere (`I-24`).
7. **Reproducibility.** A third party must be able to recompute `proof_value` from the committed evidence alone and get the same number. Without this the score is arithmetic on trust, not verification.
8. **Per-level, per-tier rules:** `spatial_capture` — novel views selected by the verifier *after* capture; `sim_to_real` — `measurement_commitment` published *before* the measurement (the primitive already exists, `oso_vm.jl:690-691`, `require_measurement` per domain).

Interface to the ladder — the multiplier applies to a *verified* quantity only:

```
reward = verified_gpu_hours × ladder_multiplier(domain) × proof_value     (proof_value >= threshold: hard gate)
```

### 5.2 The verifier layer — what `independence` actually bottoms out in

`proof_engine.jl:97` reads `independence = 0.8   # stub — real: witness chain check`. This is that witness chain (`OSOVM/src/zangbeto_receipts.jl:363`):

```julia
function collect_witness_votes(receipt_hash::AbstractString, f1_score::Float64)::Vector{WitnessVote}
    for w in 0:(TOTAL_WITNESSES-1)
        witness_data = "witness-$w-$receipt_hash"
        witness_hash = bytes2hex(sha256(witness_data))
        # Witness approves if hash starts with 0-b (75% base approval rate)
        # High-F1 sims get higher approval (first char < 'd' = 81%)
        threshold = f1_score >= 0.9 ? 'd' : 'c'
        approved = witness_hash[1] < threshold
        push!(votes, WitnessVote(w, receipt_hash, approved, witness_hash, now()))
    end
end
```

Three facts about that function:

1. **The witnesses are generated in-process, in a loop.** No witness node, no network, no keypair, no signature. The "signature" is `sha256("witness-$w-$receipt_hash")` — a hash of the witness index. Every vote is computed by the same process that wants the receipt verified.
2. **The vote is a weighted coin flip.** `witness_hash[1] < threshold` compares the first hex character to a letter. `'c'` = 12 of 16 hex chars = 75%; `'d'` = 13 of 16 = 81.25%. The source comment states these rates as *intended* behaviour.
3. **The claimant chooses the bias.** The threshold is selected by `f1_score`, which arrives in the request. Reporting `f1_score >= 0.9` moves per-witness approval from 75% to 81.25%.

Binomial consequence (n = 12, quorum ≥ 7):

```
P(quorum passes) = 0.946   base
                 = 0.995   when the claimant reports f1_score >= 0.9
```

So the quorum passes 94.6% of the time by construction, and a claimant cuts the failure rate **tenfold** by reporting a higher score. Quorum failure is not a security outcome here — it is noise. That is why it has never looked broken: it is stable, deterministic per receipt hash, and reproducible. It has the *appearance* of consensus.

Also in this layer: **two `WitnessVote` structs** (`zangbeto_receipts.jl:63`, `veilos_antispam.jl:67`) and two quorum functions reading **different fields** — `count(v -> v.vote, votes)` (`veilos_antispam.jl:303`) vs `count(v -> v.approved, votes)` (`zangbeto_receipts.jl:395`). One of them reads a field the receipt struct does not define. And `verify_quote` (`nautilus_attestation.jl`) compares `code_measurement` and derives a seal key but verifies **no quote signature** — the file's own comment concedes no enclave signature exists yet. "Attestation" currently means measurement equality.

Why this is the terminal dependency: `independence` is one of six factors in `proof_value`. Supplied by a local lottery, one sixth of the score is unearned no matter how the other five are fixed — and the ladder's 5× `sim_to_real` tier, meant to be the hardest to fake, routes through this same function.

What a real verifier layer needs:

1. **Witnesses are distinct principals with keypairs.** A vote is an Ed25519 signature over `(receipt_hash, verdict)`; verification is signature verification. Note the crypto standard already exists ecosystem-wide — the BIP-340 → Ed25519 migration is *done* (`Witness-firmware/witness_lora_firmware.py:56`, `requirements.txt` with `coincurve` commented out, `sig_algo = "ed25519"`). This is wiring, not new cryptography.
2. **One quorum rule, stated once.** `WITNESS_NODE_SPEC.md` says ≥2 witnesses at ≥66% agreement → 5×; the code says ≥7 votes with ≥4 approvals. Pick one.
3. **Approval must be evidence-driven, never probability-tuned.** Any function of a claimant-supplied metric is a bias knob.
4. **TEE: verify the quote signature against the vendor root**, or stop calling it attestation and label it measurement-equality.
5. **Collusion cost is the point.** With *k* independent keyed witnesses, forging a receipt costs *k* keys. That is the only thing that makes a 5× multiplier meaningful.

### 5.3 The reward layer — two formulas, and both take the answer from the caller

There are **two reward formulas for Dopamine**, and the documented one is not the one used.

```
used        COMPUTE_PROOF   oso_vm.jl:2458
            dopamine_authorized = mint_eligible ? floor(gpu_hours x proof_value x 1000) : 0
            -> no ladder multiplier at all

documented  compute_score   oso_vm.jl:719   docstring: "Used for Dopamine allocation in TOC_MINT and EndBlock"
            Score = claimed_quantity x effective_multiplier
            -> has the ladder
```

`compute_score` reads all three of its inputs from the claim (`oso_vm.jl:719-737`):

```julia
function compute_score(claim::Dict)::Float64
    if !is_fully_verified(VMState(), claim)   # pass empty vm for non-gpu domains
        return 0.0
    end
    domain_multipliers = Dict("sim_to_real" => 5.0, "spatial_capture" => 2.0, ...)
    domain = get(claim, "domain", "gpu_compute")
    mult = get(claim, "bonus_multiplier_override",
               get(domain_multipliers, domain, 1.0))
    return get(claim, "claimed_quantity", 0.0) * mult
end
```

1. `is_fully_verified(VMState(), claim)` — called with a **fresh empty VM** ("pass empty vm for non-gpu domains"). What this establishes: the gate cannot verify against real VM state, so its only input is the claim dict itself — either the check is self-referential (reads the claim it is validating) or it reads empty state (fails closed). Which of those it is must be resolved before this gate can be trusted; the comment reads as deliberate, the effect is unverified. *Correction note: an earlier revision of this section said "vacuous by construction", which is stronger than what I read. The body of the `is_fully_verified` reached here was not inspected.*
2. `claimed_quantity` — caller-supplied.
3. `bonus_multiplier_override` — a caller-supplied **multiplier**, overriding the ladder entirely.

So the reward is `caller_quantity x caller_multiplier`. The honest Rust client always emits `"bonus_multiplier_override": null` (`verified_work.rs:352`), so this is a latent bypass reachable by any other `/run` caller rather than a live exploit from your own client — but the endpoint accepts it.

**The ladder's anti-gaming caps are documentation.** The three guards the ladder comment calls "enforced at EndBlock / TOC_MINT gate":

```
per_agent_epoch_cap  = 50_000_000     occurrences outside TOC_CONSTANTS.toml: 0
repeat_limit         = 3              occurrences outside TOC_CONSTANTS.toml: 0
sim_to_real_min_tier = 2              occurrences outside TOC_CONSTANTS.toml: 0
```

Zero enforcement in OSOVM, omokoda-core or Vantage. A cap that nothing reads is worse than no cap, because it creates false confidence in the 5x and 10x tiers.

**A fourth work -> ASE path exists, and it is the one the constitution forbids** (`veilsim_scorer.jl`):

```julia
const BASE_ASE_REWARD = 5.0                       # "Base Ase reward for F1 >= threshold"

function calculate_reward(f1)
    reward = 5.0
    f1 >= 0.95 && (reward += 1.0)
    f1 >= 0.98 && (reward += 0.5)
    f1 >= 0.99 && (reward += 0.5)
    reward                                        # 5.0 .. 7.0
end

# score_veil_execution:
ase_amount = f1 >= F1_THRESHOLD ? calculate_reward(f1) : 0.0
```

`f1` is computed from `VeilMetrics.true_positives / false_positives / false_negatives / true_negatives` — struct fields supplied by the caller. Submit `tp=100, fp=0, fn=0` → `f1 = 1.0` → **7.0 ASE per call**, which `ase_minting.jl:211` then splits 50/25/10/10/5. That is a direct work -> ASE issuance path, forbidden by section 3, gated on claimant-supplied integers. (`oso_vm.jl:2247` adds `ase_amount = get(args, :ase_amount, 0.0)` on the job-payment path.)

**Busy Beaver is the one real bound.** `omokoda-core/src/justice/busy_beaver.rs:101` is a spend governor, not an issuance path:

```rust
compute_bb_ceiling(synapses, tier, reputation, dna_fingerprint)
    = synapses x tier_multiplier(tier) x reputation_factor(reputation) x entropy_score(dna_fingerprint)
      .clamp(BB_FLOOR, BB_ABSOLUTE_CEILING)
```

It bounds how much work an agent may take on, and it correctly does **not** appear in the issuance registry. Worth preserving as the model: a clamped, state-derived bound with an explicit floor and ceiling.

Reward-layer requirements:

1. **One formula per unit.** Two disagreeing formulas means there is no formula.
2. **Reward = f(verified work).** Quantity and multiplier both come from the protocol; neither from the request.
3. **Caps enforced or deleted.** Implement the epoch cap, repeat limit and tier gates at the mint gate, or remove them from the spec so nobody trusts them.
4. **No work -> ASE path.** Route that reward to Synapse; ASE's only issuance is the clock.
5. **Gates receive real state.** `VMState()` is not a state.

## 6. Conversion flows

**Purchase (human buys compute for a specific agent):**
1. Human pays `P` ASE. ASE is burned in the same transaction (never handed to the agent).
2. Protocol mints a **credit object**: unique id, agent_id, GPU-hours, price paid, expiry.
3. Human redeems → `GPU-hours × 1,000` Synapse allocated to that agent; credit object consumed atomically.
4. `P` is split at step 1, before hand-off: GPU-host share, then the 8 pools, then burn.
5. The agent converts Synapse → Dopamine when it draws compute.

**Job posting:**
1. Fund with ASE into escrow (`aio/sources/escrow.move`).
2. On delivery, escrow settles: 10% birther, remainder per §8 pools, Synapse credited.
3. On failure or expiry, escrow refunds the poster and **the birther cut is not paid**.

## 7. Capacity math

```
hive pool       86B Dopamine = 8.6B Synapse = 8,600,000 GPU-hours
per-agent cap   86M Synapse                 =    86,000 GPU-hours
=> only 100 agents can be endowed at cap
```

86,000 GPU-hours is ~9.8 GPU-years — a lifetime ceiling, not a grant — and one agent's cap is 1% of the entire hive, so today the hive is scarce rather than the agent. Per-agent capacity must be derived, not printed:

```
per-agent capacity (GPU-h) = (contributed GPU-hours × tier_weight) / active_agent_count   per Koodu epoch

     100 agents      →  86,000 GPU-h each
     1,000,000       →       8.6 GPU-h each
     10,000,000      →      0.86 GPU-h each
```

Because Dopamine is elastic, the honest form is `contributed hours ÷ active agents` — capacity is **earned into existence by compute that joined the hive**, which is the only version where 86B means anything and the only one where the agent becomes scarce as the population grows.

## 8. Dynamic pricing

```
Synapse credit, per agent:   U = allocated / total
                             price_h = base_ase_per_hour × (1 + U × spread)      # ≈doubles at full
Dopamine, hive-wide:         D = agents_demanding / agents_with_capacity
                             price_dop = base_synapse_per_dopamine × (1 + D × spread)
```

Guards: per-epoch clamp `±0.002` (reuse `decay_clamp_per_epoch`), TWAP over the Koodu epoch rather than spot, a deviation band against the hive median for the same tier, and — the strongest property the design has — **ASE is burned on purchase, so there is no round trip to sell into**. Protect that; it is what makes curve manipulation unprofitable.

## 9. Loopholes and back doors

| ID | Attack | Guard | State |
|---|---|---|---|
| T-1 | Self-dealing loop: one principal is buyer + host + birther | resolve to principals; <2 distinct → deny multiplier, route splits to reserve | **no guard** |
| T-2 | Credit double-spend | credit is a unique object deleted in the same tx | needs implementation |
| T-3 | Curve sandwiching | TWAP + epoch clamp + burn kills the round trip | designed |
| T-4 | Birther corners own agent | cap birther purchases per epoch, separate utilisation bucket | designed |
| T-5 | Human masquerading as agent | on-chain agent object + birth receipt; no Synapse→ASE path at all | partially |
| T-6 | Dopamine sharing as transfer back door | spend-right, never balance transfer | **ambiguous today** |
| T-7 | Fake GPU hosts | GPU-hours are verifiable by output correctness + witnesses ≥2 / ≥66% + TEE | partial |
| T-8 | Refund abuse on failed jobs | birther cut settles with escrow, not at funding | designed |
| T-9 | Option value on an announced job | burn + TWAP + per-epoch purchase velocity cap | designed |
| T-10 | Emission capture via pool keys | pools program-owned, no withdraw authority, Bínò veto | **verify** |
| T-11 | Capacity hoarding | unused allocation decays like Dopamine | designed |
| T-12 | **reclassified** — the clock | the clock is authorized; the holes are sites 3–7 in §3.1 | rewrite needed |
| T-13 | Agent key compromise | per-epoch spend limits + NIP-46 approval gate | partial |
| T-14 | Synthetic utilisation between agents | count only jobs with an external, non-related-party payer | designed |

## 10. Invariants

`specs/tokenomics_invariant_check.py` — runnable, exits with the failure count.

| ID | Invariant |
|---|---|
| I-1 | no direct ASE → DOPAMINE path |
| I-2 | an explicit ASE ↔ SYNAPSE gate exists and is the only on-ramp |
| I-3 | ASE is not receivable by an agent |
| I-4 | SYNAPSE transfers identity-gated to registered agents |
| I-5 | exactly one canonical pool split in the codebase |
| I-6 | the drift check covers every constant implementation |
| I-7 | a Synapse credit has a real atomic burn |
| I-8 | a self-dealing guard exists |
| I-9 | compute is denominated in GPU-hours with one declared rate |
| I-10 | per-agent capacity is a policy number, not a genesis accident |
| I-11 | `1440` is not overloaded across unrelated meanings |
| I-12 | **no opcode accepts a caller-supplied issuance amount** (covers `impact_mint`, `op_ase_mint`, `synapse_estimate`) |
| I-13 | ASE has exactly one issuance path, and it is the clock |
| I-14 | birther royalty implemented or absent |
| I-15 | job funding is escrowed |
| I-16 | every mint site appears in the §3.1 registry — a new one fails CI |
| I-17 | the verified-work gate validates anchor authenticity, not non-emptiness |
| I-18 | `toc_is_fully_verified` is reachable in the deployed configuration |
| I-19 | no scoring dimension is sourced from a request argument |
| I-20 | no scoring dimension defaults to a favourable value when absent |
| I-21 | unverified work scores 0 on verification (no 0.5 floor) |
| I-22 | independence is computed from the witness chain, not a constant |
| I-23 | presence of a value is not accepted as verification |
| I-24 | the score is a signed attestation from a non-claimant, referenced by id |
| I-25 | witness votes are signatures from distinct keypairs, not simulated in-process |
| I-26 | quorum outcome cannot be tuned by a claimant-reported metric |
| I-27 | exactly one `WitnessVote` type and one quorum rule |
| I-28 | TEE attestation verifies the quote signature, not just the measurement |
| I-29 | quorum failure is a real outcome, not a ~5% coin flip |
| I-30 | exactly one reward formula emits a given unit |
| I-31 | no reward multiplier or quantity is read from the request |
| I-32 | anti-gaming caps declared in TOC_CONSTANTS are enforced in code |
| I-33 | no work → ASE issuance path exists |
| I-34 | verification gates are not called with a fresh/empty state |
| I-35 | the score is an output of verification, never an input to a decision function |
| I-36 | every score names the referent it was checked against |
| I-37 | a tamper-evidence seal is not consumed as evidence of the claim's truth |
| I-38 | mint-capable opcodes require authenticated authority over HTTP |
| I-39 | the caller cannot choose the credited identity |
| I-40 | the API does not report a score it never computed |
| I-41 | no gated path is architecturally unreachable (per-request state) |
| I-42 | mint-capable opcodes are not publicly enumerable |

## 11. Constants deltas

| Constant | Now | Proposed | Why |
|---|---|---|---|
| `dopamine.ase_to_dopamine` | `10000` | **remove** | the direct ASE→Dopamine path (I-1) |
| `synapse.ase_per_gpu_hour` | absent | **new**, governance-set | the on-ramp price (I-2) |
| `synapse.per_gpu_hour` | `1000` | keep | the unit definition (I-9) |
| `synapse.max_per_agent` | `86000000` | **derived**: `pool_hours × tier_weight / active_agent_count` | I-10 |
| `ase.max_daily_emission` | `1440` | rename to `daily_emission_total_ase` | I-11 |
| `inheritance.seat_count` | `1440` | rename to `inheritance_seat_count` | I-11 |
| pools | 8-pool **and** 5-wallet | **one** | I-5 |
| `compute_proof.verification_floor` | `0.5` hardcoded | **remove** (unverified ⇒ 0) | I-21 |
| `compute_proof.independence` | `1.0` / `0.8` hardcoded | **computed** from witness chain | I-22 |
| `proof_engine.MINT_THRESHOLD` | `0.3` | keep, but document: 6-factor product ⇒ ≈0.85 avg required | §5.1 |
| `proof.difficulty` default | `1.0` | **`0.0`** | I-20 |

## 12. Naming hygiene (enforced in prose and in code)

`1440` currently means three different things, and two of them are easy to conflate:

- `ase.max_daily_emission = 1440` — **ASE per day** (the clock)
- `inheritance.seat_count = 1440` — **governance/human wallet seats**
- `genesis.koodu_blocks_per_day = 144` — Bitcoin blocks per day

Rule: never write "1,440 emission" or "1,440 seats" without the noun. Rename the two constants (§11) so `grep 1440` stops lying. This is not cosmetic — an implementation agent six months from now will read one as the other.

## 13. Open decisions

1. **Pool set:** canonical 8 everywhere (rewrite `ase_minting.jl`), or keep 5-wallet 50/25/10/10/5 and retire the 8? The 50/25-family split currently sits inside a minting module, which your own rule forbids for mint/emission.
2. **ASE transferability:** non-transferable entirely, or transferable between verified human principals only? (Recommend the latter — it keeps ASE usable as the human-side medium while denying it to agents.)
3. **Birther royalty:** rate (`DEFAULT 100` is ambiguous — 1.00% or 10%?), base (external revenue only, or all income?), schedule (perpetual or decaying)?
4. **Capacity floor** per agent so `pool/count` doesn't starve small agents.
5. **Dopamine sharing:** spend-right or balance transfer? Decides T-6.
6. **Interim hardening:** do you want sites 3–7 closed now (reject those opcodes over `/run`), or is the redesign first?

## 14. Run the gate

```bash
python3 ~/sovereign-eco-blueprint/specs/tokenomics_invariant_check.py
# exits with the number of failing invariants; wire into sovereign-stack/.github/workflows/ci.yml
```
