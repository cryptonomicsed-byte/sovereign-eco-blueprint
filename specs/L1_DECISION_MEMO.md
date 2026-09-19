# L1 Consensus Decision Memo
**Status: OPEN — decision required before Phases 15.4, 20.1, 23, 24, 25 begin**
**Written: 2026-09-16. Gatekeepers: Phases 15.4, 20.1, 23.x, 24.x, 25.3–25.8, 26.3–26.7, 27.x**

---

## The One Reason We're Even Having This Conversation

**Censorship resistance.**

Every targeted market in this ecosystem — Cuba, sub-Saharan Africa, the Philippines — is a
jurisdiction where a US-adjacent foundation, OFAC sanction pressure, or a hosting provider's
terms-of-service can freeze addresses on Sui, Arbitrum, or any other permissioned validator set.
That is not paranoia; it is documented history (Tornado Cash, Ethereum OFAC blocking, Sui
Foundation reserve control).

A sovereign L1 is the only architecture where no external party can be pressured to freeze a
user's wallet or black-hole an agent's identity. That is the argument. Everything else — "we
want our own chain," "more control," "better performance" — is not a reason.

If censorship resistance is not a concrete operational requirement today, the correct answer is:
**do not build the L1 yet**. The entire ecosystem runs on Sui AIO today and can ship the sector-
agent deployment economy this quarter without a chain.

---

## What We Already Have (Does Not Change Under Any Path)

- OSOVM Julia VM (47 .jl files) + HTTP server: the state machine is real
- AgentState (lifecycle FSM + chain-of-custody) + WorkObject (9-state FSM): the L1 objects exist
- oso-parser + oso-compiler + oso-sdk (Rust): the language layer is real
- OSO-IR schema + validator + 6 examples: the IR is real
- AIO on Sui (deployed): the economy runs now
- OSOVM_L1_SPEC.md: the design is thorough and well-reasoned

None of this work is wasted under any path. The state machine is reusable whether it runs as a
service, a rollup, or a full chain.

---

## Four Paths

### Path A — Stay on Sui (0 months additional)
Keep AIO. Run OSOVM as a verifiable off-chain service. Add a receipt anchor (emit a Sui event
per verified WorkClaim so the chain of custody is on-chain even if execution is off-chain).

**Gain:** Ship everything this quarter. No ops burden.  
**Risk:** Subject to Sui Foundation pressure and OFAC reach. A freeze costs us our entire
targeted market in one letter.  
**Verdict:** Correct for MVP. Wrong for mission.

### Path B — Sovereign Rollup (~8–16 weeks) ← RECOMMENDED
Use Celestia (or Rollkit) for data availability and consensus. Implement the OSOVM ABCI app
as the rollup state machine. Settle proofs on Celestia. Keep AIO on Sui as the economy layer;
bridge when needed.

**Gain:** Censorship resistance on the DA layer. No need to run a validator set. The
state machine work is ~80% already done. The 7 Cosmos modules become rollup state handlers
instead of full x/ modules — same code, lighter infra. Full sovereignty on execution.  
**Risk:** Bridge complexity. Celestia is still maturing. Rollup exit games need design.  
**Effort:** ~8–16 weeks to a working devnet. This is ~6× less than Path D.  
**Verdict:** Best value. Aligns with "add layers, don't replace" principle. Defers validator
ops until the ecosystem has revenue to fund them.

### Path C — Cosmos Appchain via Ignite (~16–24 weeks)
Scaffold `osovm-chain` with Ignite. Implement 7 modules (x/agent, x/work, x/capability,
x/evidence, x/reputation, x/device, x/economy). Wire OSOVM as the ABCI app. Run a devnet.

**Gain:** Full censorship resistance + sovereign validator set + Cosmos IBC interop.  
**Risk:** Validator bootstrapping problem. IBC relayer ops. Cosmos SDK dependency tree
(large, complex, Go-heavy — cannot build on ARM64 Android; must use x86 VPS).  
**Effort:** ~16–24 weeks to a working devnet. Full testnet is another 4–8 weeks.  
**Verdict:** Correct eventual destination if rollup proves insufficient. Not the right
first step — defer until rollup is live and censorship resistance is proven.

### Path D — Full Custom Cosmos L1 (~18–30 months solo)
Everything in Path C plus custom consensus parameters, custom validator economics, custom
block explorer, wallet integration, bridge work.

**Verdict:** Out of scope until Path C is proven and funded.

---

## Effort Reality Check

| Item | Path B | Path C |
|------|--------|--------|
| State machine (OSOVM ABCI) | 2–4 weeks | 2–4 weeks |
| 7 x/ modules | — | 8–16 weeks |
| Rollup DA + settlement | 2–4 weeks | — |
| Devnet | 2–4 weeks | 4–8 weeks |
| Testnet | 2–4 weeks | 4–8 weeks |
| Validator/RPC/explorer | — (Celestia provides) | 4–8 weeks |
| **Total to devnet** | **8–16 weeks** | **16–24 weeks** |

Toolchain reality: Go 1.26.4 is installed. Ignite is NOT. Julia VM is broken on ARM64
(wrong arch binary). All chain work must run on the x86 VPS (2.25.70.156). Budget accordingly.

---

## GPU.ai Fine-Tune Budget Note

$5 credit at $0.49/hr (A40) = ~10 hours of compute. Phase 28.1 (Mycelium QLoRA,
2,949 traces, 3B base model) should complete in 2–4 hours on an A40. Run it.
The fine-tuned GGUF brain is chain-independent and unblocks Phase 29.

---

## Decision Required

Mark the chosen path here and update Phase 15.4 in MASTER_TODO accordingly.

- [x] **Path A** — Stay on Sui (MVP only; accept censorship risk)
- [ ] **Path B** — Sovereign rollup via Celestia/Rollkit
- [ ] **Path C** — Cosmos appchain via Ignite
- [ ] **Path D** — Full custom L1 (future)

**Chosen:** Path A — Stay on Sui  
**Rationale:** No users yet; censorship resistance is not an operational requirement today. OSOVM runs as a verifiable off-chain service; WorkClaim receipts anchored to Sui. Revisit when ecosystem has paying users or a concrete jurisdiction pressure.  
**Target devnet date:** N/A — defer indefinitely until trigger condition fires

---

## What Unlocks Immediately After Decision

| Phase | What | Depends on |
|-------|------|-----------|
| 15.4 | Chain scaffold (rollup or Cosmos) | This decision |
| 20.1 | ABCI EndBlock Àṣẹ emission | 15.4 |
| 23.x | IR → Move compiler + host env | 15.4 |
| 24.x | WASM backend | 15.4 |
| 25.3–25.8 | 6 native contract classes | 23/24 |
| 26.3–26.7 | oso toolchain (linter/simulator/security/deployer) | 15.4 |
| 27.x | 3 reference dApps | 25/26 |
| E10 | Àṣẹ↔USDC on/off ramp | 20.1 (or Sui bridge) |

Everything else in the ecosystem (phases 7–14, 16, 18–19, 21–22, 28–29, all OS work)
is **chain-independent** and can ship now.
