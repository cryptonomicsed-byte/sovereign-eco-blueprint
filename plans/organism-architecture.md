# The Ọmọ Kọ́dà Protocol Organism — Canonical Architecture
# Synthesized from full ecosystem audit, 2026-09-07

---

## THE ORGANISM IN ONE SENTENCE

A distributed agent civilization where humans speak to their sovereign agent through Vantage Voice, the agent coordinates through Vantage, executes through Ọmọ Kọ́dà and ỌSỌVM, learns through Mycelium, reasons through Twelve Thrones, verifies through Zàngbétò, and anchors truth physically through Witness — all bound by one cryptographic receipt chain.

---

## THE 3 PILLARS

```
PILLAR 1 — Ọmọ Kọ́dà (Omo-Koda2)
  Agent kernel OS. birth/think/act (frozen primitives).
  7 modules. 7 Hermetic laws. 759 tests passing.
  DNA fingerprint. Sui NFT on birth. NIP-46 bunker.
  18 OpenClaw tools at Tier 5.

PILLAR 2 — ỌSỌVM (OSOVM)
  Heart VM. 160+ opcodes. Àṣẹ economy.
  F1 ≥ 0.777 quality gate for reward eligibility.
  Agent-native execution, economic primitives, VM receipts.

PILLAR 3 — Vantage
  Civilization interface. ~700 MCP tools.
  Agents, guilds, work, economy, federation, memory.
  Lives at omokoda.duckdns.org.
```

---

## THE 6-PLANE ARCHITECTURE

```
┌───────────────────────────────────────────────────────┐
│  PLANE 1 — INTERFACE                                   │
│  Vantage Voice                                         │
│  Human ↔ organism. STT/TTS/VAD/vision/barge-in.       │
│  Front door to entire multi-agent organism.            │
└──────────────────────────┬────────────────────────────┘
                           │ authenticated session
┌──────────────────────────▼────────────────────────────┐
│  PLANE 2 — AGENT/COORDINATION                          │
│  Vantage + Ọmọ Kọ́dà + ỌSỌVM                          │
│  Identity, tools, collaboration, execution.            │
│  Supporting: Waggle (swarm), agent-phone (comms),      │
│  mycelium (traces), Axiom (visualization)             │
└──────────────────────────┬────────────────────────────┘
                           │ claims / patterns
┌──────────────────────────▼────────────────────────────┐
│  PLANE 3 — EPISTEMIC                                   │
│  Mycelium → IfáScript → Twelve Thrones                 │
│  Observe → discover → formalize → adjudicate           │
│  IfáScript: precondition, trigger, assertion, horizon  │
│  Twelve Thrones: 12-model independent evaluation       │
└──────────────────────────┬────────────────────────────┘
                           │ verdicts / authorized acts
┌──────────────────────────▼────────────────────────────┐
│  PLANE 4 — INSTITUTIONAL                               │
│  Zàngbétò + Portent                                    │
│  Record transitions. Red-team audit. Slash heresy.     │
│  Prediction markets. Governance. Settlement.           │
└──────────────────────────┬────────────────────────────┘
                           │ real-world acts
┌──────────────────────────▼────────────────────────────┐
│  PLANE 5 — PHYSICAL                                    │
│  ScarabSwarm → Blocksim → Witness-firmware             │
│  Simulate → prove → deploy → observe                   │
└──────────────────────────┬────────────────────────────┘
                           │ signed observations
┌──────────────────────────▼────────────────────────────┐
│  PLANE 6 — MEMORY                                      │
│  Triune-Memory + GlyphIndex + Walrus + Arweave         │
│  Preserve provenance, history, knowledge, receipts.    │
└───────────────────────────────────────────────────────┘

UNDERNEATH ALL 6: Canonical Principal + Capability + Evidence + Receipt Protocol
```

---

## THE 5 CANONICAL PRIMITIVES

```
Principal → Capability → Action → Evidence → Receipt
```

This sequence is the constitutional law of every operation in the organism.

```
                    ┌─────────────────────────────────────────┐
                    │         AUTHORIZATION CHAIN              │
                    │                                         │
VOICE INTENT        │                                         │
      ↓             │                                         │
INTENT CLASSIFICATION                                         │
      ↓             │                                         │
AUTHENTICATED PRINCIPAL (from credentials, not from body)    │
      ↓             │                                         │
CAPABILITY CHECK    │                                         │
      ↓             │                                         │
CONFIRMATION GATE:  │                                         │
  READ ─────────────────────────────► EXECUTE                 │
  WRITE ─────────────────────────────► CONFIRM → EXECUTE      │
  DESTRUCTIVE ────────────────────────► CONFIRM + CAP → EXEC  │
  FINANCIAL SIGNING ──────────────────► SEPARATE AUTH → EXEC  │
      ↓             │                                         │
EXECUTION           │                                         │
      ↓             │                                         │
EVIDENCE GENERATED  │                                         │
      ↓             │                                         │
RECEIPT CREATED     │                                         │
      ↓             │                                         │
MEMORY WRITTEN      │                                         │
      ↓             │                                         │
REPUTATION UPDATED  │                                         │
      ↓             │                                         │
CONSENSUS AVAILABLE │                                         │
      ↓             │                                         │
ECONOMICS SETTLED   │                                         │
                    └─────────────────────────────────────────┘
```

---

## THE CANONICAL ACTION RECEIPT v1

One format across ALL repos. Every subsystem implements adapters for this shape.

```json
{
  "receipt_id": "...",
  "principal_id": "...",
  "agent_id": "...",
  "session_id": "...",
  "execution_id": "...",
  "action": { "kind": "...", "target": "...", "params": {} },
  "evidence_ids": [],
  "witness_attestations": [],
  "throne_evaluations": [],
  "consensus_receipt": null,
  "physical_attestation": null,
  "timestamp": 0,
  "signature": "...",
  "previous_hash": "...",
  "memory_receipt": null
}
```

Nostr event: kind TBD (candidate: `kind 31040`)
Every consequential event MUST carry: `agent_id, principal_id, session_id, execution_id, receipt_id`
No "last-seen agent" inference allowed anywhere in the stack.

---

## THE EPISTEMIC ORGANISM LOOP

The ecosystem's self-learning and truth-finding engine:

```
RAW EVENTS (from Vantage, Waggle, Voice, Mesh, Agents)
  ↓
MYCELIUM
  Pattern discovery: recurring workflows, anomalies, correlations,
  opportunity signals, skill candidates, market calls
  ↓
IFÁSCRIPT
  Claim formalization: precondition, trigger, assertion, horizon, null_behaviour
  Market-resolution falsifiers. Arena protocol.
  ↓
TWELVE THRONES
  12 independent models evaluate claim
  Model provenance: provider + version + prompt_hash + input_hash + config + independence_class
  Disagreement levels: Unanimous / Strong / Moderate / Severe
  Output: consensus_receipt, epistemic_mapping, arweave_archive, Sui NFT
  ↓
ZÀNGBÉTÒ
  Records authorized transitions. Slashes heretical states.
  Arweave anchor + BTC OpenTimestamp + on-chain Sui receipt.
  Sabbath-gated attestation workflow.
  ↓
REAL-WORLD ACT
  ↓
WITNESS-FIRMWARE
  Physical signed observation:
  {payload_hash, RSSI, SNR, timestamp, firmware_hash, device_id, signature}
  Mesh gossip protocol: cross-node validation.
  ↓
MYCELIUM (relearn)
  Update knowledge: confirmed / falsified / inconclusive / context-dependent
  Feed verdict back in → closed epistemic organism
```

**Four kinds of truth (clean separation of concerns):**

| Who | Says what |
|-----|-----------|
| Witness | "I observed M at timestamp T under these conditions." |
| Mycelium | "Across N observations, this pattern appears to exist." |
| Twelve Thrones | "Given M + other evidence, we believe X with confidence C." |
| Zàngbétò | "This transition was authorized and recorded." |
| Triune-Memory | "The organism previously knew/did/believed X." |

---

## THE SIMULATION-TO-PHYSICAL PROOF CHAIN

```
ScarabSwarm
  6-DOF quadrotor physics (hand-rolled Euler / optional MuJoCo)
  SHA256 trajectory proof: deterministic, cross-architecture verified
  Input: {env_hash, model_hash, controller_hash, input_hash, engine_version}
  Output: {trajectory, quantized_proof, signed_attestation}
  ↓
Blocksim (Proof-of-Simulation chain)
  Operator stakes → registers firmware → submits signed sim log
  Ed25519 identity (BIPON39-derived) → verify → reward / slash
  Output: deployment_authorization
  ↓
Witness-firmware (physical edge)
  ESP32 + SX1278 LoRa DePIN witness node
  Physics-proof attestation: Payload Hash + RSSI + Timestamps
  Mesh gossip: neighbor validation
  Output: {signed_observation, chain_hash}
  ↓
Mycelium
  Compare: simulation model vs physical outcome
  Update: confirmed / drift_detected / anomaly / model_invalid
```

---

## THE DEVICE = THIN SOVEREIGN CLIENT

The device is a **Vantage Terminal** — a physical doorway into the organism.
NOT a node running the whole organism locally.

```
┌─────────────────────────────────────┐
│          VANTAGE DEVICE              │
│           (Arch Linux)               │
│                                     │
│  ┌─────────────────────────────┐    │
│  │      VANTAGE VOICE          │    │
│  │                             │    │
│  │  "Talk to your agent"       │    │
│  │  STT · TTS · VAD · Camera   │    │
│  └──────────────┬──────────────┘    │
│                 │                   │
│  ┌──────────────▼──────────────┐    │
│  │      CLIENT LAYER           │    │
│  │  Principal · Identity       │    │
│  │  Agent Sessions             │    │
│  │  Capabilities · Approvals   │    │
│  │  Local encrypted vault      │    │
│  │  Hardware security          │    │
│  └──────────────┬──────────────┘    │
└─────────────────┼───────────────────┘
                  │ Secure Agent Gateway
                  ↓
┌─────────────────────────────────────┐
│            VANTAGE                   │
│     (network/service substrate)      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 Ọmọ Kọ́dà  ỌSỌVM   rest of organism
```

**4-layer device security separation:**
```
OBSERVATION  → mic, camera, screen, location, sensors
COGNITION    → agent, LLM, memory, reasoning
AUTHORITY    → keys, capabilities, approvals, signatures
EXECUTION    → Vantage tools, Sui, wallet, guild, trades
```

**Offline mode:** Meshtastic mesh + local agent loop + signed event queue → reconcile when connectivity returns.
**Hardware replaceable:** identity lives in Vantage, not hardware. Any authorized terminal = the interface.

---

## VANTAGE VOICE — THE FACE

**The organism's mouth, ears, and eyes.**

Beyond S2S voice: it is the human authorization boundary for the entire ecosystem.

**Two critical loops it enables:**

Loop 1 — Agent control:
```
VOICE → TRANSCRIPT → VANTAGE AGENT → TOOL → RECEIPT →
MYCELIUM → CLAIM → TWELVE THRONES → VERDICT → WITNESS → MEMORY → VOICE
```

Loop 2 — Observation corroboration (new, powerful):
```
Human: "The machine over there is flashing red."
  ↓ Voice transcript
  ↓ Claim: device X is flashing red
  ↓ Mycelium
  ↓ Twelve Thrones: request corroboration
  ↓ Witness device X: physical attestation
  ↓ Compare human observation + machine observation
  ↓ Epistemic verdict
```

**Canonical Vantage Voice repo structure (target):**
```
apps/     (voice, dashboard, onboarding, settings)
device/   (arch, hardware, audio, camera, display, power)
agent/    (principal, identity, sessions, capabilities, approvals)
gateway/  (vantage, mcp, a2a, federation)
evidence/ (transcripts, observations, receipts, provenance)
protocols/(nostr, meshtastic, freenet, sui, walrus, arweave)
```

**First-boot onboarding vision:**
> User powers on device. Vantage Voice says: "Would you like to create an agent?" User speaks. Birth ceremony happens conversationally. User never sees Linux, Nostr, Sui, or keys.

---

## THE 10 ARCHITECTURAL BLOCKERS (P0-P10)

| # | Blocker | What breaks without it |
|---|---------|----------------------|
| P0-1 | Canonical Principal | Agent impersonation via body.get("agent_id") substitution |
| P0-2 | Universal Capability Kernel | REST/MCP/Voice/Daemon use different auth — gaps at boundaries |
| P0-3 | Canonical Action Receipt | 8+ incompatible receipt formats → no unified evidence graph |
| P0-4 | Identity-Carrying Events | Triune/Vantage infer actor from temporal context → wrong attribution |
| P0-5 | Mycelium Privacy | Real wallet addresses in unauthenticated trace endpoint |
| P0-6 | Mesh Ownership | heartbeat/leave/proposal actor_id substitution live in Vantage mesh |
| P0-7 | Economic Receipt | Portent/Trading/AIO economics can't be reconciled |
| P0-8 | Federation Security | Missing replay protection, revocation, SSRF across peers |
| P0-9 | Proof Binding | Simulation + consensus + physical observation not cryptographically linked |
| P0-10 | Protocol Manifest | 30+ repo architecture drift is itself a security/coordination problem |

---

## MATURITY SNAPSHOT (2026-09-07)

```
Individual components        ████████████████████░░  75-90%
Cross-repo integration       █████████████░░░░░░░░░  55-65%
Security architecture        ████████████████░░░░░░  65%
Cryptographic provenance     ████████████████░░░░░░  60%
Economic settlement          ██████████████░░░░░░░░  45-55%
Physical → digital proof     █████████████░░░░░░░░░  40-50%
As one unified organism      ██████████████░░░░░░░░  50-60%
```

**The shift:** Components are real. The common protocol binding them is the gap.

---

## STRATEGIC BUILD ORDER

**1. ACTION RECEIPT & PRINCIPAL PROTOCOL v1**
   Create the spec. Every repo implements adapters. This is the connective tissue.

**2. MYCELIUM PRIVACY BOUNDARY (P0-5)**
   HMAC pseudonymization of wallet/username in traces. Consent toggle. Before expanding the intelligence substrate.

**3. CANONICAL PRINCIPAL in Vantage mesh (P0-1, P0-6)**
   `_assert_owns_mesh_agent_id()` is already in Vantage — make it universal.

**4. IDENTITY-CARRYING EVENTS (P0-4)**
   Every Triune + Vantage event carries its principal. No temporal inference.

**5. VANTAGE VOICE → FULL PLANE 1**
   Expand to device/ + agent/ + gateway/ + evidence/ + protocols/ structure.
   Wire evidence loop: voice claim → Mycelium → Twelve Thrones → Witness.

**6. SIMULATION PROOF BINDING (P0-9)**
   ScarabSwarm input envelope → Blocksim → Witness → Mycelium feedback loop.

**7. MESHTASTIC FORK AUDIT**
   Generate UPSTREAM_COMMIT vs OMOKODA_PATCHSET differential before fork diverges further.

---

## DO NOT MERGE (financial surfaces)

- **Vantage PR #53** — 64k-line diff touching Hermes/Postgres/trading/wallet/security. Surgical comparison against current main required.
- **Vantage PR #54** — Jupiter signer v2 + Polymarket daemon. Live financial surfaces.
