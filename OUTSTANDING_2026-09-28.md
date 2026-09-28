# EVERYTHING STILL TO COMPLETE — verified state, 2026-09-28

Basis: direct source verification this session. Every item marked ✓ VERIFIED
was re-checked against the tree in this pass. Items marked ⚠ INHERITED come
from the repo's own audit docs and were not independently re-verified here.

Current gate: **53 checks, 51 PASS / 2 FAIL** (I-4, I-18)
Current CI: **green** — but see §3, it runs no tests.

---

# §1 — BLOCKING (two invariants, both external infrastructure)

Neither is a code problem. Both need something that does not exist yet.

| ID | Invariant | What is missing |
|----|-----------|-----------------|
| **I-4** | Synapse transfers identity-gated to registered agents | **Vantage principal registry API.** `is_agent()` cannot return correct results without it. There is no human/agent distinction anywhere in the token layer. |
| **I-18** | The gated issuance path is reachable in the deployed config | **Zàngbétò `POST /anchor` endpoint** (tracked as E-53). `bridge/arp.rs:114` passes `zangbeto_anchor: None`; Zàngbétò's bus client returns verdicts but exposes no anchor id. Fix path: make `build_receipt` async, call `review_act()`, use the returned `verdict_id` as the anchor. |

**These two block**: Essay B's graduated human/agent quorum tiers, and every
independence/anti-Sybil mechanism (§5).

---

# §2 — THE ECONOMIC ENFORCEMENT LAYER (the tokenomics gate)

## 2.1 — Found this session, all verified ✓

**A. The per-agent cap is a LIFETIME cap wearing an epoch name.**
`PER_AGENT_EPOCH_CAP` accumulates forever — nothing resets `_EPOCH_TALLY_GLOBAL`
or `_EPOCH_COUNT_GLOBAL` (grep for `empty!`/`delete!`/clear: zero hits). The code
admits it: `oso_vm.jl:2381` — *"epoch boundary reset is TODO"*.
```
50,000,000 Dopamine ÷ 10,000 per GPU-hour = 5,000 GPU-hours, then capped forever
```
- [ ] Implement the epoch rollover, **or** rename to `PER_AGENT_LIFETIME_CAP` and say so in the invariant.

**B. The enforced cap and the declared policy are 581× apart and unconnected.**
```
enforced:  _ANTIGAMING["per_agent_epoch_cap"] = 50,000,000 Dopamine
declared:  expected_agent_count=1M => 8,600 Syn/agent = 86,000 Dopamine/epoch
           (this is what I-10's PASS evidence cites)
```
`EXPECTED_AGENT_COUNT` is declared at `constants.jl:153`, exported at `:28`, and
**read by nothing.** The comment above it claims *"per-agent epoch cap =
dopamine_genesis_pool / expected_agent_count (recomputed each epoch)"* — no code
performs that division.
- [ ] Derive `PER_AGENT_EPOCH_CAP` from `EXPECTED_AGENT_COUNT`
- [ ] Make I-10 assert the derived value equals the value the guard uses

**C. COMPUTE_PROOF is still inert — and now for a worse reason.**
```julia
oso_vm.jl:2500  quality = clamp(Float64(get(receipt_record, "f1_score", 0.0)), 0.0, 1.0)
```
`f1_score` was **deliberately removed** from the receipt by I-19. So this read
always yields the `0.0` default. `proof_value = difficulty × quality × …` is a
product, so it is always 0.0 and `mint_eligible` always false.
- [ ] Reconcile: either restore a measured quality source, or delete the factor and say the proof is 5-dimensional
- Note: this was **Decision A** (leave inert, no bypass) — that decision stands; this is the record that it is still the state.

**D. `novelty = 1.0` is hardcoded** (`oso_vm.jl:2515`) — a pinned no-op factor in the product.

**E. The three new ledgers have no size cap or eviction** ✓
```
_EPOCH_TALLY_GLOBAL[agent_id]  — one entry per agent, forever
_EPOCH_COUNT_GLOBAL[job_id]    — one entry per job_id, forever  ← worst: per-job, attacker-influencable
_TIER_REGISTRY_GLOBAL          — populated by the Vantage bridge
```
Same memory-DoS shape already noted for `_RECEIPT_STORE_GLOBAL` and
`_TOC_CONTRIBUTIONS_GLOBAL`. Four globals, no eviction, all caller-keyed.
- [ ] Add a size cap / eviction policy to all of them

## 2.2 — Carried from the invariant finish-list (REMAINING_WORK.md)

- [ ] I-3 — ASE transfers human-only: needs the same principal registry as I-4
- [ ] I-14 — birther royalty: `compute_birther_royalty(rate, 0.0)` with revenue hardcoded; adjacent comment says "stub until human-originated revenue is tracked"
- [ ] I-17 — `anchor_present()` is format + non-emptiness (≥8 chars, no whitespace); no Ed25519
- [ ] I-25 — witness network: `request_witness_votes` returns empty → quorum fails 100%
- [ ] I-26 / I-29 — approval rate derived from the claimant's own reported F1
- [ ] I-27 — two witness-vote types still coexist (`AntispamWitnessVote`, `WitnessVote`)
- [ ] I-28 — TEE quote: measurement checked, signature not
- [ ] I-32 — `_ANTIGAMING` dict exists so TOML keys appear as string literals; see §2.1A/B
- [ ] I-35 — score used as an input to a decision (`veilsim_scorer.jl:162`)
- [ ] I-36 / I-37 — `referent_id` exists and the seal binds it, but "must be set by a non-claimant" is a **comment, not a check**
- [ ] I-38 / I-39 — `server.jl` auth: `current_sender` from a request field
- [ ] I-41 — module-level globals accepted as persistence by policy; the detector was relaxed rather than the store hardened
- [ ] I-49 — passes on symbol references in `test/`, not on tests that execute (see §3)

---

# §3 — TEST INFRASTRUCTURE (the largest systemic gap) ✓

**CI runs no Julia test at all.** `.github/workflows/invariants.yml` does:
checkout ×5 → install Julia → instantiate → **load-check (`include`)** → run gate
→ hard gate. That is the entire Julia execution.

**31 test files exist in `test/`. Three are referenced anywhere:**
```
referenced:   vm_core_test.jl · server_handlers_test.jl · determinism_real.jl
never run:    28 files
```
- [ ] **Build `runtests.jl`** covering all test files (the Makefile comment already says this is a TODO)
- [ ] **Add a CI step that runs the test suite**, not just the load-check
- [ ] Note: `make test` cannot run on Termux at all — the Julia binary is broken there (`unexpected e_type: 2`). Tests must run on the VPS or in CI.

**Why this matters more than any single invariant:** three load-breaking breaks
and one runtime `MethodError` shipped in this session because no CI step loads or
executes the VM. A test that is never run and a test that does not exist are the
same thing to a deploy.

---

# §4 — THE ECONOMIC ENGINE (designed, not connected) ✓

Everything below is verified still true in this pass.

- [ ] **`VerifiedGPUWork` is never constructed.** Zero instances in the tree. The type that means "verified work" has never been instantiated.
- [ ] **`authorize_toc_mint()` is never called.** The Rust gate requiring `is_fully_verified()` (osovm_proof + witnesses + zangbeto receipt + hardware attestation) has never been entered.
- [ ] **`anchor_present()` is the only live gate** on GPU_CONTRIBUTION — a format check. `VANTAGE_URL` is read and never set anywhere.
- [ ] **The hardware provider is never paid.** `provider_id` is checked for distinctness (`check_self_deal`) then never credited. `resource_meter.jl`'s `AgentBalance` has no provider field; `provider_leaderboard` returns `agent_id`; the mint credits `vm.synapse_balance[agent_id]`.
- [ ] **`/api/ucx/settle` does not exist in Vantage** — verified zero hits. It is the endpoint the constitution (`§3.4`, flow diagram) names as the destination for the ComputePool fraction (15% of every emission).
- [ ] **No GPU market exists**: no listing/discovery, no offer, no price, no order, no lease primitive. `§8 Dynamic pricing` in the tokenomics spec is formulae in prose only.
- [ ] **No link from GPU contribution to LLM funding** — zero hits for `llm_cost` / `fund_llm` / `llm_budget` / `llm_credit`.
- [ ] **`ifa_compiler_bridge.jl` does not invoke the Techgnosis compiler** and is not loaded by `server.jl` or `oso_vm.jl`.

---

# §5 — THE TRUST / ATTESTATION LAYER

- [ ] **Authority receipts do not exist.** An action receipt says *"entity X did Y"*. An authority receipt would say *"A commanded B within bounds [lo,hi] until T"*. Without it, blame across a delegation chain (agent copilots drone → drone errs) is **undecidable**. `DELEGATE (0x2d)` exists; it emits no bounded directive; `DISPUTE (0x25)` cannot resolve against bounds that were never recorded.
- [ ] **Devices are possessions, not entities.** `agent_devices.agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE` — a mower cannot accept a job, sign a receipt, or be blamed. `class device` exists in Ọ̀ṢỌ́; the schema disagrees.
- [ ] **No independence-domain registry.** The whole independence signal is `independence = provider_id != agent_id ? 1.0 : 0.0` plus a 0.0 stub for circular supply. No ownership, operator, hardware lineage, network, funding, or credential-authority model. This is the prerequisite for Sybil resistance and for §1's tiers.
- [ ] **The composition rule is unwritten.** `proof_value` is a product of six factors and is 0.0 today because one is uninstrumented — a live demonstration of what happens when the rule is multiplication. Any per-factor combination (Jev judgments, trust weights) must state the rule, and it must not be a plain product.
- [ ] **Thresholds are not policy-owned.** Three module literals: `F1_THRESHOLD` (veilos_antispam), `score >= 55/35` (signals.py), `PUMPFUN_SCAN_CONVICTION = 0.72` (Vantage config, the one with the auto-order side effect).
- [ ] **Jev calibration is unmeasured** — no key. Primitives and pricing verified from docs; calibration is not. This gates any Jev integration.

---

# §6 — ECOSYSTEM CONFLICTS (each needs a decision, not code)

1. **The opcode space has FORKED from Techgnosis** ✓ verified. 7 opcodes implemented; 5 collide:
```
0x1f  MERKLE_ROOT        vs  RECEIPT
0x28  SABBATH            vs  NONREENTRANT
0x29  NONREENTRANT       vs  REQUIRE            ← reentrancy guard → assertion no-op
0x2a  GENESIS_FLAW_TOKEN vs  EMIT
0x2b  VEIL               vs  GENESIS_FLAW_TOKEN ← simulation → token mint
```
   Latent (nothing loads the bridge) but it sits on a mint and a security guard. **Blocks any new opcode section**, including entertainment.
2. **Two architectures**: `protocol-layer-synthesis.md` = 7 planes (incl. Twin&Simulation, Sui in Memory); `organism-architecture.md` = 6 planes (neither). Pick one.
3. **The canonical jury repo is on the retired account**: `Twelve-thrones` remote is `Bino-Elgua/Twelve-thrones`. Same for `Evil-twin`, `Vanity-eth-`.
4. **The constitution contradicts its own constants**: `THREE_TIER_ECONOMIC_CONSTITUTION.md:171-174` gives pool splits that disagree with `TOC_CONSTANTS.toml` and the running code on **5 of 8 pools**. Nothing checks prose against constants.
5. **Àṣẹ cannot fund GPU rental**: 216 GPU-h/day fixed (ungrowable) vs Dopamine's 8.6M elastic. Constitution `:40` and `§3.4` forbid it explicitly.
6. **`omokoda-agent` `.gitmodules` points at the retired account** for two submodules (`absorbed/lang/vibe` → `Bino-Elgua/vibe-lang`, `study/Claude-2` → `Bino-Elgua/Claude-2`).
7. **`sovereign-eco-blueprint` has both `master` and `main`**; the blueprint is on `master` only. `main` may be stale.

---

# §7 — PROTOCOL LAYER (⚠ inherited from ecosystem-audit)

Per `ecosystem-audit/ECOSYSTEM_AUDIT_INDEX.md`:
```
DIP       BROKEN      (types solid, crypto broken)
ARP       PARTIAL
Witness   BROKEN
VCP       IMPLEMENTED
```
- [ ] DIP crypto
- [ ] ARP completion
- [ ] Witness node/broker
- [ ] Confirm the audit is still current (it predates this session's work)

---

# §8 — BUILD ORDER TO THE ENDGAME (Tier 0 → 4.4)

**Tier 0 — Foundations**
- [ ] 0.1 Canonical Types (`sovereign-types`)
- [ ] 0.2 DID / Identity Root — agent birth, stable DID

**Tier 1 — DIP**
- [ ] 1.1 Envelope + Router · 1.2 Identity Document · 1.3 Nostr adapter · 1.4 MCP adapter · 1.5 A2A adapter · 1.6 Meshtastic adapter

**Tier 2 — VCP**
- [ ] 2.1 Manifest schema · 2.2 Handshake · 2.3 Discovery daemon
- [ ] **2.4a RuView ESP32 adapter — FIRST ($9/node, immediate value)**
- [ ] 2.4b Bruce M5Stack fleet (BLE → Hive Mind) · 2.4 Unitree Go2
- [ ] 2.5 Session + commands · 2.6 Session receipt · 2.7 Revocation + mesh

**Tier 3 — TSP**
- [ ] 3.1 Twin schema + gate · 3.2 Capture receipt 31020 · 3.3 Scene receipt 31030 · 3.4 Proof-of-simulation · 3.5 Proof-of-observation · 3.6 Twin licensing

**Tier 4 — Integration**
- [ ] 4.1 VCP→TSP · 4.2 DIP→TSP · 4.3 DIP→VCP
- [ ] **4.4 FULL LOOP** — Reality → Proof → Learning, no human intervention

**Physical layer build order**
- [ ] VCP spec v1 → discovery daemon → RuView → M5Stack → Go2 → spatial-mining power profile → pipeline Phase A → CesiumJS ≥1.35 → 31020 wired → CSI fused → 31030 → active perception → temporal 4D

---

# §9 — DECISIONS NEEDED (cannot be coded past)

1. **Opcode fork** — which space wins, Techgnosis or OSOVM?
2. **7-plane vs 6-plane** — which architecture is canonical?
3. **Àṣẹ vs Synapse for GPU** — human leg Àṣẹ, machine leg Synapse?
4. **Epoch rollover** — implement it, or rename to lifetime?
5. **COMPUTE_PROOF** — restore a quality source, or declare the proof 5-dimensional?
6. **`main` vs `master`** on sovereign-eco-blueprint — which is the default?
7. **TradingOS** — `archive/apps-services-infra-layout` (has the unique `infra/`) vs the remote's `packages/` build. Main sits 1/6 diverged.
8. **`vm_core.jl`** — retire it (and lose the repo's only working test suite until ported) or own two VMs?

---

# §10 — IN ONE LINE PER LAYER

```
ECONOMY       designed, gated on paper, not connected. Provider never paid.
              /api/ucx/settle missing. No market. Cap is lifetime, mislabeled epoch,
              enforcing 581x the declared policy, reading a field I-19 removed.
TRUST         witnesses are stubs; no authority receipts, so blame is undecidable;
              devices are possessions; independence is one string compare.
TESTS         CI runs zero tests. 28 of 31 test files never execute.
PROTOCOLS     DIP broken, ARP partial, Witness broken, VCP done.
CONFLICTS     6 open, 2 of them (opcode fork, plane count) block all new work.
ENDGAME       Tier 0 barely started. 4.4 (the full loop) is the finish line.
```

**Highest-leverage single item:** `runtests.jl` + a CI step that runs it. Every
other item on this list is unverifiable until a test suite actually executes —
and five separate defects shipped this session precisely because nothing did.
