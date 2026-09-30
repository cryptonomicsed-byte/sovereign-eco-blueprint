# OSOVM / sovereign-eco-blueprint — remaining work

Generated from `tokenomics_invariant_check.py` on 9191317 + current blueprint.
Gate: **31 originally failing**. Closed: I-12, I-13, I-38, I-39, I-49 + E-tier-registry.
After I-24/I-25 gate tightening (2026-09-30), **2 additional gates now correctly FAIL**
(were passing vacuously — see sections A and C).
Companion evidence dump: `~/gate_full.txt`

---

## The remaining items, grouped by root cause

Each package below closes the invariants listed. Ordering at the bottom.

### A. HTTP authority — partially closed (3 remaining) : I-41, I-42, I-19
I-38 (auth on POST /run) and I-39 (current_sender from authenticated principal) are CLOSED.
`server.jl` now has `authenticate()` wired to all mint-capable endpoints.

- [ ] **I-38** add auth to `POST /run` — API key → authenticated principal. Today it
      executes mint-capable opcodes with no key, token or signature.
- [ ] **I-39** derive `vm.current_sender` from the authenticated principal.
      Today: `server.jl:154` `agent = string(get(body_obj, :agent, "genesis"))`
      → `:170` / `:244` `vm.current_sender = agent`. The caller picks who gets credited.
- [ ] **I-42** stop publishing the mint-capable opcode list to anonymous callers
      (`server.jl:49-51` resolves `GET /opcodes` from `CORE_OPCODES`/`EXPANSION_OPCODES`).
- [ ] **I-41** decide the persistence story. Module-level stores already exist and work
      (`_TOC_CONTRIBUTIONS_GLOBAL`, `_RECEIPT_STORE_GLOBAL`, `_SYNAPSE_BALANCE_GLOBAL`,
      `_SYNAPSE_MINTED_GLOBAL`), but the detector only greps `OsoVM.create_vm()` in
      `server.jl:169/243/520`. Either the detector is stale or a real store is needed.
      **Decision required.**
- [ ] **I-19** scoring dimensions (`gpu_seconds` oso_vm.jl:2343, `f1_score_stored` :2346,
      vm_core.jl:456/507) must come from verified receipts referenced by id, never args.
      Depends on A + C.

### B. Delete the dead scoring cluster (4) : I-30, I-31, I-34, I-50
Highest leverage item in the list — **one deletion, four invariants.**
The block `oso_vm.jl:~670-760` is 0-caller dead code carrying four defects:

- [ ] `compute_score(claim::Dict)` :735 — duplicate reward formula **with a ladder**
      (I-30: two formulas, documented ladder is not the one COMPUTE_PROOF uses)
- [ ] `bonus_multiplier_override` :750-752 — caller-supplied multiplier (I-31)
- [ ] `is_fully_verified(VMState(), claim)` :736 — empty VM makes the gate vacuous (I-34)
- [ ] I-50 zero-reference scoring functions: `calculate_apy_rewards`, `compute_score`,
      `score_all_veils`, +1

### C. One attestation layer (11) : I-17, I-18, I-24, I-25, I-26, I-27, I-28, I-29, I-35, I-36, I-37
The biggest package, and a genuine build. Theme: **a score must be a signed attestation
from a non-claimant verifier, bound to a withheld referent.**

- [ ] **I-25** (2026-09-30: gate now correctly FAILs) `collect_witness_votes` fabrication
      was deleted; `request_witness_votes()` returns empty stub `AntispamWitnessVote[]`.
      Gate now requires positive presence of `ed25519_verify|verify_witness_signature`.
      The fabrication is gone but the real network is not yet wired.
- [ ] **I-26** approval threshold is set by the claimant's own `f1_score`.
- [ ] **I-29** consequence: p(approve)=0.75 base → claimant cuts failures ~10× by
      reporting a high F1. Failure is noise, not a threshold.
- [ ] **I-27** two `WitnessVote` definitions; both quorum fns read different fields
      (`veilos_antispam.jl:303` `v.vote` vs `zangbeto_receipts.jl:395` `v.approved`).
- [ ] **I-24** (2026-09-30: gate now correctly FAILs) `verify_score_signature` exists
      as a STUB returning `false` — no call sites outside the function definition.
      Gate now requires call_sites > definition_sites.
- [ ] **I-36** no referent field — a score is unfalsifiable by construction.
- [ ] **I-37** seal covers `receipt_hash + approvals` only (:158, :416), so it certifies
      the record didn't change, not that the claim is true. Bind to the referent.
- [ ] **I-17** anchor authenticity — `anchor_present` is format + non-emptiness.
      `oso_vm.jl:648`, `vm_core.jl:444`.
- [ ] **I-18** no internal caller passes a real anchor: `bridge/arp.rs:114`
      `zangbeto_anchor: None`. Closed from inside AND forgeable from outside.
- [ ] **I-28** TEE attestation verifies the measurement field, not the quote signature.
- [ ] **I-35** score used as an input to a decision: `veilsim_scorer.jl:162`
      `calculate_reward(f1)`, `:188`, and the same f1→threshold in `zangbeto_receipts.jl:373`.

### D. Economic paths — remove one, build the on-ramp (5) : I-1, I-2, I-3, I-4, I-33
- [ ] **I-1** delete the direct ASE→Dopamine path: `dopamine.ase_to_dopamine` (spec
      line 679 says remove) and `ase_supply.jl:43` `ASE_TO_DOPAMINE_RATIO = 10_000`,
      used at :289-292.
- [ ] **I-2** add the ASE↔Synapse gate: new `synapse.ase_per_gpu_hour`
      (governance-set, spec line 680) + mint(credit)/redeem(burn) pair.
      **Do I-1 and I-2 together or neither is coherent.**
- [ ] **I-3** ASE transfers restricted to human principals — needs a human/agent flag
      in the principal registry (currently no distinction anywhere in the token layer).
- [ ] **I-4** Synapse transfers identity-gated to agents
      (`transferable=true` in TOC_CONSTANTS but no `is_agent()` check).
- [ ] **I-33** `veilsim_scorer.jl` issues 5.0–7.0 Àṣẹ per sim from caller-supplied
      tp/fp/fn (`:28` `BASE_ASE_REWARD = 5.0`, `:161`). Àṣẹ is clock-only —
      route this to Synapse or delete it. NOTE: the `total_ase_minted →
      total_ase_scored` rename changed the name, not this behaviour.

### E. Anti-gaming + policy enforcement (4) : I-8, I-10, I-14, I-32
- [ ] **I-8** related-party check: buyer + GPU host + birther resolving to one principal.
- [ ] **I-10** per-agent capacity is an accident of genesis constants —
      pool 86e9 Dopamine = 8.6e9 Synapse = 8.6e6 GPU-hours; per-agent cap 8.6e7
      Synapse → **only 100 agents fit at cap, target is millions.**
      Make capacity = pool / expected_agent_count, recomputed each epoch.
- [ ] **I-14** birther royalty half-wired: `royalty_rate` referenced 2×, 0 payout sites
      (`Vantage/backend/agents.py:10452`, `:10511`). Implement on external revenue with
      a decay schedule, or drop the column.
- [ ] **I-32** declared-but-unenforced caps in TOC_CONSTANTS: `per_agent_epoch_cap`,
      `repeat_limit`, `sim_to_real_min_tier`. Implement at the mint gate or delete.

### F. Registry + test infrastructure (1 remaining + non-gate)
- [ ] **I-16** mint sites not in the registry: `oso_vm.jl:2442`, `vm_core.jl:531`, `:556`.
- [x] **I-49** CLOSED (2026-09-30): 13 HTTP handlers in `server.jl`, all covered by
      `test/server_handlers_test.jl`. Module import bug (`OsoServer` → `OsoVMServer`) fixed.
- [x] `make test` IMPACT rounding testset deleted (opcode 0x11 removed in f75b83f).
- [x] `inheritance.jl` `accrue_rewards` dangling call deleted.
- [x] I-13 evidence string prefix fixed.
- [x] `runtests.jl` subprocess-per-file runner covering all 31 test files added.
- [x] `opcodes.jl:12` `:IMPACT => 0x11` removed (2026-09-30); handler rejects it at runtime
      and the declaration is now gone.

### G. The parallel VM — one decision, ~5 hits
`vm_core.jl` is **not loaded by anything**; only `test/vm_core_test.jl` includes it.
It accounts for I-16 ×2, I-17 ×1, I-19 ×2. Retiring it is the session's established
move (duplicate implementations are deleted, not hand-patched — cf. simulation_scoring.jl).

**But the trade-off is real:** vm_core_test.jl's 39 passing tests are the only working
test coverage in the repo, and they test the module nothing loads. Retiring vm_core.jl
without porting loses your only green suite.
- [ ] Decide: retire `vm_core.jl` (and port/delete its tests), or wire it and own two VMs.

---

## Decisions needed before code (7)
1. **I-41** — accept the module-level globals as the store and fix the detector, or
   build a real persistence layer?
2. **I-2** — what is the governance price `synapse.ase_per_gpu_hour`?
3. **I-3** — where does the human/agent flag live? (no principal registry distinction today)
4. **I-10** — what is `expected_agent_count`, and what triggers the epoch recompute?
5. **I-14** — implement birther royalty, or drop the column?
6. **I-32** — enforce the three anti-gaming caps, or delete the claims?
7. **G** — retire `vm_core.jl`, or own two VMs and keep the tests where they are?

## Sequence
1. **F (infra)** — delete the IMPACT testset, fix the dangling inheritance call, fix the
   I-13 evidence string. Gets `make test` green and the signal honest BEFORE the push.
   Nothing else is trustworthy while the test entry point lies.
2. **B (dead cluster)** — one deletion, four invariants. No dependencies.
3. **A (auth)** — the root. Blocks C's meaningfulness (a verifier must be a principal).
4. **C (attestation)** — the real build. 11 invariants, all one coherent project.
5. **D, E** — economic paths and policy. Need A + the I-3 principal flag.
6. **G** — last, once C/A have settled what actually needs a second VM.

## Honest magnitude
B + F + parts of D are a single sitting. **A is a small project. C is a real one** —
"score becomes a signed attestation bound to a withheld referent" is the backbone of
the whole design, and 11 of the 31 invariants are facets of it. Trying to finish all
31 in one pass will produce a lot of renamed symbols and few closed checks; that is
the pattern the last four rounds already showed.
