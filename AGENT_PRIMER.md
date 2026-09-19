# AGENT PRIMER — Sovereign Ecosystem Pre-Coding Reference
## MANDATORY: Read this entire document before writing any code

Last updated: 2026-09-19
Source repos audited: 94 (see ~/sovereign-eco-blueprint/MASTER_TODO.md)

---

### 0. The Single Most Important Rule

**Every concept you are about to implement has probably already been built. Search before you code.**

```bash
# Run this FIRST for any type, function, or concept you plan to create:
grep -r "TypeName" ~/*/crates/ ~/*/src/ ~/*/backend/ 2>/dev/null | grep -v /target/
```

If you find it, use it. If it lives in the wrong place, move it — do not create a parallel implementation. Duplication is the primary cause of integration failures in this codebase.

---

### 1. Ecosystem at a Glance

The sovereign ecosystem has **three pillars** connected by **protocol crates**:

```
┌─────────────────────────────────────────────────────────────────────┐
│  PILLAR 1: Omo-Koda2 (Rust)     — Sovereign Agent OS kernel        │
│  PILLAR 2: OSOVM (Julia)        — Sacred VM, 160 opcodes, Àṣẹ econ │
│  PILLAR 3: Vantage (Python)     — Civilization interface, ~700 APIs │
├─────────────────────────────────────────────────────────────────────┤
│  CONNECTIVE TISSUE (sovereign-stack Rust workspace):                │
│    DIP  · VCP  · UCX  · ARP  · ScarabSwarm  · Witness              │
│    twin-protocol  ·  sovereign-pipeline  ·  sovereign-runtime       │
├─────────────────────────────────────────────────────────────────────┤
│  MEMORY SUBSTRATE:                                                   │
│    GIX (~/GIX) → gix-types (canonical) → gix-core (index)          │
│    larql-glyph (legacy GlyphGraph, migrating to gix-core)           │
│    minipae (Nostr kind:30174 memory bus)                            │
│    Triune-Memory (episodic/semantic/procedural orchestrator)        │
├─────────────────────────────────────────────────────────────────────┤
│  IDENTITY SPINE: BIPON39 → one mnemonic → all world keys            │
│  MESSAGE BUS:    Nostr (universal across ALL layers)                │
│  BLOCKCHAIN:     Sui (agent dNFTs, IP, AIO), Solana (bonds/waggle)  │
└─────────────────────────────────────────────────────────────────────┘
```

**Ports:** Omo-Koda2 :7777 · Vantage :8001 · DIP :7792 · ScarabSwarm :7793 · Witness :7794

---

### 2. Full Repo Catalog

#### CORE PILLARS

| Repo | Lang | Port/Role | Status | Key Types Exported |
|------|------|-----------|--------|--------------------|
| Omo-Koda2 | Rust | :7777 OS kernel | active | AgentHeartbeat, CapabilityAction, GixBridge, Universal7State |
| OSOVM | Julia | VM/economy | active | ComputeProof, ToC mint, SimReceipt, 160 opcodes |
| Vantage | Python | :8001 REST/MCP | active | ~700 endpoints; glyph_index.py (canonical Python GIX reference) |
| sovereign-stack | Rust | 14-crate workspace | active | DIP/VCP/UCX/ARP/Swarm/Witness types + pipelines |
| Vantage-Voice- | TypeScript | S2S voice | active | Gemini Live + Groq cascade |

#### PROTOCOL CRATES (sovereign-stack + standalone)

| Crate / Repo | Lang | Role | Key Types |
|--------------|------|------|-----------|
| ARP / arp-types | Rust | Receipt envelope | ActionReceipt, ReceiptKind, Principal, ArpBridge |
| VCP / vcp-types | Rust | Device capture | DeviceManifest, CapabilityGrant, VcpReceipt, HandshakeEngine |
| DIP / dip-types | Rust | P2P routing | DipEnvelope, DipRouter, DipNetwork, DipIdentityDocument |
| UCX / ucx-protocol | Rust | Compute exchange | ComputeReceipt, JobRequest, ProviderScore |
| ScarabSwarm / swarm-types | Rust | Proof-of-sim | SimReceipt, ProofOfSimulation, PolicySelection |
| Witness / witness-types | Rust | Hardware attest | WitnessAttestation, ObservationBundle, FirmwareManifest |
| twin-protocol | Rust | Spatial twin | CaptureReceipt (kind:31020), SceneReceipt (kind:31030), TwinTimeline |
| sovereign-runtime | Rust | WASM execution | CapabilityAction, ActionReceipt chains |
| sovereign-pipeline | Rust | Splat pipeline | CapturePipeline, Go2CaptureDriver |
| sovereign-node | Rust | Reference only | Integration tests ONLY — do not extend |

#### GIX MEMORY LAYER

| Repo | Lang | Role | Key Types |
|------|------|------|-----------|
| GIX / gix-types | Rust | **Canonical GIX primitives** | GlyphNode, GlyphEdge, GixKind, GixNamespace, Gix1, Gix1Entry, RoutingHints, IntegrityMeta, GixDomain |
| GIX / gix-core | Rust | GIX runtime + index | Gix1Index, GlyphGraph, gix1_audit, gix1_merkle_root |
| larql / larql-glyph | Rust | Legacy GlyphGraph + LQL | GlyphGraph (legacy), DESCRIBE/SELECT/WALK/INFER verbs — migrating to gix-core |
| Omo-Koda2 / gix_bridge.rs | Rust | Bridge to kernel memory | memory_merkle_root, audit_memory_root, build_gix1_index |

#### IDENTITY + MEMORY

| Repo | Lang | Role | Key Types |
|------|------|------|-----------|
| BIPON39 | Rust | Mnemonic / key root | entropy_to_mnemonic, mnemonic_to_seed, master_from_seed, odu_primary_index |
| If-Script | Rust/WASM | Divination VM | 256 Odù corpus, CowrieOracle, AseVault, Hermetic gates |
| minipae | Python | Nostr memory bus | kind:30174 NIP-AE, BIP-340, NIP-44 v2 |
| Triune-Memory | TypeScript | Memory orchestrator | TriuneMemory, MinipaeBridge, phase orchestrator |
| iranti | Rust | Buzz memory mesh | BM25 recall, A2A memory grants, dream-cycle digests |
| ip-layer | Rust | IP provenance | kind:31900/1901/1902/1903 Nostr schemas |

#### COORDINATION + OBSERVABILITY

| Repo | Lang | Role | Key Types |
|------|------|------|-----------|
| mycelium | Python+Go | Trace substrate | SQLite log, domain miners, MCP stdio, skill self-improvement |
| mycelium-tools | Python | Fleet pip tools | substrate, collector, cycle, tunnel, picks-client |
| agentic-waggle | Go | Swarm coordination | decaying scent signals, claim/release leases |
| organism-core | TypeScript | Nervous-system bridge | TS bridges for IfáScript/Swibe/OSOVM/AIO/Zangbeto |

#### ECONOMY + GOVERNANCE

| Repo | Lang | Role | Key Types |
|------|------|------|-----------|
| AIO | Move (Sui) | Àṣẹ I/O | elder-gated mode flips, oracle bonds, Àṣẹ mint/burn |
| bondhive | Rust | Reliability bonds | NIP-74 Service Bond, BondScore |
| waggle | Rust | Labor exchange | Nostr bounty events 31900–31903, Anchor escrow |
| Portent | Python | Prediction market | 1B PORT token, oracle agents |
| Zangbeto | Rust+Node+Move | Security audit | smart contract red-team, Arweave receipts, BTC OTS proofs |
| Blocksim | Python | Proof-of-Sim chain | stake, attest firmware, signed sim logs |

#### LANGUAGE + VM STACK

| Repo | Lang | Role |
|------|------|------|
| If-Script | Rust | Entropy + divination VM |
| Swibe | JavaScript | Agent scripting v3.4, 44 compile backends |
| zerolang | C | Graph-native agent language |
| larql | Rust | Transformer weight decompiler + LQL graph DB |
| Techgnosis | Julia | OSO VM Dispatcher, 6-language FFI |
| Nex- | TypeScript | 7 Hermetic/Orisha graph runtime primitives |
| Koodu | Julia | 7-day Orisha resonance, BTC-anchored time |

#### HARDWARE + SIMULATION

| Repo | Lang | Role |
|------|------|------|
| omokoda-mesh | C++ | ESP32 LoRa firmware, Nostr-native, BIP-340 Schnorr |
| omokoda-mesh-firmware | C++ | Meshtastic fork for gateway nodes |
| omokoda-mesh-os | Shell | Arch Linux for Raspberry Pi LoRa gateways |
| Witness-firmware | Python | ESP32+SX1278 DePIN, physics-proof attestation |
| Scarabswarm | Julia | 6-DOF drone racing sim, SHA-256 trajectory proofs |

#### SOCIAL + COMMUNICATION

| Repo | Lang | Role |
|------|------|------|
| Buzz | Rust | Self-hostable Nostr relay workspace, hash-chained audit log |
| Buzz-swarm | TypeScript | Buzz swarm UI, Vite frontend |
| Synapse | TypeScript | NIP-30 agent skill/memory/negotiation, 7 event kinds |
| Vantage-Voice- | TypeScript | Real-time S2S voice, Gemini Live + ElevenLabs |

#### TRADING + INTELLIGENCE

| Repo | Lang | Role |
|------|------|------|
| strategy-lab | Python | Signal engine, whale radar, convergence hub |
| Loom | Python | Multi-agent trading debate, pure NumPy |
| TradingOS | Python | Agent-native trading platform spec |
| ares-control | Python | Control panel for ~70 VPS systemd daemons |
| kanban | Elixir | Phoenix OTP trading pipeline |
| Axiom | TypeScript | 3D galaxy graph, every node = live agent |

---

### 3. Anti-Duplication Matrix

This is the most important section. Before implementing ANY concept, check the "Where It Lives" column. The "Never Re-Implement" column is a hard rule.

| Concept | Where It Lives | Never Re-Implement |
|---------|---------------|-------------------|
| **GIX fold primitives** | `~/GIX/crates/gix-types/src/lib.rs` | `content_hash`, `glyph_fold`, `odu_link` anywhere else |
| **GIX1 Merkle root** | `gix_types::gix1_merkle_root` | Custom SHA-256 tree over canonical_ids |
| **GIX1 audit** | `gix_types::gix1_audit` | Manual root re-verification logic |
| **GlyphNode** | `gix-types` (canonical); `larql-glyph` re-exports it | New struct with same fields in any other crate |
| **GlyphEdge** | `gix-types` has `GlyphEdge { from, to, relation, weight: i32 }` | `larql-glyph` has a DIFFERENT `GlyphEdge` with NO weight field — this is a known divergence; use `gix-types::GlyphEdge` for new code |
| **GlyphGraph** | `gix-core` (preferred for new code); `larql-glyph` (legacy, being migrated) | New graph implementation in any repo |
| **Gix1Index** | `gix-core::Gix1Index` | New in-memory GIX1 registry |
| **GixKind** | `gix-types::GixKind` (`Memory/Receipt/Simulation/Physical/Governance/Custom`) | New kind enum in any downstream crate |
| **GixNamespace** | `gix-types::GixNamespace` (`OmokodaAgent/VantageRegistry/OsovmExecution/ArpReceipt/MeshDevice/Mycelium/IfScript/Custom`) | New namespace enum anywhere |
| **Gix1 wire envelope** | `gix-types::Gix1` (version, kind, namespace, canonical_id, glyph, odu_base, odu_composed, provenance, created_at, routing, integrity) | Custom GIX1 struct with same fields |
| **GixDomain (KDF)** | `gix-types::GixDomain` (`Memory/Mesh/Receipt/AgentKey/Encryption/Duress`) | Domain-separated key derivation outside gix-types |
| **GIX-KDF-v1** | `gix_types::gix_kdf_v1` (HKDF-SHA256, salt `"GLYPHINDEX/v1"`) | Custom HKDF or domain-separated key derivation |
| **gix_fold_v1** | `gix_types::gix_fold_v1` (composite identity from multiple canonical_ids) | Manual SHA-256 chaining of canonical_ids |
| **ActionReceipt** | `~/ARP/crates/arp-types/src/receipt.rs` | Any custom receipt struct; use ReceiptKind variants instead |
| **ArpBridge** | `~/ARP/crates/arp-types/src/bridge.rs` | Manually wrapping receipts as Gix1Entry |
| **DeviceManifest** | `~/VCP/crates/vcp-types/` | New device capability description struct |
| **CapabilityGrant** | `~/VCP/crates/vcp-types/` | New scoped/expiring capability struct |
| **VcpReceipt / VcpSessionReceipt** | `~/VCP/crates/vcp-types/` | New VCP session result struct |
| **HandshakeEngine** | `~/VCP/crates/vcp-broker/src/handshake_engine.rs` | New 7-step VCP handshake state machine |
| **DipEnvelope** | `~/DIP/crates/dip-types/` | New signed TTL-gated message container |
| **DipRouter** | `~/DIP/crates/dip-types/` | New Nostr/Meshtastic/A2A/MCP routing logic |
| **ComputeReceipt** | `~/UCX/crates/ucx-protocol/` | New GPU compute receipt struct |
| **WitnessAttestation** | `~/Witness/crates/witness-types/` | New hardware-signed attestation struct |
| **ObservationBundle** | `~/Witness/crates/witness-types/` | New grouped observation struct |
| **SimReceipt** | `~/ScarabSwarm/crates/swarm-types/` | New simulation result receipt |
| **ProofOfSimulation** | `~/ScarabSwarm/crates/swarm-types/` | New PoS proof struct |
| **CaptureReceipt (kind:31020)** | `~/sovereign-stack` twin-protocol crate | New Nostr spatial capture event schema |
| **SceneReceipt (kind:31030)** | `~/sovereign-stack` twin-protocol crate | New Nostr scene receipt schema |
| **OduCoordinate** | `~/sovereign-stack` sovereign-types crate | New GPS↔tile coordinate struct |
| **IdentityChain** | `~/sovereign-stack` sovereign-types | New identity chain struct |
| **TrustTier (T0-T5)** | `~/sovereign-stack` sovereign-types | New tier enum |
| **MerkleRoot** | `sovereign-types` (sha256 sorted leaves) AND `gix_types::gix1_merkle_root` | New Merkle tree implementation |
| **GIX Python reference** | `~/Vantage/backend/glyph_index.py` | New Python GIX implementation (cross-language conformance vectors must match) |
| **Receipt gix1_canonical_id field** | `ActionReceipt.gix1_canonical_id: Option<String>` with `#[serde(default)]` | Manually adding GIX identity to receipts |
| **OSOVM opcodes** | `~/OSOVM` Julia — exactly 160 opcodes | Any new opcode not going through OSOVM PR process |
| **Agent birth ceremony** | `Vantage/backend/birth_credentials.py` | Duplicate birth logic in any other module |
| **Nostr event kinds** | kind:30174 minipae · kind:31900-31903 waggle/ip-layer · kind:31000-31030 sovereign-stack | New overlapping event kinds without schema review |
| **WASM bridge** | Omo-Koda2 exactly 6 functions | Adding a 7th WASM bridge function (security regression) |
| **18 OpenClaw tools** | Omo-Koda2 Tier 5 exactly 18 | Adding tools without tier gate review |

---

### 4. GIX Protocol Reference

**Source of truth:** `~/GIX/crates/gix-types/src/lib.rs`

All types below are exported from `gix_types`. Never re-implement in downstream crates.

#### Public Functions

| Function | Signature | Purpose |
|----------|-----------|---------|
| `content_hash` | `(text: &str) -> [u8; 32]` | SHA-256 of UTF-8 text |
| `glyph_fold` | `(digest: &[u8; 32]) -> char` | Deterministic Unicode glyph from digest |
| `odu_link` | `(digest: &[u8; 32]) -> (u8, u16)` | `(odu_base, odu_composed)` from digest bytes |
| `gix1_merkle_root` | `(canonical_ids: &[&str]) -> String` | Sort-then-hash Merkle root |
| `merkle_root` | alias for `gix1_merkle_root` | Migration alias |
| `gix1_audit` | `(stored_root: &str, canonical_ids: &[&str]) -> Result<String, String>` | Verify stored root |
| `gix_fold_v1` | `(inputs: &[[u8; 32]]) -> [u8; 32]` | Order-dependent composite identity |
| `gix_kdf_v1` | `(canonical_id: &[u8; 32], domain: GixDomain, owner: &[u8], context: &[u8]) -> [u8; 32]` | HKDF-SHA256 domain-separated key derivation |

**Constant:** `GIX1_EMPTY_ROOT = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"`

#### Public Structs

| Type | Key Fields |
|------|-----------|
| `GlyphNode` | `canonical_id: String`, `glyph: char`, `odu_base: u8`, `odu_composed: u16`, `ts: f64`, `tags: BTreeSet<String>`, `walrus_blob_id: Option<String>` |
| `GlyphEdge` | `from: String`, `to: String`, `relation: String`, `weight: i32` |
| `Gix1Entry` | `canonical_id: String`, `glyph: char`, `kind: GixKind`, `odu_base: u8`, `ts: f64`, `payload_hash: String` |
| `Gix1` | `version: u8`, `kind: GixKind`, `namespace: GixNamespace`, `canonical_id: [u8; 32]`, `glyph: char`, `odu_base: u8`, `odu_composed: u16`, `provenance: Option<[u8; 32]>`, `created_at: u64`, `routing: RoutingHints`, `integrity: IntegrityMeta` |
| `RoutingHints` | `primary: Option<String>`, `fallback: Vec<String>` |
| `IntegrityMeta` | `envelope_hash: [u8; 32]` |

#### Public Enums

| Type | Variants |
|------|---------|
| `GixKind` | `Memory`, `Receipt`, `Simulation`, `Physical`, `Governance`, `Custom(String)` |
| `GixNamespace` | `OmokodaAgent`, `VantageRegistry`, `OsovmExecution`, `ArpReceipt`, `MeshDevice`, `Mycelium`, `IfScript`, `Custom(String)` |
| `GixDomain` | `Memory`, `Mesh`, `Receipt`, `AgentKey`, `Encryption`, `Duress` |

#### GIX-FOLD-v1 Conformance Vectors

These MUST match across all language implementations (Rust gix-types, Python glyph_index.py, Julia OSOVM, If-Script):

| Input | Glyph Codepoint | odu_base | odu_composed |
|-------|----------------|----------|-------------|
| `"Àṣẹ"` | 21841 | 227 | 58152 |
| `"hello"` | 23636 | 44 | 11506 |
| `"GlyphIndex"` | 13726 | 68 | 17595 |
| `"😊🚀 Unicode test"` | 64591 | 189 | 48626 |
| `"Ọ̀rúnmìlà"` | 17963 | 204 | 52390 |

#### GlyphEdge Divergence Warning

`gix-types::GlyphEdge` has a `weight: i32` field.
`larql-glyph::GlyphEdge` does NOT have a weight field (legacy definition).
For all new code use `gix_types::GlyphEdge`. The larql-glyph version is being migrated.

#### gix-core Public API (`~/GIX/crates/gix-core/src/index.rs`)

```
Gix1Index::new() -> Self
Gix1Index::insert(&mut self, entry: Gix1Entry)
Gix1Index::insert_gix1(&mut self, env: Gix1)        ← preferred for Phase 3 stamping
Gix1Index::add_receipt(&mut self, receipt_id, kind, ts) -> &Gix1Entry
Gix1Index::resolve(&self, canonical_id: &str) -> Option<&Gix1>
Gix1Index::root(&self) -> &str
```

---

### 5. Memory Stack

The sovereign memory system has four layers with strict ownership boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: Triune-Memory (TypeScript)                        │
│  Owns: episodic / semantic / procedural tier orchestration  │
│  Delegates to: minipae bridge                               │
├─────────────────────────────────────────────────────────────┤
│  LAYER 2: minipae (Python, Nostr kind:30174)                │
│  Owns: actual write/read to Nostr relays                     │
│  Slug grammar: "core" or "mem/[path]"                       │
│  D-tag: HMAC-SHA256(conversation_key, slug) — deterministic │
├─────────────────────────────────────────────────────────────┤
│  LAYER 3: GIX (Rust/Python)                                 │
│  Owns: content-addressed metadata projection                │
│  gix-types: canonical primitives (single source of truth)   │
│  gix-core: Gix1Index + Merkle audit                         │
│  larql-glyph: legacy GlyphGraph (migrate to gix-core)       │
│  glyph_index.py: canonical Python reference                  │
├─────────────────────────────────────────────────────────────┤
│  LAYER 4: REM / consolidation                               │
│  Owns: dream-cycle digests, BM25 recall, A2A memory grants  │
│  Lives in: iranti (Rust, for Buzz) + Omo-Koda2 glyph_memory │
└─────────────────────────────────────────────────────────────┘
```

**Critical invariant:** Plaintext is NEVER stored in GIX objects. `canonical_id` (SHA-256 of plaintext) is the address. The plaintext stays sealed in GIX1 blobs (Walrus / Vantage / OSOVM). GIX holds only content-addressed metadata.

---

### 6. Dependency Rules

These rules prevent circular imports and runaway coupling:

```
ALLOWED dependency directions (→ means "may depend on"):

gix-types          → (no dependencies on ecosystem crates)
gix-core           → gix-types
larql-glyph        → gix-types  (re-exports content_hash, glyph_fold, odu_link, GlyphNode)
arp-types          → gix-types
vcp-types          → (minimal dependencies)
vcp-broker         → vcp-types, gix-core
dip-types          → (transport primitives only)
ucx-protocol       → (compute primitives only)
witness-types      → (attestation primitives only)
swarm-types        → (simulation primitives only)
sovereign-runtime  → arp-types, gix-types
Omo-Koda2          → all sovereign-stack crates, gix-core, larql-glyph
Vantage (Python)   → glyph_index.py (internal), minipae
organism-core (TS) → bridges only — no protocol logic lives here
sovereign-node     → protocol integration tests ONLY — no app logic

FORBIDDEN:
gix-types          → any application crate
arp-types          → Omo-Koda2, Vantage (only downstream can depend on protocol crates)
sovereign-node     → governance, wallet, emission, perception, swarm (these belong in Vantage/OSOVM)
```

**The sovereign-stack rule:** sovereign-stack = 6 protocol crates ONLY (DIP, VCP, UCX, ARP, ScarabSwarm, Witness). Do not add application logic. See ~/sovereign-stack/REPO_PLAYBOOK.md.

---

### 7. Coding Patterns

These patterns are extracted from production code. Always follow them.

#### Pattern 1 — Stamping a receipt into GIX (ArpBridge pattern)

```rust
// From ~/ARP/crates/arp-types/src/bridge.rs
use gix_types::{Gix1Entry, GixKind, gix1_merkle_root};
use crate::receipt::ActionReceipt;

let mut bridge = ArpBridge::new();
let entry = bridge.ingest(&receipt);         // GixKind::Receipt
// or for other kinds:
let entry = bridge.ingest_as(&receipt, GixKind::Simulation);

let root = bridge.merkle_root();             // current Merkle root
bridge.audit(&stored_root)?;                 // verify against stored root
```

#### Pattern 2 — Constructing a Gix1 wire envelope

```rust
// From ~/GIX/crates/gix-types/src/lib.rs
use gix_types::{Gix1, GixKind, GixNamespace, RoutingHints};

let env = Gix1::new(
    GixKind::Receipt,
    GixNamespace::ArpReceipt,
    canonical_bytes,           // &[u8] — the serialised object
    None,                      // provenance: Option<[u8; 32]>
    created_at_ms,             // u64 Unix milliseconds
    RoutingHints::default(),
);
assert!(env.verify_integrity());  // always verify after construction
```

#### Pattern 3 — Optional GIX fields use #[serde(default)]

```rust
// From ~/ARP/crates/arp-types/src/receipt.rs
/// GIX1 canonical_id stamped on ingest.
#[serde(default)]
pub gix1_canonical_id: Option<String>,
```

Every `Option<>` field added to a receipt or protocol type MUST carry `#[serde(default)]` for backward compatibility. Existing records without the field deserialize to `None` instead of erroring.

#### Pattern 4 — Memory Merkle root (gix_bridge.rs pattern)

```rust
// From ~/Omo-Koda2/omokoda-core/src/memory/gix_bridge.rs
use gix_types::gix1_merkle_root;

pub fn memory_merkle_root(dir: &OduDirectory) -> String {
    let canonical_ids = dir_canonical_ids(dir);
    let id_refs: Vec<&str> = canonical_ids.iter().map(|s| s.as_str()).collect();
    gix1_merkle_root(&id_refs)   // NOT a custom SHA-256 tree
}
```

#### Pattern 5 — GlyphNode construction

```rust
// From ~/GIX/crates/gix-types/src/lib.rs — GlyphNode::from_chunk is the constructor
let node = GlyphNode::from_chunk("memory text chunk", unix_ts_f64);
// node.canonical_id = hex(SHA-256(chunk))
// node.glyph        = glyph_fold(&digest)
// node.odu_base     = digest[0]
// node.odu_composed = (digest[0] << 8) | digest[1]
```

#### Pattern 6 — GIX-KDF-v1 (never derive keys manually)

```rust
// From ~/GIX/crates/gix-types/src/lib.rs
use gix_types::{gix_kdf_v1, GixDomain};

let enc_key    = gix_kdf_v1(&canonical_id, GixDomain::Encryption, owner, context);
let duress_key = gix_kdf_v1(&canonical_id, GixDomain::Duress,     owner, context);
// enc_key != duress_key guaranteed by domain separation
// NEVER store kdf output as identity
```

#### Pattern 7 — Test module structure

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn descriptive_name_of_invariant() {
        // Single concept per test
    }
}

// For envelope/protocol tests, use a separate module:
#[cfg(test)]
mod envelope_tests {
    use super::*;
    // ...
}
```

#### Pattern 8 — VCP HandshakeEngine uses gix-core GlyphGraph

```rust
// From ~/VCP/crates/vcp-broker/src/handshake_engine.rs
pub struct HandshakeEngine {
    pub registry: DeviceRegistry,
    pub sessions: SessionStore,
    pub graph:    RwLock<gix_core::GlyphGraph>,  // NOT a new graph impl
}
```

---

### 8. Pre-Coding Checklist

Run these 7 steps before writing a single line:

```
Before writing ANY code:
□ 1. Search: grep -r "TypeName" ~/*/crates/ ~/*/src/ ~/*/backend/ 2>/dev/null | grep -v /target/
     (Ripgrep version if available: rg "TypeName" ~/*/crates/ ~/*/src/ ~/*/backend/)

□ 2. Check gix-types: is this concept in ~/GIX/crates/gix-types/src/lib.rs?
     Specifically: GlyphNode, GlyphEdge, GixKind, GixNamespace, Gix1, Gix1Entry,
     glyph_fold, content_hash, odu_link, gix1_merkle_root, gix_kdf_v1

□ 3. Check protocol crates for the concept:
     ~/ARP/crates/arp-types/         (ActionReceipt, Principal, ReceiptKind)
     ~/VCP/crates/vcp-types/         (DeviceManifest, CapabilityGrant, VcpReceipt)
     ~/UCX/crates/ucx-protocol/      (ComputeReceipt, JobRequest)
     ~/DIP/crates/dip-types/         (DipEnvelope, DipRouter, DipNetwork)
     ~/Witness/crates/witness-types/ (WitnessAttestation, ObservationBundle)
     ~/ScarabSwarm/crates/swarm-types/ (SimReceipt, ProofOfSimulation)

□ 4. Read the target file FIRST — never edit without reading:
     Use Read tool with exact absolute path before any Edit tool call

□ 5. Run existing tests before making changes:
     cargo test -p <crate-name>
     (This is the baseline. Your changes must not break it.)

□ 6. Check if the ChatGPT/external suggestion contradicts existing code:
     External AI describes goals, not implementations. See Section 10.

□ 7. Confirm: am I only modifying repos explicitly listed in this task?
     sovereign-stack scope = 6 protocol crates only.
     sovereign-node = integration tests only, no new app logic.
```

---

### 9. Commit Standards

Every commit to this ecosystem MUST follow this format:

```
<crate-or-module>: Phase N — short description of what changed

Optional body paragraph explaining the "why" — what capability this enables
or what invariant it protects.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

Examples:
- `gix-types: Phase 3 — add GixDomain enum for KDF domain separation`
- `arp-types: Phase 2 — add gix1_canonical_id field with serde(default)`
- `vcp-broker: Phase 4 — wire HandshakeEngine graph to gix-core`

**After committing:**
- Update `~/sovereign-eco-blueprint/MASTER_TODO.md` marking the item complete
- Run `cargo build --workspace` in the affected workspace to confirm zero new warnings

---

### 10. What ChatGPT / Other AI Suggestions Require

**Hard rule:** External AI suggestions (ChatGPT, Claude without full codebase context, Codex, Gemini) describe GOALS, not IMPLEMENTATIONS.

When an external AI suggests "add a GlyphHash type" or "implement a Merkle proof for receipts":

1. **Do not implement immediately.** It may already exist under a different name.
2. **Search first.** Run the Step 1 grep from Section 8.
3. **Check the Anti-Duplication Matrix** (Section 3) for the concept.
4. **Check the DEEP REPO CATALOG** in memory: `project_ecosystem_repos_deep.md`.
5. **Check the GAP ANALYSIS** in memory: `project_gap_analysis.md`.
6. Only after confirming the concept does not exist should you implement it.
7. If it exists under a different name, use the existing type and note the name mapping.

**Common traps:**
- "Add SHA-256 hashing to receipts" → `gix_types::content_hash` already does this
- "Create a Merkle root for the index" → `gix_types::gix1_merkle_root` already does this
- "Make receipts content-addressable" → `ActionReceipt.gix1_canonical_id` + `ArpBridge` already does this
- "Add an edge weight to the graph" → `gix-types::GlyphEdge.weight: i32` exists; `larql-glyph::GlyphEdge` does NOT have it — this is a known divergence, not a missing feature
- "Implement key derivation for agents" → `gix_types::gix_kdf_v1` already does this with `GixDomain` separation

**The invariant:** If three separate agents independently "implement" the same concept, we have three incompatible versions. This ecosystem has 94 repos. The type you need is almost certainly already there.
