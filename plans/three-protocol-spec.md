# The Three Protocols — Engineering Specification Map
# DIP · VCP · TSP (Twin & Simulation Protocol)
# Written: 2026-09-08

---

## WHY THREE, NOT ONE

These are three distinct problems:

```
DIP   — How do heterogeneous decentralized networks interoperate?
VCP   — How does my agent connect to and control this physical device?
TSP   — How do we capture, own, simulate, and license physical reality?
```

They stack. TSP runs on top of VCP. VCP runs on top of DIP.
DIP speaks through A2A, MCP, Nostr, Meshtastic — it does NOT replace them.

---

## PROTOCOL 1 — DIP (Decentralized Interoperability Protocol)

### What it solves

An agent living in Vantage needs to collaborate with an agent on Nostr.
A Meshtastic node needs to send an event into an A2A workflow.
A Freenet document needs to be cited as evidence in an IfáScript claim.

Today: none of these interoperate. DIP is the grammar that makes them speak.

### Core Concept: The DIP Envelope

Every cross-network message is wrapped in a DIP envelope. The envelope is
the lingua franca — each protocol gets an adapter that reads/writes it.

```
DIP ENVELOPE
┌──────────────────────────────────────────────────────┐
│  version:       "dip/1"                              │
│  message_id:    <uuid>                               │
│  origin:        { network, address, public_key }     │
│  destination:   { network, address }                 │
│  principal_id:  <canonical agent DID>                │
│  agent_id:      <agent identity>                     │
│  session_id:    <session>                            │
│  kind:          capability | message | evidence |    │
│                 receipt | event | claim              │
│  payload:       { ... }    ← protocol-specific       │
│  routing:       [hop1, hop2, ...]                    │
│  ttl:           <seconds>                            │
│  timestamp:     <unix ms>                            │
│  signature:     <principal signs envelope>           │
└──────────────────────────────────────────────────────┘
```

### The 6 DIP Message Kinds

```
CAPABILITY    Agent declares what it can do / requests what it needs
MESSAGE       Cross-network agent communication
EVIDENCE      Signed observations, attestations, proof bundles
RECEIPT       Action completion records (carries the 5 canonical primitives)
EVENT         Broadcast notifications (pub/sub across networks)
CLAIM         IfáScript-compatible claim routed for epistemic evaluation
```

### Protocol Adapters (what DIP wraps)

```
DIP ADAPTER LAYER
  ├── A2A adapter       — agent↔agent task delegation
  ├── MCP adapter       — agent↔tool invocation
  ├── Nostr adapter     — kind routing, NIP-01 envelope ↔ DIP envelope
  ├── Meshtastic adapter — protobuf ↔ DIP envelope (compressed)
  ├── Freenet adapter   — content-addressed document ↔ DIP evidence
  └── libp2p adapter    — gossip / pub-sub ↔ DIP events
```

Each adapter is a two-function interface:
```
to_dip(native_message) → DIP_Envelope
from_dip(DIP_Envelope) → native_message
```

### Identity Bridging (the critical part)

One agent has many protocol-specific addresses. DIP knows they're the same:

```
CANONICAL DID (the root)
  ├── did:vantage:abc123          → Vantage identity
  ├── npub1xyz...                 → Nostr identity
  ├── 0x...                       → Ethereum/Sui address
  ├── meshtastic:!deadbeef        → Mesh node ID
  └── a2a:agent@ecosystem.local   → A2A identity

DIP Identity Document:
{
  "did": "did:vantage:abc123",
  "equivalences": [
    { "network": "nostr",       "address": "npub1xyz...",   "proof": "<sig>" },
    { "network": "meshtastic",  "address": "!deadbeef",     "proof": "<sig>" },
    { "network": "a2a",         "address": "agent@...",     "proof": "<sig>" }
  ],
  "created": 1234567890,
  "signature": "<canonical key signs all>"
}
```

Any DIP node that resolves the DID gets all equivalences. Message addressed
to ANY representation reaches the same agent.

### DIP State Machine (per session)

```
DISCONNECTED
  → DISCOVERED     (found peer on some network)
  → IDENTIFYING    (exchanged DIP identity documents)
  → AUTHENTICATED  (verified signatures, resolved equivalences)
  → NEGOTIATING    (exchanging capability declarations)
  → SESSION_OPEN   (messages, evidence, receipts flowing)
  → SESSION_CLOSED (clean disconnect, receipt issued)
  → REVOKED        (capability withdrawn mid-session)
```

### DIP Routing

DIP does NOT require direct peer connections. It routes:

```
SOURCE NETWORK → DIP Router → DESTINATION NETWORK

Router knows:
  - Which networks it has adapters for
  - Which DIDs it has seen on which networks
  - Which routes have succeeded/failed recently

Routing strategies:
  DIRECT:  source adapter → destination adapter (one hop)
  RELAY:   source → DIP relay node → destination
  BRIDGE:  source network peer → bridge node → destination network peer
  MESH:    Meshtastic multi-hop (off-grid, delay-tolerant)
```

### DIP Repo Structure

```
dip/
  specification/
    dip-core.md          ← wire format, envelope schema
    dip-identity.md      ← DID bridging, equivalence proofs
    dip-routing.md       ← router algorithm, relay spec
    dip-adapters.md      ← adapter interface spec
    dip-conformance.md   ← what "DIP-compatible" means
  reference-rust/        ← reference impl: core + all adapters
    src/
      envelope.rs
      identity.rs
      router.rs
      adapters/
        a2a.rs
        mcp.rs
        nostr.rs
        meshtastic.rs
        freenet.rs
        libp2p.rs
  sdk-go/               ← Go SDK (for Vantage services)
  sdk-python/           ← Python SDK (for agents)
  sdk-typescript/       ← TS SDK (for Vantage Voice)
  conformance/          ← test vectors, interop test suite
```

### DIP Build Order

```
Phase DIP-1  Core envelope schema (Rust types + JSON schema)
Phase DIP-2  Identity document + equivalence proofs (sign/verify)
Phase DIP-3  Nostr adapter (first real adapter — Nostr is well-spec'd)
Phase DIP-4  MCP adapter (agent↔tool routing through DIP)
Phase DIP-5  A2A adapter (agent↔agent across networks)
Phase DIP-6  DIP Router (local routing table, direct hops)
Phase DIP-7  Meshtastic adapter (compressed, delay-tolerant)
Phase DIP-8  libp2p adapter (gossip, pub-sub events)
Phase DIP-9  Freenet adapter (content-addressed evidence)
Phase DIP-10 Relay nodes + conformance test suite
```

---

## PROTOCOL 2 — VCP (Vantage Capability Protocol)

### What it solves

My agent wants to control a Unitree Go2 robot. Or a DJI drone. Or the lights
in a building. Each manufacturer has its own API. VCP is the ONE protocol
any device implements — then any Vantage agent can connect to it.

Think: Bluetooth profiles, but for agent-controlled physical machines.

### Core Concept: The Capability Surface

Every VCP device exposes a typed, scoped, authorized set of capabilities.
Capabilities are NOT raw commands. They are semantic actions with safety
constraints built in.

```
CAPABILITY SURFACE (robot example)
  locomotion.walk(direction, speed)     — requires: locomotion grant
  locomotion.stop()                     — always available (safety)
  navigation.follow(principal_id)       — requires: navigation grant
  navigation.goto(waypoint)             — requires: navigation + geofence grant
  camera.stream(quality)                — requires: camera.read grant
  camera.snapshot()                     — requires: camera.read grant
  telemetry.subscribe(fields[])         — requires: telemetry.read grant
  speaker.say(text)                     — requires: speaker.output grant
  firmware.update(pkg)                  — requires: firmware grant + MFA
  safety.disable()                      — NOT GRANTABLE (hardcoded off)
```

### The VCP Handshake (full state machine)

```
STEP 1 — DISCOVERY
  Device broadcasts: VCP/1 beacon (BLE / mDNS / Meshtastic)
  Beacon contains: device_id, manufacturer, protocol_version, capability_summary

STEP 2 — MANIFEST REQUEST
  Agent → Device: GET manifest
  Device → Agent: Agent Device Manifest (full JSON)

STEP 3 — CHALLENGE / AUTHENTICATION
  Device → Agent: challenge_nonce
  Agent → Device: { principal_id, agent_id, sig(challenge_nonce, principal_key) }
  Device verifies: DIP identity lookup → confirms agent is who they claim

STEP 4 — CAPABILITY NEGOTIATION
  Agent → Device: capability_request { capabilities: [...], purpose: "...", duration: "15min" }
  Device → Vantage: authorization_check (principal has permission to grant this?)
  Vantage → Device: authorized | denied | partial
  Device → Agent: capability_grant (signed, scoped, expiring)

STEP 5 — SESSION
  Agent ↔ Device: command channel (agent → device commands)
  Device → Agent: telemetry stream, observations, events
  Both: heartbeat every 30s

STEP 6 — RECEIPT
  On disconnect: Device issues VCP Receipt
  {
    session_id, device_id, agent_id, principal_id,
    capabilities_used[], commands_issued[], telemetry_summary,
    duration_ms, outcome, signature
  }

STEP 7 — REVOCATION (any time)
  Principal → Device: revoke(session_id)
  Agent → Device: disconnect()
  Device: session_closed, capability_grant invalidated
  Meshtastic: revocation_broadcast (propagates to offline nodes)
```

### Agent Device Manifest (full schema)

```json
{
  "device_id":          "unitree:go2:7f42a3b1",
  "manufacturer":       "Unitree",
  "model":              "Go2",
  "protocol_version":   "vcp/1",
  "dip_identity":       "did:device:unitree:go2:7f42...",
  "firmware_version":   "1.3.2",
  "capabilities": [
    {
      "id":             "locomotion",
      "description":    "Basic walking and movement control",
      "params":         { "max_speed_ms": 1.5, "gait_modes": ["walk","trot","bound"] },
      "requires_grant": true,
      "safety_level":   "standard"
    },
    {
      "id":             "navigation",
      "description":    "Autonomous navigation to waypoints",
      "params":         { "geofence_required": true },
      "requires_grant": true,
      "safety_level":   "elevated"
    },
    {
      "id":             "camera.read",
      "description":    "Access camera stream and snapshots",
      "params":         { "streams": ["front","chin","left","right","back"], "max_resolution": "1080p" },
      "requires_grant": true,
      "safety_level":   "standard"
    },
    {
      "id":             "telemetry.read",
      "description":    "Subscribe to robot state and sensor data",
      "requires_grant": true,
      "safety_level":   "low"
    },
    {
      "id":             "emergency_stop",
      "description":    "Halt all motion immediately",
      "requires_grant": false,
      "safety_level":   "none"
    }
  ],
  "safety": {
    "emergency_stop":   true,
    "geofence":         true,
    "collision_avoidance": "required",
    "max_speed":        1.5,
    "ungrantable":      ["firmware.update","safety.disable","max_speed_override"]
  },
  "transport": ["ble", "wifi", "usb"],
  "identity": { "public_key": "...", "cert_chain": "..." }
}
```

### Capability Grant (signed token)

```json
{
  "grant_id":       "grant:abc123",
  "session_id":     "session:xyz789",
  "device_id":      "unitree:go2:7f42a3b1",
  "agent_id":       "did:vantage:agent:koda",
  "principal_id":   "did:vantage:principal:user01",
  "capabilities":   ["locomotion", "camera.read", "telemetry.read"],
  "limits": {
    "max_speed":              "1.5 m/s",
    "geofence":               "enabled",
    "geofence_radius_m":      100,
    "collision_avoidance":    "required"
  },
  "issued_at":      1725734400000,
  "expires_at":     1725735300000,
  "revocable":      true,
  "signature":      "<device signs grant>"
}
```

### VCP Command Protocol (in-session)

Commands are semantic, not raw bytes:

```
COMMAND ENVELOPE
{
  "cmd_id":       "<uuid>",
  "session_id":   "<session>",
  "agent_id":     "<agent>",
  "capability":   "locomotion",
  "action":       "walk",
  "params":       { "direction": "forward", "speed": 0.8, "duration_s": 5 },
  "timestamp":    <unix_ms>,
  "signature":    "<agent signs>"
}

RESPONSE ENVELOPE
{
  "cmd_id":       "<echoed>",
  "status":       "accepted" | "executing" | "completed" | "failed" | "denied",
  "telemetry":    { ... },  ← optional real-time state
  "timestamp":    <unix_ms>,
  "signature":    "<device signs>"
}
```

### VCP Adapter Hierarchy

```
VCP CORE (protocol, handshake, grants, receipts)
  │
  ├── ROBOT ADAPTER
  │     ├── Unitree Go2/G1     (WebRTC + Go2 SDK)
  │     ├── Boston Dynamics Spot (BD API)
  │     └── Generic ROS2       (ROS2 topics → VCP commands)
  │
  ├── DRONE ADAPTER
  │     ├── DJI               (Mobile SDK / MSDK)
  │     ├── PX4               (MAVLink → VCP)
  │     └── ArduPilot         (MAVLink → VCP)
  │
  ├── IoT ADAPTER
  │     ├── Home Assistant    (REST/WS → VCP)
  │     ├── Matter            (Matter fabric → VCP)
  │     └── Zigbee            (ZHA → VCP)
  │
  ├── VEHICLE ADAPTER
  │     ├── OBD-II            (ELM327 → VCP)
  │     └── CAN bus           (raw CAN → VCP)
  │
  └── INDUSTRIAL ADAPTER
        ├── OPC-UA            (OPC-UA server → VCP)
        ├── MQTT              (topics → VCP events)
        └── Modbus            (registers → VCP telemetry)
```

### VCP Repo Structure

```
vcp/
  specification/
    vcp-core.md             ← handshake, state machine, wire format
    vcp-manifest.md         ← Agent Device Manifest schema
    vcp-grants.md           ← Capability Grant schema + rules
    vcp-commands.md         ← Command/Response envelope
    vcp-receipts.md         ← Session Receipt schema
    vcp-revocation.md       ← Revocation broadcast protocol
    vcp-safety.md           ← Safety rules: what can never be granted
    vcp-conformance.md      ← What "VCP-compatible" means
  reference-rust/           ← core protocol in Rust (for firmware)
    src/
      handshake.rs
      manifest.rs
      grants.rs
      commands.rs
      receipts.rs
      revocation.rs
      transport/
        ble.rs
        wifi.rs
        meshtastic.rs
  device-sdk/               ← SDK for device manufacturers (C/Rust)
  firmware-sdk/             ← SDK for embedded VCP endpoints
  adapters/
    unitree-go2/
    ros2/
    mavlink/
    home-assistant/
    matter/
  conformance/              ← test suite + device certification spec
```

### VCP Build Order

```
Phase VCP-1  Core spec: manifest schema + capability grant schema
Phase VCP-2  Handshake state machine (Rust reference impl)
Phase VCP-3  BLE + Wi-Fi discovery daemon (in Vantage-Voice)
Phase VCP-4  First adapter: Unitree Go2 (locomotion + camera + telemetry)
Phase VCP-5  Session commands + telemetry stream
Phase VCP-6  Receipts wired to canonical receipt format
Phase VCP-7  Revocation (mid-session + offline Meshtastic broadcast)
Phase VCP-8  ROS2 generic adapter (covers most research robots)
Phase VCP-9  MAVLink adapter (covers most drones)
Phase VCP-10 IoT: Home Assistant adapter (covers most smart home)
Phase VCP-11 Conformance test suite → manufacturer certification path
```

---

## PROTOCOL 3 — TSP (Twin & Simulation Protocol)

### What it solves

A robot scans a room. Whose scan is it? How do we prove it? Can I license
someone else the right to simulate in my captured environment? How do I
prove my simulation was valid? How does a buyer know the twin is accurate?

TSP is the protocol for making physical reality into ownable, provable,
licensable digital artifacts.

### Core Concept: The Twin Asset

A Twin Asset is a cryptographically-identified, versioned, owned, licensed
digital representation of a physical place or object.

```
TWIN ASSET
┌──────────────────────────────────────────────────────┐
│  twin_id:          "twin:sha256:abc123..."           │
│  version:          3                                 │
│  owner_did:        "did:vantage:principal:user01"    │
│  creator_did:      "did:vantage:agent:koda"          │
│  contributors:     [did, did, ...]                   │
│                                                      │
│  PHYSICAL REGION                                     │
│  lat_lon_bbox:     [minlat, minlon, maxlat, maxlon]  │
│  altitude_range:   [min_m, max_m]                    │
│  capture_epoch:    [start_ts, end_ts]                │
│                                                      │
│  DATA HASHES (Merkle-bound)                          │
│  rgb_hash:         sha256(rgb_frames[])              │
│  depth_hash:       sha256(depth_frames[])            │
│  lidar_hash:       sha256(lidar_scans[])             │
│  imu_hash:         sha256(imu_records[])             │
│  slam_hash:        sha256(slam_trajectory)           │
│  splat_hash:       sha256(gaussian_splat.ply)        │
│  geometry_hash:    sha256(mesh.obj)                  │
│  semantic_hash:    sha256(labels.json)               │
│  environment_hash: sha256(physics_params.json)       │
│                                                      │
│  QUALITY                                             │
│  f1_score:         0.831                             │
│  coverage_pct:     94.2                              │
│  reconstruction_engine: "julia-gsplat/2.1"          │
│                                                      │
│  PROVENANCE                                          │
│  evidence_ids:     [receipt:31020:..., ...]          │
│  capture_devices:  [device_id, ...]                  │
│  camera_ids:       [cam_id, ...]                     │
│  pose_estimates:   [pose_estimate_hash, ...]         │
│                                                      │
│  LICENSING                                           │
│  license:          "vcp-twin-v1/exclusive"           │
│  usage_rights:     ["simulate", "view", "annotate"]  │
│  revenue_split:    { owner: 0.7, contributors: 0.3 } │
│  sui_object_id:    "0x..."                           │
│                                                      │
│  MERKLE ROOT (binds all fields)                      │
│  merkle_root:      "sha256:..."                      │
│  signature:        "<owner signs merkle root>"       │
└──────────────────────────────────────────────────────┘
```

### TSP Message Types

```
CAPTURE_RECORD       Per-capture: device, modality, timestamps, hashes
TWIN_CREATION        Assembled Twin Asset (receipt kind: 31030)
TWIN_UPDATE          New version (incremental rescan, better coverage)
TWIN_TRANSFER        Ownership transfer (new owner signs)
SIM_JOB              Simulation run request against a Twin
SIM_RECEIPT          Proof-of-Simulation: params + merkle commitment + witnesses
VALIDATION_REQUEST   Ask another agent to reproduce/validate a sim result
VALIDATION_RECEIPT   Proof-of-Validation: validator confirms or disputes
OBSERVATION_RECORD   Witness attests physical outcome after sim→real execution
TWIN_LICENSE_GRANT   Permission to simulate/view/annotate a Twin Asset
```

### Capture Receipt (kind 31020)

Issued per-capture run. The atomic unit of contribution.

```json
{
  "kind":           31020,
  "receipt_id":     "receipt:31020:abc...",
  "agent_id":       "did:vantage:agent:koda",
  "principal_id":   "did:vantage:principal:user01",
  "device_ids":     ["phone:pixel9:...", "robot:go2:7f42"],
  "modalities":     ["rgb", "depth", "imu"],
  "coverage_pct":   72.4,
  "f1_score":       0.831,
  "frame_count":    8420,
  "duration_ms":    94000,
  "lat_lon_bbox":   [-33.8688, 151.2093, -33.8650, 151.2140],
  "capture_ts":     [1725734400000, 1725734494000],
  "raw_hashes":     { "rgb": "sha256:...", "depth": "sha256:..." },
  "novelty_score":  0.67,
  "privacy_flags":  [],
  "signature":      "<agent signs>"
}
```

### Scene Receipt (kind 31030)

Issued when a full Twin Asset is assembled. Creates the IP Root.

```json
{
  "kind":           31030,
  "receipt_id":     "receipt:31030:def...",
  "twin_id":        "twin:sha256:abc123...",
  "agent_id":       "did:vantage:agent:koda",
  "principal_id":   "did:vantage:principal:user01",
  "capture_receipts": ["receipt:31020:...", "receipt:31020:..."],
  "reconstruction_engine": "julia-gsplat/2.1",
  "splat_hash":     "sha256:...",
  "geometry_hash":  "sha256:...",
  "semantic_hash":  "sha256:...",
  "f1_score":       0.891,
  "coverage_pct":   94.2,
  "merkle_root":    "sha256:...",
  "sui_object_id":  "0x...",
  "license":        "vcp-twin-v1",
  "signature":      "<principal signs>"
}
```

### Proof-of-Simulation Receipt

Issued after a valid simulation run. Binds sim parameters + outputs + witness.

```json
{
  "kind":           "proof_of_simulation",
  "receipt_id":     "receipt:sim:ghi...",
  "twin_id":        "twin:sha256:abc123...",
  "sim_engine":     "osovm/2.0",
  "agent_id":       "did:vantage:agent:koda",
  "params":         { "robot_model": "go2", "policy": "energy_min", "trajectories": 100000 },
  "selected_policy": {
    "id":           "policy_B",
    "energy":       61,
    "risk":         0.04
  },
  "merkle_commitment": "sha256:...",
  "all_policies_hash": "sha256:...",
  "witness_ids":    ["did:witness:node01", "did:witness:node02"],
  "timestamp":      1725734400000,
  "signature":      "<agent signs merkle commitment>"
}
```

### Proof-of-Observation Receipt

Issued by physical Witness after real-world execution.

```json
{
  "kind":           "proof_of_observation",
  "receipt_id":     "receipt:obs:jkl...",
  "sim_receipt_id": "receipt:sim:ghi...",
  "witness_id":     "did:witness:node01",
  "observed":       { "actual_energy": 63, "distance_m": 14.2, "duration_s": 22 },
  "sim_predicted":  { "energy": 61, "distance_m": 13.8, "duration_s": 21 },
  "delta_pct":      { "energy": 3.2, "distance": 2.9 },
  "outcome":        "validated",
  "hardware_sig":   "<witness firmware signs with TPM key>",
  "timestamp":      1725735000000
}
```

### TSP Twin Lifecycle

```
RAW CAPTURE
  → [31020 Capture Receipt] per device/run
  → [F1 gate: ≥ 0.777]
  → RECONSTRUCTION (Julia gsplat)
  → [31030 Scene Receipt] → IP Root on Sui
  → TWIN ASSET v1

TWIN UPDATE
  → New capture fills gaps
  → [31020] → Reconstruction → [31030 v2]
  → Old version archived, new version canonical

TWIN LICENSING
  → License Grant: { twin_id, grantee, rights, duration, fee }
  → [License Receipt] on Sui
  → Grantee can now run SIM_JOB against the Twin

SIMULATION
  → [SIM_JOB] against Twin
  → [SIM_RECEIPT] = Proof-of-Simulation
  → Physical execution
  → [OBSERVATION_RECORD] = Proof-of-Observation
  → Mycelium: sim vs reality delta → model update
```

### TSP Marketplace Products (distinct licenses)

```
PRODUCT               LICENSE TYPE        PRICE BASIS
Raw captures          per-frame           novelty × modality
Reconstruction        per-twin            coverage × f1
Semantic twin         per-twin            completeness × labels
Sim environment       per-run OR time     physics fidelity
Sim results           per-policy-set      trajectory count
Knowledge             per-claim           confidence × validation
```

### TSP Repo Structure

```
twin-protocol/
  specification/
    tsp-core.md             ← Twin Asset schema, Merkle structure
    tsp-capture.md          ← Capture Receipt (31020) spec
    tsp-scene.md            ← Scene Receipt (31030) spec
    tsp-simulation.md       ← Proof-of-Simulation spec
    tsp-observation.md      ← Proof-of-Observation spec
    tsp-licensing.md        ← License Grant types + rules
    tsp-marketplace.md      ← Product types, pricing models
    tsp-conformance.md
  schemas/
    twin_asset.json
    capture_receipt.json
    scene_receipt.json
    sim_receipt.json
    obs_receipt.json
    license_grant.json
  reference-rust/
    src/
      twin.rs
      receipts/
        capture.rs
        scene.rs
        sim.rs
        observation.rs
      licensing.rs
      merkle.rs
      quality.rs
  julia-sdk/                ← Gaussian splat pipeline integration
  python-sdk/               ← COLMAP / data pipeline integration
  move-contracts/           ← Sui: Twin NFT, License NFT, revenue split
  conformance/
```

### TSP Build Order

```
Phase TSP-1  Twin Asset schema (Rust types + JSON schema)
Phase TSP-2  Capture Receipt (31020): schema + sign + verify
Phase TSP-3  Scene Receipt (31030): schema + Merkle commitment + Sui anchor
Phase TSP-4  F1 quality gate wired to capture pipeline (reject < 0.777)
Phase TSP-5  Julia gsplat → TSP Twin Asset (hash all outputs, sign)
Phase TSP-6  Proof-of-Simulation receipt (ỌSỌVM integration)
Phase TSP-7  Proof-of-Observation receipt (Witness firmware integration)
Phase TSP-8  License Grant system (types + Sui NFT)
Phase TSP-9  Twin marketplace (product listing, fee routing, revenue split)
Phase TSP-10 Validation receipts + cross-agent twin verification
```

---

## HOW THE THREE PROTOCOLS CONNECT

```
HUMAN says "Koda, scan this room."
  ↓
VCP   — Agent connects to robot + drone cameras (session established)
VCP   — Device manifests declare capture capability
TSP   — Pipeline begins: capture records accumulate
TSP   — 31020 receipts issued per capture (F1 gate)
TSP   — 31030 issued when scene assembled (IP Root → Sui)
DIP   — Another agent (on Nostr) asks to license the Twin
DIP   — DIP envelope bridges Nostr → Vantage
TSP   — License Grant issued, sim rights granted
TSP   — SIM_JOB runs against Twin (ỌSỌVM)
TSP   — Proof-of-Simulation receipt
VCP   — Agent commands robot to execute winning policy
TSP   — Proof-of-Observation receipt (Witness attests)
DIP   — Receipt propagated back to Nostr agent
DIP   — IfáScript claim issued, routed via DIP to Twelve Thrones
```

---

## CRITICAL IMPLEMENTATION RULES

### DIP
- NEVER replace A2A or MCP — only wrap them
- Identity equivalences MUST be bidirectionally verifiable (both sides sign)
- Routing failures must be retried with backoff, not silently dropped
- Every DIP message carries: principal_id + agent_id + session_id + message_id

### VCP
- Safety capabilities (emergency_stop) are NEVER gated behind a grant
- Firmware update + safety disable are UNGRANTABLE (hardcoded)
- Capability grants have MAX TTL of 24 hours, default 15 minutes
- Revocation must propagate even if device goes offline (Meshtastic broadcast)
- Every VCP action carries: principal_id + agent_id + device_id + capability_id

### TSP
- F1 score < 0.777 → capture receipt REJECTED (no partial credit below gate)
- Twin Asset Merkle root MUST bind all data hashes — any field change = new version
- Simulation receipts MUST commit to ALL candidate policies (not just selected)
- Observation receipts are signed by hardware TPM — software signatures invalid
- Ownership transfers require signature from BOTH current owner AND new owner

---

## THE CANONICAL 5 PRIMITIVES — APPLIED TO EACH PROTOCOL

```
              Principal    Capability    Action      Evidence      Receipt
DIP           DID owner    Adapter cap   Route msg   DIP envelope  DIP receipt
VCP           principal_id Capability    VCP command Telemetry     VCP session receipt
TSP           twin owner   License grant Capture/sim Capture data  31020/31030/sim/obs
```

Every consequential event in all three protocols flows through these 5.
No exceptions.
