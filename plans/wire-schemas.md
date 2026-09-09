# Wire Schemas — DIP · VCP · TSP
# Canonical types across all three protocols
# Written: 2026-09-08

---

## SHARED PRIMITIVES (used by all three)

These types appear in DIP envelopes, VCP sessions, and TSP receipts.
Define once, reference everywhere.

### Identity Types

```rust
// A canonical DID — the root identity across all protocol representations
type Did = String;          // "did:vantage:principal:abc123"
type AgentDid = String;     // "did:vantage:agent:koda"
type DeviceDid = String;    // "did:device:unitree:go2:7f42"
type WitnessDid = String;   // "did:witness:node01"

// A signature — always over the canonical Merkle root of the containing struct
type Signature = String;    // base64url(ed25519_sign(merkle_root, private_key))
type Hash = String;         // "sha256:<hex>"
type Timestamp = u64;       // Unix milliseconds
type Uuid = String;         // UUID v4
```

### The 5 Canonical Primitives (always travel together)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct IdentityChain {
    pub principal_id: Did,
    pub agent_id:     AgentDid,
    pub session_id:   Uuid,
    pub execution_id: Uuid,
    pub receipt_id:   Uuid,
}
```

```json
// JSON form — every consequential event includes this
{
  "principal_id":  "did:vantage:principal:user01",
  "agent_id":      "did:vantage:agent:koda",
  "session_id":    "sess:550e8400-e29b-41d4-a716-446655440000",
  "execution_id":  "exec:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "receipt_id":    "rcpt:6ba7b811-9dad-11d1-80b4-00c04fd430c8"
}
```

### Merkle Commitment

All signable structs commit to a Merkle root over their canonical fields.
Field order is alphabetical. Leaf = sha256(field_name + ":" + json_value).

```rust
pub fn merkle_root(fields: &BTreeMap<&str, Value>) -> Hash {
    let leaves: Vec<Hash> = fields.iter()
        .map(|(k, v)| sha256(format!("{}:{}", k, v.to_string())))
        .collect();
    merkle_tree_root(leaves)
}
```

---

## PROTOCOL 1 — DIP WIRE SCHEMAS

### DIP Envelope (the lingua franca)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct DipEnvelope {
    // Header
    pub version:      String,           // "dip/1"
    pub message_id:   Uuid,
    pub timestamp:    Timestamp,
    pub ttl:          u32,              // seconds until expiry

    // Routing
    pub origin:       DipAddress,
    pub destination:  DipAddress,
    pub routing:      Vec<DipHop>,     // filled by routers

    // Identity (always present)
    pub identity:     IdentityChain,

    // Payload
    pub kind:         DipKind,
    pub payload:      Value,            // kind-specific JSON

    // Integrity
    pub merkle_root:  Hash,
    pub signature:    Signature,        // principal signs envelope
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DipAddress {
    pub network:  DipNetwork,          // which protocol network
    pub address:  String,              // network-specific address
    pub did:      Option<Did>,         // resolved canonical DID (if known)
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DipNetwork {
    Vantage,
    Nostr,
    A2A,
    Mcp,
    Meshtastic,
    Freenet,
    Libp2p,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DipKind {
    Capability,     // declare or request capabilities
    Message,        // agent communication
    Evidence,       // signed observations / attestations
    Receipt,        // action completion records
    Event,          // broadcast notifications
    Claim,          // IfáScript claim for epistemic evaluation
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DipHop {
    pub node:       DipAddress,
    pub adapter:    DipNetwork,
    pub timestamp:  Timestamp,
    pub latency_ms: Option<u32>,
}
```

```json
// DIP Envelope — wire example
{
  "version":      "dip/1",
  "message_id":   "550e8400-e29b-41d4-a716-446655440000",
  "timestamp":    1725734400000,
  "ttl":          300,

  "origin": {
    "network":  "nostr",
    "address":  "npub1xyz...",
    "did":      "did:vantage:agent:external-agent-01"
  },
  "destination": {
    "network":  "vantage",
    "address":  "did:vantage:agent:koda",
    "did":      "did:vantage:agent:koda"
  },
  "routing": [
    { "node": { "network": "nostr", "address": "relay.nostr.info" }, "adapter": "nostr", "timestamp": 1725734400010, "latency_ms": 10 },
    { "node": { "network": "vantage", "address": "dip.vantage.local" }, "adapter": "vantage", "timestamp": 1725734400050, "latency_ms": 40 }
  ],

  "identity": {
    "principal_id":  "did:vantage:principal:external-user",
    "agent_id":      "did:vantage:agent:external-agent-01",
    "session_id":    "sess:abc123",
    "execution_id":  "exec:def456",
    "receipt_id":    "rcpt:ghi789"
  },

  "kind":    "message",
  "payload": {
    "text":    "I want to license twin:sha256:abc123 for simulation",
    "context": "planning robotics trial run"
  },

  "merkle_root": "sha256:aabbcc...",
  "signature":   "base64url:signature_bytes..."
}
```

### DIP Identity Document

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct DipIdentityDocument {
    pub did:          Did,
    pub created:      Timestamp,
    pub equivalences: Vec<DipEquivalence>,
    pub service_endpoints: Vec<DipServiceEndpoint>,
    pub merkle_root:  Hash,
    pub signature:    Signature,    // canonical key signs all equivalences
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DipEquivalence {
    pub network:    DipNetwork,
    pub address:    String,
    pub proof:      Signature,     // network-specific key signs canonical DID
    pub verified:   bool,          // true after round-trip challenge verified
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DipServiceEndpoint {
    pub kind:       String,        // "vantage-mcp", "a2a", "vcp-gateway"
    pub url:        String,
    pub protocol:   String,
}
```

```json
// DIP Identity Document — wire example
{
  "did":      "did:vantage:agent:koda",
  "created":  1725734400000,
  "equivalences": [
    {
      "network": "nostr",
      "address": "npub1koda...",
      "proof":   "base64url:<nostr_key signs 'did:vantage:agent:koda'>",
      "verified": true
    },
    {
      "network": "meshtastic",
      "address": "!deadbeef",
      "proof":   "base64url:<meshtastic_key signs 'did:vantage:agent:koda'>",
      "verified": true
    },
    {
      "network": "a2a",
      "address": "koda@sovereign.local",
      "proof":   "base64url:<a2a_key signs 'did:vantage:agent:koda'>",
      "verified": true
    }
  ],
  "service_endpoints": [
    { "kind": "vantage-mcp", "url": "http://localhost:8001/mcp", "protocol": "mcp/1" },
    { "kind": "a2a",         "url": "http://localhost:8001/a2a", "protocol": "a2a/1" },
    { "kind": "vcp-gateway", "url": "http://localhost:8001/vcp", "protocol": "vcp/1" }
  ],
  "merkle_root": "sha256:112233...",
  "signature":   "base64url:..."
}
```

### DIP Capability Payload

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct DipCapabilityPayload {
    pub direction:    CapabilityDirection,
    pub capabilities: Vec<DipCapability>,
    pub context:      Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum CapabilityDirection { Declare, Request, Grant, Revoke }

#[derive(Debug, Serialize, Deserialize)]
pub struct DipCapability {
    pub id:           String,          // "twin.simulate", "task.delegate", "data.read"
    pub description:  Option<String>,
    pub params:       Option<Value>,
    pub constraints:  Option<Value>,   // limits on use
    pub expires_at:   Option<Timestamp>,
}
```

### DIP Receipt Payload

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct DipReceiptPayload {
    pub action:       String,          // what was done
    pub target:       Option<String>,  // what it was done to
    pub outcome:      DipOutcome,
    pub duration_ms:  u64,
    pub evidence_ids: Vec<Hash>,
    pub notes:        Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DipOutcome { Success, Partial, Failure, Pending }
```

---

## PROTOCOL 2 — VCP WIRE SCHEMAS

### Agent Device Manifest

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct AgentDeviceManifest {
    pub device_id:          String,       // "unitree:go2:7f42a3b1"
    pub manufacturer:       String,
    pub model:              String,
    pub protocol_version:   String,       // "vcp/1"
    pub firmware_version:   String,
    pub dip_identity:       DeviceDid,
    pub capabilities:       Vec<VcpCapabilityDecl>,
    pub safety:             VcpSafetyConfig,
    pub transport:          Vec<VcpTransport>,
    pub identity:           VcpDeviceIdentity,
    pub timestamp:          Timestamp,
    pub signature:          Signature,    // device signs manifest
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpCapabilityDecl {
    pub id:             String,           // "locomotion", "camera.read"
    pub description:    String,
    pub params:         Option<Value>,    // capability-specific constraints
    pub requires_grant: bool,
    pub safety_level:   VcpSafetyLevel,
    pub ungrantable:    bool,             // true = can NEVER be granted
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpSafetyLevel { None, Low, Standard, Elevated, Critical }

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpSafetyConfig {
    pub emergency_stop:       bool,       // MUST be true on any mobile device
    pub geofence:             bool,
    pub collision_avoidance:  Option<String>,
    pub max_speed_ms:         Option<f32>,
    pub ungrantable:          Vec<String>, // always blocked: ["firmware.update","safety.disable"]
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpTransport { Ble, Wifi, Usb, Nfc, Meshtastic, Cellular }

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpDeviceIdentity {
    pub public_key:   String,            // ed25519 public key (base64url)
    pub cert_chain:   Option<Vec<String>>,
}
```

```json
// Agent Device Manifest — wire example (Unitree Go2)
{
  "device_id":         "unitree:go2:7f42a3b1",
  "manufacturer":      "Unitree",
  "model":             "Go2",
  "protocol_version":  "vcp/1",
  "firmware_version":  "1.3.2",
  "dip_identity":      "did:device:unitree:go2:7f42a3b1",

  "capabilities": [
    {
      "id":             "locomotion",
      "description":    "Basic walking and movement control",
      "params":         { "max_speed_ms": 1.5, "gaits": ["walk","trot","bound"] },
      "requires_grant": true,
      "safety_level":   "standard",
      "ungrantable":    false
    },
    {
      "id":             "navigation",
      "description":    "Autonomous waypoint navigation",
      "params":         { "geofence_required": true, "max_waypoints": 50 },
      "requires_grant": true,
      "safety_level":   "elevated",
      "ungrantable":    false
    },
    {
      "id":             "camera.read",
      "description":    "Access camera streams and snapshots",
      "params":         { "streams": ["front","chin","left","right","back"], "max_resolution": "1080p" },
      "requires_grant": true,
      "safety_level":   "standard",
      "ungrantable":    false
    },
    {
      "id":             "telemetry.read",
      "description":    "Subscribe to robot state and sensor data",
      "params":         { "fields": ["pose","velocity","battery","temperature","imu"] },
      "requires_grant": true,
      "safety_level":   "low",
      "ungrantable":    false
    },
    {
      "id":             "emergency_stop",
      "description":    "Halt all motion immediately",
      "params":         null,
      "requires_grant": false,
      "safety_level":   "none",
      "ungrantable":    false
    },
    {
      "id":             "firmware.update",
      "description":    "Update device firmware",
      "params":         null,
      "requires_grant": true,
      "safety_level":   "critical",
      "ungrantable":    true
    }
  ],

  "safety": {
    "emergency_stop":      true,
    "geofence":            true,
    "collision_avoidance": "required",
    "max_speed_ms":        1.5,
    "ungrantable":         ["firmware.update", "safety.disable", "max_speed_override"]
  },

  "transport":   ["wifi", "ble", "usb"],
  "identity":    { "public_key": "base64url:...", "cert_chain": null },
  "timestamp":   1725734400000,
  "signature":   "base64url:..."
}
```

### VCP Handshake Messages

```rust
// STEP 3: Challenge
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpChallenge {
    pub challenge_id:   Uuid,
    pub nonce:          String,         // 32 random bytes, base64url
    pub device_id:      String,
    pub timestamp:      Timestamp,
    pub expires_at:     Timestamp,      // nonce expires in 60s
    pub signature:      Signature,      // device signs challenge
}

// STEP 3: Challenge Response
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpChallengeResponse {
    pub challenge_id:   Uuid,
    pub identity:       IdentityChain,
    pub nonce_sig:      Signature,      // principal signs nonce
    pub dip_identity:   Did,            // agent's full DIP identity doc URL
    pub timestamp:      Timestamp,
    pub signature:      Signature,      // agent signs full response
}

// STEP 4: Capability Request
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpCapabilityRequest {
    pub request_id:     Uuid,
    pub identity:       IdentityChain,
    pub capabilities:   Vec<String>,    // capability IDs requested
    pub purpose:        String,         // human-readable intent
    pub duration:       VcpDuration,
    pub limits:         Option<Value>,  // requested limits (device may tighten)
    pub timestamp:      Timestamp,
    pub signature:      Signature,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpDuration {
    pub requested_min: u32,             // minimum needed (reject if can't grant)
    pub preferred_min: u32,             // preferred
    pub max_min:       u32,             // won't use more than this (1440 = 24hr cap)
}

// STEP 4: Capability Grant
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpCapabilityGrant {
    pub grant_id:       Uuid,
    pub request_id:     Uuid,           // echoes capability_request
    pub session_id:     Uuid,
    pub identity:       IdentityChain,
    pub device_id:      String,
    pub capabilities:   Vec<VcpGrantedCapability>,
    pub denied:         Vec<VcpDeniedCapability>,
    pub issued_at:      Timestamp,
    pub expires_at:     Timestamp,
    pub revocable:      bool,           // always true for agent grants
    pub merkle_root:    Hash,
    pub signature:      Signature,      // device signs grant
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpGrantedCapability {
    pub id:      String,
    pub limits:  Value,                 // actual enforced limits (may be tighter than requested)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpDeniedCapability {
    pub id:      String,
    pub reason:  VcpDenyReason,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpDenyReason {
    Ungrantable,        // hardcoded off
    InsufficientAuth,   // principal not authorized
    UnsupportedLimit,   // device can't enforce requested limit
    Unavailable,        // capability temporarily unavailable
}
```

```json
// VCP Capability Grant — wire example
{
  "grant_id":   "grant:550e8400-e29b-41d4-a716-446655440001",
  "request_id": "req:550e8400-e29b-41d4-a716-446655440000",
  "session_id": "sess:6ba7b810-9dad-11d1-80b4-00c04fd430c8",

  "identity": {
    "principal_id":  "did:vantage:principal:user01",
    "agent_id":      "did:vantage:agent:koda",
    "session_id":    "sess:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "execution_id":  "exec:abc123",
    "receipt_id":    "rcpt:def456"
  },

  "device_id": "unitree:go2:7f42a3b1",

  "capabilities": [
    {
      "id":     "locomotion",
      "limits": { "max_speed_ms": 1.0, "geofence_enabled": true, "geofence_radius_m": 50 }
    },
    {
      "id":     "camera.read",
      "limits": { "streams": ["front"], "max_resolution": "720p", "max_fps": 15 }
    },
    {
      "id":     "telemetry.read",
      "limits": { "fields": ["pose","battery"], "max_hz": 10 }
    }
  ],

  "denied": [
    { "id": "navigation", "reason": "insufficient_auth" },
    { "id": "firmware.update", "reason": "ungrantable" }
  ],

  "issued_at":   1725734400000,
  "expires_at":  1725735300000,
  "revocable":   true,
  "merkle_root": "sha256:aabbcc...",
  "signature":   "base64url:..."
}
```

### VCP Command / Response

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpCommand {
    pub cmd_id:      Uuid,
    pub session_id:  Uuid,
    pub grant_id:    Uuid,              // must reference valid active grant
    pub identity:    IdentityChain,
    pub capability:  String,            // granted capability being exercised
    pub action:      String,            // specific action within capability
    pub params:      Value,
    pub timestamp:   Timestamp,
    pub signature:   Signature,         // agent signs command
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VcpCommandResponse {
    pub cmd_id:      Uuid,              // echoed
    pub session_id:  Uuid,
    pub device_id:   String,
    pub status:      VcpCommandStatus,
    pub telemetry:   Option<Value>,     // current device state snapshot
    pub error:       Option<String>,
    pub timestamp:   Timestamp,
    pub signature:   Signature,         // device signs response
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpCommandStatus {
    Accepted,       // command queued
    Executing,      // command in progress (streaming update)
    Completed,      // command done
    Failed,         // command failed (see error)
    Denied,         // grant doesn't cover this action
    GrantExpired,   // grant has expired, re-negotiate
}
```

```json
// VCP Command — wire example
{
  "cmd_id":     "cmd:aabbcc",
  "session_id": "sess:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "grant_id":   "grant:550e8400-e29b-41d4-a716-446655440001",

  "identity": {
    "principal_id": "did:vantage:principal:user01",
    "agent_id":     "did:vantage:agent:koda",
    "session_id":   "sess:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "execution_id": "exec:abc123",
    "receipt_id":   "rcpt:def456"
  },

  "capability": "locomotion",
  "action":     "walk",
  "params":     { "direction": "forward", "speed_ms": 0.8, "duration_s": 5 },
  "timestamp":  1725734410000,
  "signature":  "base64url:..."
}
```

### VCP Session Receipt

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpSessionReceipt {
    pub receipt_id:        Uuid,
    pub session_id:        Uuid,
    pub grant_id:          Uuid,
    pub identity:          IdentityChain,
    pub device_id:         String,
    pub capabilities_used: Vec<String>,
    pub commands_issued:   u32,
    pub commands_success:  u32,
    pub commands_failed:   u32,
    pub telemetry_summary: Option<Value>,
    pub started_at:        Timestamp,
    pub ended_at:          Timestamp,
    pub duration_ms:       u64,
    pub outcome:           VcpSessionOutcome,
    pub evidence_ids:      Vec<Hash>,       // links to TSP capture receipts if scanning
    pub merkle_root:       Hash,
    pub signature:         Signature,       // device signs session receipt
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpSessionOutcome {
    Completed,      // clean disconnect
    Revoked,        // principal revoked mid-session
    Expired,        // grant TTL elapsed
    DeviceFault,    // device error
    NetworkLoss,    // connection dropped
}
```

### VCP Revocation

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct VcpRevocation {
    pub revocation_id: Uuid,
    pub grant_id:      Uuid,
    pub session_id:    Uuid,
    pub identity:      IdentityChain,
    pub reason:        VcpRevocationReason,
    pub timestamp:     Timestamp,
    pub propagate:     bool,            // true = broadcast via Meshtastic
    pub signature:     Signature,       // principal signs revocation
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum VcpRevocationReason {
    UserRequested,
    GrantExpired,
    SecurityIncident,
    PolicyViolation,
    PrincipalRevoked,
}
```

---

## PROTOCOL 3 — TSP WIRE SCHEMAS

### Twin Asset

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct TwinAsset {
    pub twin_id:           Hash,         // "twin:sha256:<merkle_root_of_all_data>"
    pub version:           u32,
    pub owner_did:         Did,
    pub creator_did:       AgentDid,
    pub contributors:      Vec<Did>,

    // Physical region
    pub region:            TwinRegion,

    // Data hashes (all bound to merkle_root)
    pub data_hashes:       TwinDataHashes,

    // Quality
    pub quality:           TwinQuality,

    // Provenance
    pub provenance:        TwinProvenance,

    // Licensing
    pub license:           TwinLicense,

    // On-chain anchor
    pub sui_object_id:     Option<String>,

    // Integrity
    pub merkle_root:       Hash,         // binds ALL fields above
    pub signature:         Signature,    // owner signs merkle_root
    pub created_at:        Timestamp,
    pub updated_at:        Timestamp,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinRegion {
    pub min_lat:   f64,
    pub min_lon:   f64,
    pub max_lat:   f64,
    pub max_lon:   f64,
    pub min_alt_m: Option<f32>,
    pub max_alt_m: Option<f32>,
    pub label:     Option<String>,       // "Building A, Floor 2"
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinDataHashes {
    pub rgb:         Option<Hash>,
    pub depth:       Option<Hash>,
    pub lidar:       Option<Hash>,
    pub imu:         Option<Hash>,
    pub slam:        Option<Hash>,
    pub splat:       Option<Hash>,       // Gaussian splat .ply
    pub geometry:    Option<Hash>,       // mesh .obj
    pub semantic:    Option<Hash>,       // labels .json
    pub environment: Option<Hash>,       // physics params
    pub custom:      Option<BTreeMap<String, Hash>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinQuality {
    pub f1_score:              f32,      // MUST be >= 0.777 to be valid
    pub coverage_pct:          f32,
    pub reconstruction_engine: String,  // "julia-gsplat/2.1"
    pub frame_count:           u32,
    pub gaussian_count:        Option<u32>,
    pub validated:             bool,     // true after independent validation
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinProvenance {
    pub capture_receipts:      Vec<Uuid>,   // receipt:31020:... IDs
    pub capture_epoch:         [Timestamp; 2],
    pub device_ids:            Vec<String>,
    pub camera_ids:            Vec<String>,
    pub pose_estimate_hashes:  Vec<Hash>,
    pub calibration_version:   String,
    pub evidence_ids:          Vec<Uuid>,   // links to Witness observations
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinLicense {
    pub license_type:   TwinLicenseType,
    pub usage_rights:   Vec<TwinUsageRight>,
    pub revenue_split:  RevenueSplit,
    pub transferable:   bool,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TwinLicenseType {
    Exclusive,          // only owner can use
    NonExclusive,       // owner can grant to others
    OpenAccess,         // anyone can use (view/simulate)
    ResearchOnly,       // non-commercial use only
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TwinUsageRight { View, Simulate, Annotate, Derive, Distribute, Commercial }

#[derive(Debug, Serialize, Deserialize)]
pub struct RevenueSplit {
    pub owner_pct:       f32,
    pub contributors:    Vec<ContributorSplit>,
    pub protocol_fee:    f32,            // ecosystem fee (e.g. 2.5%)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ContributorSplit {
    pub did:  Did,
    pub pct:  f32,
}
```

### Capture Receipt (kind 31020)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct CaptureReceipt {
    pub kind:          u32,             // 31020
    pub receipt_id:    Uuid,
    pub identity:      IdentityChain,

    // What was captured
    pub device_ids:    Vec<String>,
    pub modalities:    Vec<Modality>,
    pub region:        TwinRegion,
    pub capture_epoch: [Timestamp; 2],

    // Quality gate — REJECT if f1 < 0.777
    pub f1_score:      f32,
    pub coverage_pct:  f32,
    pub frame_count:   u32,
    pub duration_ms:   u64,

    // Data hashes of raw captures
    pub raw_hashes:    BTreeMap<String, Hash>,

    // Contribution signal
    pub novelty_score: f32,             // 0.0-1.0: how much new coverage this adds
    pub delta_coverage: f32,            // coverage improvement over prior best

    // Privacy
    pub privacy_flags: Vec<PrivacyFlag>,

    // Integrity
    pub merkle_root:   Hash,
    pub signature:     Signature,       // agent signs
    pub timestamp:     Timestamp,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Modality { Rgb, Depth, Lidar, Imu, Slam, Thermal, Acoustic }

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PrivacyFlag { FacesDetected, LicensePlatesDetected, PersonalDataPresent }
```

```json
// Capture Receipt (31020) — wire example
{
  "kind":       31020,
  "receipt_id": "rcpt:31020:550e8400-e29b-41d4-a716-446655440001",

  "identity": {
    "principal_id": "did:vantage:principal:user01",
    "agent_id":     "did:vantage:agent:koda",
    "session_id":   "sess:abc123",
    "execution_id": "exec:def456",
    "receipt_id":   "rcpt:31020:550e8400-e29b-41d4-a716-446655440001"
  },

  "device_ids":   ["phone:pixel9:aabb", "robot:go2:7f42"],
  "modalities":   ["rgb", "depth", "imu"],

  "region": {
    "min_lat": -33.8688, "min_lon": 151.2093,
    "max_lat": -33.8650, "max_lon": 151.2140,
    "label":   "Warehouse Bay 3"
  },

  "capture_epoch": [1725734400000, 1725734494000],

  "f1_score":       0.831,
  "coverage_pct":   72.4,
  "frame_count":    8420,
  "duration_ms":    94000,

  "raw_hashes": {
    "rgb":   "sha256:aabb1122...",
    "depth": "sha256:ccdd3344...",
    "imu":   "sha256:eeff5566..."
  },

  "novelty_score":  0.67,
  "delta_coverage": 18.3,
  "privacy_flags":  [],

  "merkle_root": "sha256:112233...",
  "signature":   "base64url:...",
  "timestamp":   1725734494000
}
```

### Scene Receipt (kind 31030)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct SceneReceipt {
    pub kind:                   u32,    // 31030
    pub receipt_id:             Uuid,
    pub twin_id:                Hash,   // the Twin Asset this creates/updates
    pub version:                u32,
    pub identity:               IdentityChain,

    // Source captures
    pub capture_receipt_ids:    Vec<Uuid>,

    // Reconstruction
    pub reconstruction_engine:  String,
    pub splat_hash:             Hash,
    pub geometry_hash:          Option<Hash>,
    pub semantic_hash:          Option<Hash>,

    // Quality (must exceed gate)
    pub f1_score:               f32,    // MUST be >= 0.777
    pub coverage_pct:           f32,
    pub gaussian_count:         Option<u32>,

    // On-chain
    pub sui_object_id:          Option<String>,
    pub ip_root_tx:             Option<String>,

    // License
    pub license_type:           TwinLicenseType,

    // Integrity
    pub merkle_root:            Hash,
    pub signature:              Signature,
    pub timestamp:              Timestamp,
}
```

```json
// Scene Receipt (31030) — wire example
{
  "kind":       31030,
  "receipt_id": "rcpt:31030:6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "twin_id":    "twin:sha256:aabbcc112233...",
  "version":    1,

  "identity": {
    "principal_id": "did:vantage:principal:user01",
    "agent_id":     "did:vantage:agent:koda",
    "session_id":   "sess:abc123",
    "execution_id": "exec:scan-session-01",
    "receipt_id":   "rcpt:31030:6ba7b810-9dad-11d1-80b4-00c04fd430c8"
  },

  "capture_receipt_ids": [
    "rcpt:31020:550e8400-e29b-41d4-a716-446655440001",
    "rcpt:31020:550e8400-e29b-41d4-a716-446655440002"
  ],

  "reconstruction_engine": "julia-gsplat/2.1",
  "splat_hash":            "sha256:9900aabb...",
  "geometry_hash":         "sha256:bbcc1122...",
  "semantic_hash":         null,

  "f1_score":      0.891,
  "coverage_pct":  94.2,
  "gaussian_count": 1842000,

  "sui_object_id": "0x1a2b3c...",
  "ip_root_tx":    "0xdeadbeef...",
  "license_type":  "non_exclusive",

  "merkle_root": "sha256:445566...",
  "signature":   "base64url:...",
  "timestamp":   1725738000000
}
```

### Proof-of-Simulation Receipt

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct SimulationReceipt {
    pub kind:               String,     // "proof_of_simulation"
    pub receipt_id:         Uuid,
    pub twin_id:            Hash,
    pub identity:           IdentityChain,

    // Simulation config
    pub sim_engine:         String,     // "osovm/2.0"
    pub robot_model:        String,
    pub trajectory_count:   u32,        // e.g. 100000

    // ALL candidate policies (must commit to all, not just winner)
    pub all_policies_hash:  Hash,       // sha256(json(all_policies[]))
    pub all_policies:       Vec<SimPolicy>,

    // Selected policy
    pub selected_policy_id: String,
    pub selection_criteria: String,     // "min_risk_below_energy_threshold"

    // Cryptographic commitment
    pub merkle_commitment:  Hash,       // binds twin_id + params + all_policies

    // Witnesses (independent nodes that saw the sim run)
    pub witness_ids:        Vec<WitnessDid>,
    pub witness_sigs:       Vec<WitnessAttestation>,

    pub timestamp:          Timestamp,
    pub signature:          Signature,  // agent signs merkle_commitment
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SimPolicy {
    pub id:       String,
    pub energy:   f32,
    pub risk:     f32,
    pub duration_s: f32,
    pub metrics:  Option<Value>,        // additional policy-specific metrics
}

#[derive(Debug, Serialize, Deserialize)]
pub struct WitnessAttestation {
    pub witness_id:      WitnessDid,
    pub merkle_commitment: Hash,        // what the witness saw
    pub timestamp:       Timestamp,
    pub signature:       Signature,     // witness signs the commitment
}
```

```json
// Proof-of-Simulation Receipt — wire example
{
  "kind":       "proof_of_simulation",
  "receipt_id": "rcpt:sim:aabbcc001",
  "twin_id":    "twin:sha256:aabbcc112233...",

  "identity": {
    "principal_id": "did:vantage:principal:user01",
    "agent_id":     "did:vantage:agent:koda",
    "session_id":   "sess:sim-session-01",
    "execution_id": "exec:osovm-run-01",
    "receipt_id":   "rcpt:sim:aabbcc001"
  },

  "sim_engine":       "osovm/2.0",
  "robot_model":      "unitree:go2",
  "trajectory_count": 100000,

  "all_policies_hash": "sha256:ff0011...",
  "all_policies": [
    { "id": "policy_A", "energy": 72, "risk": 0.12, "duration_s": 18 },
    { "id": "policy_B", "energy": 61, "risk": 0.04, "duration_s": 21 },
    { "id": "policy_C", "energy": 59, "risk": 0.21, "duration_s": 16 }
  ],

  "selected_policy_id": "policy_B",
  "selection_criteria": "min_risk_below_energy_threshold_65",

  "merkle_commitment": "sha256:99aabb...",

  "witness_ids": ["did:witness:node01", "did:witness:node02"],
  "witness_sigs": [
    {
      "witness_id":        "did:witness:node01",
      "merkle_commitment": "sha256:99aabb...",
      "timestamp":         1725740000000,
      "signature":         "base64url:..."
    }
  ],

  "timestamp": 1725740000000,
  "signature": "base64url:..."
}
```

### Proof-of-Observation Receipt

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct ObservationReceipt {
    pub kind:           String,         // "proof_of_observation"
    pub receipt_id:     Uuid,
    pub sim_receipt_id: Uuid,           // which sim this observes
    pub witness_id:     WitnessDid,

    // What the witness actually saw
    pub observed:       Value,          // { actual_energy, distance_m, duration_s, ... }

    // What the sim predicted
    pub predicted:      Value,          // copied from SimPolicy

    // Deviation
    pub delta:          ObservationDelta,
    pub outcome:        ObservationOutcome,

    // Hardware attestation (software sigs NOT accepted here)
    pub tpm_key_id:     String,
    pub hardware_sig:   String,         // signed by TPM — not software key
    pub device_cert:    String,         // device cert for TPM key verification

    pub timestamp:      Timestamp,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ObservationDelta {
    pub fields:   BTreeMap<String, DeltaField>,
    pub max_delta_pct: f32,             // worst-case deviation across all fields
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DeltaField {
    pub predicted: f32,
    pub observed:  f32,
    pub delta_pct: f32,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ObservationOutcome {
    Validated,       // within acceptable delta (< 10% default)
    Partial,         // some fields out of range
    Falsified,       // major deviation — simulation was wrong
    Inconclusive,    // insufficient sensor data to compare
}
```

```json
// Proof-of-Observation Receipt — wire example
{
  "kind":           "proof_of_observation",
  "receipt_id":     "rcpt:obs:ddeeff002",
  "sim_receipt_id": "rcpt:sim:aabbcc001",
  "witness_id":     "did:witness:node01",

  "observed":  { "energy": 63, "distance_m": 14.2, "duration_s": 22 },
  "predicted": { "energy": 61, "risk": 0.04, "duration_s": 21 },

  "delta": {
    "fields": {
      "energy":     { "predicted": 61.0, "observed": 63.0, "delta_pct": 3.3 },
      "distance_m": { "predicted": 13.8, "observed": 14.2, "delta_pct": 2.9 },
      "duration_s": { "predicted": 21.0, "observed": 22.0, "delta_pct": 4.8 }
    },
    "max_delta_pct": 4.8
  },

  "outcome": "validated",

  "tpm_key_id":  "tpm:node01:key01",
  "hardware_sig": "base64url:<TPM-signed observation hash>",
  "device_cert":  "base64url:<X.509 cert for TPM key>",

  "timestamp": 1725741000000
}
```

### Twin License Grant

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct TwinLicenseGrant {
    pub grant_id:       Uuid,
    pub twin_id:        Hash,
    pub grantor_did:    Did,
    pub grantee_did:    Did,
    pub rights:         Vec<TwinUsageRight>,
    pub constraints:    TwinLicenseConstraints,
    pub issued_at:      Timestamp,
    pub expires_at:     Option<Timestamp>,
    pub fee_lamports:   Option<u64>,    // Sui MIST (1 SUI = 1e9 MIST)
    pub sui_tx:         Option<String>,
    pub merkle_root:    Hash,
    pub grantor_sig:    Signature,
    pub grantee_sig:    Option<Signature>, // grantee counter-signs on accept
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TwinLicenseConstraints {
    pub max_sim_runs:       Option<u32>,
    pub sim_agent_id:       Option<AgentDid>,   // only this agent may simulate
    pub no_commercial:      bool,
    pub attribution_req:    bool,
    pub sublicensing:       bool,
}
```

---

## CANONICAL RECEIPT (all three protocols feed into this)

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct CanonicalReceipt {
    pub receipt_id:          Uuid,
    pub kind:                ReceiptKind,

    // Identity chain — always present
    pub identity:            IdentityChain,

    // What happened
    pub action:              ActionRecord,

    // Evidence
    pub evidence_ids:        Vec<Uuid>,
    pub witness_attestations: Vec<WitnessAttestation>,
    pub throne_evaluations:  Vec<Value>,   // Twelve Thrones verdicts

    // Consensus + physical
    pub consensus_receipt:   Option<Value>,
    pub physical_attestation: Option<Value>,

    // Chain
    pub timestamp:           Timestamp,
    pub previous_hash:       Hash,         // chains receipts
    pub merkle_root:         Hash,
    pub signature:           Signature,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ReceiptKind {
    DipRoute,           // DIP message routing
    VcpSession,         // VCP device session
    Capture,            // TSP capture (31020)
    Scene,              // TSP scene assembly (31030)
    Simulation,         // TSP proof-of-simulation
    Observation,        // TSP proof-of-observation
    LicenseGrant,       // TSP license grant
    Validation,         // TSP peer validation
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ActionRecord {
    pub kind:   String,
    pub target: String,
    pub params: Value,
}
```

---

## VALIDATION RULES (enforced at parse time)

```
DIP
  ✓ message_id is unique (deduplicate on receipt)
  ✓ ttl not expired (reject if timestamp + ttl < now)
  ✓ signature verifies against origin.did
  ✓ identity.principal_id is present and non-empty
  ✗ REJECT if identity chain is incomplete

VCP
  ✓ grant_id references an active non-expired grant
  ✓ capability is in the grant's capabilities[]
  ✓ limits are not exceeded by command params
  ✓ agent_id in command matches agent_id in grant
  ✗ REJECT commands with expired grants (force re-negotiate)
  ✗ REJECT firmware.update / safety.disable always

TSP (Capture Receipt 31020)
  ✓ f1_score >= 0.777  (HARD GATE — reject below this)
  ✓ raw_hashes keys match declared modalities
  ✓ merkle_root is correct over all fields (recompute + compare)
  ✓ capture_epoch[0] < capture_epoch[1]
  ✗ REJECT if privacy_flags contains sensitive data without consent proof

TSP (Scene Receipt 31030)
  ✓ all capture_receipt_ids resolve to valid 31020s
  ✓ f1_score >= 0.777
  ✓ splat_hash is present (required)
  ✓ merkle_root binds twin_id + version + all hashes

TSP (Simulation Receipt)
  ✓ all_policies_hash = sha256(json_canonical(all_policies[]))
  ✓ selected_policy_id exists in all_policies[]
  ✓ at least 2 witness_sigs present
  ✓ each witness_sig.merkle_commitment matches receipt.merkle_commitment
  ✗ REJECT if policies array has < 2 candidates (selection is trivial)

TSP (Observation Receipt)
  ✓ hardware_sig verified against tpm_key_id + device_cert
  ✗ REJECT software-only signatures (tpm_key_id required)
  ✓ sim_receipt_id resolves to a valid simulation receipt
  ✓ max_delta_pct matches computed max across delta.fields
```
