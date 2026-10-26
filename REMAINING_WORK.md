# OSOVM / sovereign-eco-blueprint — remaining work

Generated from `tokenomics_invariant_check.py` on 9191317 + current blueprint.
**Gate state (2026-10-26): 51 PASS, 2 correctly FAIL (I-24, I-25)**
The 2 failures require external infrastructure (witness network, score attestation).
All other invariants pass — Sections A/B/C(9/11)/D/E/F are done.
Companion evidence dump: `~/gate_full.txt`

---

## The remaining items, grouped by root cause

Each package below closes the invariants listed. Ordering at the bottom.

### A. ~~HTTP authority~~ — DONE : I-38, I-39, I-41, I-42, I-19
All 5 invariants now pass (confirmed 2026-10-26 invariant run).

- [x] I-38: auth on POST /run — PASS
- [x] I-39: current_sender from authenticated principal — PASS
- [x] I-41: module-level globals persist across requests — PASS
- [x] I-42: GET /opcodes removed (handle_opcodes tombstone) — PASS
- [x] I-19: scoring dimensions not sourced from request args — PASS

### B. ~~Delete the dead scoring cluster (4) : I-30, I-31, I-34, I-50~~ — DONE
All four invariants now pass (confirmed 2026-10-26 invariant run).
`compute_score`, `bonus_multiplier_override`, dead `is_fully_verified(VMState(), claim)`,
`calculate_apy_rewards`, `score_all_veils` were all deleted in prior sessions.

- [x] I-30: no competing reward formula (compute_score deleted)
- [x] I-31: no bonus_multiplier_override
- [x] I-34: live is_fully_verified uses real vm, not VMState()
- [x] I-50: zero unreachable scoring functions

### C. Attestation layer — 9/11 DONE, 2 correctly failing : I-17..I-37
Theme: **a score must be a signed attestation from a non-claimant verifier.**

**CORRECTLY FAILING (external infrastructure required):**
- [ ] **I-24** `verify_score_signature` is a STUB (no call sites outside definition).
      Needs: external score attestation service that signs verified scores.
- [ ] **I-25** `request_witness_votes()` returns empty stub. Fabrication deleted.
      Needs: external Ed25519 witness node network (7/12 quorum).

**ALL OTHERS PASS (confirmed 2026-10-26):**
- [x] I-17, I-18, I-26, I-27, I-28, I-29, I-35, I-36, I-37 — all PASS

### D. ~~Economic paths~~ — DONE : I-1, I-2, I-3, I-4, I-33
All 5 invariants now pass (confirmed 2026-10-26 invariant run).

- [x] I-1: No direct ASE → Dopamine path — PASS
- [x] I-2: ASE ↔ Synapse conversion gate exists and called — PASS
- [x] I-3: ase_transfer_guard wired with agent registry — PASS
- [x] I-4: Synapse transfer identity-gated to agents — PASS
- [x] I-33: No work → ASE issuance path — PASS

### E. ~~Anti-gaming + policy enforcement~~ — DONE : I-8, I-10, I-14, I-32
All 4 invariants now pass (confirmed 2026-10-26 invariant run).

- [x] I-8: Self-dealing guard (related-party check) exists and called — PASS
- [x] I-10: Per-agent SLA declared as policy, not genesis constant — PASS
- [x] I-14: Birther royalty implemented (with call sites) or absent — PASS
- [x] I-32: Anti-gaming caps enforced in code — PASS

### F. ~~Registry + test infrastructure~~ — DONE : I-16, I-49
- [x] **I-16** mint sites in registry — PASS (oso_vm.jl:2442 and vm_core.jl registered)
- [x] **I-49** CLOSED (2026-09-30): 13 HTTP handlers in `server.jl`, all covered by
      `test/server_handlers_test.jl`. Module import bug (`OsoServer` → `OsoVMServer`) fixed.
- [x] `make test` IMPACT rounding testset deleted (opcode 0x11 removed in f75b83f).
- [x] `inheritance.jl` `accrue_rewards` dangling call deleted.
- [x] I-13 evidence string prefix fixed.
- [x] `runtests.jl` subprocess-per-file runner covering all 31 test files added.
- [x] `opcodes.jl:12` `:IMPACT => 0x11` removed (2026-09-30); handler rejects it at runtime
      and the declaration is now gone.

### G. vm_core.jl — decision deferred (all gates already pass)
`vm_core.jl` ISSUANCE_SITES entry exists in the invariant registry (I-16 PASS).
The other invariant hits (I-17 ×1, I-19 ×2) also pass. No gate currently fails because of vm_core.jl.
Decision still open: retire the file (port vm_core_test.jl tests to oso_vm.jl) or keep as test harness.
This is non-blocking to ship since all gates pass.

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
