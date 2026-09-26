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

So the anchor is validated for **non-emptiness, not authenticity**. `zangbeto_anchor: "x"` satisfies the entire verified-work gate. Combined with the amount override at site 8, the complete bypass is two calls:

```
1. POST /run {opcode:"GPU_CONTRIBUTION", args:{agent_id:"A", provider_id:"P",
                gpu_seconds:1, zangbeto_anchor:"x"}}
   → records toc_contributions["A"] = 1, emits GpuContribution with anchor "x"

2. POST /run {opcode:"TOC_MINT", args:{agent_id:"A", gpu_seconds:1,
                zangbeto_anchor:"x", synapse_estimate:999999999}}
   → toc_is_fully_verified passes (1 >= 1, anchor non-empty)
   → minted_synapse = 999,999,999   (caller override wins)
```

Result: ~1,000,000 GPU-hours of Synapse claimed from one GPU-second and a one-character anchor. The F1 gate, the witness rules and the TEE attestation are all downstream of a check that never actually happened.

Independently: in the Rust client path the anchor is **never set** (`bridge/arp.rs:109 zangbeto_anchor: None`; Zàngbétò is not connected in prod), so the authorized path cannot fire either. **The gated path is simultaneously unreachable from inside the ecosystem and forgeable from outside it.** That is the whole security story of the mint authority.

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
