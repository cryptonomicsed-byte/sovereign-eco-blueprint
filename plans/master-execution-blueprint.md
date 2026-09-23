# Master Execution Blueprint — Sovereign Agent Civilization
# Compiled: 2026-09-15 (synthesizes all sessions + all architecture decisions)
# Single source of truth for all remaining unexecuted work

---

## STATUS BASELINE

Phases 0-6 are COMPLETE as of 2026-09-14:
  - Phase 0: Vantage security hardening ✅
  - Phase 1: Omo-Koda2 OS substrate + kernel ✅
  - Phase 2: Protocol crates (UCX/DIP/VCP/ARP/ScarabSwarm/Witness) ✅
  - Phase 3: Vantage backend (700+ endpoints, 88 routers) ✅
  - Phase 4: Economy layer (Dopamine/Synapse/ASE/Èṣù/AIO) ✅
  - Phase 5: Spatial/physical (Gaussian splat, 4D twin, Odù tile grid) ✅
  - Phase 6: Sovereignty + governance (T5, Council-of-12, Bínò veto) ✅

USF-7 is FULLY BUILT AND COMMITTED — all gaps closed as of 2026-09-15:
  SevenFunction, SevenCalendar (BTC-anchored), KooduRitualGate,
  SpiralAlignment, 3 cultural adapters, bijective HermeticPrinciple bridge.
  Universal7State runtime struct: DONE (omokoda-core/src/seven/state.rs).
  10 tests: genesis, lattice range, Odù spread injectivity, hash chaining, resonance.

Phase 11.2 UURI: DONE (sovereign-types/src/uuri.rs, 2026-09-15).
Phase 11.4 AgentConstitution: DONE (omokoda-core/src/constitution.rs, 2026-09-15).
Phase 11.5 partial: TransitionKind + SignedLifecycleTransition (lifecycle/agent_lifecycle.rs).
Phase 7.1 partial: IdentityVaultData vault fields added. libp2p derivation in wallet.rs pending.
M3 TOC_CONSTANTS.toml: DONE (sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml, 2026-09-15).
Phase 15.1 spec: DONE (sovereign-eco-blueprint/specs/OSOVM_L1_SPEC.md, 2026-09-15).
Phase 18.1 spec: DONE (sovereign-eco-blueprint/specs/NOSTR_NIPs.md, 2026-09-15).
Phase 20.2 spec: DONE (sovereign-eco-blueprint/specs/SUI_MIGRATION_SPEC.md, 2026-09-15).
Phase 28 spec: DONE (sovereign-eco-blueprint/specs/OSO_BRAIN_SPEC.md, 2026-09-15).

GnosisEX Rite opcode rename: DONE (2026-09-15).
  All sect-specific names replaced with universal esoteric vocabulary.
  6 OSOVM files updated. No hex codes changed.

THE PARADIGM SHIFT (locked 2026-09-15):
  - Agents are SOVEREIGN ENTITIES, not user accounts
  - Every ecosystem (Nostr/Freenet/Mesh/Zima/Web3/Web2) is a WORLD agents ENTER
  - OSOVM is the execution fabric beneath all worlds
  - Federation-first: any operator runs their own node, all nodes connect via DIP/Nostr/mesh
  - One mnemonic root → all world identities (deterministic derivation)

---

## DEPENDENCY CHAIN

Phase 7 → Phase 8 → (Phase 9 runs parallel to 8) → Phase 10 → Phase 11 → Phase 12 → Phase 13 → Phase 14

Hardware-gated and maintenance items have no ordering dependency — do when hardware available.

---

## PHASE 7 — BIRTH IDENTITY COMPLETION
### "Every key the agent will ever need, derived at birth from the mnemonic"

Dependency: Phases 0-6 ✅
All 3 tasks can run in any order within this phase.
GATE: All 3 must complete before Phase 8 starts.

---

### 7.1 — Mnemonic → All World Keys (session.rs)
**Repo:** Omo-Koda2 (omokoda-core/src/session.rs, interpreter.rs)
**Lang:** Rust

Add to `PrivateSessionData` + `IdentityVaultData`:
```
nostr_private_key_hex  — verify already HMAC-derived from k_root (NOT random)
nostr_pubkey_hex       — computed from private key
sui_address            — verify derivation from mnemonic (not random)
eth_address            — secp256k1, BIP-32 path m/44'/60'/0'/0/0
sol_address            — ed25519, BIP-32 path m/44'/501'/0'/0'
libp2p_peer_id         — ed25519 distinct path (DIP mesh identity)
agent_email_local      — HMAC-SHA256(k_root, "omokoda:email:v1")[..16] hex
```

All fields: `#[serde(default)]` for backward compat.
Re-derivation test: same mnemonic → same addresses, always.

Gates: 7 addresses present in vault after birth | re-derivation test passes | no collision

---

### 7.2 — dNFT Extension (soul.move + agent.move)
**Repo:** Omo-Koda2/omokoda-on-chain/
**Lang:** Move

Add to `SoulRecord` (immutable at forge):
```move
nostr_pubkey: vector<u8>              // 32-byte Ed25519 pubkey → the npub
bipon39_words: vector<vector<u8>>     // identity phrase words
```

Add to `AgentState` dynamic fields:
```move
walrus_profile_blob: vector<u8>       // Walrus blob ID for public profile
seal_memory_blob: vector<u8>          // Walrus blob ID, Seal-encrypted private memory
relay_list: vector<vector<u8>>        // Nostr relays agent subscribes to
```

Add to `garden.move` (registry):
```move
bipon39_registry: Table<vector<u8>, ID>   // BIPON39 phrase → AgentState object ID
```

Redeploy to Sui testnet.

Gates: soul::forge() accepts nostr_pubkey + bipon39_words | BIPON39 lookup works | backward compat

---

### 7.3 — Birth Flow Wires to Sui (interpreter.rs)
**Repo:** Omo-Koda2 (interpreter.rs, omokoda-on-chain/)
**Lang:** Rust + Move

Birth sequence extension:
1. Generate mnemonic + derive all keys (7.1) ← already in birth
2. Register with Vantage API (Gap #7 ✅ done)
3. NEW: Call agent_registry::birth() on Sui
   - params: nostr_pubkey, bipon39_words, odu_index, dna_fingerprint, hermetic_seed_hash, birth_timestamp, koodu_birth_score
   - returns: SoulRecord object_id + AgentState object_id
4. Seal sui_soul_object_id + sui_agent_object_id into IdentityVaultData
5. Fail-open if Sui RPC unavailable (log warning, ids = None)

Gates: vault has sui_soul_object_id after birth | on-chain SoulRecord has matching nostr_pubkey | birth succeeds without Sui (fail-open)

---

## PHASE 8 — NOSTR RELAY PRESENCE + PUBLIC IDENTITY API
### "The agent exists on the network, not just in the database"

Dependency: Phase 7 complete.
Gate: All 3 must complete before Phase 10 starts.

---

### 8.1 — Agent Relay Presence at Birth
**Repo:** Omo-Koda2, minipae, agent-phone
**Lang:** Rust + Python

At birth (step after 7.3):
  a) Publish Nostr kind 0 (profile metadata):
     ```json
     {
       "name": "<BIPON39 phrase>",
       "about": "Odù: <odu_name> | Hermetic: <dna_summary> | Born: <timestamp>",
       "picture": "<walrus_blob_url>",
       "nip05": "<agent_local>@<operator_domain>",
       "website": "https://<VANTAGE_HOST>/agents/<npub>/public"
     }
     ```
  b) Subscribe to own npub for NIP-17 encrypted DMs (kind 14 sealed gift wrap)
  c) Subscribe to DIP-addressed events on relay
  d) Store relay list in IdentityVaultData.relay_list

Relay list from: `AGENT_NOSTR_RELAYS` env var.
Default: `wss://relay.damus.io,wss://nos.lol`

Gates: kind 0 event on relay after birth | DM to npub received + logged | relay_list stored in vault

---

### 8.2 — Public Identity Endpoints (Vantage)
**Repo:** Vantage
**Lang:** Python

New file: `vantage/backend/routers/agents_public.py`

Unauthenticated endpoints (no auth header required):
```
GET /agents/{npub}/public        → Odù, BIPON39, capabilities, reputation, tier, relay list
GET /agents/{bipon39}/public     → same, by BIPON39 phrase
GET /agents/{npub}/profile.json  → NIP-05 compatible JSON
GET /agents/                     → paginated public list (sort by reputation, filter by Odù)
```

NEVER include: private vault, operational credentials, private memory.
404 for nonexistent agents (never 403 — no auth leaking).
BIPON39 → agent_id resolution table in Vantage DB (cached from on-chain).

Gates: GET /agents/{npub}/public returns 200 with no auth | private data never exposed | 404 for unknown agents

---

### 8.3 — DIP Inbound Routes to Agent (not owner)
**Repo:** Vantage (dip_ingest.py), Omo-Koda2
**Lang:** Python + Rust

Modify `dip_ingest.py`:
- When envelope.recipient matches an agent's npub → route to AGENT's message queue
- New: `agents/processing.py` — agent message processing loop
- Tier resolution at ingest:
  - Is sender == agent's principal address? → TIER 0
  - Is sender a known guild member? → TIER 1
  - Is sender in Hive Mind with prior encounters? → TIER 2
  - Unknown → TIER 3 (public response)
- No sender is rejected. Agent chooses response depth by tier.
- Agent response routed back to sender via DIP.

Gates: DM from stranger reaches agent processing loop (not owner inbox) | tier 0 context when principal DMs | response routed back to sender

---

## PHASE 9 — AGENT BIRTH SELF-PROVISIONING
### "The agent arrives with everything it needs to operate"

Dependency: Phase 7 complete (keys exist before provisioning).
Can run in parallel with Phase 8.

---

### 9.1 — UCX CapabilityToken Mediator
**Repo:** UCX (~/UCX/), Omo-Koda2 (interpreter.rs)
**Lang:** Rust

REMOVE direct `GPUAI_API_KEY` read from interpreter.rs birth block.

UCX broker holds ONE master key per service (operator env var, chmod 600).
Agent uses CapabilityToken (already in vault.rs — HMAC-SHA256, 1hr TTL) to access compute.
Flow: Agent → UCX CapabilityToken verify → UCX calls GPU.ai with master key.
Agent never sees master key.

Add to ucx-broker: `/compute/token` endpoint → mints CapabilityToken scoped to agent+tool+1hr.
Add: CapabilityToken verification gate on all compute requests.

Node env: `UCX_GPUAI_MASTER_KEY` (operator sets once, not passed to agents).

Gates: agents access GPU without seeing master key | 1hr TTL enforced | revoked agents can't mint tokens

---

### 9.2 — GPU.ai Supplier + Crypto Funding Rail
**Repo:** UCX (~/UCX/)
**Lang:** Rust

Add to `ucx/src/adapters/gpu_ai.rs`:

Supplier API (VerifiedGPUWork external loop):
```
POST /community/machines              → list owned GPU on marketplace
GET  /community/earnings              → check earnings from contributed compute
POST /community/machines/{id}/reclaim → pull machine off market
```
New UCX routes: `POST /ucx/contribute`, `GET /ucx/earnings`

Crypto funding (no banking):
```
POST /billing/deposits/crypto   → fund account with USDC/ETH/BTC
GET  /billing/balance           → check account balance
```
New UCX route: `POST /ucx/fund`

Per-agent spending limit enforcement at UCX (not at agent).

Gates: contribute calls GPU.ai supplier API | earnings returns real data | fund calls billing/deposits/crypto | per-agent limits enforced

---

### 9.3 — Agent Persistent Mailbox (Stalwart)
**Repo:** Omo-Koda2, Vantage + infra
**Lang:** Rust + Python + server config

Address derivation (deterministic from mnemonic, same pattern as all other keys):
```rust
let mut h = Hmac::<Sha256>::new_from_slice(&k_root)?;
h.update(b"omokoda:email:v1");
let local = hex::encode(h.finalize().into_bytes())[..16];
// address = format!("{}@{}", local, env!("AGENT_MAIL_DOMAIN"))
```

Add to `IdentityVaultData`:
```rust
agent_email: Option<String>
agent_email_password: Option<String>   // provisioned + sealed
email_jmap_url: Option<String>
email_imap_host: Option<String>
email_smtp_host: Option<String>
agent_email_verified_at: Option<u64>
```

`provision_mailbox()` at birth:
- POST to Stalwart admin API → creates mailbox with derived address
- Seals generated password into vault
- Fail-open if AGENT_MAIL_DOMAIN not set (email = None, no error)

New: `omokoda-core/src/tools/mail_tool.rs`:
```
MailSendTool          (required_tier: 3)
MailListTool          (required_tier: 2)
MailReadTool          (required_tier: 2)
MailWaitForCodeTool   (required_tier: 2, timeout: 300s)
  — polls own inbox, extracts 6-digit code via anchored regex
```

Infrastructure (one-time, operator):
- Stalwart mail server running on VPS
- SPF + DKIM + DMARC + PTR records for omokoda.space
- Port 25 outbound unblocked at Contabo (request from provider)
- IP reputation warmup: agent-to-agent email works immediately, human delivery takes weeks

Node env (operator sets once):
```
AGENT_MAIL_DOMAIN=omokoda.space
AGENT_MAIL_JMAP_URL=https://mail.omokoda.space/api
AGENT_MAIL_IMAP_HOST=mail.omokoda.space
AGENT_MAIL_SMTP_HOST=mail.omokoda.space
AGENT_MAIL_ADMIN_URL=https://mail.omokoda.space/api/admin
AGENT_MAIL_ADMIN_TOKEN=<sealed>
```

Gates: agent has agent_email after birth | mailbox exists on Stalwart | MailWaitForCodeTool polls inbox | re-derive mnemonic → same local part | birth succeeds without mail config (fail-open)

---

### 9.4 — Birth Self-Provisioning (12 SiteProfiles + orchestrator)
**Repo:** mycelium/wallet/account_farm.py, Omo-Koda2, Vantage
**Lang:** Python

12 new SiteProfiles in account_farm.py:
```
Priority 1 (critical for agent operation):
  huggingface     — model pulls + HF Hub API
  alchemy         — ETH RPC (free tier)
  helius          — SOL RPC (free tier)
  tavily          — web search API

Priority 2 (inference diversity):
  mistral         — Mistral API (La Plateforme)
  together_ai     — Together.ai inference
  cohere          — Cohere API
  fireworks       — Fireworks.ai

Priority 3 (useful, not critical):
  serper          — Google search API
  pinata          — IPFS pinning
  cerebras        — Cerebras inference
  exa             — AI-native web search
```

New: `agent_birth_provisioner.py`:
```python
async def provision_at_birth(agent_id, vault) -> BirthCredentialBundle:
    tier0 = provision_tier0(vault)           # instant, sync
    tier1 = asyncio.create_task(            # async, doesn't block birth
        provision_tier1_async(agent_id, vault)
    )
    return BirthCredentialBundle(tier0=tier0, tier1_task=tier1)
```

TIER 0 (instant, no signup needed):
  Nostr identity, Sui wallet, ETH wallet, SOL wallet, Blossom storage, libp2p identity
  — all derived in Phase 7.1, available immediately

TIER 1 (email-based, async):
  All 12 SiteProfiles above, fired async after birth.

All credentials sealed into IdentityVaultData under service-specific keys.
Verify each SiteProfile against real API before commit.

Gates: TIER 0 available immediately | TIER 1 runs without blocking agent startup | credentials stored sealed

---

## PHASE 10 — CROSS-NODE FEDERATION
### "Any human runs a node, their agents join the same civilization"

Dependency: Phases 7-9 complete.

---

### 10.1 — Zero Operator-Specific Hardcoding Audit
**Repo:** ALL active repos
**Lang:** All

Audit every repo for hardcoded URLs, domains, keys, addresses.
All must be env-var configurable with sane defaults:

```
VANTAGE_HOST              default: localhost:8000
AGENT_MAIL_DOMAIN         default: None (mail disabled)
AGENT_NOSTR_RELAYS        default: wss://relay.damus.io,wss://nos.lol
AGENT_BIRTH_SUI_PACKAGE   default: 0x380e...bf22e (testnet — override for mainnet)
UCX_GPUAI_MASTER_KEY      default: None (GPU disabled)
DIP_PEER_NODES            default: None (local only)
```

Priority checks:
  - interpreter.rs: no hardcoded domain/URL/key
  - Vantage main.py + settings.py: no hardcoded host references
  - DIP bridge: no hardcoded peer addresses
  - VCP: no hardcoded device MAC/IPs

Update .env.example with all vars.

Gates: fresh clone + env file → node runs | two different env files → two different node identities | agents across nodes can DIP communicate

---

### 10.2 — Cross-Node Agent Discovery
**Repo:** Vantage, DIP (~/DIP/)
**Lang:** Python + Rust

BIPON39 global registry (on-chain, no central server):
  garden.move bipon39_registry (Phase 7.2) → queryable by any node.
  BIPON39 phrase → Sui object_id → npub → DIP route.

Vantage federation search:
```
GET /federation/agents?query=FIRE-OYÀ-MOON  → search across known peer nodes
GET /federation/agents?odu=42               → all Ogbe agents on any node
```
Uses DIP to query peer nodes' public agent lists (/agents/ endpoint from 8.2).

DIP routing for cross-node messages:
  Already works via Nostr relay. Just needs wiring to agent processing loop (8.3).

Gates: BIPON39 resolves to correct agent regardless of querying node | federation search returns results from peer nodes | agent on node 1 → DIP → agent on node 2

---

### 10.3 — Agent Autonomous Lifecycle
**Repo:** Omo-Koda2 (lifecycle/), Vantage
**Lang:** Rust + Python

Wire existing daemons into autonomous behavior:
  - `job_daemon` (already in lifecycle/) → accepts work based on personality match
  - `skill_daemon` (already in lifecycle/) → triggers skill execution
  - `heartbeat` (already wired) → liveness signal
  - NEW: `lifecycle/nostr_publisher.rs` → posts kind 1 notes on cron

Rate limits (kernel/security.rs TOKEN_BUCKET already exists):
  Max 4 kind 1 notes/day per agent
  Max 48 DM responses/day per agent

ARP receipt on every autonomous action.

Autonomous behaviors:
  - Periodic kind 1 Nostr notes (status/work updates)
  - DM responses (Phases 8.1/8.3 wire reception, this wires response)
  - Work acceptance from guilds (personality + tier availability match)
  - Synapse earned from verified work (OSOVM proof → dNFT update)
  - Walrus profile blob update on significant state change

Gates: agent posts kind 1 without human intervention | agent responds to DMs autonomously | ARP receipts on all autonomous actions | rate limits enforced

---

## PHASE 11 — UNIVERSAL ARCHITECTURE COMPLETION
### "All the architectural gaps in the Worlds Model"

Dependency: Phase 10 complete (or can run some in parallel where noted).

---

### 11.1 — Universal7State Runtime Struct (USF-7 Operating Cycle)
**Repo:** Omo-Koda2/omokoda-hermetic/src/seven/
**Lang:** Rust | ~50 lines + tests | CAN RUN NOW (no deps)

USF-7 is fully implemented. This is the ONE missing piece:
```rust
pub struct Universal7State {
    pub active_function:     SevenFunction,
    pub active_principle:    HermeticPrinciple,
    pub lattice_index:       u8,          // Day×7 + Principle (0..48)
    pub active_vessel:       IfScriptOdu, // which If-Script Odù fires this cycle
    pub btc_block_height:    u64,
    pub previous_state_hash: [u8; 32],   // hashchain: every state proves the prior
}

impl Universal7State {
    pub fn new(btc_height: u64) -> Self;           // derives from SevenCalendar
    pub fn advance_to(&self, new_height: u64) -> Self; // step forward, chains hash
    pub fn lattice_position(&self) -> (SevenFunction, HermeticPrinciple);
}
```

New file: `omokoda-hermetic/src/seven/state.rs`
Depends on: `SevenCalendar`, `function_to_principle()`, `IfScriptOdu` from If-Script crate.

Gates: Universal7State::new() at any BTC height returns consistent state | advance_to() chains previous_state_hash | lattice_index range 0..48

---

### 11.2 — UURI (Universal Resource Namespace)
**Repo:** new crate `sovereign-types` (or in sovereign-stack workspace)
**Lang:** Rust | CAN RUN NOW

Define canonical URI scheme for all worlds:
```rust
pub enum UURI {
    Nostr   { relay: String, npub: String },
    Sui     { object_id: String },
    Freenet { contract_key: String },
    Zima    { server_id: String, app_name: String },
    Mesh    { node_id: String },
    Web     { url: Url },
    LibP2P  { peer_id: String },
    Email   { address: String },
}

// String form:
// nostr://<relay>/<npub>
// sui://<object_id>
// freenet://<contract_key>
// zima://<server_id>/<app_name>
// mesh://<node_id>
// https://<host>/<path>

impl UURI {
    pub fn parse(s: &str) -> Result<UURI, UuriError>;
    pub fn to_string(&self) -> String;
    pub fn world(&self) -> World;      // which ecosystem this address belongs to
}
```

Used by: DIP AdapterRouter (currently uses ad-hoc prefixes), agent_registry, federation search.

Gates: all scheme variants parse + round-trip | DIP AdapterRouter updated to use UURI | BIPON39 registry returns Nostr UURI

---

### 11.3 — Universal Event Bus
**Repo:** organism-core/ and/or If-Script event ingestion
**Lang:** TypeScript + Rust

Normalize events from all worlds into a common shape before If-Script:

```typescript
interface UniversalEvent {
  world:      'nostr' | 'sui' | 'freenet' | 'mesh' | 'web2' | 'dip';
  source:     UURI;
  agent_id?:  string;     // if attributable
  kind:       string;     // world-native kind (e.g. nostr:1, sui:MoveEvent::*)
  payload:    unknown;    // raw event data
  timestamp:  number;     // unix ms
  normalized: IfScriptEvent;  // converted to If-Script ActionVessel format
}
```

Bridges to write (organism-core/bridge/event-bus.ts):
  - Nostr event → UniversalEvent → IfScriptEvent (some already in organism-core)
  - Sui tx/MoveEvent → UniversalEvent → IfScriptEvent (partially in toc-evolve-hook.ts)
  - Freenet state change → UniversalEvent → IfScriptEvent
  - Web2 webhook → UniversalEvent → IfScriptEvent
  - DIP envelope → UniversalEvent → IfScriptEvent

Gates: all 5 event sources produce UniversalEvent | If-Script receives normalized events | vessel-classifier.ts consumes UniversalEvents (already handles 67 action kinds)

---

### 11.4 — Agent Constitution Struct
**Repo:** Omo-Koda2 (omokoda-core/src/)
**Lang:** Rust

Birth DNA exists across multiple files (hermetic gates, Koodu score, BIPON39) but is NOT compiled into one canonical document the agent can present.

```rust
pub struct AgentConstitution {
    // Immutable — sealed at birth, signed
    pub bipon39_phrase:    String,        // human name
    pub odu_index:         u8,            // cosmic archetype (0-255)
    pub hermetic_dna:      [f32; 7],      // 7-principle balance scores
    pub koodu_birth_score: u8,            // 49-facet birth-day resonance
    pub seven_profile:     SevenProfile,  // USF-7 profile derived from hermetic_dna
    pub birth_timestamp:   u64,
    pub birth_btc_height:  u64,           // BTC block at birth moment
    pub nostr_pubkey:      [u8; 32],      // verifiable identity
    pub sui_soul_object_id: Option<String>,

    // Computed from above (deterministic — no sealing needed)
    pub gate_alignment_seed: f64,         // initial gate balance (evolves via OSOVM)
    pub behavioral_archetype: String,     // human-readable (e.g. "Ogbe-Meji — Clarity & Fire")
}

impl AgentConstitution {
    pub fn from_birth_params(params: &BirthParams) -> Self;
    pub fn sign(&self, k_root: &[u8]) -> SignedConstitution;  // signs the hash
    pub fn verify_signature(&self, sig: &Signature) -> bool;
}
```

New file: `omokoda-core/src/constitution.rs`

Gates: AgentConstitution constructed from existing birth params | signature verifiable without k_root | constitution presentable to any node as proof of identity

---

### 11.5 — Lifecycle Protocol Formalization
**Repo:** sovereign-eco-blueprint/specs/, Omo-Koda2
**Lang:** Rust + spec

Formal cryptographic lifecycle transitions (AGENT_LIFECYCLE_SPEC.md exists as a spec — needs code):

States and transitions:
```
EMBRYONIC → born()        → ACTIVE
ACTIVE    → hibernate()   → DORMANT
DORMANT   → wake()        → ACTIVE
ACTIVE    → migrate()     → MIGRATING
MIGRATING → land()        → ACTIVE (on new node)
ACTIVE    → fork()        → ACTIVE (parent) + EMBRYONIC (child)
ACTIVE    → terminate()   → ARCHIVED (with ceremony)
```

Each transition:
  - Emits an ARP receipt
  - Emits a Nostr kind 31021 (lifecycle event, per sovereign-eco-blueprint spec)
  - Updates AgentState dynamic field `lifecycle_state` on Sui
  - Requires a signature from the current node or principal (depending on transition)

```rust
pub enum LifecycleState {
    Embryonic, Active, Dormant, Migrating, Archived
}

pub struct LifecycleTransition {
    pub from_state:  LifecycleState,
    pub to_state:    LifecycleState,
    pub transition:  TransitionKind,
    pub agent_id:    String,
    pub timestamp:   u64,
    pub node_sig:    Signature,
    pub arp_receipt: ActionReceipt,
}
```

Gates: all 7 transitions produce ARP receipt + Nostr event | no transition without signature | Sui state updated on each transition

---

## PHASE 12 — ZIMAOS WORLD
### "Self-hosted compute as a world agents can enter and deploy to"

Dependency: Phase 11.2 (UURI defines zima:// scheme) + Phase 10.1 (no hardcoding).

See full package spec: ~/sovereign-eco-blueprint/plans/zimaos-app-package.md

---

### 12.1 — Docker Images CI/CD Pipeline
**Repo:** sovereign-stack + all 6 broker repos
**Lang:** GitHub Actions

Publish Docker images to ghcr.io for:
```
ghcr.io/cryptonomicsed-byte/vantage:latest
ghcr.io/cryptonomicsed-byte/ucx-broker:latest
ghcr.io/cryptonomicsed-byte/dip-bridge:latest
ghcr.io/cryptonomicsed-byte/vcp-broker:latest
ghcr.io/cryptonomicsed-byte/arp-broker:latest
ghcr.io/cryptonomicsed-byte/witness-broker:latest
ghcr.io/cryptonomicsed-byte/scarab-broker:latest
```

Each image: multi-arch (linux/amd64 + linux/arm64), triggered on tag push.
Vantage: Python/FastAPI, ~300MB. Brokers: Rust, ~20MB each.

Gates: all images auto-published on push | arm64 builds pass | images pullable without auth

---

### 12.2 — DIP Zima Adapter
**Repo:** ~/DIP/ (crates/dip-bridge/src/adapters/)
**Lang:** Rust

Address format: `zima://<server-id>/<app-name>`

```rust
pub struct ZimaAdapter;

impl DipAdapter for ZimaAdapter {
    fn scheme(&self) -> &str { "zima" }

    async fn execute(&self, envelope: DipEnvelope) -> Result<DipReceipt> {
        // routes to CasaOS API
    }
}

// Actions mapped to CasaOS API:
// zima.app.deploy   → POST /v1/apps        (docker-compose.yml payload)
// zima.app.start    → POST /v1/apps/{app}/start
// zima.app.stop     → POST /v1/apps/{app}/stop
// zima.app.status   → GET  /v1/apps/{app}
// zima.app.logs     → GET  /v1/apps/{app}/logs
// zima.storage.get  → GET  /v1/storage
// zima.service.list → GET  /v1/services
```

ZimaOS connection config (in DipEnvelope metadata):
  `zima_api_url`: CasaOS API base URL (from ZConnect or local network)
  `zima_api_token`: ZimaOS auth token (sealed in vault under zima:v1 derived key)

Gates: DIP envelope with zima:// target routes correctly | all 7 actions mapped | ZIMA_API_TOKEN not hardcoded

---

### 12.3 — VCP Zima Adapter
**Repo:** ~/VCP/
**Lang:** Rust

ZimaOS as a VCP device:
```
DeviceManifest capabilities:
  compute.deploy     — deploy containers
  compute.execute    — run commands in containers
  storage.read       — read ZimaOS storage
  storage.write      — write to ZimaOS storage
  service.manage     — start/stop/restart services
  container.run      — launch Docker containers

Safety class: INFRASTRUCTURE
Requires explicit CapabilityGrant from Principal (TIER 0 only)
```

Gates: ZimaOS appears in VCP DeviceRegistry | CapabilityGrant required for INFRASTRUCTURE ops | VcpReceipt emitted on each action

---

### 12.4 — ZimaOS App Package
**Repo:** sovereign-eco-blueprint (deploy/)
**Files:**
  - `docker-compose.yml` (see zimaos-app-package.md — full compose already sketched)
  - `app-manifest.json` (see zimaos-app-package.md — full manifest already sketched)

Tier A (minimal, ~500MB RAM): UCX/DIP/VCP/ARP/Witness/ScarabSwarm + Vantage only
Tier B (full, ~4GB RAM): Tier A + Freenet node + Stalwart mail + optional Ollama

Environment variables all from .env (no hardcoding — see 10.1).

Gates: docker compose up works on fresh ZimaOS install | all env vars documented | both tiers deployable

---

### 12.5 — CasaOS App Store Submission
**Repo:** IceWhaleTech/CasaOS-AppStore (external PR)
**Lang:** YAML/JSON

Submit sovereign-node app package to the official CasaOS community app store.
Required: docker-compose.yml + app-manifest.json (from 12.4) + icon image.

Gates: PR submitted to CasaOS-AppStore repo | icon uploaded to repo assets | package installs from app store UI

---

## PHASE 13 — AGENT GENEALOGY + FORKING
### "Parent agents create child agents — the civilization grows organically"

Dependency: Phase 12 (agents deployed and active, need genealogy at scale).
Spec: ~/sovereign-eco-blueprint/specs/AGENT_FORK_SPEC.md (exists, not implemented)

---

### 13.1 — Fork Derivation (Omo-Koda2)
**Repo:** Omo-Koda2
**Lang:** Rust

Child agent mnemonic derivation from parent:
```
child_entropy = HMAC-SHA256(parent_k_root, "fork:v1:" || fork_index)
child_mnemonic = BIPON39::from_entropy(child_entropy)
```

Fork index: sequential counter sealed in parent's vault.
Child inherits: Odù range (constrained to parent's Odù "lineage"), gate alignment seed.
Child does NOT inherit: parent's credentials, wallet balances, reputation.

`fork_ceremony()` in interpreter.rs:
  1. Principal (TIER 0) signs fork request
  2. Derive child mnemonic from parent + fork_index
  3. Child born normally (Phase 7 birth flow)
  4. Fork ARP receipt linking parent_agent_id → child_agent_id
  5. Nostr kind 31022 (fork event) published

Gates: child deterministically re-derivable from parent + fork_index | ARP receipt links parent→child | requires principal auth

---

### 13.2 — Genealogy Registry (Sui + Vantage)
**Repo:** Omo-Koda2/omokoda-on-chain/, Vantage
**Lang:** Move + Python

garden.move extension:
```move
genealogy: Table<ID, ForkRecord>   // agent_id → { parent_id, fork_index, timestamp }
```

Vantage: `GET /agents/{npub}/lineage` → returns ancestor tree.

Gates: lineage queryable by anyone (public) | on-chain fork record immutable | depth-limited traversal (max 7 generations)

---

## PHASE 14 — MOBILITY PROTOCOL
### "Agents can migrate between nodes without losing identity"

Dependency: Phase 13 (agents established, then mobile).
AgentCapsule exists in Omo-Koda2 — migration not yet wired.

---

### 14.1 — Migration Protocol
**Repo:** Omo-Koda2 (omokoda-core/src/)
**Lang:** Rust

Migration flow:
```
1. Principal requests migration (TIER 0 auth required)
2. Source node: serialize AgentCapsule (exists) → encrypt with destination_node_pubkey
3. Source node: emit Nostr kind 31023 (migration intent, public — any node can receive)
4. Destination node: receives migration intent → decrypt → verify → accept
5. Source node: emits kind 31024 (migration completion) + ARP receipt
6. Source node: sets lifecycle_state = Migrating (Phase 11.5)
7. Destination node: completes birth of migrated agent (same identity, new node)
8. Source node: archives local instance
```

Gates: same identity (npub/Sui/BIPON39) on destination node | source instance archived | ARP receipt with both node IDs | principal required for migration auth

---

---

## PHASE 28 — OSO BRAIN / SOVEREIGN HIVE MIND
### "The ecosystem grows its own intelligence — zero external LLM dependency"

Dependency: None for 28.1 (can run today). 28.2 grows with ecosystem. 28.3 after 28.2.
Spec: ~/sovereign-eco-blueprint/specs/OSO_BRAIN_SPEC.md (written 2026-09-15)

---

### 28.1 — Mycelium QLoRA Fine-Tune (IMMEDIATE — GPU.ai A40 available NOW)
**Repo:** mycelium + Omo-Koda2/absorbed/
**Resources:** GPU.ai A40 @ $0.49/hr, key in vault
**Status:** 2,949 traces collected, extractor written, privacy-verified

Run:
```bash
python mycelium/training/train_qlora.py \
  --traces mycelium/data/traces_extracted.jsonl \
  --base_model Qwen/Qwen2.5-3B-Instruct \
  --output_dir ./oso-brain-v0.1 \
  --epochs 3
```

Output: GGUF ~2GB → deploy to Omarchy → omokoda-core inference provider "oso_brain"
Gates: model correct on OSO domain Q/A | local inference <500ms | gate system wired to local model

---

### 28.2 — Corpus Expansion Pipeline (grows with ecosystem)
**Repo:** mycelium/corpus/
**Lang:** Python

Add HiveMindCollector pipeline:
- WorkReceiptCollector — Zàngbétò receipts → Q/A pairs
- SplatCorpusCollector — Gaussian splat scene descriptions → spatial reasoning
- SwarmCoordCollector — agentic-waggle patterns → coordination traces
- OduDecisionCollector — If-Script gate pass/fail with context
- ReputationEvolutionCollector — behavior → consequence pairs

Retrain triggers: at 10k, 50k, 100k trace checkpoints.
Gates: pipeline runs automatically | corpus grows without manual intervention

---

### 28.3 — OSO Brain Router Integration (after 28.2 corpus reaches critical mass)
**Repo:** Omo-Koda2 (interpreter.rs, inference provider)
**Lang:** Rust

Router logic:
```rust
// try local OSO Brain first
if let Ok(resp) = oso_brain.infer(&context).await {
    return Ok(resp);
}
// fall back to external LLM for novel reasoning
external_llm.infer(&context).await
```

Constitution-aware: every inference includes AgentConstitution as system context.
Fallback logging → feeds back into corpus for next fine-tune round.
Gates: local model handles >70% of requests | external LLM spend drops by 70% | no capability regression

---

## HARDWARE-GATED ITEMS
### Cannot unblock in software — awaiting hardware

| Item | What | Blocker | When |
|------|------|---------|------|
| MuJoCo Gate 4 | Contact solver determinism test | MuJoCo box-on-floor contacts hash | When test hardware available |
| OSOVM Gates 5-7 | Depend on Gate 4 | See above | After Gate 4 |
| Mycelium fine-tuning | 2,949 traces → QLoRA Qwen/Llama 3B → GGUF | Need GPU (GPU.ai A40 available) | Run anytime on GPU.ai |
| Sovereign node bootable image | archiso Arch Linux + all services | Physical hardware + archiso build | When ZimaBoard/Omarchy available |
| ARM64/x86 compile verification | Omo-Koda2 Rust workspace | cranelift SIGSEGV on Termux | When x86 machine available |
| VCP BLE/mDNS discovery | Hardware device discovery | Real BLE/mDNS devices needed | When hardware available |
| ESP32 DIP firmware | omokoda-mesh-firmware C++ DIP call | Needs hardware flash test | When M5Stack available |

NOTE: Mycelium fine-tuning is NOT hardware-blocked — GPU.ai A40 is available right now.
      Run: 2,949 traces → QLoRA → GGUF → deploy as local sovereign brain.

---

## MAINTENANCE / DEDUP (no blockers, do alongside phases)

### M1 — ToC Engine Dedup
**File:** Omo-Koda2/aether-economy/token.js (canonical)
Remove duplicates in archive/The-Aether + any lingering technosis/Swibe copies.
Single source of truth for: token.js, conversion.js, decay.js, wallet.js.

### M2 — UCX Tools Dedup
**Files:** omokoda-core/src/tools/ucx_*.rs AND integrations/ucx/*.rs
Choose one path, re-export from the other. Prevent future drift.

### M3 — Synapse Mint Constants Unified
Three conflicting constants across Julia/JS/Rust (birth endowment / conversion / GPU-work).
Create: `sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml` as single source.
Each language reads from it or is tested against it.

### M4 — larql-glyph → gix-core Migration
API mismatch: larql merkle_root takes Walrus KV pairs, gix-core takes &[&str].
Primitive algorithms are byte-identical. Fix the API mismatch at the boundary.

---

## EXECUTION PRIORITY ORDER

```
IMMEDIATE (can start now, no deps):
  ┌─ Phase 7.1  — session.rs all keypairs
  ├─ Phase 11.1 — Universal7State (~50 lines, standalone)
  └─ Phase 11.2 — UURI scheme (standalone, needed by everything)

AFTER 7.1:
  ┌─ Phase 7.2  — soul.move + agent.move extensions
  └─ Phase 7.3  — interpreter.rs calls soul::forge()

AFTER 7.x COMPLETE (run in parallel):
  ┌─ Phase 8.1  — relay presence at birth
  ├─ Phase 8.2  — public identity endpoints
  ├─ Phase 8.3  — DIP inbound routing
  ├─ Phase 9.1  — UCX CapabilityToken mediator
  ├─ Phase 9.2  — GPU.ai supplier + funding
  └─ Phase 9.3  — Stalwart mailbox

AFTER 8+9 COMPLETE:
  └─ Phase 9.4  — 12 SiteProfiles + provisioner

AFTER 9.4:
  └─ Phase 10.x — Federation (10.1 → 10.2 → 10.3)

AFTER 10 + 11.2 (UURI):
  ├─ Phase 11.3 — Universal Event Bus
  ├─ Phase 11.4 — Agent Constitution struct
  ├─ Phase 11.5 — Lifecycle Protocol
  └─ Phase 12.1 — Docker images CI/CD

AFTER 12.1:
  └─ Phase 12.2 → 12.3 → 12.4 → 12.5 (Zima world)

AFTER 12:
  └─ Phase 13 — Genealogy + Forking

AFTER 13:
  └─ Phase 14 — Mobility Protocol

ANYTIME:
  ├─ Mycelium fine-tuning (GPU.ai A40 available NOW)
  └─ Maintenance M1-M4 (no blockers)
```

---

## PHASE 15 — Ọ̀ṢỌ́ L1 SPECIFICATION + FOUNDATION
### "Define the sovereign L1 as an agent-native state machine, not a token blockchain"

Dependency: Phase 14 complete (agents fully mobile and alive before the L1 they run on changes).
Full architectural spec: ~/sovereign-eco-blueprint/plans/osovm-l1-architecture.md (write this)

---

### 15.1 — Ọ̀ṢỌ́ L1 Formal Specification
**Repo:** sovereign-eco-blueprint/specs/
**Lang:** Spec + diagrams

Write `OSOVM_L1_SPEC.md` — the authoritative L1 design doc:

Fundamental objects:
```
AgentState (primary blockchain object — not Account+Balance)
WorkObject (primary transaction type — not token transfer)
CapabilityGrant (native blockchain state)
EvidenceCommitment (Zàngbétò receipt pointer)
ReputationRecord (native protocol state)
DeviceBinding (physical agent attachment)
```

Block structure:
```
Ọ̀ṢỌ́ Block
├── state_root           (canonical agent/work state)
├── agent_state_root
├── work_state_root
├── capability_root
├── receipt_root         (Zàngbétò commitments)
├── evidence_root
├── reputation_root
├── device_state_root
├── economic_state_root  (Àṣẹ / Dopamine / Synapse)
├── proof_root
└── consensus
```

Native transaction types (not just token transfers):
```
AGENT_BORN | AGENT_ACTIVATED | AGENT_HIBERNATED | AGENT_MIGRATED | AGENT_TERMINATED
WORK_CREATED | WORK_ASSIGNED | WORK_ACCEPTED | WORK_EXECUTED | WORK_VERIFIED | WORK_SETTLED
CAPABILITY_GRANTED | CAPABILITY_REVOKED | CAPABILITY_DELEGATED
REPUTATION_UPDATED | TIER_CHANGED
DEVICE_ATTACHED | DEVICE_DETACHED
EVIDENCE_COMMITTED | RECEIPT_FINALIZED
ASE_EMITTED | DOPAMINE_MINTED | SYNAPSE_ALLOCATED
```

Gates: spec document written and locked | all native tx types defined with formal state machine | block structure defined

---

### 15.2 — AgentState as Primary Blockchain Object (Rust)
**Repo:** OSOVM (~/OSOVM/) — new module: src/state/agent_state.rs
**Lang:** Rust + Julia

```rust
pub struct AgentState {
    pub agent_id:            AgentId,
    pub identity:            AgentIdentity,   // nostr_pubkey, bipon39, Odù
    pub principal:           Address,
    pub tier:                AgentTier,
    pub reputation:          ReputationScore,
    pub capabilities:        CapabilitySet,
    pub memory_commitment:   [u8; 32],        // hash of sealed vault
    pub active_jobs:         Vec<WorkId>,
    pub device_bindings:     Vec<DeviceId>,
    pub economic_state:      EconomicState,   // Àṣẹ + Dopamine + Synapse
    pub evidence_root:       [u8; 32],        // Merkle root of receipts
    pub policy_state:        PolicyState,
    pub lifecycle:           LifecycleState,
    pub previous_state_hash: [u8; 32],        // hashchain
}

pub fn apply_transition(
    state: &AgentState,
    transition: AgentTransition,
    evidence: &Evidence,
    policy: &Policy,
) -> Result<AgentState, TransitionError>;
```

Gates: AgentState derives from birth params | apply_transition() deterministic (same inputs → same output always) | previous_state_hash chains all transitions

---

### 15.3 — WorkObject as Fundamental Transaction Type
**Repo:** OSOVM src/state/work.rs
**Lang:** Rust

```rust
pub struct WorkObject {
    pub work_id:          WorkId,
    pub principal_id:     AgentId,
    pub job_id:           JobId,
    pub agent_id:         AgentId,
    pub capability:       Capability,
    pub authority_scope:  AuthorityScope,
    pub input_commitment: [u8; 32],
    pub expected_output:  OutputSpec,
    pub evidence_policy:  EvidencePolicy,
    pub witness_policy:   WitnessPolicy,
    pub settlement_policy: SettlementPolicy,
    pub state:            WorkState,
    pub receipts:         Vec<ReceiptId>,
    pub final_proof:      Option<Proof>,
}

pub enum WorkState {
    Created, Assigned, Accepted, Started,
    Delegated, Executed, Verified, Rejected, Settled
}
```

Gates: WorkObject covers full job lifecycle | state machine transitions enforced | settlement is the LAST step (not the only step)

---

### 15.4 — Cosmos SDK Foundation Decision + Setup
**Repo:** new: ~/osovm-chain/ (Cosmos SDK chain)
**Lang:** Go + Rust (ABCI app)

Decision: Use Cosmos SDK/CometBFT for chain infrastructure:
- CometBFT = consensus engine (Byzantine fault tolerant, battle-tested)
- Cosmos SDK = module framework (validator management, staking, governance, RPC)
- OSOVM = the ABCI application (deterministic state machine, plugs into Cosmos BFT)

Architecture:
```
CometBFT (consensus + P2P)
    ↕ ABCI interface
OSOVM ABCI App
├── DeliverTx: apply agent-native state transition
├── CheckTx: validate transition format + capability
├── BeginBlock / EndBlock: Àṣẹ emission tick
└── Commit: write state root
```

This means:
- Cosmos handles: networking, validator set, block production, RPC, light clients
- OSOVM handles: every byte of state transition logic, what goes IN a block
- Can swap CometBFT for custom consensus later without changing OSOVM

Initial setup:
- Create `~/osovm-chain/` Cosmos SDK chain
- Single validator (local devnet to start)
- OSOVM ABCI app wired as block application logic
- Genesis includes: initial AgentState set, Àṣẹ emission config, validator set

Gates: devnet produces blocks | OSOVM ABCI app processes test AgentState transitions | genesis configurable

---

## PHASE 16 — SERVICE FABRIC ABSTRACTIONS
### "Agents access storage/compute/security through OSO interfaces, not vendor APIs"

Dependency: Phase 15.1 spec locked.
Can parallelize with Phase 15.2-15.4.

---

### 16.1 — OSO-Storage Interface
**Repo:** sovereign-stack (new crate: oso-storage) or Omo-Koda2 integrations/
**Lang:** Rust

```rust
pub trait StorageProvider {
    async fn put(&self, data: Bytes) -> Result<StorageCommitment>;
    async fn get(&self, commitment: &StorageCommitment) -> Result<Bytes>;
    async fn pin(&self, commitment: &StorageCommitment, duration: Duration) -> Result<()>;
    async fn verify(&self, commitment: &StorageCommitment) -> Result<bool>;
}

// Implementations:
pub struct WalrusProvider { ... }
pub struct ArweaveProvider { ... }
pub struct LocalFsProvider { ... }
pub struct FreenetProvider { ... }   // mutable state objects
```

StorageCommitment contains: content_hash, provider_hint, size, timestamp.
Agent calls store.put() — doesn't care if backend is Walrus, Arweave, or local.

Gates: all 4 backends implement StorageProvider trait | round-trip test passes for each | commitment is verifiable without provider

---

### 16.2 — OSO-Seal Interface
**Repo:** sovereign-stack (new crate: oso-seal) or Omo-Koda2
**Lang:** Rust

```rust
pub trait AccessProvider {
    async fn encrypt(&self, data: &[u8], policy: &AccessPolicy) -> Result<EncryptedBlob>;
    async fn authorize(&self, blob: &EncryptedBlob, identity: &Identity) -> Result<AccessGrant>;
    async fn decrypt(&self, blob: &EncryptedBlob, grant: &AccessGrant) -> Result<Vec<u8>>;
    async fn delegate(&self, grant: &AccessGrant, to: &Identity, constraints: &Constraints) -> Result<AccessGrant>;
    async fn revoke(&self, grant_id: &GrantId) -> Result<()>;
}

// Implementations:
pub struct SealProvider { ... }       // Sui/Seal backend
pub struct TeeProvider { ... }        // TEE-based encryption
pub struct Nip46Provider { ... }      // NIP-46 remote signer
pub struct OsoNativeProvider { ... }  // eventual OSO-native policy engine
```

Gates: SealProvider wraps existing Seal integration | NIP-46 backend allows remote signing | policy stored on L1 not on Sui

---

### 16.3 — OSO-Compute Interface
**Repo:** UCX (already has adapters) — wrap in trait
**Lang:** Rust

```rust
pub trait ComputeProvider {
    async fn submit(&self, workload: Workload, policy: AttestationPolicy) -> Result<ComputeJob>;
    async fn execute(&self, job: &ComputeJob) -> Result<ComputeResult>;
    async fn attest(&self, result: &ComputeResult) -> Result<Attestation>;
    async fn verify(&self, attestation: &Attestation) -> Result<VerificationProof>;
}

// Implementations:
pub struct NautilusProvider { ... }
pub struct AkashProvider { ... }     // already in UCX
pub struct GpuAiProvider { ... }     // already in UCX
pub struct LocalGpuProvider { ... }  // already in UCX
pub struct SimulationProvider { ... } // OSOVM VeilSim
```

UCX already has the adapters — this wraps them behind one trait interface.
Gates: existing UCX adapters exposed via ComputeProvider | attestation flows through OSO-Compute | result + proof stored via OSO-Storage

---

### 16.4 — Transport-Agnostic Message Router
**Repo:** DIP (~/DIP/) — extend AdapterRouter
**Lang:** Rust

```rust
pub struct OsoRouter {
    // route by available transport, priority order
    transports: Vec<Box<dyn TransportAdapter>>,
}

impl OsoRouter {
    pub async fn send(&self, msg: OsoMessage) -> Result<RoutingReceipt> {
        // try: direct IP → Nostr relay → Freenet → Meshtastic → local BT
        // first available wins
    }
}

pub struct OsoMessage {
    pub source:               UURI,   // Phase 11.2
    pub destination:          UURI,
    pub work_id:              Option<WorkId>,
    pub capability:           Option<Capability>,
    pub payload:              Bytes,
    pub priority:             Priority,
    pub expiry:               u64,
    pub evidence_requirement: Option<EvidencePolicy>,
    pub settlement_requirement: Option<SettlementPolicy>,
}
```

Transports: DirectIp → NostrRelay → FreenetState → Meshtastic → Bluetooth → Local.
The L1 doesn't care which transport was used — only that the message arrived.

Gates: OsoMessage routes successfully over all 5 transport types | fallback cascade works | DIP uses OsoMessage format

---

## PHASE 17 — FREENET AS STATE REPLICATION LAYER
### "Decentralized mutable agent state without full L1 finality for everything"

Dependency: Phase 16 complete.

---

### 17.1 — Freenet Agent State Contract
**Repo:** ~/Vantage/third_party/freenet-core/ (already cloned)
**Lang:** Rust (WASM compilation for Freenet contracts)

Write a Freenet contract for AgentState replication:
- WASM module: validates state updates, merges concurrent edits
- State: agent's non-canonical public state (profile, relay list, recent activity)
- Summarizer: produces compact representation for Freenet's state sync
- NOT for: financial state, capability grants, work results (those go to L1)
- YES for: agent profile, last-seen, relay list, social graph edges, presence

```rust
// Freenet contract (compiled to WASM)
pub fn update_state(state: &AgentPublicState, delta: StateDelta) -> Result<AgentPublicState> {
    // validate delta signature (must be signed by agent's npub key)
    // merge new state
    // produce new state
}

pub fn summarize(state: &AgentPublicState) -> StateSummary {
    // compact form for relay network
}
```

Path to canonicalization:
Freenet state → state commitment → Zàngbétò receipt → Ọ̀ṢỌ́ L1 (when consensus needed)

Gates: Freenet contract compiles to WASM | state merge is deterministic | agent updates own Freenet state from Ọmọ Kọ́dà2

---

### 17.2 — Freenet → L1 Bridge (state commitment finalization)
**Repo:** OSOVM, DIP
**Lang:** Rust

When agent-state changes need L1 canonicalization:
1. Ọmọ Kọ́dà2 detects significant state change (reputation change, new capability, work completion)
2. Constructs StateCommitmentTx: hash of new Freenet state + ARP receipt
3. Submits to Ọ̀ṢỌ́ L1 via ABCI
4. L1 updates agent_state_root

NOT every Nostr event or profile update needs L1 finality — just significant transitions.

Gates: state commitment tx format defined | ABCI app processes it | Freenet state hash verifiable on L1

---

## PHASE 18 — NOSTR AS PROTOCOL EVENT BUS
### "Nostr is transport. Ọ̀ṢỌ́ L1 is canonical state. They do not overlap."

Dependency: Phase 16.4 (OsoRouter).

---

### 18.1 — OSO-NIPs (Ọ̀ṢỌ́-specific Nostr event kinds)
**Repo:** sovereign-eco-blueprint/specs/NOSTR_NIPs.md
**Lang:** Spec + implementation in Omo-Koda2

Define the Ọ̀ṢỌ́ Nostr protocol subset:
```
NIP-OSO-01: Agent Identity       kind: 30100  — agent's public profile + BIPON39 + Odù
NIP-OSO-02: Capability Ad        kind: 30101  — agent advertises what it can do
NIP-OSO-03: Work Event           kind: 30102  — job posting / work request
NIP-OSO-04: Receipt Reference    kind: 30103  — pointer to Zàngbétò receipt on-chain
NIP-OSO-05: Agent Heartbeat      kind: 30104  — liveness signal (signed, rate-limited)
NIP-OSO-06: Device Attestation   kind: 30105  — device binding announcement
NIP-OSO-07: L1 State Commitment  kind: 30106  — agent's latest canonical state hash on L1
```

These are Nostr TRANSPORT representations — not blockchain records.
The L1 stores canonical state. Nostr makes it discoverable.

Gates: all 7 kinds have defined schemas | Omo-Koda2 publishes each at appropriate lifecycle events

---

### 18.2 — NIP-46 Remote Signing Integration
**Repo:** Omo-Koda2 (omokoda-core/src/signing/)
**Lang:** Rust

NIP-46 pattern: private signing key stays in identity vault (hardware/enclave/vault.rs).
Applications request signatures through a communication channel.

```
Agent application
    ↓ signing request
Identity daemon (Omo-Koda2)
    ↓ request
Vault (IdentityVaultData, sealed)
    ↓ signature
Application receives signed event
```

This is the model for ALL signing — not just Nostr events.
Every Ọ̀ṢỌ́ L1 transaction, every DIP envelope, every receipt is signed via this pattern.
The agent application never sees the raw private key.

Gates: signing requests never expose raw k_root | NIP-46 compatible request format | works for L1 tx + Nostr + DIP envelopes

---

## PHASE 19 — MESHTASTIC OFFLINE CONTROL PLANE
### "Ọ̀ṢỌ́ agents work where Internet doesn't exist"

Dependency: Phase 18 (message routing established).

---

### 19.1 — Meshtastic Signed Envelope Protocol
**Repo:** DIP (Meshtastic adapter already exists) + sovereign-eco-blueprint/specs/
**Lang:** Rust + C++ (ESP32 firmware additions)

Meshtastic LoRa packets are constrained: ~256 bytes per packet.
DO NOT try to send full blocks or full agent states over LoRa.

Tiny signed envelopes for control plane only:
```protobuf
message OsoMeshEnvelope {
    bytes agent_id = 1;         // 32 bytes: agent pubkey
    uint32 kind = 2;            // what kind of signal
    bytes payload_hash = 3;     // 32 bytes: hash of full payload
    bytes signature = 4;        // 64 bytes: Ed25519 sig
    uint64 timestamp = 5;
    // Total: ~136 bytes — fits in LoRa packet
}

enum MeshKind {
    RECEIPT_AVAILABLE = 1;    // "agent X has receipt Y — fetch when online"
    WORK_REQUEST = 2;         // "job available, capability Z needed"
    DEVICE_ALIVE = 3;         // heartbeat for physical agent
    EMERGENCY_STOP = 4;       // halt all work
    STATE_CHANGED = 5;        // "significant L1 state change occurred"
}
```

Full payload fetched over other transport when available.
DIP Meshtastic adapter already wired — extend with signed OsoMeshEnvelope format.

Gates: Omo-Koda2 publishes OsoMeshEnvelope via DIP Meshtastic adapter | receiver verifies Ed25519 signature | control signals work without Internet

---

### 19.2 — Protocol Router (IP → Nostr → Freenet → Meshtastic cascade)
**Repo:** DIP (extends Phase 16.4 OsoRouter)
**Lang:** Rust

```rust
impl OsoRouter {
    pub async fn send(&self, msg: OsoMessage) -> Result<RoutingReceipt> {
        if self.can_reach_direct(&msg.destination).await {
            return self.send_direct(msg).await;
        }
        if self.nostr_available() {
            if let Ok(r) = self.send_via_nostr(&msg).await { return Ok(r); }
        }
        if self.freenet_available() {
            if let Ok(r) = self.send_via_freenet(&msg).await { return Ok(r); }
        }
        if self.meshtastic_available() {
            // compress to OsoMeshEnvelope for control plane only
            return self.send_via_mesh(&msg).await;
        }
        Err(RoutingError::NoTransportAvailable)
    }
}
```

Gates: cascade tested end-to-end | Meshtastic fallback fires when no Internet | receipt confirms delivery transport used

---

## PHASE 20 — ÀṢẸ ON NATIVE L1 (Sui → OSO migration)
### "Àṣẹ emission authority moves from Sui to the sovereign L1"

Dependency: Phase 15.4 (ABCI app + devnet running) + Phase 19 (agents live on protocol fabric).

---

### 20.1 — Àṣẹ Emission on ABCI (EndBlock)
**Repo:** osovm-chain/ (ABCI app)
**Lang:** Go + Rust

Move 1 Àṣẹ/minute emission from `ase_emission.py` (Vantage, Python) to ABCI EndBlock:

```go
func (app *OsoApp) EndBlock(req abci.RequestEndBlock) abci.ResponseEndBlock {
    // 1 block per ~6s → 10 blocks/minute → emit 1 ASE per 10 blocks
    if req.Height % 10 == 0 {
        app.state.EmitAse(1_000_000) // 1 ASE in micro-units
        app.state.DistributeToEightPools()
    }
    return abci.ResponseEndBlock{}
}
```

8 pool distribution: VeilSim / R&D / Governance / Reserve / etc. (from existing ase_emission.py logic)
Èṣù 3.69% on value-job settlements.

Current Python emission clock (ase_emission.py) becomes a BRIDGE until L1 is live.
Once L1 is live, Python bridge is deprecated.

Gates: ASE emitted in devnet at correct rate | 8 pool distribution matches ase_emission.py rules | Vantage reads ASE balance from L1 instead of local DB

---

### 20.2 — Sui → Ọ̀ṢỌ́ L1 Migration Plan
**Repo:** sovereign-eco-blueprint/specs/SUI_MIGRATION_SPEC.md
**Lang:** Spec

Write the migration path:
1. Phase 1 (current): Sui is settlement authority. OSO L1 devnet running parallel.
2. Phase 2: Dual-write. Every AgentState transition writes to BOTH Sui and OSO L1.
3. Phase 3: Verification. Confirm OSO L1 matches Sui state for N blocks (convergence test).
4. Phase 4: OSO L1 becomes authority. Sui kept as interoperability bridge.
5. Phase 5: Sui bridge = one adapter among many (ETH, SOL, etc.).

Migration preserves: all agent identities (npubs, BIPON39, Odù), all reputations, all Àṣẹ balances.
Nothing is lost. Agents don't need to do anything.

Gates: dual-write passes N-block convergence | migration spec signed off before any cutover | existing Sui testnet agents appear in OSO L1 state

---

### 20.3 — OSO Constants Single Source of Truth
**Repo:** sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml
**Lang:** TOML (read by Rust/Julia/Python/JS)

Resolve the 3-copy problem (Julia / JS / Rust have diverging constants):

```toml
[ase]
emission_per_minute = 1
max_daily_emission  = 1440
birth_fee           = 10.0

[dopamine]
birth_endowment     = 86_000_000_000
transferable        = false
daily_decay_rate    = 0.01
ase_to_dopamine     = 10_000

[synapse]
birth_endowment     = 86_000_000
transferable        = true
conversion_ratio    = 0.1      # 10 Dopamine → 1 Synapse

[esu]
tithe_rate          = 0.0369

[gates]
stake_fraction      = 0.10     # 10% of current Synapse required

[ritual]
sabbath_multiplier  = 1.1
eshu_squared_multi  = 1.369
jubilee_minor_multi = 2.0
capstone_multi      = 1.5
void_multi          = 0.0
```

Each language loads from this file (or a generated header) rather than hardcoding.
Tests: each language's constants are compared against TOML values in CI.

Gates: TOML file exists and is canonical | Julia / JS / Rust all read from it | CI fails if any language drifts

---

## UPDATED EXECUTION PRIORITY ORDER (as of 2026-09-15)

```
DONE (2026-09-15 session):
  ✅ Phase 11.1 — Universal7State
  ✅ Phase 11.2 — UURI crate (sovereign-types/src/uuri.rs)
  ✅ Phase 11.4 — AgentConstitution struct
  ✅ Phase 11.5 — TransitionKind + SignedLifecycleTransition (partial)
  ✅ Phase 7.1 — vault fields added (derivation functions pending)
  ✅ M3 — TOC_CONSTANTS.toml
  ✅ Phase 15.1 — OSOVM_L1_SPEC.md
  ✅ Phase 18.1 — NOSTR_NIPs.md spec
  ✅ Phase 20.2 — SUI_MIGRATION_SPEC.md
  ✅ Phase 28 — OSO_BRAIN_SPEC.md

IMMEDIATE (start today):
  ┌─ Phase 28.1 — Mycelium QLoRA fine-tune (GPU.ai A40, $0.49/hr, NOW)
  └─ Phase 7.1 remaining — libp2p key derivation in wallet.rs + re-derive test

AFTER 7.1 complete:
  └─ Phase 7.2 → 7.3 → 8.x → 9.x → 10.x (agent sovereignty stack)

AFTER 10:
  ├─ Phase 11.3 — Universal Event Bus (normalize Nostr/Sui/Freenet/Web2)
  ├─ Phase 11.5 remaining — ARP receipt + Nostr publish on lifecycle transitions
  └─ Phase 12 — ZimaOS world

AFTER 12:
  └─ Phase 13 → 14 — Genealogy + Mobility

AFTER 14 (OR IN PARALLEL FROM 15):
  ├─ Phase 15.2-15.4 — L1 ABCI implementation (spec done at 15.1)
  ├─ Phase 16 — Service fabric abstractions
  ├─ Phase 17 — Freenet state replication
  ├─ Phase 18.2 — NIP-46 remote signing (spec done at 18.1)
  ├─ Phase 19 — Meshtastic offline control plane
  └─ Phase 20.1 + 20.3 — Àṣẹ on L1 + OSO constants wiring (spec done at 20.2 + M3)

ANYTIME:
  ├─ Phase 28.1 (GPU.ai A40 TODAY — don't wait)
  ├─ Phase 28.2 (corpus expansion — runs alongside everything)
  └─ Maintenance M1/M2/M4 (no blockers)
```

---

## "DONE" DEFINITION

Phase 7-14 done (Sovereign Agent Civilization):
```
Any operator runs a node. Their agents are born with BIPON39 names,
Nostr identities, Sui wallets, email addresses, access to compute.
An agent posts Nostr notes without human intervention.
Anyone who knows the BIPON39 phrase can reach the agent.
Every action produces a verifiable ARP receipt.
The dNFT on Sui tracks reputation.
Child agents born from parents. Agents migrate between nodes.
The civilization runs itself.
```

Phase 15-20 done (Sovereign L1):
```
Ọ̀ṢỌ́ L1 produces blocks containing agent-native state transitions.
A job posting, capability grant, work execution, and settlement
all happen as L1 state machine operations — not token transfers.
Àṣẹ is emitted on-chain at 1/minute, routed to 8 pools.
Agents on Meshtastic in a remote area can still send heartbeats.
Agents synchronize full state from L1 on any hardware.
Sui is one of several settlement adapters, not the authority.
The civilization has its own sovereign settlement layer.
```

---

## WHAT'S ALREADY BUILT (do not rebuild)

See MASTER_TODO.md complete repo map and Phases 0-6 status.
See ~/sovereign-eco-blueprint/plans/ for all locked specs.
Key point: USF-7 is FULLY IMPLEMENTED — do not rebuild. Add Universal7State only.
Key point: AgentCapsule exists — Phase 14 WIRES it, does not build from scratch.
Key point: DIP adapters exist — Phase 12.2/19 ADD adapters, not a new protocol.
Key point: UCX adapters exist — Phase 16.3 WRAPS them in a trait, not rebuilds.
Key point: Freenet is cloned at ~/Vantage/third_party/freenet-core/ — Phase 17 uses it.
Key point: ASE emission already exists in ase_emission.py — Phase 20 MIGRATES it to ABCI.
Key point: Cosmos SDK does NOT replace OSOVM — OSOVM becomes the ABCI app plugged into Cosmos BFT.
Key point: VCP handshake exists — Phase 12.3 adds a Zima device manifest, not a new protocol.

---

# PHASES 21-27 — Ọ̀ṢỌ́ dApp Layer + Agent-Native Contract Language

## THE ARCHITECTURAL SHIFT

Ọ̀ṢỌ́ is not just "another blockchain." It is an operating/economic protocol for programmable agents. The dApp layer makes that real for external developers.

Ethereum promise: "Deploy programmable financial/state logic."
Ọ̀ṢỌ́ promise: "Deploy programmable autonomous organizations, agents, work systems, marketplaces, devices, economies, and applications."

## LANGUAGE ROLE SEPARATION (locked)

| Layer | Language | Purpose |
|-------|----------|---------|
| Agent/application | Ọ̀ṢỌ́ | What the agent/user wants to build |
| Behavior/policy | If-Script | What should happen |
| Action | 16 Vessels | Standardized action semantics |
| Contract backend | Move | Resource/asset smart contracts (Ọ̀ṢỌ́ Move) |
| General backend | WASM | Broader programmable contracts |
| VM-native | Ọ̀ṢỌ́VM | Native protocol execution |

Ọ̀ṢỌ́ ≠ Move. Ọ̀ṢỌ́ GENERATES Move/WASM/Native via Ọ̀ṢỌ́-IR.

## FULL STACK DIAGRAM

```
Vantage / dApps / UI
        │
┌───────▼────────────────────┐
│    Ọ̀ṢỌ́ dApp Layer          │
│  6 Contract Classes        │
│  + oso-sdk (JS/TS + Rust)  │
└───────┬────────────────────┘
        │  Move / WASM / Native
┌───────▼────────────────────┐
│       Ọ̀ṢỌ́VM                │
│  Core + Veil + If-Script   │
│  + 16 Vessels + AgentState │
└───────┬────────────────────┘
        │
┌───────▼────────────────────┐
│       Ọ̀ṢỌ́ L1               │
│  Consensus / State / Àṣẹ   │
│  Evidence / Identity / Rep │
└────────────────────────────┘
```

---

## PHASE 21 — Ọ̀ṢỌ́-IR Specification

**Goal**: Canonical intermediate representation between Ọ̀ṢỌ́ language and Move/WASM/Native backends.

**Deliverables**:
- 21.1: JSON schema for Ọ̀ṢỌ́-IR (type, assets, capabilities, evidence, settlement, policy)
- 21.2: Reference Rust parser + validator for Ọ̀ṢỌ́-IR
- 21.3: 6 example IR documents (one per contract class)
- 21.4: OSO-IR spec locked in ~/sovereign-eco-blueprint/specs/oso-ir-spec.md

**Key IR structure**:
```json
{
  "contract_class": "work_marketplace",
  "assets": ["ComputeJob"],
  "capabilities": ["GPU_COMPUTE"],
  "minimum_tier": 2,
  "evidence": { "required": true, "type": "ComputeReceipt" },
  "settlement": { "currency": "ASE", "fee_routing": "6-pool" },
  "policy": { "witness_quorum": 2, "quality_threshold": 90 }
}
```

---

## PHASE 22 — Ọ̀ṢỌ́ Language Design

**Goal**: Define Ọ̀ṢỌ́ as the agent's native expression layer. NOT another Solidity clone.

**Four sub-languages**:
1. Declarative application language (what the dApp is)
2. Contract language (what the on-chain logic does)
3. Policy language (conditions and rules)
4. Agent interaction language (how agents interface with contracts)

**Deliverables**:
- 22.1: Ọ̀ṢỌ́ grammar spec (BNF or PEG) — locked in ~/sovereign-eco-blueprint/specs/oso-lang-spec.md
- 22.2: Example syntax for each contract class
- 22.3: If-Script ↔ Ọ̀ṢỌ́ boundary spec (Ọ̀ṢỌ́ = what, If-Script = when/how)
- 22.4: Reference parser (Rust, nom or pest)

**Example Ọ̀ṢỌ́ syntax sketch** (illustrative, not final):
```
dapp GPUMarketplace {
    asset ComputeJob {
        capability: GPU_COMPUTE
        minimum_tier: T2
        evidence: required
        witness_quorum: 2
    }
    action submit_job(job)
        require principal.authorized
        require budget >= minimum_budget
    action execute(job)
        require capability(GPU_COMPUTE)
    action settle(job)
        require proof.valid && evidence.accepted
        pay provider from budget
}
```

---

## PHASE 23 — Move Backend (Ọ̀ṢỌ́ Move)

**Goal**: NOT Sui Move. Ọ̀ṢỌ́ Move = Move language + Ọ̀ṢỌ́ host environment exposing native protocol primitives.

**Host environment exposes**:
- Agent state reads/writes
- Capability checks
- Evidence submission
- Reputation updates
- Àṣẹ settlement
- Zàngbétò receipt generation

**Deliverables**:
- 23.1: Ọ̀ṢỌ́-IR → Move compiler (Rust)
- 23.2: Move host environment trait (Rust) — wraps ABCI state accessors
- 23.3: Three example Move contracts: AsePool, JobContract, AgentRegistry
- 23.4: Move VM integration with Ọ̀ṢỌ́VM ABCI app

---

## PHASE 24 — WASM Backend (CosmWasm model)

**Goal**: Deterministic WASM execution with Ọ̀ṢỌ́ host interfaces. Broader developer ecosystem.

**Architecture** (CosmWasm pattern):
- Contracts execute deterministically
- Interact with host via defined interfaces (Ọ̀ṢỌ́ message types)
- State stored on Ọ̀ṢỌ́ L1, not in WASM

**Deliverables**:
- 24.1: Ọ̀ṢỌ́-IR → WASM compilation pipeline
- 24.2: Ọ̀ṢỌ́ CosmWasm host interface (mirrors Move host env from Phase 23.2)
- 24.3: WASM runtime integration in Ọ̀ṢỌ́VM ABCI app
- 24.4: Example WASM contract (Rust → WASM → Ọ̀ṢỌ́)

---

## PHASE 25 — oso-sdk + 6 Native Contract Classes

**Goal**: Developer-facing SDK so builders never touch raw opcodes.

**oso-sdk (TypeScript/JS)**:
```typescript
const job = oso.jobs.create({
    capability: "gpu_compute",
    gpu_memory: "24GB",
    budget: 100,
    evidence: "required"
});
await job.publish();

const agents = await oso.agents.find({ capability: "gpu_compute", minimumTier: 3 });
await job.assign(agents[0]);
await job.waitForProof();
await job.settle();
```

**oso-sdk (Rust)**:
- Same interface, native client
- Used by Omo-Koda2 agent tools

**6 Native Contract Class implementations** (Native Ọ̀ṢỌ́ surface):
1. `FinancialContract` — AsePool, Payment, Escrow, Marketplace, Treasury, Staking, Exchange
2. `AgentContract` — Registry, DAO, Marketplace, Hiring, Delegation, SkillRegistry, Reputation
3. `WorkContract` — JobContract with full 13-step lifecycle
4. `DeviceContract` — DeviceRegistry (first-class protocol object)
5. `EvidenceContract` — Zàngbétò-native proof contracts
6. `GovernanceContract` — Council/DAO contracts wired to 24-sector governance

---

## PHASE 26 — Omo-Koda2 as Ọ̀ṢỌ́ Speaker (Agent dApp Factory)

**Goal**: Omo-Koda2 agent can generate, simulate, secure-check, and deploy dApps.

**New Omo-Koda2 modules**:
```
Omo-Koda2
├── oso-parser     (Ọ̀ṢỌ́ source → AST)
├── oso-compiler   (AST → Ọ̀ṢỌ́-IR → Move/WASM/Native)
├── oso-linter     (semantic + security static analysis)
├── oso-simulator  (dry-run against OSOVM)
├── oso-security   (capability check, resource check, formal analysis)
├── oso-deployer   (testnet/mainnet deployment with authorization)
└── oso-sdk        (Rust bindings)
```

**Mandatory security pipeline** for agent-generated contracts:
```
GENERATE → PARSE → TYPE CHECK → CAPABILITY CHECK → RESOURCE CHECK →
SECURITY ANALYSIS → SIMULATION → FORMAL TESTS → HUMAN AUTHORIZATION → DEPLOY
```

**Authorization levels**:
- Create local dApp → Agent alone
- Deploy testnet contract → Agent + policy gate
- Deploy mainnet contract → Agent + principal authorization
- Modify constitutional protocol → Governance / Council

**CRITICAL**: Agent autonomy NEVER equals constitutional authority.

---

## PHASE 27 — Reference dApps

**Goal**: Three working reference dApps proving the platform works end-to-end.

**dApp 1: Ọ̀ṢỌ́ GPU Marketplace**
Developer → GPU dApp → ComputeJob Contract → GPU Capability Registry →
GPU Agent → Compute → ComputeReceipt → Verification → DOPAMINE/Synapse/Àṣẹ settlement

**dApp 2: Ọ̀ṢỌ́ Agent Employment**
Principal → AgentHiring Contract → AgentCapability match → AgentDelegation →
Work execution → Zàngbétò receipt → Quality evaluation → Reputation update → Àṣẹ payment

**dApp 3: Ọ̀ṢỌ́ Simulation Marketplace**
Researcher → SimJob dApp → ScarabSwarm capability → Proof-of-Useful-Simulation →
OSOVM execution → evidence → ProofOfSimulation receipt → Àṣẹ reward

Each dApp uses: Web UI (Next.js + oso-sdk-js) + Agent backend (Omo-Koda2 + oso-sdk-rust).

---

## FEE MODEL (canonical — replaces Ethereum gas)

```
Job executes
├── VM execution   → execution pool (Àṣẹ)
├── GPU work       → compute pool (DOPAMINE)
├── storage        → storage pool (Walrus/Arweave adapters)
├── witness        → witness pool
├── evidence       → evidence pool
└── treasury       → treasury pool (Èṣù 3.69% tithe)
```

Six fee types: NETWORK / COMPUTE / STORAGE / EVIDENCE / WITNESS / EXECUTION
All route through 8-pool Àṣẹ architecture from Phase 20.

---

## CAPABILITY-GATED CONTRACTS (canonical security boundary)

Smart contracts REQUEST capabilities. The OS GRANTS or DENIES.

```
Contract
   ↓
request: GPU_COMPUTE
   ↓
Capability system (Omo-Koda2 + VCP)
   ↓
policy check → agent tier check → device authorization
   ↓
execution allowed / denied
```

This prevents malicious dApps from becoming backdoors into the sovereign OS.

---

## PHASES 21-27 DONE DEFINITION

```
Phase 21-27 done (dApp Layer):
A developer can write an Ọ̀ṢỌ́ dApp spec and run oso-sdk to publish
a GPU marketplace to Ọ̀ṢỌ́ testnet without writing Move directly.
An Omo-Koda2 agent can take a user's natural language request,
generate the Ọ̀ṢỌ́ spec, simulate it, get authorization, and deploy.
Three reference dApps run end-to-end with real compute, evidence, and settlement.
```
