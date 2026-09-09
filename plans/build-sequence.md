# Build Sequence — DIP · VCP · TSP
# Cross-Protocol, Dependency-Ordered
# Written: 2026-09-08

---

## READING THIS DOCUMENT

Each phase has:
  - WHAT:    What gets built
  - OUTPUTS: What artifacts exist after this phase
  - GATES:   What must be true before the next phase starts
  - REPOS:   Which repos are touched
  - LANGS:   Primary languages

Phases within a tier can run in parallel.
Phases across tiers are strictly sequential — a gate must pass.

---

## TIER 0 — FOUNDATIONS (no protocol yet, just types)

These exist before any protocol message is sent.
Everything above depends on them being correct.

### Phase 0.1 — Canonical Types Library

WHAT:
  - IdentityChain struct (principal_id, agent_id, session_id, execution_id, receipt_id)
  - Merkle commitment function (BTreeMap field order, sha256 leaves)
  - Signature types (ed25519 sign/verify wrappers)
  - Hash type (sha256:hex string format)
  - Timestamp type (u64 unix ms)
  - DipOutcome, VcpSessionOutcome, ObservationOutcome enums
  - JSON Schema equivalents of all Rust types (for non-Rust SDKs)

OUTPUTS:
  - crate: sovereign-types  (Rust)
  - pkg:   @sovereign/types (TypeScript)
  - pkg:   sovereign-types  (Python)

GATES:
  ✓ Merkle function produces identical output across all 3 language impls
  ✓ Sign/verify round-trips in all 3 languages
  ✓ JSON Schema validates all sample payloads from wire-schemas.md

REPOS:   sovereign-types (new)
LANGS:   Rust · TypeScript · Python

---

### Phase 0.2 — DID / Identity Root

WHAT:
  - DID generation: did:vantage:principal:<sha256(public_key)>
  - DID Document format
  - DID resolution (local + Vantage registry)
  - Canonical agent birth: keygen → DID → identity document → Vantage registration
  - Agent identity: one canonical DID + multiple protocol equivalences (stub — no DIP yet)

OUTPUTS:
  - Agent birth produces: { did, public_key, private_key, identity_doc }
  - Identity doc stored: Vantage DB + (eventually) Sui
  - Ọmọ Kọ́dà: birth endpoint returns full identity chain

GATES:
  ✓ Born agent has a stable DID that survives process restart
  ✓ Two different agents have different DIDs
  ✓ Identity doc is signed and verifiable offline

REPOS:   Ọmọ Kọ́dà · Vantage
LANGS:   Rust · Python

---

## TIER 1 — DIP CORE (interoperability grammar)

Depends on: Tier 0 complete

### Phase 1.1 — DIP Envelope + Routing Core

WHAT:
  - DipEnvelope struct (all fields from wire-schemas.md)
  - DipAddress, DipNetwork, DipKind, DipHop
  - Envelope builder: fill + sign
  - Envelope verifier: check signature, check TTL, check message_id uniqueness
  - In-memory routing table: network → adapter registration
  - DipRouter: route(envelope) → next_hop | local_delivery | drop

OUTPUTS:
  - crate: dip-core
  - DipRouter running in Vantage process

GATES:
  ✓ Envelope with expired TTL is rejected
  ✓ Duplicate message_id is deduplicated
  ✓ Envelope signed by wrong key is rejected
  ✓ Router can deliver to local Vantage agents

REPOS:   dip/ (new)
LANGS:   Rust

---

### Phase 1.2 — DIP Identity Document

WHAT:
  - DipIdentityDocument struct
  - DipEquivalence: foreign network address + proof (foreign key signs canonical DID)
  - Equivalence verifier: challenge → response → mark verified
  - Identity resolver: DID → DipIdentityDocument (local cache + remote fetch)

OUTPUTS:
  - Identity documents stored + resolvable
  - Agents can prove they own multiple network addresses

GATES:
  ✓ Add Nostr equivalence, verify it resolves
  ✓ Add Meshtastic equivalence, verify it resolves
  ✓ Two-way challenge: DIP resolver asks foreign network to sign DID, confirms

REPOS:   dip/
LANGS:   Rust

---

### Phase 1.3 — First DIP Adapter: Nostr

WHAT:
  - to_dip(NostrEvent) → DipEnvelope
  - from_dip(DipEnvelope) → NostrEvent
  - Nostr relay connection (subscribe to DIP-tagged events)
  - DIP-over-Nostr: use kind:20000-29999 (ephemeral) for messages, kind:30000+ for receipts
  - Nostr → DipRouter → local agent delivery

OUTPUTS:
  - Vantage agent can receive a DIP message sent from a Nostr client
  - Vantage agent can send a DIP message that appears as a Nostr event

GATES:
  ✓ Send DIP message from Nostr client, receive in Vantage agent
  ✓ Send DIP receipt from Vantage, verify on Nostr relay
  ✓ Identity equivalence: Nostr npub ↔ DID

REPOS:   dip/ · Vantage
LANGS:   Rust · Python

---

### Phase 1.4 — DIP MCP Adapter

WHAT:
  - Wrap MCP tool calls in DIP envelope
  - DipKind::Capability for tool capability declaration
  - DipKind::Message for tool invocation
  - DipKind::Receipt for tool result
  - MCP tool call → DIP envelope → routed → delivered → response → DIP receipt

OUTPUTS:
  - All MCP tool calls in Vantage carry full DIP identity chain
  - Cross-agent tool invocation via DIP (not just local)

GATES:
  ✓ Agent A calls Agent B's tool via DIP (different processes)
  ✓ Receipt issued + verifiable
  ✓ Identity chain intact end-to-end

REPOS:   dip/ · Vantage
LANGS:   Rust · Python

---

### Phase 1.5 — DIP A2A Adapter

WHAT:
  - A2A task delegation wrapped in DIP envelope
  - DipKind::Capability for A2A capability declaration
  - A2A message → DIP → A2A adapter → remote agent
  - Agent discovery via DIP (find agents by capability across networks)

OUTPUTS:
  - Cross-network agent collaboration (Vantage ↔ any A2A-compatible network)
  - DIP becomes the routing layer for all cross-agent work

GATES:
  ✓ Delegate task from Vantage agent to external A2A agent
  ✓ Result returned as DIP receipt
  ✓ Identity verified both directions

REPOS:   dip/ · Vantage · Ọmọ Kọ́dà
LANGS:   Rust · Python

---

### Phase 1.6 — DIP Meshtastic Adapter

WHAT:
  - Compact DIP envelope (binary, not JSON — fits in 240-byte mesh packet)
  - Meshtastic protobuf ↔ compact DIP
  - Delay-tolerant routing: store-and-forward queue
  - Off-grid agent operation: send commands via mesh, receive receipts on reconnect
  - Meshtastic revocation broadcast (for VCP — phase 2.7 uses this)

OUTPUTS:
  - Agent operates across mesh networks with no Internet
  - Receipts queued locally, sync to Vantage on reconnect

GATES:
  ✓ Send DIP command via mesh node, execute on remote device, receipt queued
  ✓ Reconnect to Internet, receipt synced + verified
  ✓ Compact envelope fits in single mesh packet

REPOS:   dip/ · Vantage-Voice (BLE/mesh daemon)
LANGS:   Rust · C (Meshtastic firmware plugin)

---

## TIER 2 — VCP CORE (agent → physical device)

Depends on: Phase 0.1 + 0.2 + 1.1 complete (DIP envelope must exist for identity)

### Phase 2.1 — VCP Spec + Manifest Schema

WHAT:
  - AgentDeviceManifest JSON Schema (from wire-schemas.md) — validated, versioned
  - VcpCapabilityDecl, VcpSafetyConfig, VcpTransport types
  - Manifest builder (device-side SDK)
  - Manifest verifier (Vantage-side)
  - Safety rule enforcer: ungrantable[] is hardcoded — no override path

OUTPUTS:
  - Devices can produce a manifest
  - Vantage can parse + validate a manifest
  - Safety rules enforced at parse time

GATES:
  ✓ Manifest with firmware.update marked ungrantable:false is REJECTED
  ✓ Manifest verifier catches missing emergency_stop
  ✓ Round-trip: build → serialize → deserialize → verify OK

REPOS:   vcp/ (new) · Vantage
LANGS:   Rust

---

### Phase 2.2 — VCP Handshake State Machine

WHAT:
  - Full 7-step handshake (Discovery → Challenge → Auth → Negotiate → Grant → Session → Receipt)
  - VcpChallenge + VcpChallengeResponse (nonce sign/verify)
  - VcpCapabilityRequest → authorization check → VcpCapabilityGrant
  - Grant as signed token: device signs, agent verifies before sending commands
  - Session ID assigned on grant issue
  - State machine: DISCONNECTED → DISCOVERED → IDENTIFYING → AUTHENTICATED → NEGOTIATING → SESSION_OPEN

OUTPUTS:
  - Two processes can complete a VCP handshake locally (mock device)
  - Grant issued, commands flow only within granted capabilities

GATES:
  ✓ Handshake with wrong key rejected at challenge step
  ✓ Requested capability not in manifest → denied (not errored)
  ✓ Grant issued with correct expiry and limits

REPOS:   vcp/
LANGS:   Rust

---

### Phase 2.3 — BLE + Wi-Fi Discovery Daemon

WHAT:
  - BLE scanner: look for VCP/1 service UUID beacon
  - mDNS scanner: look for _vcp._tcp.local
  - Discovery event: { device_id, manufacturer, capabilities_summary, transport[] }
  - Vantage-Voice discovery feed: "UNITREE GO2 found [locomotion, camera, telemetry]"
  - Agent can ask: "what VCP devices are near me?"

OUTPUTS:
  - Discovery daemon running in Vantage-Voice process
  - Agent gets live list of nearby VCP devices

GATES:
  ✓ Simulated BLE beacon detected and parsed
  ✓ Discovery event delivered to Vantage agent via MCP tool
  ✓ Device disappears from list when beacon stops

REPOS:   Vantage-Voice · vcp/
LANGS:   Rust · Python (MCP tool wrapper)

---

### Phase 2.4 — First VCP Adapter: Unitree Go2

WHAT:
  - Go2 SDK wrapper → VCP command translator
  - VCP locomotion.walk → Go2 SDK move() call
  - VCP camera.read → Go2 camera stream
  - VCP telemetry.read → Go2 state subscribe
  - VCP emergency_stop → Go2 stop() (always available, no grant check)
  - Go2 telemetry → VcpCommandResponse stream

OUTPUTS:
  - Agent can walk a real Go2 via VCP commands
  - Camera stream accessible via VCP
  - Telemetry (pose, battery, IMU) flowing

GATES:
  ✓ Command without active grant is rejected
  ✓ Speed limit in grant is enforced (Go2 won't exceed grant.limits.max_speed_ms)
  ✓ emergency_stop works with no grant (always)
  ✓ Session receipt issued on disconnect

REPOS:   vcp/adapters/unitree-go2/ · Vantage
LANGS:   Rust · Python

---

### Phase 2.5 — VCP Session + Command Protocol

WHAT:
  - VcpCommand → VcpCommandResponse (request/response over WebSocket)
  - VcpCommandStatus streaming: Accepted → Executing → Completed
  - Heartbeat: 30s keepalive, session dies without heartbeat
  - Command queue: device can buffer commands if busy
  - Telemetry subscription: agent subscribes to specific fields at specific Hz

OUTPUTS:
  - Full bidirectional session: agent commands ↔ device telemetry
  - Commands are non-blocking (fire, get status stream)

GATES:
  ✓ Command to non-granted capability returns Denied (not crash)
  ✓ Grant expiry mid-session: next command returns GrantExpired
  ✓ Heartbeat miss × 3 → session closed + receipt issued

REPOS:   vcp/
LANGS:   Rust

---

### Phase 2.6 — VCP Session Receipt

WHAT:
  - VcpSessionReceipt: built incrementally during session, finalized on close
  - capabilities_used[] tracking per command
  - Commands issued / success / failed counts
  - Telemetry summary: mean/min/max for numeric fields
  - evidence_ids[]: links to TSP capture receipts if scanning occurred
  - Receipt signed by device, delivered to agent

OUTPUTS:
  - Every VCP session produces a verifiable receipt
  - Receipt stored in Vantage receipt store
  - Receipt feeds into CanonicalReceipt format

GATES:
  ✓ Receipt produced on clean disconnect
  ✓ Receipt produced on revocation (VcpSessionOutcome::Revoked)
  ✓ Receipt produced on heartbeat timeout
  ✓ Merkle root correct over all receipt fields

REPOS:   vcp/ · Vantage
LANGS:   Rust · Python

---

### Phase 2.7 — VCP Revocation + Meshtastic Broadcast

WHAT:
  - VcpRevocation message (principal signs, device enforces)
  - In-session revocation: current session closed immediately
  - Offline revocation: VcpRevocation stored, delivered on next device contact
  - Meshtastic broadcast: revocation_broadcast packet (compact, signed)
    → propagates through mesh to reach device even with no direct connection
  - Revocation log: device keeps list of revoked grant_ids

OUTPUTS:
  - Principal can revoke any session from anywhere, including offline
  - Revocation propagates through mesh network

GATES:
  ✓ Revoke active session → session closes, commands rejected
  ✓ Revoke offline device → revocation queued → delivered on next contact
  ✓ Revocation broadcast reaches device via 3-hop mesh relay

REPOS:   vcp/ · dip/adapters/meshtastic/
LANGS:   Rust · C (mesh firmware)

---

## TIER 3 — TSP CORE (physical reality as owned artifacts)

Depends on: Phase 0.1 + 0.2 complete. Phase 2.4+ ideal but not required.

### Phase 3.1 — Twin Asset Schema + Quality Gate

WHAT:
  - TwinAsset struct (full schema from wire-schemas.md)
  - TwinDataHashes: hash all modalities
  - TwinQuality: f1_score gate (REJECT < 0.777)
  - TwinRegion: lat/lon/alt bounding box
  - Merkle commitment over all Twin fields
  - Twin ID = sha256(merkle_root) — deterministic from content

OUTPUTS:
  - Twin Assets can be created, validated, serialized
  - Quality gate enforced at construction (not just validation)

GATES:
  ✓ Twin with f1_score = 0.776 is rejected at construction
  ✓ Twin with f1_score = 0.777 is accepted
  ✓ Changing any data hash changes twin_id
  ✓ Two twins with identical data produce identical twin_id

REPOS:   twin-protocol/ (new)
LANGS:   Rust

---

### Phase 3.2 — Capture Receipt (31020)

WHAT:
  - CaptureReceipt struct (from wire-schemas.md)
  - Capture pipeline integration: after each gsplat run → emit 31020
  - F1 gate: compute f1_score, reject if < 0.777
  - Raw hash computation: sha256 each modality data file
  - Novelty scoring: compare against existing twin coverage (if any)
  - Privacy flags: detect faces/plates in RGB frames
  - Receipt stored in Vantage receipt store

OUTPUTS:
  - Every capture run that passes F1 gate produces a 31020 receipt
  - Failed captures produce a rejection record (not a receipt)

GATES:
  ✓ Capture with bad coverage fails F1, no receipt
  ✓ Capture with good coverage passes F1, receipt issued
  ✓ Receipt includes correct raw_hashes for all modalities
  ✓ Privacy flags populated when faces detected

REPOS:   twin-protocol/ · Vantage (capture pipeline)
LANGS:   Rust · Julia (gsplat integration) · Python (COLMAP integration)

---

### Phase 3.3 — Scene Receipt (31030) + Sui Anchor

WHAT:
  - SceneReceipt struct
  - Assembler: combine N × 31020 receipts → 31030
  - Reconstruction engine integration: Julia gsplat → splat_hash, geometry_hash
  - F1 gate on assembled scene (must be >= 0.777 over whole scene)
  - Sui Move contract: Twin NFT minting from 31030 receipt
  - IP Root on Sui: sui_object_id written back to receipt
  - Walrus / Arweave: store raw splat data, embed Walrus blob ID in receipt

OUTPUTS:
  - Assembled twin scene → 31030 receipt → Sui NFT (IP Root)
  - Twin is now an owned, on-chain artifact
  - Owner can prove provenance from capture through assembly

GATES:
  ✓ 31030 receipt links to valid 31020 receipts
  ✓ Sui NFT minted, object ID returned
  ✓ Twin provenance traceable: NFT → 31030 → 31020s → devices
  ✓ Duplicate scene attempt: idempotent (same merkle_root → same twin_id)

REPOS:   twin-protocol/ · Vantage · Move contracts (Sui)
LANGS:   Rust · Julia · Move

---

### Phase 3.4 — ỌSỌVM + Twin Integration (Proof-of-Simulation)

WHAT:
  - SimulationReceipt struct
  - ỌSỌVM: consume Twin Asset as simulation environment
  - Run N trajectories against twin (robot model + physics + layout)
  - Produce all_policies[] with energy/risk/duration per policy
  - Compute all_policies_hash = sha256(canonical JSON of all_policies)
  - Agent selects policy, records selection_criteria
  - Merkle commitment: binds twin_id + params + all_policies_hash
  - Witness request: send commitment to 2+ witness nodes for attestation
  - Issue SimulationReceipt

OUTPUTS:
  - Every ỌSỌVM sim run against a Twin produces a signed SimulationReceipt
  - Multiple candidate policies committed to — not just the winner
  - At least 2 independent witnesses attest the commitment

GATES:
  ✓ Simulation with < 2 candidate policies rejected
  ✓ Simulation without witness attestations rejected
  ✓ all_policies_hash verifies against all_policies[]
  ✓ Selected policy exists in all_policies[]

REPOS:   ỌSỌVM · twin-protocol/ · Vantage
LANGS:   Julia · Rust

---

### Phase 3.5 — Witness + Proof-of-Observation

WHAT:
  - ObservationReceipt struct
  - Witness firmware: after robot executes policy, record actual outcome
  - TPM signing: hardware_sig signed by TPM key (not software)
  - Deviation computation: delta per field, max_delta_pct
  - Outcome classification: Validated / Partial / Falsified / Inconclusive
  - Receipt delivered to Vantage + stored
  - Mycelium event: sim_vs_real delta → pattern mining

OUTPUTS:
  - Every physical execution of a sim-selected policy produces an ObservationReceipt
  - Sim accuracy tracked over time (Mycelium learns the gap)
  - Falsified simulations trigger model update

GATES:
  ✓ Software-only signature rejected
  ✓ delta.max_delta_pct < 10% → Validated
  ✓ delta.max_delta_pct > 30% → Falsified
  ✓ Mycelium receives sim/obs pair, logs pattern

REPOS:   Witness-firmware · twin-protocol/ · Mycelium
LANGS:   Rust (firmware) · C (TPM interface)

---

### Phase 3.6 — Twin Licensing + Marketplace

WHAT:
  - TwinLicenseGrant struct
  - License types: Exclusive / NonExclusive / OpenAccess / ResearchOnly
  - Usage rights: View / Simulate / Annotate / Derive / Distribute / Commercial
  - Sui Move: License NFT (derived from Twin NFT)
  - Fee routing: lamports → revenue split → owner + contributors + protocol fee
  - License check in simulation: SIM_JOB validates license before running
  - Marketplace listing: twin_id + license_type + price + available_rights

OUTPUTS:
  - Twins can be licensed to other agents
  - Revenue flows to owner + contributors automatically
  - Simulation runs are gated by license

GATES:
  ✓ Unlicensed agent cannot run simulation against licensed twin
  ✓ License fee routed: 70% owner, 27.5% contributors, 2.5% protocol
  ✓ License NFT transferred on acceptance

REPOS:   twin-protocol/ · Vantage · Move contracts
LANGS:   Rust · Move

---

## TIER 4 — INTEGRATION (three protocols working together)

Depends on: Tier 1 Phase 1.3 + Tier 2 Phase 2.4 + Tier 3 Phase 3.3 all complete

### Phase 4.1 — VCP → TSP: Capture Session Wires Together

WHAT:
  - VCP session (robot scanning) → TSP capture pipeline automatically
  - VCP camera.read frames → TSP raw capture buffer
  - VCP session receipt evidence_ids[] ← TSP 31020 receipt IDs
  - Single "Koda, scan this room" command → VCP session + TSP capture + 31020 receipt

OUTPUTS:
  - One user command produces: VCP session receipt + TSP capture receipt + (eventually) twin

GATES:
  ✓ VCP session ends → evidence_ids populated with 31020 receipt IDs
  ✓ 31020 receipt references VCP device_ids
  ✓ Provenance chain: VCP grant → VCP session → 31020 → 31030 → Sui NFT

REPOS:   Vantage · vcp/ · twin-protocol/
LANGS:   Python · Rust

---

### Phase 4.2 — DIP → TSP: Cross-Network Twin Licensing

WHAT:
  - External agent on Nostr sends DIP message requesting twin license
  - DIP Nostr adapter routes to Vantage
  - Vantage agent evaluates: does requestor have rights? what's the price?
  - License Grant issued via DIP receipt
  - Grantee counter-signs via DIP (Nostr side)
  - Sui tx settled, license NFT transferred

OUTPUTS:
  - Twin can be licensed to any DIP-connected agent, regardless of network

GATES:
  ✓ Nostr agent sends DIP license request, receives DIP grant receipt
  ✓ Sui tx confirming license visible on-chain
  ✓ Cross-network round-trip < 5 seconds

REPOS:   dip/ · twin-protocol/ · Vantage
LANGS:   Rust · Python

---

### Phase 4.3 — DIP → VCP: Cross-Network Device Control

WHAT:
  - Remote agent (on A2A or Nostr network) controls a VCP device via DIP
  - DIP routes command envelope to VCP gateway
  - VCP gateway validates DIP identity against VCP grant
  - Command executed, telemetry + receipt returned via DIP

OUTPUTS:
  - Any DIP-connected agent can operate any VCP device they hold a grant for

GATES:
  ✓ A2A agent sends DIP command → VCP device executes
  ✓ Identity chain intact: DIP principal_id = VCP grant's agent_did
  ✓ Receipt returned via DIP to originating network

REPOS:   dip/ · vcp/ · Vantage
LANGS:   Rust

---

### Phase 4.4 — Full Loop: Scan → Sim → Execute → Observe → Learn

WHAT:
  - End-to-end integration test of the complete organism loop:

  1. VCP: agent connects to Go2 + drone, requests locomotion + camera
  2. TSP: capture session → 31020 receipts (F1 gate)
  3. TSP: 31030 scene receipt → Sui NFT
  4. TSP: ỌSỌVM simulation → 100k trajectories → 3 candidate policies
  5. TSP: SimulationReceipt (merkle commitment + 2 witnesses)
  6. VCP: agent commands Go2 to execute winning policy
  7. TSP: Witness firmware records actual outcome → ObservationReceipt
  8. Mycelium: sim vs real delta → new miner finding
  9. DIP: receipt chain propagated to Nostr + archived to Arweave

OUTPUTS:
  - One complete Reality → Proof → Learning loop, fully receipted

GATES:
  ✓ All receipts produced (VCP session, 31020, 31030, sim, obs)
  ✓ Provenance chain cryptographically verifiable start to finish
  ✓ Mycelium receives sim/obs pair
  ✓ DIP propagates final receipt to external network

REPOS:   ALL
LANGS:   ALL

---

## PHASE SUMMARY TABLE

| Phase | Name | Tier | Depends On | Key Output |
|-------|------|------|-----------|------------|
| 0.1 | Canonical Types | 0 | — | sovereign-types crate |
| 0.2 | DID / Identity Root | 0 | 0.1 | Agent birth, stable DID |
| 1.1 | DIP Envelope + Router | 1 | 0.1+0.2 | DIP routing working |
| 1.2 | DIP Identity Doc | 1 | 1.1 | Multi-network equivalence |
| 1.3 | Nostr Adapter | 1 | 1.2 | DIP-over-Nostr |
| 1.4 | MCP Adapter | 1 | 1.2 | DIP-wrapped tool calls |
| 1.5 | A2A Adapter | 1 | 1.2 | Cross-network agent collab |
| 1.6 | Meshtastic Adapter | 1 | 1.2 | Off-grid DIP |
| 2.1 | VCP Manifest Schema | 2 | 0.1+0.2+1.1 | Devices declare capabilities |
| 2.2 | VCP Handshake | 2 | 2.1 | Auth + grant working |
| 2.3 | Discovery Daemon | 2 | 2.1 | Find nearby VCP devices |
| 2.4 | Unitree Go2 Adapter | 2 | 2.2+2.3 | Control real robot |
| 2.5 | Session + Commands | 2 | 2.4 | Full command/telemetry loop |
| 2.6 | Session Receipt | 2 | 2.5 | Every session receipted |
| 2.7 | Revocation + Mesh | 2 | 2.6+1.6 | Offline revocation works |
| 3.1 | Twin Schema + Gate | 3 | 0.1 | Twin Assets valid/invalid |
| 3.2 | Capture Receipt 31020 | 3 | 3.1 | F1-gated capture receipts |
| 3.3 | Scene Receipt 31030 | 3 | 3.2 | Twins on Sui |
| 3.4 | Proof-of-Simulation | 3 | 3.3 | ỌSỌVM sim receipted |
| 3.5 | Proof-of-Observation | 3 | 3.4 | Physical outcome receipted |
| 3.6 | Twin Licensing | 3 | 3.3 | Twins licensable, revenue flows |
| 4.1 | VCP → TSP | 4 | 2.6+3.2 | Scan session → Twin provenance |
| 4.2 | DIP → TSP | 4 | 1.3+3.6 | Cross-network licensing |
| 4.3 | DIP → VCP | 4 | 1.5+2.5 | Remote device control via DIP |
| 4.4 | Full Loop | 4 | ALL | End-to-end organism running |

---

## PARALLEL WORK OPPORTUNITIES

These can run at the same time without blocking each other:

```
AFTER 0.1+0.2:
  ├── DIP track: 1.1 → 1.2 → [1.3, 1.4, 1.5, 1.6 in parallel]
  ├── VCP track: 2.1 → 2.2 → [2.3, 2.4 in parallel] → 2.5 → 2.6 → 2.7
  └── TSP track: 3.1 → 3.2 → 3.3 → [3.4, 3.6 in parallel] → 3.5

EARLIEST PHYSICAL DEMO (robot scans room, twin on Sui):
  0.1 → 0.2 → 2.1 → 2.2 → 2.3 → 2.4 → 3.1 → 3.2 → 3.3
  (skip DIP entirely for local-only demo)

EARLIEST CROSS-NETWORK DEMO (Nostr agent licenses a twin):
  add: 1.1 → 1.2 → 1.3 → 3.6 → 4.2
```

---

## WHAT "DONE" LOOKS LIKE

```
DIP DONE when:
  - Any DIP-connected agent can send a message to any other
    regardless of which network they're on
  - Identity is verifiable across all equivalences
  - Meshtastic works offline, syncs on reconnect

VCP DONE when:
  - Any manufacturer can implement VCP once and work with any Vantage agent
  - Walk up, connect, use, walk away — clean session + receipt every time
  - Revocation works offline via mesh

TSP DONE when:
  - Scan a real place → Twin on Sui in < 2 hours
  - Another agent can license and simulate against it
  - Physical execution produces an ObservationReceipt that proves sim accuracy
  - Mycelium learns from the gap

ALL THREE DONE when:
  - Phase 4.4 complete end-to-end
  - Reality → Proof → Learning loop runs without human intervention
  - Every step in the loop is receipted and cryptographically verifiable
```
