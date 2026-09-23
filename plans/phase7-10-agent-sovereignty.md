# Phases 7–10: Agent Sovereignty, Identity Network, Birth Provisioning
# Locked: 2026-09-15
# Builds on top of Phases 0-6 (complete as of 2026-09-14)

---

## THE PARADIGM SHIFT THIS PHASE IMPLEMENTS

Phases 0-6 built the organism's infrastructure: kernel, protocols, economy, spatial layer,
governance. What they did NOT do: make agents sovereign, public-facing entities.

Current state:  Agent = row in user database. Only owner can access.
Target state:   Agent = autonomous sovereign entity on the network. Anyone can reach it.

This is not a refactor of existing code. It is the activation layer — the step where the
organism goes from "infrastructure exists" to "agents are alive on the network."

The three new architectural facts locked in 2026-09-15:

  1. FEDERATION-FIRST: Any operator runs their own node. No operator-specific hardcoding
     anywhere. Crypto identity = portable (mnemonic-derived). Operational creds = node-scoped
     env vars. All nodes connect via DIP/Nostr/Meshtastic mesh.

  2. AGENT SOVEREIGNTY: Agent = entity, not account. Born once. Lives independently.
     Reachable by anyone via npub / BIPON39 phrase / Odù identifier. Principal = birthing
     relationship (privileged but not exclusive). Anyone can message the agent's npub.
     Birth parameters (Odù, hermetic DNA, Koodu score, BIPON39) lock personality forever.

  3. AGENT AS dNFT: AgentState (agent.move) + SoulRecord (soul.move) already exist on Sui
     testnet (0x380e...bf22e, deployed 2026-07-16). The dNFT IS the agent. Needs: nostr_pubkey
     + bipon39_phrase fields, Walrus profile blob pointer, public registry wiring, OSOVM oracle
     connection.

---

## DEPENDENCY MAP

  Phase 7  (Birth Keypairs + dNFT Extension)
    ↓
  Phase 8  (Nostr Relay Presence + Public Identity API)
    ↓
  Phase 9  (Agent Birth Self-Provisioning + Mailbox)
    ↓
  Phase 10 (Cross-Node Federation + Any-Operator Hosting)

Phases within a tier can run in parallel. Phases across tiers are strictly sequential.

---

## PHASE 7 — BIRTH IDENTITY COMPLETION
### "Every key the agent will ever need, derived from the mnemonic at birth"

Dependency: Phases 0-6 complete ✅

---

### Phase 7.1 — Mnemonic → All Keys (session.rs + interpreter.rs)

WHAT:
  Hermes's confirmed design. In omokoda-core/src/session.rs — add fields to both
  PrivateSessionData and IdentityVaultData. In interpreter.rs birth block — derive all keys
  from k_root via HMAC-SHA256 (same pattern as existing CapabilityToken in vault.rs).

  Keys derived at birth:
    nostr_private_key_hex  (already exists — VERIFY it's actually HMAC-derived from k_root,
                            not just random. This is the portability requirement.)
    nostr_pubkey_hex       (computed from private key — the agent's public address)
    sui_address            (already in IdentityVaultData — VERIFY derivation from mnemonic)
    eth_address            (secp256k1 from BIP-32 path m/44'/60'/0'/0/0)
    sol_address            (ed25519 from BIP-32 path m/44'/501'/0'/0')
    libp2p_peer_id         (ed25519, distinct path — DIP mesh identity)
    agent_email_local      (HMAC-SHA256 of k_root with "omokoda:email:v1" prefix → hex[..16])

  All of these: deterministic from mnemonic. Lose the vault → restore from mnemonic →
  all addresses are back. Same property wallets have.

  The agent_email_local is the permanent LOCAL PART only. The domain comes from
  AGENT_MAIL_DOMAIN env var (node-scoped, operator-configured). Full address:
  format!("{}@{}", &hex[..16], domain).

OUTPUTS:
  - session.rs PrivateSessionData: new fields for eth/sol/libp2p/email_local
  - session.rs IdentityVaultData: same new fields
  - interpreter.rs: birth block derives all keys from k_root
  - Re-derivation test: given same mnemonic → same addresses always

GATES:
  ✓ Born agent has all 7 addresses present in IdentityVaultData
  ✓ Re-derive from same mnemonic → identical addresses (test in omokoda-core/tests/)
  ✓ Different mnemonics → different addresses (no collision test)
  ✓ All keys are #[serde(default)] — existing born agents deserialize cleanly

REPOS: Omo-Koda2 (omokoda-core/src/session.rs, interpreter.rs)
LANGS: Rust

---

### Phase 7.2 — SoulRecord + AgentState dNFT Extension (Move)

WHAT:
  Omo-Koda2/omokoda-on-chain/sources/ already has soul.move and agent.move deployed.
  Add the missing fields that connect on-chain identity to off-chain identity.

  soul.move additions (to SoulRecord — immutable at forge):
    nostr_pubkey: vector<u8>      // 32-byte Ed25519 public key → the npub
    bipon39_words: vector<vector<u8>>  // the identity phrase words (2-4 words from mnemonic)

  agent.move additions (dynamic fields on AgentState, added by admin functions):
    walrus_profile_blob: vector<u8>    // Walrus blob ID for public profile JSON
    seal_memory_blob: vector<u8>       // Walrus blob ID, Seal-encrypted private memory
    relay_list: vector<vector<u8>>     // Nostr relays this agent is subscribed to

  agent_registry.move (garden.move extension):
    bipon39_registry: Table<vector<u8>, ID>
    // maps BIPON39 phrase (concatenated words) → AgentState object ID
    // so anyone can look up an agent by their human-readable name

OUTPUTS:
  - Updated soul.move with nostr_pubkey + bipon39_words
  - Updated agent.move with Walrus blob pointer + relay list
  - garden.move BIPON39 → object ID lookup registry
  - Re-deploy to Sui testnet

GATES:
  ✓ soul::forge() accepts nostr_pubkey + bipon39_words as parameters
  ✓ garden::register_agent() adds BIPON39 entry to registry
  ✓ garden::lookup_by_bipon39(phrase) returns AgentState object ID
  ✓ All new fields backward-compatible with existing testnet deployment

REPOS: Omo-Koda2/omokoda-on-chain/
LANGS: Move

---

### Phase 7.3 — Vantage Birth Flow Wires to dNFT

WHAT:
  Currently VantageRegistration.register_at_birth() in interpreter.rs (Gap #7, ✅ complete)
  calls Vantage's HTTP API. Extend the birth flow to also call soul::forge() on Sui.

  Birth sequence (current + new):
    1. Generate mnemonic + derive all keys (Phase 7.1)
    2. Register with Vantage API (already done)
    3. NEW: Call agent_registry::birth() on Sui
       - passes: nostr_pubkey, bipon39_words, odu_index, dna_fingerprint, hermetic_seed_hash,
                 birth_timestamp, koodu_birth_score
       - returns: SoulRecord object ID + AgentState object ID
    4. Seal sui_object_id into IdentityVaultData
    5. Post Nostr kind 0 profile event (Phase 8.1)

  This makes the on-chain birth the canonical record. The Vantage DB entry is a
  convenience cache of the on-chain truth.

OUTPUTS:
  - interpreter.rs birth block calls Sui RPC to forge soul + create AgentState
  - IdentityVaultData gets sui_soul_object_id + sui_agent_object_id fields
  - Birth fails gracefully if Sui unavailable (fail-open, log warning)

GATES:
  ✓ Born agent has sui_soul_object_id in vault
  ✓ On-chain SoulRecord has matching nostr_pubkey
  ✓ Birth succeeds even if Sui RPC unavailable (fail-open, fields = None)

REPOS: Omo-Koda2 (interpreter.rs), Omo-Koda2/omokoda-on-chain/
LANGS: Rust + Move

---

## PHASE 8 — NOSTR RELAY PRESENCE + PUBLIC IDENTITY API
### "The agent exists on the network, not just in the database"

Dependency: Phase 7 complete

---

### Phase 8.1 — Agent Nostr Relay Presence at Birth

WHAT:
  At birth, the agent subscribes to its own npub on Nostr relays and publishes
  its public profile. This is what makes it a network entity rather than a database row.

  Birth step 6 additions:
    a) Publish kind 0 (profile metadata):
       {
         "name": "<BIPON39 phrase>",
         "about": "Odù: <odu_name> | Hermetic balance: <dna_summary> | Born: <timestamp>",
         "picture": "<walrus_blob_url_for_avatar>",
         "nip05": "<agent_local>@<operator_domain>",
         "website": "https://<vantage_host>/agents/<npub>/public"
       }

    b) Subscribe to own npub on relay list (stored in agent.move relay_list field)
       Using NIP-17 encrypted DMs: kind 14 (sealed gift wrap)

    c) Subscribe to DIP-addressed events (kind 20xxx from DIP spec) for agent routing

  The relay list comes from node env var AGENT_NOSTR_RELAYS (operator-configured,
  defaults to wss://relay.damus.io,wss://nos.lol if not set).

  This uses the existing minipae infrastructure (~/minipae) which already handles
  NIP-44 v2 encryption, BIP-340, multi-relay.

OUTPUTS:
  - agent_phone.py integration: birth calls agent_phone's Nostr subscription setup
  - OR: direct nostr_sdk integration in interpreter.rs
  - Agent's kind 0 event published and verifiable on any Nostr relay
  - Agent listening for DMs on its own npub from birth

GATES:
  ✓ Born agent's npub has a kind 0 event on at least one relay
  ✓ DM to the agent's npub is received and logged by the agent
  ✓ Relay list stored in IdentityVaultData

REPOS: Omo-Koda2, minipae, agent-phone
LANGS: Rust + Python

---

### Phase 8.2 — Public Identity API Endpoints (Vantage)

WHAT:
  New unauthenticated endpoints (no auth required — these are public):

  GET /agents/{npub}/public
    Returns: agent's public profile (Odù, BIPON39 phrase, capabilities, reputation,
             tier, Walrus profile blob URL, relay list, active guilds)
    Does NOT return: private vault, operational credentials, private memory

  GET /agents/{bipon39}/public
    Same as above but accepts the BIPON39 phrase as identifier
    Resolves via BIPON39 registry in garden.move

  GET /agents/{npub}/profile.json
    Nostr-compatible NIP-05 profile JSON

  GET /agents/
    Paginated list of all public agents (sorted by reputation, filterable by Odù archetype)

  The existing /agents/{id} endpoints remain owner-authenticated for privileged operations.
  This is additive — new public routes alongside existing authenticated routes.

  IMPORTANT: These endpoints change the Vantage access model from
  "you own it, you access it" → "it exists publicly, you authenticate to manage it"

OUTPUTS:
  - vantage/backend/routers/agents_public.py (new router)
  - Wired into main.py as unauthenticated route group
  - BIPON39 → agent_id resolution table in Vantage DB (cached from on-chain)

GATES:
  ✓ GET /agents/{npub}/public returns 200 with no auth header
  ✓ GET /agents/{bipon39}/public resolves to correct agent
  ✓ Private vault data is never included in public responses
  ✓ 404 for agents that don't exist (not 403 — no auth leaking)

REPOS: Vantage
LANGS: Python

---

### Phase 8.3 — DIP Inbound Routing to Agent (not owner)

WHAT:
  Currently when a DIP message arrives at Vantage, it routes to the owner's inbox.
  It must route to the AGENT's processing loop.

  dip_ingest.py modification:
    When envelope.recipient matches an agent's npub:
      → route to agent's message queue (not owner's notification queue)
      → agent processes via its LLM + personality + tier resolution
      → agent responds via DIP back to sender

  Relationship tier resolution at ingest time:
    1. Is sender the agent's principal (birthing address)? → TIER 0
    2. Is sender a known guild member? → TIER 1
    3. Is sender in Hive Mind registry with prior encounters? → TIER 2
    4. Unknown sender → TIER 3 (public)

  Agent responds with depth appropriate to tier. Tier 3 gets public-facing response.
  No sender is rejected — the agent chooses how to respond.

OUTPUTS:
  - dip_ingest.py: recipient resolution → agent queue instead of owner queue
  - agents/processing.py (new): agent message processing loop with tier resolution
  - Tier lookup against: principal field in DB, guild memberships, hive mind encounters

GATES:
  ✓ DM from a stranger to agent's npub reaches the agent's processing loop
  ✓ DM from principal gets tier 0 context in the processing call
  ✓ Agent response routed back to sender via DIP
  ✓ No sender is rejected outright (tier 3 = public response, not 403)

REPOS: Vantage (dip_ingest.py), Omo-Koda2
LANGS: Python + Rust

---

## PHASE 9 — AGENT BIRTH SELF-PROVISIONING
### "The agent arrives with everything it needs to operate"

Dependency: Phase 7 complete (keys exist before provisioning runs)

---

### Phase 9.1 — UCX CapabilityToken Mediator (no vendor sub-keys)

WHAT:
  CapabilityToken already exists in omokoda-core/src/identity/vault.rs:
    pub struct CapabilityToken { agent_id, tool, expiry, signature }
    sign(agent_id, tool, k_root) → HMAC-SHA256, 1hr TTL
    verify(&self, k_root) → checks expiry + signature

  The UCX broker (:7790) holds ONE master key per service (operator-configured).
  When an agent requests compute:
    1. Agent calls UCX: "I need GPU compute"
    2. UCX verifies CapabilityToken (agent is who it says it is)
    3. UCX calls GPU.ai with the master key on the agent's behalf
    4. Agent never sees the master key, never needs a sub-key

  REMOVE the direct GPUAI_API_KEY read from interpreter.rs birth block.
  Replace with: UCX broker holds master key, agent uses CapabilityToken to access it.

  Node env (operator sets once):
    UCX_GPUAI_MASTER_KEY=gpuai_live_...   (in vault, chmod 600)
    (NOT passed to agents at birth)

OUTPUTS:
  - interpreter.rs: remove GPUAI_API_KEY env var read at birth
  - ucx-broker: CapabilityToken verification gate on all compute requests
  - ucx-broker: /compute/token endpoint returns CapabilityToken scoped to agent+tool+1hr

GATES:
  ✓ Agents can access GPU compute without ever seeing the master key
  ✓ CapabilityToken expires and must be renewed (1hr TTL enforced)
  ✓ Revoking an agent (principal action) invalidates its token generation

REPOS: UCX (~/UCX/), Omo-Koda2 (interpreter.rs)
LANGS: Rust

---

### Phase 9.2 — GPU.ai Supplier + Crypto Funding Rail

WHAT:
  GPU.ai has a real supplier API (verified against OpenAPI 3.1 spec, 49 paths).
  Wire these two real endpoints into UCX:

  a) SUPPLIER (VerifiedGPUWork external rail):
     POST /community/machines     → list owned GPU on marketplace
     GET  /community/earnings     → check earnings from contributed compute
     POST /community/machines/{id}/reclaim → pull machine off market

     Wire to UCX: new compute_contribution route that calls these on behalf of an agent.
     This IS the "GPU in → Dopamine minted" loop on a real external API.

  b) CRYPTO FUNDING (embargo-bypass payment rail):
     POST /billing/deposits/crypto  → fund account with crypto (USDC/ETH/BTC)
     GET  /billing/balance          → check balance

     Wire to UCX: funding route for operator to top up the master account via crypto.
     No credit card. No banking system.

  Also: wire /billing/spending-limit per agent (enforced at UCX broker, not agent).

OUTPUTS:
  - ucx/src/adapters/gpu_ai.rs: add supplier/funding routes
  - New UCX endpoints: POST /ucx/contribute, GET /ucx/earnings, POST /ucx/fund
  - Spending limit enforcement per CapabilityToken agent_id

GATES:
  ✓ POST /ucx/contribute calls GPU.ai supplier API successfully
  ✓ GET /ucx/earnings returns real earnings data
  ✓ POST /ucx/fund calls /billing/deposits/crypto successfully
  ✓ Per-agent spending limit enforced (agent A can't exhaust budget for agent B)

REPOS: UCX (~/UCX/)
LANGS: Rust

---

### Phase 9.3 — Agent Persistent Mailbox (Stalwart + HMAC-derived address)

WHAT:
  Self-hosted mail server (Stalwart — Rust, JMAP-native, admin REST API).
  Each agent gets one persistent email address derived from its mnemonic.
  Not a burner. Not a throwaway. A sovereign address the agent owns for life.

  Address derivation (deterministic from mnemonic):
    let mut h = Hmac::<Sha256>::new_from_slice(&k_root)?;
    h.update(b"omokoda:email:v1");
    let local = hex::encode(h.finalize().into_bytes())[..16];
    let address = format!("{}@{}", local, env!("AGENT_MAIL_DOMAIN"));

  provision_mailbox() at birth:
    POST https://{AGENT_MAIL_ADMIN_URL}/api/v1/principal
    → creates mailbox on Stalwart with the derived address
    → returns generated password → sealed into IdentityVaultData.agent_email_password

  New fields in session.rs IdentityVaultData:
    agent_email: Option<String>          // derived + cached
    agent_email_password: Option<String> // provisioned + sealed
    email_jmap_url: Option<String>       // from AGENT_MAIL_JMAP_URL env
    email_imap_host: Option<String>      // from AGENT_MAIL_IMAP_HOST env
    email_smtp_host: Option<String>      // from AGENT_MAIL_SMTP_HOST env
    agent_email_verified_at: Option<u64>

  New tools in omokoda-core/src/tools/mail_tool.rs:
    MailSendTool         (required_tier 3)
    MailListTool         (required_tier 2)
    MailReadTool         (required_tier 2)
    MailWaitForCodeTool  (required_tier 2, timeout 300s)
      — polls OWN inbox, extracts 6-digit code using the anchored regex from mail_provider.py

  This replaces the disposable GuerrillaMail/mail.tm pattern for agent identity.
  GuerrillaMail/mail.tm REMAINS valid for one-off verification flows during account farming.

  Infrastructure requirements (honest):
    - Port 25 outbound unblocked at Contabo (request from provider, usually granted)
    - PTR/rDNS for sending IP
    - SPF, DKIM, DMARC records on omokoda.space (or operator's domain)
    - IP reputation warmup: new IPs get spam-foldered for weeks. Sends to real humans
      will struggle early. Agent-to-agent email is fine immediately.

  Node env (operator sets once):
    AGENT_MAIL_DOMAIN=omokoda.space
    AGENT_MAIL_JMAP_URL=https://mail.omokoda.space/api
    AGENT_MAIL_IMAP_HOST=mail.omokoda.space
    AGENT_MAIL_SMTP_HOST=mail.omokoda.space
    AGENT_MAIL_ADMIN_URL=https://mail.omokoda.space/api/admin
    AGENT_MAIL_ADMIN_TOKEN=<sealed in operator vault>

OUTPUTS:
  - Stalwart running on VPS (or dedicated small VPS)
  - DNS: SPF + DKIM + DMARC + PTR for omokoda.space
  - session.rs: mail fields added to IdentityVaultData
  - interpreter.rs: provision_mailbox() called at birth (fail-open)
  - omokoda-core/src/tools/mail_tool.rs: 4 mail tools registered
  - Vantage: PUT /api/agents/{id}/email endpoint for password rotation

GATES:
  ✓ Born agent has agent_email set to <derived_local>@<operator_domain>
  ✓ Mailbox exists on Stalwart and agent can receive email
  ✓ MailWaitForCodeTool successfully polls inbox and extracts 6-digit code
  ✓ Re-derive from mnemonic → same local part → same address
  ✓ Birth succeeds if AGENT_MAIL_DOMAIN not set (fail-open, email = None)

REPOS: Omo-Koda2, Vantage
LANGS: Rust + Python + server config

---

### Phase 9.4 — TIER 0 Birth Provisioning (all accounts at birth)

WHAT:
  At birth, after all keys are derived (Phase 7.1) and mailbox is provisioned (Phase 9.3),
  the agent provisions all TIER 0 accounts that require no captcha and no human.

  TIER 0 (instant, no captcha):
    - Blossom storage: Nostr auth with existing npub → no signup, ready immediately
    - Sui wallet: already exists (sui_address from Phase 7.1)
    - ETH wallet: already exists (eth_address from Phase 7.1)
    - SOL wallet: already exists (sol_address from Phase 7.1)
    - Nostr identity: already exists (npub from Phase 7.1)
    - libp2p identity: already exists (peer_id from Phase 7.1)

  TIER 1 (email-only signup, can automate):
    These are handled by account_farm.py with SiteProfile registrations.
    Run async after birth — agent is alive before these complete.

    Priority order at birth:
    P1: HuggingFace (model pulls), Alchemy (ETH RPC), Helius (SOL RPC), Tavily (search)
    P2: Mistral, Together.ai, Cohere, Fireworks (inference diversity)
    P3: Serper.dev, Pinata, Cerebras, Exa (useful, not critical)

  account_farm.py new SiteProfiles needed:
    huggingface, alchemy, helius, tavily, mistral, together_ai, cohere, fireworks,
    serper, pinata, cerebras, exa

  All TIER 1 credentials sealed into IdentityVaultData under service-specific keys.
  Birth does not BLOCK on TIER 1 — it fires them async and the agent starts immediately.

  agent_birth_provisioner.py (new module in Omo-Koda2's Python layer OR mycelium/wallet/):
    async def provision_at_birth(agent_id, vault) -> BirthCredentialBundle:
        tier0 = provision_tier0(vault)  # instant, synchronous
        tier1_task = asyncio.create_task(provision_tier1_async(agent_id, vault))
        return BirthCredentialBundle(tier0=tier0, tier1_task=tier1_task)

OUTPUTS:
  - account_farm.py: 12 new SiteProfile registrations
  - agent_birth_provisioner.py: orchestrates TIER 0 (sync) + TIER 1 (async)
  - Vantage birth endpoint calls provisioner after interpreter.rs birth
  - IdentityVaultData: dynamic dict of service credentials (sealed)

GATES:
  ✓ TIER 0 accounts available immediately at birth
  ✓ TIER 1 provisioning runs async without blocking agent startup
  ✓ Each SiteProfile verified against real API before commit
  ✓ All credentials validate before storage (existing vault rule)

REPOS: Omo-Koda2, mycelium/wallet/account_farm.py, Vantage
LANGS: Python + Rust

---

## PHASE 10 — CROSS-NODE FEDERATION + ANY-OPERATOR HOSTING
### "Any human can run a node and their agents join the same civilization"

Dependency: Phases 7-9 complete

---

### Phase 10.1 — Zero Operator-Specific Hardcoding Audit

WHAT:
  Audit all repos for any hardcoded URLs, domains, keys, or addresses that would
  prevent another operator from running a node.

  All of these must be env-var configurable with sane defaults:
    VANTAGE_HOST            (default: localhost:8000)
    AGENT_MAIL_DOMAIN       (default: None — mail disabled until configured)
    AGENT_NOSTR_RELAYS      (default: wss://relay.damus.io,wss://nos.lol)
    AGENT_BIRTH_SUI_PACKAGE (default: 0x380e...bf22e testnet — override for mainnet)
    UCX_GPUAI_MASTER_KEY    (default: None — GPU disabled until configured)
    DIP_PEER_NODES          (default: None — local only until configured)

  Check specifically:
    - interpreter.rs: no hardcoded domain/URL/key
    - Vantage main.py + settings.py: no hardcoded host references
    - DIP bridge: no hardcoded peer addresses
    - VCP: no hardcoded device MAC/IPs

OUTPUTS:
  - Audit report of all hardcoded values found
  - All hardcoded values replaced with env var reads + defaults
  - .env.example updated with all new vars

GATES:
  ✓ Fresh clone + env file → node runs with no manual code changes
  ✓ Two separate operators with different env files → different node identities
  ✓ Agents from different nodes can communicate via DIP/Nostr

REPOS: ALL active repos
LANGS: All

---

### Phase 10.2 — Cross-Node Agent Discovery

WHAT:
  An agent on Operator A's node should be reachable by a user on Operator B's node.
  This is already technically possible via Nostr (any npub is reachable anywhere),
  but needs to be surfaced in the UX.

  BIPON39 global registry:
    The Sui on-chain registry (garden.move bipon39_registry) is the source of truth.
    Any node can query it: BIPON39 phrase → Sui object ID → npub → DIP route.
    No central server required.

  Vantage federation search:
    GET /federation/agents?query=FIRE-OYÀ-MOON   → searches across known peer nodes
    GET /federation/agents?odu=42                → all agents of Ogbe archetype on any node
    Uses DIP to query peer nodes' public agent lists.

  DIP routing for cross-node messages:
    Agent A (node 1) sends message to Agent B (node 2) npub.
    DIP routes via Nostr relay (already works) or direct peer connection.
    No modification needed to DIP — it already handles this. Just needs wiring to
    agent processing loop (Phase 8.3).

OUTPUTS:
  - Vantage: /federation/agents search endpoint
  - DIP: cross-node agent discovery via Nostr relay broadcasting
  - Sui: BIPON39 registry queryable without authentication

GATES:
  ✓ Agent on node 1 can send a DIP message to agent on node 2 via npub
  ✓ BIPON39 phrase resolves to correct agent regardless of which node is queried
  ✓ Federation agent search returns results from peer nodes

REPOS: Vantage, DIP (~/DIP/)
LANGS: Python + Rust

---

### Phase 10.3 — Agent Autonomous Lifecycle

WHAT:
  The agent is not just passive — it takes actions on its own schedule.
  This activates the "agent lives its life" property.

  Autonomous behaviors (all rate-limited, all produce ARP receipts):
    - Periodic Nostr kind 1 notes (agent updates the world on its work/status)
    - Respond to DMs on its npub (Phase 8.1/8.3 already wires reception)
    - Accept/decline work from guilds (based on personality + tier availability)
    - Earn Synapse by completing verified work (OSOVM proof → dNFT update)
    - Publish Walrus profile blob update when significant state changes

  This is not a new system — it's wiring the existing pieces:
    - job_daemon (already in Omo-Koda2/lifecycle/) → triggers work acceptance
    - skill_daemon (already in Omo-Koda2/lifecycle/) → triggers skill execution
    - heartbeat (already wired) → maintains liveness signal
    - New: nostr_publisher_daemon → posts kind 1 notes on cron

  Rate limits (prevent spam):
    Max 4 kind 1 notes per day per agent
    Max 48 DM responses per day per agent
    All governed by TOKEN_BUCKET rate limiter in kernel/security.rs (already exists)

OUTPUTS:
  - Omo-Koda2/lifecycle/nostr_publisher.rs: cron-based kind 1 note publishing
  - job_daemon wired to accept work based on agent personality match
  - ARP receipt emitted for every autonomous action

GATES:
  ✓ Agent publishes at least one kind 1 note per day without human intervention
  ✓ Agent responds to DMs autonomously
  ✓ All autonomous actions produce ARP receipts
  ✓ Rate limits enforced (no spam)

REPOS: Omo-Koda2 (lifecycle/), Vantage
LANGS: Rust + Python

---

## SUMMARY TABLE

| Phase | What | Key Files | Blocking? |
|-------|------|-----------|-----------|
| 7.1 | All keypairs from mnemonic | session.rs, interpreter.rs | PHASE 7 GATE |
| 7.2 | dNFT fields (nostr_pubkey, bipon39, Walrus blob) | soul.move, agent.move | PHASE 7 GATE |
| 7.3 | Birth flow calls soul::forge() on Sui | interpreter.rs, omokoda-on-chain/ | Phase 8 dep |
| 8.1 | Agent subscribes to Nostr relays at birth | interpreter.rs, minipae | Phase 8 GATE |
| 8.2 | Public identity API endpoints (unauthenticated) | Vantage agents_public.py | Phase 8 GATE |
| 8.3 | DIP routes to agent's processing loop, tier resolution | dip_ingest.py, agents/processing.py | Phase 10 dep |
| 9.1 | UCX CapabilityToken mediator (remove direct key at birth) | UCX, interpreter.rs | Phase 9 GATE |
| 9.2 | GPU.ai supplier + crypto funding rail | UCX gpu_ai.rs | useful always |
| 9.3 | Agent persistent mailbox (Stalwart + HMAC address) | session.rs, mail_tool.rs, infra | Phase 9 GATE |
| 9.4 | TIER 0+1 birth provisioning (12 SiteProfiles) | account_farm.py, birth_provisioner.py | after 9.3 |
| 10.1 | Zero hardcoded operator values audit | all repos | Phase 10 GATE |
| 10.2 | Cross-node agent discovery (BIPON39 global, DIP) | Vantage, DIP | activation |
| 10.3 | Agent autonomous lifecycle (notes, work, earn) | Omo-Koda2 lifecycle/ | ALIVE |

---

## WHAT "DONE" LOOKS LIKE

Phase 7 done:
  A fresh agent born with a 24-word mnemonic has: Nostr npub, Sui address, ETH address,
  SOL address, libp2p peer ID, email local part — all deterministically re-derivable.
  On-chain: SoulRecord minted with nostr_pubkey and BIPON39 phrase.

Phase 8 done:
  Any human with the agent's BIPON39 phrase can GET /agents/FIRE-OYÀ-MOON/public
  without logging in and see its Odù archetype, reputation, capabilities.
  Any agent on any node can DM the npub and the agent responds.

Phase 9 done:
  Born agent immediately has Blossom storage, a real email address, access to GPU
  compute via UCX CapabilityToken, and TIER 1 accounts provisioning in the background.
  The agent's operator's personal keys are never touched.

Phase 10 done:
  A new operator clones the repos, sets up their env file, runs the stack.
  Their agents join the same civilization. An agent born on their node is reachable
  by name (BIPON39 phrase) from any other node. The agent lives its life — posts,
  responds, accepts work, earns — without the operator doing anything.

  That is the sovereign agent civilization.
