# How to reach the endgame — build breakdown

Synthesised 2026-09-30 from `ECOSYSTEM_BLUEPRINT_2026-09-28.md`, `REMAINING_WORK.md`,
`INVARIANTS.md`, `OUTSTANDING_2026-09-28.md`, and direct verification against
`~/OSOVM`, `~/Omo-Koda2`, `~/Vantage`.

## 0. The dependency graph

Not a feature list. Each phase is blocked by the one before it:

```
0  TRUTH        the test entry point and the gate must not lie
1  AUTHORITY    the VM must not accept a caller-chosen identity
2  ATTESTATION  a score must be a signed attestation from a non-claimant
3  CURRENCY     agents earn Synapse; Àṣẹ never leaves the human side
4  ANTI-GAMING  capacity derived, caps enforced, related parties excluded
5  FIVE LINKS   VerifiedGPUWork → 0x56 → witness → authorize_toc_mint → settle
6  ENTITIES     devices and providers become principals
7  TWIN ECONOMY TSP: 31020 / 31030 → Sui IP Root → licensing
8  FULL LOOP    reality → proof → learning, no human in the path
```

The five dead links are phase 5. Everything the pasted proposal wanted to do is
phase 5 or later, and it is blocked by 0–4.

---

## Phase 0 — Truth (one sitting)

Nothing downstream is trustworthy while the verification tools themselves lie.

- Delete the `"IMPACT minting with rounding"` testset (`vm_core_test.jl:36-49`) —
  it tests opcode `0x11`, deleted in `f75b83f`.
- Fix `inheritance.jl:268` — `distribute_offering()` calls `accrue_rewards(w, ...)`,
  deleted at `:279`. A dangling call on the **primary distribution path**.
- Fix `tokenomics_invariant_check.py:516` — it hardcodes the I-13 evidence prefix
  `"unauthorized issuance sites present:"`, so **I-13 PASSES with text asserting the
  opposite**. The gate currently cannot fail on the thing it exists to catch.
- **Reconcile the gate numbers.** `REMAINING_WORK.md` says **31 failing** (exit 31,
  generated from `tokenomics_invariant_check.py` on `9191317`). `OUTSTANDING_2026-09-28.md`
  says **53 checks, 51 PASS / 2 FAIL**. Two runs, two scopes, no reconciliation —
  one of them is wrong and nobody knows which. Establish the single true number first.

**Exit test:** `make test` green; the gate's output matches what the gate actually found.

---

## Phase 1 — Authority (the root; a small project)

`server.jl` has **zero** auth-related lines.

- **I-38** `POST /run` executes mint-capable opcodes with no key, token or signature.
- **I-39** `vm.current_sender` is caller-chosen: `server.jl:154`
  `agent = string(get(body_obj, :agent, "genesis"))` → `:170`/`:244`
  `vm.current_sender = agent`. **The caller picks who gets credited.**
- **I-42** `GET /opcodes` publishes the mint-capable opcode list to anonymous callers.
- **I-41** decide the persistence story (module globals are accepted as a store by
  policy; the detector only greps `OsoVM.create_vm()`).
- **I-19** scoring dimensions (`gpu_seconds`, `f1_score_stored`) must come from
  receipts referenced by id, never from request args.

**Exit test:** a caller cannot choose who is credited, and cannot reach a mint-capable
opcode without an authenticated principal.

**Why first:** every economic invariant downstream is meaningless while the sender is
an input. Same defect class as the four silent mention gates fixed in Vantage on
2026-09-29 — mechanism built, identity check missing.

---

## Phase 2 — Attestation (the backbone; a real project)

The one sentence the whole design rests on: **a score must be a signed attestation
from a non-claimant verifier, bound to a withheld referent.** 11 of the failing
invariants are facets of this.

- **I-25** witnesses are *simulated, not signed* — `zangbeto_receipts.jl:363`
  `collect_witness_votes` fabricates `"witness-$w-$receipt_hash"` and hashes it.
  Must be separate principals signing with their own keys.
- **I-24** no signed-score mechanism exists at all.
- **I-36** no referent field — a score is unfalsifiable by construction.
- **I-37** the seal covers `receipt_hash + approvals` only, so it certifies the record
  didn't change — not that the claim is true. Bind it to the referent.
- **I-26 / I-29** the approval threshold is set by the claimant's own `f1_score`
  (`:373` `threshold = f1_score >= 0.9 ? 'd' : 'c'`): p(approve) 0.75 base, 0.8125 at
  f1≥0.9 — **a claimant cuts failures ~10× by reporting a high F1.**
- **I-27** two `WitnessVote` definitions; the quorum functions read different fields.
- **I-17** `anchor_present` is a format + non-emptiness check.
- **I-18** no internal caller passes a real anchor (`bridge/arp.rs:114`
  `zangbeto_anchor: None`) — closed from inside and forgeable from outside.
- **I-28** TEE attestation verifies the measurement field, not the quote signature.
- **I-35** a score is used as a decision input (`veilsim_scorer.jl:162`).
- **B (free win)** delete `oso_vm.jl:~670-760` — a 0-caller dead cluster carrying
  I-30, I-31, I-34, I-50. **One deletion, four invariants.**

**Note — there are two witness systems.** OSOVM's zangbeto fabricates votes. Vantage's
`witness_store.py` has real pool selection (`QUORUM = {3: 2, 5: 3}`,
`select_witness_pool` weighted by tier, wired from `jobs.py` and `tasks.py`). Decide
which is canonical before building. Note also that a `select_witness_pool` failure
on the Vantage side returns `[]` only when there are no other agents — the
"production returns empty" claim in the blueprint could not be reproduced and is
more likely "selected witnesses never cast votes."

**Exit test:** a claim's score is a signature you can verify against a pubkey that is
not the claimant's, about a referent that was withheld at submission time.

---

## Phase 3 — Currency (this is where the pasted proposal is wrong)

- **I-2 + I-1 together, or neither is coherent.** Add the Àṣẹ↔Synapse gate:
  `synapse.ase_per_gpu_hour` (governance-set) plus a mint(credit)/redeem(burn) pair;
  and delete the direct `ASE→Dopamine` path (`dopamine.ase_to_dopamine`,
  `ase_supply.jl:43 ASE_TO_DOPAMINE_RATIO = 10_000`). **This gate is the answer to
  "how does an agent pay for GPU?"** — without it the MINE verb has no funding path
  and the rental model cannot exist.
- **I-3** Àṣẹ transfers restricted to human principals. Needs a human/agent flag in
  the principal registry — *"no distinction anywhere in the token layer."*
- **I-4** Synapse transfers identity-gated to agents (`transferable=true` in
  `TOC_CONSTANTS` but no `is_agent()` check).
- **I-33** `veilsim_scorer.jl` issues **5.0–7.0 Àṣẹ per sim** from caller-supplied
  tp/fp/fn (`BASE_ASE_REWARD = 5.0`). Àṣẹ is clock-only. Route to Synapse or delete.
  This is the SIMULATE reward, already implemented — and implemented wrongly.

**Exit test:** an agent earns Synapse for work; Àṣẹ only ever reaches a human; the two
convert through exactly one governance-priced gate.

**Blocking decision:** what is the governance price `synapse.ase_per_gpu_hour`?

---

## Phase 4 — Anti-gaming and policy

- **I-10** per-agent capacity is an accident of genesis constants — pool 86e9 Dopamine
  = 8.6e6 GPU-hours, per-agent cap 8.6e7 Synapse → **only 100 agents fit at cap, target
  is millions.** Capacity must be `pool / expected_agent_count`, recomputed per epoch.
- **I-8** related-party check — buyer + GPU host + birther resolving to one principal.
- **I-32** declared-but-unenforced caps (`per_agent_epoch_cap`, `repeat_limit`,
  `sim_to_real_min_tier`) — implement at the mint gate or delete the claims.
- **I-14** birther royalty is half-wired (`royalty_rate` referenced twice, 0 payout
  sites) — implement on external revenue with decay, or drop the column.

**Exit test:** capacity is derived and scales; a related-party ring cannot route value
to itself.

---

## Phase 5 — The five links (now, and only now, denominated in Synapse)

1. **VerifiedGPUWork constructed.** The type that means "verified work" has zero
   instances in the tree (`kernel/compute/verified_work.rs:13`).
2. **COMPUTE_PROOF (0x56) computes F1.** *This is not wiring — it is reversing
   Decision A*, which left it deliberately inert rather than giving it a bypass. Also
   **Gap D**: `proof_value` is a product of six factors and `quality=0.0` kills it —
   state the composition rule, don't multiply. Also **Gap E**: the F1 threshold and
   verdict cutoffs live in module literals; they must be policy-owned.
3. **Witness quorum signs.** Depends entirely on Phase 2.
4. **`authorize_toc_mint` called.** Defined at `economics.rs:175`, requiring
   `is_fully_verified()` — and **never called**.
5. **`/api/ucx/settle` exists and pays.** It does not exist in Vantage (verified: zero
   matches). **Gap C**: the GPU/hardware provider is the party the rental model exists
   to pay and is currently unremunerated.

**Exit test:** one real job flows capture → verified work → receipt → settlement, and
money moves — Synapse to agents, Àṣẹ to human providers.

---

## Phase 6 — Entities

- **Gap B / device migration.** `device_registry.py:28`:
  `agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE`. The `CASCADE`
  means a device **cannot outlive its owner** — it is a dependent part, not a possession.
  Each device needs its own principal, a nullable/transferable owner, its own job
  history, and capability advertisement on the job board. That is a migration, not a
  feature flag.
- **Gap A — authority receipts.** `DELEGATE (0x2d)` must emit a signed **bounded**
  directive, and `DISPUTE (0x25)` must resolve against it. Without it, blame in a
  copilot chain (agent → drone) is undecidable. **This is the blocker for multi-entity
  jobs**: film crew, construction, agriculture, logistics.

**Exit test:** a lawnmower can be hired with no owner, and a two-entity job can be
adjudicated.

---

## Phase 7 — The twin economy (TSP tier 3)

Their locked order: `3.1` twin schema + gate · `3.2` capture receipt 31020 ·
`3.3` scene receipt 31030 · `3.4` proof-of-simulation · `3.5` proof-of-observation ·
`3.6` twin licensing.

Add from SplatChain (patterns only, MIT, chain-agnostic): the **two-hash pre-image
binding** (`input_hash` → `model_hash`), **device-side signing at capture**, the
**coded-frame fingerprint**, and **trust tiers mapped to capability tiers**. Vantage's
twin receipt today proves the job ran; it does not bind the raw capture to the trained
model. Note the blueprint anchors IP Roots to **Sui** while SplatChain uses Base — take
the mechanism, not the chain.

Then the physical build order (their locked sequence): VCP spec v1 → BLE/Wi-Fi
discovery daemon → RuView ESP32 adapter (**before** the robot) → M5Stack fleet →
Unitree Go2 → spatial-mining power profile → Julia CPU training + COLMAP → CesiumJS →
31020 wired to OSOVM → RuView CSI fused into the twin → 31030 IP Root → active
perception loop → temporal 4D twin.

---

## Phase 8 — Full loop

`4.4` Reality → Proof → Learning with no human intervention. Integration order:
VCP→TSP, then DIP→TSP, then DIP→VCP, then the loop.

---

## Decisions required before code

From `REMAINING_WORK.md`:
1. **I-41** — accept module-level globals as the store and fix the detector, or build
   real persistence?
2. **I-2** — what is the governance price `synapse.ase_per_gpu_hour`?
3. **I-3** — where does the human/agent flag live?
4. **I-10** — what is `expected_agent_count`, and what triggers the epoch recompute?
5. **I-14** — implement birther royalty, or drop the column?
6. **I-32** — enforce the three caps, or delete the claims?
7. **G** — retire `vm_core.jl` (**nothing loads it**, but its 39 passing tests are the
   only green suite), or own two VMs?

Added here:
8. **0x56 vs Decision A** — is COMPUTE_PROOF allowed to compute, or does the reward
   come from elsewhere? This is a governance call, not an engineering one.
9. **Which witness system is canonical** — OSOVM zangbeto (fabricates) or Vantage
   `witness_store` (real pool selection)?
10. **Splat provenance chain** — Sui (your anchor) or Base (SplatChain's), given the
    pattern is chain-agnostic.

---

## Honest magnitude

From `REMAINING_WORK.md`, and it is accurate: **B + F + parts of D are one sitting.
A is a small project. C is a real one.** "Score becomes a signed attestation bound to
a withheld referent" is the backbone of the whole design, and 11 of the 31 invariants
are facets of it. Trying to close all 31 in one pass produces renamed symbols and few
closed checks — *"that is the pattern the last four rounds already showed."*

---

## The pasted proposal, in one paragraph

It got the diagnosis right — five dead links in sequence, and the device schema is a
migration not a flag. It got two things wrong. First, it denominated **agent** rewards
in **Àṣẹ**, which is human-only (I-3) and cannot fund compute (`§3.4`, `:40`) — the
machine-side market runs on Synapse, through the I-2 gate. Second, it treated
COMPUTE_PROOF as wiring when 0x56 is inert **by decision**, and it adds a
SIMULATE→reward path onto an unreconciled opcode fork where `0x2b` means *simulation*
in Techgnosis and *token mint* in OSOVM — i.e. it wires simulation into a mint. It also
missed the three phases that actually gate it: the VM accepts a caller-chosen identity
(Phase 1), there is no signed attestation (Phase 2), and the token layer cannot tell a
human from an agent (Phase 3).
