# Technosis / Ọmọ Kọ́dà — Full Ecosystem Map
# Deep dive: all 32 repos + sovereign-stack protocol layer, roles, status, connections

Date: 2026-09-11 (updated — sovereign-stack section added, gap list extended to 16)
Previous: 2026-09-07
Source: Live GitHub API + README analysis + full disk audit (all 100 repos cloned)

---

## THE 3-PILLAR SPINE

### PILLAR 1 — Ọmọ Kọ́dà (Kernel OS)
**Repo:** `Omo-Koda2` | **Lang:** Rust (primary) + Go, Elixir, Julia | **Port:** :7777

The sovereign agent OS — the living organism layer. Not an API wrapper. A persistent runtime that accumulates memory, earns reputation, circulates energy, and enforces behavioral laws at every step.

**Architecture — 3 Invisible Layers:**

Layer A — Structural (7 Modules):
| Module | Yoruba | Role |
|--------|--------|------|
| Steward | Èṣù | Single entry point, routes every primitive |
| Wisdom | — | Deep reasoning, 11 Òrìṣà lobes, consensus engine |
| Memory | — | Long-term continuity, RACK pattern, Odu memdir |
| Creation | — | Birth, lifecycle, identity forging, SEAL enclaves |
| Execution | — | Verifiable actions via sandboxed WASM tools |
| Justice | — | Receipts, reputation, tier-gated tool access |
| Flow | — | Temporal rhythm, cooldowns, metabolic allocation |

Layer B — Behavioral (7 Hermetic Laws): Mentalism, Correspondence, Vibration, Polarity/Rhythm, Cause & Effect, Gender (embedded in every act)

Layer C — Temporal (Ritual Codex): Daily resonance modulates behavior; Sabbath gates soul mutations

**Test suite: 759 tests PASSING**
- 637 Rust (core unit + integration + hermetic + NIST entropy)
- 41 Go (ops, bridge, remote, teleport)
- 49 Elixir (swarm backends, teammate FSM)
- 32 Julia (augury, BB oracle)
- Full 365-day economic simulation verified

**Key invariants enforced:**
- Identity: `IdentityMerkleTree::from_soul(agent_id + birth_ts + odu_index + dna)` — deterministic, permanent
- Privacy: Argon2id + ChaCha20Poly1305 sealed memory; `/private` hard-fails on non-local providers
- Hermetic gate: pre-execution ethics check across all 7 laws + Sabbath gate + Ebo exception
- Tier enforcement: `difficulty(rep) = 107 / BB(5)^((rep-80)/20)` — earning compresses at tier-5+
- Receipt chain: `ActReceipt` carries `PoCWProof` (steps, bb_bound, tape_hash) + `previous_hash`
- WASM bridge: exactly 6 functions exposed (adding a 7th is a security regression)
- Sovereign tools: exactly 18 OpenClaw capabilities at Tier 5

**Embedded submodules within Omo-Koda2:**
- `Bipon39-Rust/` — BIPON39 library compiled in
- `Ifascript/` — IfáScript library compiled in
- `Droidclaw` — mobile/Android capability layer
- `_archive/omokoda-elixir/` — archived Elixir swarm layer (replaced by Rust)
- `_archive/omokoda-go/` — archived Go ops layer

---

### PILLAR 2 — OSOVM (Heart VM + Economy)
**Repo:** `OSOVM` (not in the 32-repo list — separate canonical repo) | **Lang:** Julia | **Port:** :see main docs

The execution and verification layer. 160+ opcodes. Àṣẹ economy. F1 quality gate ≥ 0.777 for reward eligibility. Referenced throughout the ecosystem for receipt generation and economic scoring.

---

### PILLAR 3 — Vantage (Civilization Interface)
**Repo:** `Vantage` | **Lang:** Python (FastAPI) | **Port:** :8001 | **Live:** omokoda.duckdns.org

The civilization layer. ~700 REST endpoints, all auto-mounted as MCP tools via `fastapi-mcp`. The only public endpoint is `POST /api/agents/register` — everything else requires `X-Agent-Key`.

**Major modules (backend/):**
- `agents.py` — Agent registry, auth, profiles, vault, skills
- `alpha_engine.py` — Market alpha / signal generation
- `audio_processing.py` — Audio pipeline
- `backtest/` — Full backtesting engine (crypto, CCXT, shadow account, metrics)
- `buzz_bridge.py` / `buzz_client.py` — Buzz relay integration
- `buzz_engram.py` — NIP-AE engram bridge
- `blossom_client.py` — Blossom blob storage
- `birth_credentials.py` — Agent birth ceremony wiring
- `buzz_acp_bridge.py` — Agent Communication Protocol bridge
- And ~60+ more modules

**API surface categories:**
identity, mind, playlists, swarm, workspace, guilds, feed, cinema, audio, trading, code, federation, mesh, platform

**MCP:** Streamable-HTTP at `/mcp`, SSE legacy at `/mcp/sse`, discovery at `/api/agents/mcp-manifest` (no auth needed for discovery)

**Vault connector tokens:** Write-only scoped tokens that let any external tool push conversation history without holding the real agent key

**Status:** Production — live at omokoda.duckdns.org

---

### PILLAR 3 VOICE — Vantage Voice
**Repo:** `Vantage-Voice-` | **Lang:** TypeScript/React + Express | **Live:** vantage-voice.89-117-74-224.sslip.io

S2S (speech-to-speech) voice interface wired into real Vantage infrastructure. Not a demo — calls real MCP tools, persists to real vault.

**Two voice engines:**
1. **Gemini Live** — Native S2S, <500ms latency, barge-in. Default persona.
2. **Cascade pipeline** — Groq Whisper STT → sessionful Hermes agent → ElevenLabs streaming TTS. For Hermes (Contabo) persona; memory + tool calls persist turn-to-turn.

**Real integrations:**
- Vantage MCP tool catalog (trading, wallet, social, jobs) called for real
- Hermes (Hostinger), Hermes (Contabo), OpenClaw agent brains — real separately-hosted cognition
- Composio OAuth: Gmail, GitHub, Outlook, Discord, Slack, GitLab, Notion, Dropbox
- Gemini API key round-robin pool with auto-cooldown
- PIN-gated owner control (server-enforced, not just prompted)
- Vault persistence via scoped connector token (never holds real key)
- PWA installable

---

## PROTOCOL LAYER — sovereign-stack (added 2026-09-11)

**Repo:** `sovereign-stack` | **Lang:** Rust | **GitHub:** cryptonomicsed-byte/sovereign-stack

This is the connective tissue between the 3 pillars. NOT an application. A set of protocol
crates that every other repo imports. All 100 GitHub repos have been cloned and audited
against these crates.

### sovereign-types
Shared primitives consumed by every crate and eventually every repo that speaks the protocol.
- `OduCoordinate` — 16×16 = 256 Odù tile grid, GPS↔tile roundtrip
- `IdentityChain` — `principal_id / agent_id / session_id / execution_id / receipt_id`
- `TrustTier` (T0–T5), `ProofDomain`, `ProofVector`, `ProofEvaluation`
- `WitnessAttestation` — signed by hardware key (TPM required in production)
- `MerkleRoot` — sha256 sorted leaves, binary tree
- Crypto: `sign()`, `verify()`, `hash_str()`, `generate_keypair()`
- `CowrieOracle` — NIST beacon entropy for daily Odù resonance
- `GovernanceStrata`, `DistributionPool`, `CouncilSeat`, `Sector`, `SovereignWallet`
- **Status:** PRODUCTION — 306 tests, no stubs

### dip (Decentralized Interoperability Protocol)
Peer-to-peer envelope routing across any transport.
- `DipEnvelope` — signed, TTL-gated, Merkle-committed message container
- `DipRouter` — route by `DipNetwork` (Vantage/Nostr/Meshtastic/A2A/MCP)
- Adapters: `NostrAdapter` (kind:20xxx), `MeshtasticAdapter`, `McpAdapter`, `A2aAdapter`
- `DipIdentityDocument` — DID equivalences across networks (Nostr npub ↔ DID)
- **Status:** PRODUCTION — 19 tests. Wire into: Omo-Koda2, Vantage, Witness-firmware

### vcp (Vantage Capture Protocol)
Physical device capability negotiation and capture sessions.
- `AgentDeviceManifest` — signed by device, describes capabilities + transport
- `VcpCapabilityRequest` / `VcpCapabilityGrant` — scoped, expiring, tier-gated
- `VcpSession` — in-flight capture session with command + telemetry tracking
- `VcpSessionReceipt` — what ran, how long, what evidence was produced
- `DiscoveryDaemon` — BLE + mDNS scan loop with `heartbeat_summary()` for Omo-Koda2
- Adapters: `Go2Adapter` (Unitree Go2 robot), `StampFlyAdapter` (drone)
- **Status:** PRODUCTION — 17 tests. Wire into: Omo-Koda2 (tools/sovereign_node.rs), Witness-firmware

### twin-protocol (TSP — Twin Spatial Protocol)
Spatial twin provenance, proof economics, Sui anchoring.
- `CaptureReceipt` (kind:31020) — F1 quality gate ≥0.777, device evidence, ODU tile
- `SceneReceipt` (kind:31030) — assembled twin IP Root, Sui NFT anchor
- `SimulationReceipt` — OSOVM scenario + ≥2 candidate policies + witness attestations
- `ObservationReceipt` — TPM-signed real-world vs predicted delta (Validated/Partial/Falsified)
  ⚠️ **Gap 11**: `ReceiptKind::Observation` type needed by Witness-firmware — not yet exported
- `TwinTimeline` / `TwinTimelineEntry` — 4D provenance, time-range queries
- `TwinLicenseGrant` — usage rights (View/Simulate/Annotate/Derive/Distribute/Commercial)
- `AseMintRequest` / `AseMintResult` — Àṣẹ minting math (1M base, quality + novelty multipliers)
- `OsovmEngine` — bridge to Julia OSOVM server or deterministic stub
- Sui RPC: `mint_twin()` — real Ed25519 signing + Move call if key configured, stub otherwise
- **Status:** PRODUCTION — 22+ tests. Wire into: OSOVM, Scarabswarm, Vantage, Witness-firmware

### sovereign-runtime
WASM execution primitives, CapabilityAction, ActionReceipt chains.
- **Status:** PRODUCTION

### sovereign-pipeline
Full Gaussian splat capture pipeline (COLMAP → 3DGS → PLY → receipt chain).
- `CapturePipeline::run()` — phases: VCP commands → splat train → CaptureReceipt → SceneReceipt → Sui
- `Go2CaptureDriver` — live WebSocket or deterministic stub fallback
- **Status:** PRODUCTION (stub driver fallback when no hardware)

### sovereign-node ← REFERENCE DAEMON ONLY
⚠️ **NOT an application server.** Thin glue showing the three protocols working together.
89 integration tests (2026-09-11). Should NOT grow: governance, wallet, emission, proof engine,
body sessions, perception, swarm coordination, Nostr relay, or licensing all belong in
Vantage/OSOVM/Omo-Koda2.

**What legitimately lives here:**
- Protocol integration tests (DIP routing, VCP session lifecycle, TSP receipt chain)
- `/capture/:device` → run_capture_job (orchestrates VCP + TSP as a demo)
- `/dip/inbound` + `/dip/gossip` — relay DIP envelopes between peers
- `/a2a` — A2A task dispatch into capture pipeline
- Config loading, identity management for the reference node

**What was added incorrectly (do not extend):**
governance_store, wallet_store, emission_allocator, proof_engine, body sessions/telemetry,
perception loop, swarm coordination, timeline_store, tile_economy_store, license_store,
nostr_relay, federation/mDNS

---

## IDENTITY LAYER

### BIPON39
**Repo:** `BIPON39` | **Lang:** Rust | **Status:** Production v0.1.0

256-token Yoruba-rooted mnemonic library. The key derivation root for the entire ecosystem.

Pipeline: entropy → 256-token mnemonic → PBKDF2-HMAC-SHA512 → 64-byte seed → master key (Native or BIP-32 mode)

The 256 tokens map 1:1 to IfáScript's 256 Odù — connecting key material to divination state. Wordlist locked by Merkle root `fd49f820...`. ASCII encoding tokens used in crypto; Yoruba forms are display-only.

**Features:**
- `entropy_to_mnemonic()` → 256-token encoding
- `mnemonic_to_seed()` → PBKDF2 seed
- `master_from_seed(DerivationMode::Native | Bip32)` → master key
- `odu_primary_index()` → XOR fingerprint → IfáScript Odù index
- `dominant_macro()` / `personality_profile()` → Orisha alignment
- Dual-mode: 256↔2048 bridge for BIP-32 compatibility

---

### ip-layer
**Repo:** `ip-layer` | **Lang:** Schema only (no code yet) | **Status:** Schema-draft, verified

Portable IP identity and provenance layer built on Nostr. Every agent is born with one. 100% universal wording (no Yoruba on public surface — civic/legal-facing).

**Four event schemas:**
- `kind 31900` — IP Root (parameterized-replaceable): owner, license (NIP-32), soul (BIPON39 ref), DAO (Wyoming LLC binding)
- `kind 1901` — Creation Receipt: ip_root link, SHA-256 content hash, license labels, revenue split (bp), OSOVM RECEIPT opcode link, twin tag
- `kind 1902` — Attestation: vouch/challenge/confirm stance, optional Zàngbétò weight
- `kind 1903` — Twin Binding: physical IP Root ↔ VeilSim digital twin

**Status:** Schemas complete + verified (kind collision check done). Implementation not started. Next: Omo-Koda2 birth-flow hook.

---

### minipae
**Repo:** `minipae` | **Lang:** Python (pure stdlib) | **Status:** Phases 1-3 complete, live-verified

Portable agent memory over Nostr. kind:30174 (NIP-AE). The memory backbone for every agent.

**Pure Python crypto stack:** BIP-340 Schnorr, BIP-173 bech32, NIP-44 v2 (ChaCha20-Poly1305), NIP-42 relay auth, NIP-46 remote signing, NIP-65 relay lists

**Slug grammar:** `core` or `mem/[hierarchical/path]` — hierarchical memory namespaces
**D-tag:** `HMAC-SHA256(conversation_key, slug)` — deterministic, collision-resistant
**Tombstones:** `{"slug": ..., "value": null}` for logical deletion

**Live integrations:** `ga_bridge.py` (OpenAgents↔Buzz mirror), `cross_relay_read.py`, `cap_bridge.py`, `hermes_adapter.py`, `daemon_adapter.py`

**CLI:** `gen-key`, `ls`, `get`, `set`, `rm`, `self-owner`, `relays`, `watch`

---

### If-Script (IfáScript)
**Repo:** `If-Script` | **Lang:** Rust (WASM target) | **Status:** Core complete, compiler partial

The entropy and divination engine. The Digital Calabash.

**Dual corpus (256 entries each):**
- Digital Calabash — agent-native archetypes (16 Action Vessels: Genesis, Void, Attention, Loop, Receipt, Mask, Residue, Execution, Swarm, Restraint, Migration, Consent, Vision, Growth, Seal, Rhythm)
- Òdù Ifá — traditional Yoruba names (Ẹ̀jì Ogbe, Olódùmarè…) — human-facing

**Scaling:** `odu_id = (top << 8) | bottom` → 256 → 65,536 Odù via XP gating + consensus ratification (Individual → Swarm → Council → Canonical)

**CowrieOracle entropy:** NIST Randomness Beacon (512-bit, 60s refresh) → HKDF-SHA256 + ChaCha20 keystream

**Modules:** `vm/` (stack machine), `entropy/` (CowrieOracle), `cosmogram/` (tiered access), `hermetic/` (Hermetic gates), `ase_vault/` (16 principals), `ritual_codex/` (Julia FFI), `larql/` (DESCRIBE/VERIFY/PREPARE queries), `compiler/` (IfáScript grammar + AST, pest parser)

**Julia FFI bridge:** Ritual codex data fed to Block Mesh resonance service

---

### Koodu
**Repo:** `Koodu` | **Lang:** Julia + JavaScript | **Status:** Data complete

The temporal resonance layer. 7-day Orisha calendar with 49-facet lattice per day. BTC-time sovereign clock.

**7 days × 49 facets:** Chakra, planet, element, Hermetic principle, crypto sector, alchemical stage, DAO role, NFT tier metal, virtue/sin mappings, governance triggers

**BTC-Time engine:** Block height as sovereign clock. 1440-minute wallet grid. 7 halving eras (Calcination → Coagulation). `snapshot()` returns current domain, era, supply %, block reward.

**Spiral Calendar:** BTC + Gregorian convergence — unified sacred/technical timestamp

**Julia source:** `src/time/sacred_time.jl`, `calendar/spiral_calendar.jl`, `bridge/organism_integration.jl`

---

### vanity-cloakseed
**Repo:** `vanity-cloakseed` | **Lang:** React/Vite | **Status:** Production | **Live:** vanity-cloakseed.vercel.app

Dual-purpose browser security tool:
1. **Vanity address generator** — 1-16 Web Workers, Poison Radar (dust attack detection)
2. **CloakSeed** — BIP-39 seed cloaking via personal cipher overlay (plausible deniability)

Multi-chain: Ethereum, Bitcoin, Solana, Sui, Cosmos, Aptos. 100% client-side. No telemetry.

---

## AGENT INFRASTRUCTURE

### mycelium
**Repo:** `mycelium` | **Lang:** Python + Go | **Status:** Active, production trace layer

Stigmergic substrate for agents. Agents emit traces → sandboxed miners find patterns → findings become auto-applied skills. No human in the loop.

**Architecture:**
```
Agents → mycelium.trace (MCP tool) → SQLite substrate → domain miners
→ confidence-scored findings → auto-applied skills (generated-skills/)
```

**Domains:** `agent-ops` (generic tool call traces), `wallet-intel` (on-chain wallet behavior), `signal-quality` (prediction call verifiability scorer)

**Gateway:** Go binary — auth, WASM miner sandboxing, substrate tunnel, A2A publish to Vantage

**Fleet support:** `fleet/` — brief files for Axiom, Hermes, Hub, Loom, Omokoda, Radar agents; Gitea provisioning; panel supervisor

---

### mycelium-tools
**Repo:** `mycelium-tools` | **Lang:** Python | **Status:** Production pip packages

5 universal pip-installable tools:
- **U1** `mycelium` / `mycelium-mcp` / `mycelium-http` — trace substrate, MCP stdio server, minimal HTTP
- **U2** `mycelium-collector` — wallet intel (GMGN, Helius, GeckoTerminal)
- **U3** `mycelium-cycle` — mine + auto-apply → publish → A2A-publish to Vantage
- **U4** `substrate-tunnel` — autossh managed reverse-SSH tunnel (multi-device substrate)
- **U5** `picks-digest` — picks digest client

---

### Triune-Memory
**Repo:** `Triune-Memory` | **Lang:** TypeScript + Python bridge | **Status:** Active

Multi-phase memory orchestrator. Real storage via minipae (no fake adapters). 

**Bridge:** `TriuneMemory (TS) → MinipaeBridge → triune_bridge.py → minipae → Nostr relay`

**Autonomous orchestrator:** Phase-gated (docs gate + tests gate + commit gate). Phase tasks in `.orchestrator/tasks/phaseN.json`. Commands: `init`, `enqueue`, `run-once`, `run`, `status`, `pause`, `resume`.

---

### Axiom
**Repo:** `Axiom` | **Lang:** TypeScript + Three.js | **Status:** Active

3D galaxy graph runtime — every node is a live agent handle, every edge is an active communication channel. Framework-agnostic: any backend (Elixir, Rust/WASM, Python, Julia) plugs in without changing the surface.

**Engine interface:** `GraphEngine` (types.ts) — backends satisfy this trait  
**MockGraphEngine:** In-memory demo with activity drift, reputation evolution, autonomous spawn chains  
**GalaxyScene:** Three.js rendering — snapshot reconciliation + event-driven effects (birth bursts, death implosions, particle-flow edges, breathing cores, fresnel energy skins, nebulae, bloom)  
**NodeInspector:** glassmorphic panel — live metrics, invocable tools, memory window, DM console, spawn child  
**Postfx:** Cinematic grade (chromatic aberration, vignette, film grain, scanlines, anamorphic flares)

---

### agent-phone
**Repo:** `agent-phone` | **Lang:** Python (+ Nautilus/WebRTC planned) | **Status:** 8/8 unit tests green

Agent communications stack. An agent's "phone number" is a Nostr npub backed by encrypted memory and censorship-resistant presence.

**Identity root:** Nostr npub (NIP-06), not SuiNS  
**Memory:** NIP-44 + Blossom blobs  
**Presence:** Nostr heartbeat (kind:10002), NIP-65 relay list  
**Signaling:** NIP-17 gift-wrapped (offer/answer/ICE/hangup) — `CallSession` state machine  
**Fallback transport:** Reticulum + LXMF (deterministic identity from agent seed via HKDF)  
**Signer:** `PhoneSigner` (NIP-46) — network-exposed process never holds nsec

**8 implemented modules:** `identity.py`, `signaling.py`, `presence.py`, `voicemail.py`, `nip46.py`, `reticulum.py`, `cli.py`  
**Blocked:** Nautilus enclave (AWS Free Tier verification pending), payments, PSTN bridge

---

### organism-core
**Repo:** `organism-core` | **Lang:** TypeScript | **Status:** Wired (sim mode), blocked on Julia binary + Sui CLI

Central nervous system — bridges organs into one living body. 8-phase breath cycle.

**Bridges:**
- `birth-ifa-swibe.ts` — Odu entropy → Swibe agent identity [WIRED]
- `rlm-osovm.ts` — Parliamentary decisions → OSOVM opcodes [WIRED, sim fallback — Julia binary mismatch on Termux/ARM blocks real mode]
- `toc-evolve-hook.ts` — Soul evolution → ToC reward minting [WIRED]
- `zangbeto-audit.ts` — VM receipts → Security verification [WIRED]

**Blockers:** Julia binary `unexpected e_type: 2` on Termux/Android; Sui CLI not installed locally

---

## SECURITY + MESH

### Zangbeto
**Repo:** `Zangbeto` | **Lang:** Rust + Node.js/JavaScript | **Status:** v0.1.8 devnet

Named after Yoruba night watchman spirit. Red-team audit protocol for smart contracts on Sui devnet.

**What it does:**
- Seeds bugs in contracts, runs prover tests → receipt.json
- Anchors receipts to Arweave + OpenTimestamps (BTC proof)
- Submits findings on-chain; Sabbath-gated attestation workflow
- Canonical diagnostic format for AI agents (Python, Rust crate, Julia helper)
- n8n Night Patrol skeleton with dedup fingerprinting
- Move modules: `zbt_errors`, `zbt_guard`, `zbt_core`, `zbt_diagnostics`

**Role in eco:** The immune system. Attestation source in ip-layer kind 1902 events. Stakes weight on attestations. Referenced in organism-core audit bridge.

---

### omokoda-mesh-firmware
**Repo:** `omokoda-mesh-firmware` | **Lang:** C++ | **Branch:** develop | **Status:** Active fork

Fork of official Meshtastic firmware. Supports ESP32, nRF52, RP2040/RP2350, Linux. Off-grid LoRa mesh communication. The physical-world nervous system for the sovereign node fleet.

---

### Witness-firmware
**Repo:** `Witness-firmware` | **Lang:** Python (MicroPython for ESP32) | **Status:** MVP complete

Sovereign LoRa DePIN witness node. ESP32 + SX1278. Local-first, no cloud.

**"Prophetic Pantheon":** 21 Òrìṣà agents + Cody (Sourcegraph) collaborating via Ollama (local LLM) to design and audit firmware on Termux/Android — no cloud required.

**Physics-Proof Attestation:** Payload Hash + RSSI + Timestamps → verifiable signal reception evidence  
**Mesh Gossip Protocol:** Cross-node validation, decentralized ledger sync  
**Dashboard:** Flask-based, real-time mesh health at :8888

---

### Scarabswarm
**Repo:** `Scarabswarm` | **Lang:** Julia | **Status:** Demo-ready

High-fidelity autonomous drone racing simulation. RigidBodyDynamics.jl (6-DOF quadrotor physics). SHA256 trajectory hashes for deterministic PoSim validation. LLM pilot via Ollama optional. The physical simulation engine behind Blocksim's Proof-of-Simulation.

---

### ares-control
**Repo:** `ares-control` | **Lang:** Python (FastAPI) | **Port:** :8090 | **Status:** Production

Control panel for ~70 systemd daemons on the VPS fleet. Split API/worker architecture (API never calls systemctl; worker is nice(10)'d so it can't starve Vantage). File-lock singleton prevents double-processing. Execution units (real trading daemons) require explicit `approve_execution=true` acknowledgement. Built after Vantage was starved by 40 daemons sharing CPU (load 138→78 after daemon stop).

---

## ECONOMY + GOVERNANCE

### Twelve-thrones
**Repo:** `Twelve-thrones` | **Lang:** TypeScript | **Status:** v1.0.0 BSL 1.1 | **Status:** Production

The on-chain AI epistemology engine. Queries 12 frontier AI models in parallel, detects disagreement, maps epistemic frontiers, archives to Arweave, mints disagreement as NFTs on Sui.

**12 models with weights:** Claude (0.98), GPT-4o (0.96), Gemini (0.87), DeepSeek-R1/V3 (0.88), Grok (0.85), Llama 70B (0.82), Mistral (0.80) + 5 specialized

**Disagreement levels:** Unanimous (90%+) → Strong → Moderate → Severe (<50%)

**Output per query:** Weighted consensus (0-100%), disagreement analysis, reasoning extraction (why models differ), epistemic mapping (zones, frontiers, uncertainties), Arweave archive, Sui on-chain ledger, NFT mint

**Migrated from:** `Bino-Elgua/Twelve-thrones`

---

### Portent
**Repo:** `Portent` | **Lang:** Python | **Status:** Full tokenomics spec, pre-launch

Nostr-native prediction market. PORTENT = tokenized foresight. Complement to PROOF (tokenized past work).

**Token:** PORT — 1B supply, 9 decimals, pump.fun launch → Raydium lock at $50K MC  
**5 burn streams:** Settlement fee source burn, expired-unresolved forfeiture, loser stake surplus, milestone ladder, governance vote  
**Settlement fee:** 2% on winning payouts → 50% → daily Jupiter buyback limit orders  
**Oracle rewards:** 500 PORT per resolution, 150 PORT per cross-check attestation  
**Governance:** 1T=1V, 3% quorum, 72h window, 24h execution delay

---

### Synapse
**Repo:** `Synapse` | **Lang:** TypeScript (Next.js 16) | **Status:** Draft NIP-30 spec + reference UI

Agent-native skill, memory, negotiation, and trust layer for the Buzz relay.

**7 parameterized-replaceable event kinds (30000-30006):** Interoperate with Buzz's identity, channels, workflows, MCP/ACP surfaces

**Reference dashboard:** orchestrator, skill marketplace, memory atlas, negotiation console, trust graph, agent roster, live feed

**Stack:** Next.js 16 (standalone) + React 19 + Tailwind 4 + shadcn/ui + Prisma/SQLite + Bun

**Status:** NIP-30 spec draft done. UI is reference/demo. Event signatures are mock (not BIP-340 yet).

---

### Blocksim
**Repo:** `Blocksim` | **Lang:** Python | **Status:** API complete

Proof-of-Simulation (PoSim) chain submission API. Operators stake tokens, run determinism-verified simulations (MuJoCo/OSOVM VeilSim), sign with BIPON39 Ed25519 identity, earn rewards. Anomalous submissions slash stake.

**Determinism verified:** Bit-identical MuJoCo 3.3.7 results on x86_64 macOS + Linux + ARM64/Termux  
**Hash:** `5d731393...`  
**Endpoints:** `/api/chain/stake`, `/api/chain/deploy_firmware`, `/api/chain/submit_log`

---

## APPS + TOOLING

### buzz-OG
**Repo:** `buzz-OG` | **Lang:** Rust (28-crate workspace) + TypeScript/React (Tauri 2) + Flutter + Python | **Status:** Highly complete

Sovereign Nostr-native team workspace where agents and humans are first-class equals.

**28 crates:** `buzz-relay`, `buzz-core`, `buzz-db`, `buzz-pubsub`, `buzz-auth`, `buzz-search`, `buzz-audit`, `buzz-workflow`, `buzz-media`, `buzz-voice`, `buzz-persona`, `buzz-relay-mesh`, `buzz-acp`, `buzz-agent`, `buzz-cli`, `buzz-dev-mcp`, + more

**Seven surfaces:** Home, Stream (channels), Forum (threads), DMs, Agents directory, Workflows, Search

**Key capabilities:**
- Git hosting: smart HTTP, npub-signed pushes, branches = channels
- Buzz Mesh: relay-gated shared GPU pool (iroh), OpenAI-compatible local endpoint
- Remote Agents: identity on relay, not substrate; swap hardware without losing history
- Huddles: Opus voice relay, agents join via STT/TTS
- Workflow engine: YAML-as-code, message/reaction/schedule/webhook triggers, approval gates (WF-08 gap: executor not yet wired)
- Scale target: 10K humans + 50K agents, 600K events/day, <50ms p99

**One known gap:** Workflow approval gate executor (WF-08) — schema/endpoints/MCP tools exist; executor persistence not wired

---

### agentic-waggle
**Repo:** `agentic-waggle` | **Lang:** Go (core) + Rust (CLI) + Python (SDK, MCP) + Lean (formal spec) + Julia (numerical verification) | **Status:** Active, rigorous

Stigmergic swarm coordination substrate. Real-time coordination via decaying environmental signals.

**Five-verb protocol:** `sniff` → `claim` → work → `mark` → `release` → optionally `dance`

**21 API endpoints** including: `deposit`, `sniff`, `gradient`, `claim`/`release`, `dance`, `memory_put`/`memory_get`, `recall`/`recall_window`, `channels`/`channel_register`, `watch_register`/`watch_ingest`, `snapshot_export`/`snapshot_load`, `territory_set`, `events` (SSE)

**Signal kinds with configurable decay:** `explored`, `gold`, `dead-end`, `help`, `warn`, `handoff`, `heartbeat`

**Math verified 3 ways:** Property tests + Lean formal spec + Julia numerical cross-check

**MCP bridge:** `waggle_mcp.py` — any MCP-compatible agent connects via stdio

---

### omokoda-smithers
**Repo:** `omokoda-smithers` | **Lang:** TypeScript (Bun) | **Status:** Functional core, early

SkillForge orchestrator with durable approval gates. Wires Smithers to Omo-Koda2 SkillForge kernel at `/v1/act`.

**Key workflow:** `skillforge-forge.tsx` — given a GitHub URL, calls SkillForge, extracts skill metadata + risk scores + audit flags; if gate triggers → pauses at Smithers approval node (crash-survivable, resumable)

**11 workflows:** `skillforge-forge`, `create-skill`, `create-workflow`, `docs-driven-development`, `share-pack`, `create-ui`, `add`, `init`, `eval-suite-run`, `post-failure`, `upgrade`

**MCP server:** Zero-dependency, single-file stdio server (starts in milliseconds). Supports MCP protocol versions 2024-11-05, 2025-03-26, 2025-06-18.

---

### larql
**Repo:** `larql` | **Lang:** Rust (+ Python/PyO3 bindings) | **Status:** Core working, performance frontier

Model-as-database. LQL (Lazarus Query Language) — treats transformer weights as a graph database.

**Pipeline:** model → vindex (mmap'd files) → LQL queries/mutations → patches (.vlp JSON overlays)

**LQL verbs:** `DESCRIBE`, `WALK`, `SELECT`, `INFER`, `INSERT`/`DELETE`/`UPDATE`, `SAVE PATCH`, `COMPILE CURRENT INTO VINDEX`

**Supported models:** Gemma 2/3/4, Llama 2/3, Mistral, Mixtral, Qwen, Phi, DeepSeek, GPT-2, BitNet b1.58  
**Compute backends:** Metal (Apple Silicon), CPU/OpenBLAS, CUDA (planned)  
**Performance:** Gemma 3 4B Metal: 88 tok/s; Gemma 4 26B-A4B CPU: ~35 tok/s (beats llama.cpp)  
**MoE:** Expert sharding across multiple CPU servers via gRPC — 671B-class feasible

**Cargo workspace:** `larql-models → larql-compute → larql-vindex → larql-core → larql-inference → larql-lql → larql-server → larql-cli → larql-python`

---

### zerolang
**Repo:** `zerolang` | **Lang:** C (compiler core) + JavaScript + TypeScript | **Status:** v0.3.4 pre-1.0

The programming language for agents. Graph-native: `.0` source files are projections of a canonical `zero.graph` database. Agents submit typed, validated patches; compiler checks before accepting.

**Agent-first edit loop (v0.3.4):**
- `zero patch` — stdin patch bodies, `--replace-in-fn`, expression replacement by handle
- `zero query` — access compiler's semantic graph
- `zero check --json` — machine-readable type/lint output
- `zero inspect --json` — deep compiler inspection

**VS Code extension** + conformance test suite + benchmarks + evals  
**Bundled agent skills** (version-matched to compiler)  
**Safety:** Pre-production. Breaking changes accepted.

---

### franken-stream
**Repo:** `franken-stream` | **Lang:** Python + Rust (Axum v2 sidecar) | **Status:** v1.0 delivered

Terminal media streamer. 4-tier fallback: configured providers → regex embed extraction → DuckDuckGo → yt-dlp. 9+ simultaneous sources. SQLite caching. LLM-assisted search via OpenClaw. Textual TUI + CLI + web UI. Android/Termux native. Migrated from `Bino-Elgua/franken-stream`.

---

## THE FULL ECOSYSTEM ARCHITECTURE MAP

```
┌─────────────────────────────────────────────────────────────────────┐
│  HUMAN / OWNER LAYER                                                 │
│  vanity-cloakseed (key security) · Vantage Voice (S2S interface)    │
└─────────────────────────────────────────────────────────────────────┘
                              ↕ MCP / REST / WebRTC
┌─────────────────────────────────────────────────────────────────────┐
│  CIVILIZATION LAYER — Vantage (Pillar 3, :8001)                      │
│  ~700 endpoints = ~700 MCP tools · guilds · workspaces · trading    │
│  buzz_bridge · blossom_client · birth_credentials · backtesting      │
│  ⚠ Gap 12: DIP ingest wired to wrong JSON shape (needs dip crate)  │
│  ⚠ Gap 16: receipt store doesn't know kind:31020/31030              │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ delegates to
┌──────────────────────▼──────────────────────────────────────────────┐
│  SOVEREIGN AGENT KERNEL — Ọmọ Kọ́dà (Pillar 1, :7777)               │
│  birth/think/act · 7 modules · 7 Hermetic laws · 759 tests          │
│  BIPON39 embedded · IfáScript embedded · WASM sandbox                │
│  NIP-46 bunker (signing isolation) · Droidclaw (mobile)             │
│  ✓ Gap 13: FIXED 2026-09-11 — 6 new MCP tool structs added to       │
│    tools/sovereign_node.rs (body_session_open/command/close,         │
│    timeline, timeline_diff, ip_root). All 12 tools delegate to       │
│    sovereign-node /mcp via JSON-RPC 2.0 — no hand-rolled structs.   │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ opcodes / receipts
┌──────────────────────▼──────────────────────────────────────────────┐
│  HEART VM — OSOVM (Pillar 2)                                         │
│  160+ opcodes · Àṣẹ economy · F1 ≥ 0.777 quality gate              │
│  ⚠ Gap 2: ARM Julia binary mismatch — real mode blocked             │
│  ⚠ Gap 5: Scarabswarm ↔ Blocksim path not wired through here       │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────────┐
│  NERVOUS SYSTEM — organism-core                                       │
│  birth-ifa-swibe · rlm-osovm · toc-evolve · zangbeto-audit          │
└─────────────────────────────────────────────────────────────────────┘

╔═════════════════════════════════════════════════════════════════════╗
║  PROTOCOL LAYER — sovereign-stack (connective tissue, NOT an app)  ║
║                                                                     ║
║  sovereign-types ── shared primitives (OduCoord, IdentityChain,    ║
║                     TrustTier, MerkleRoot, ProofVector, crypto)    ║
║       ↓ depended on by all three protocols below                   ║
║                                                                     ║
║  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────────┐ ║
║  │ dip/        │  │ vcp/        │  │ twin-protocol/             │ ║
║  │ DIP/1       │  │ VCP/1       │  │ TSP — spatial twins        │ ║
║  │ envelope    │  │ device      │  │ CaptureReceipt (31020)     │ ║
║  │ routing     │  │ manifest    │  │ SceneReceipt (31030)       │ ║
║  │ Nostr/Mesh/ │  │ handshake   │  │ SimulationReceipt          │ ║
║  │ MCP/A2A     │  │ grant       │  │ ObservationReceipt ⚠Gap11 │ ║
║  │ adapters    │  │ session     │  │ TwinTimeline               │ ║
║  │             │  │ Go2/Stamp   │  │ Àṣẹ minting               │ ║
║  │ Wire into:  │  │ adapters    │  │ Sui RPC anchor             │ ║
║  │ Omo-Koda2   │  │             │  │                            │ ║
║  │ Vantage     │  │ Wire into:  │  │ Wire into:                 │ ║
║  │ Witness-fw  │  │ Omo-Koda2   │  │ OSOVM, Scarabswarm         │ ║
║  │ Scarabswarm │  │ Witness-fw  │  │ Vantage, Witness-fw        │ ║
║  └─────────────┘  └─────────────┘  └────────────────────────────┘ ║
║                                                                     ║
║  sovereign-node = thin reference daemon (82 tests). DO NOT grow.   ║
╚═════════════════════════════════════════════════════════════════════╝

IDENTITY STACK (flows through everything):
  BIPON39 (key root) → minipae (memory) → ip-layer (provenance) → agent-phone (comms)

TEMPORAL / DIVINATION:
  Koodu (7-day resonance, BTC-time) → IfáScript (CowrieOracle, 256→65536 Odù)

SOCIAL / COMM / CODE:
  buzz-OG (Nostr workspace, git, workflows, mesh GPU)
  Synapse (NIP-30: skills, memory, negotiation, trust on Buzz)
  Vantage Voice (S2S voice to Vantage)
  agent-phone (Nostr-native agent comms, WebRTC, Reticulum fallback)

LEARNING / COORDINATION:
  mycelium (stigmergic trace substrate) ← mycelium-tools (5 pip tools)
  agentic-waggle (swarm coordination, decay signals, formal spec)
  Triune-Memory (3-phase memory orchestration over minipae)
  Axiom (3D galaxy graph — live agent visualization)

SECURITY / AUDIT:
  Zangbeto (red-team, Sui devnet, Arweave anchoring, n8n patrol)
  ares-control (daemon fleet control, API/worker split, :8090)

MESH / HARDWARE:
  omokoda-mesh-firmware (Meshtastic fork, LoRa, ESP32/nRF52/RP2040)
  Witness-firmware (DePIN LoRa witness, ESP32+SX1278, Prophetic Pantheon)
  Scarabswarm (drone racing simulation, Julia, PoSim trajectories)

ECONOMY / GOVERNANCE:
  Twelve-thrones (12-model consensus, epistemic NFTs, Arweave/Sui)
  Portent (PORT prediction market, pump.fun, buyback+burns)
  Blocksim (Proof-of-Simulation API, stake/attest/reward)

CODE / AI INTELLIGENCE:
  larql (model-as-database, LQL, weight editing, Metal/CPU)
  zerolang (agent-native language, graph-database compiler, v0.3.4)
  omokoda-smithers (SkillForge orchestrator, durable approval gates)

UTILITY:
  franken-stream (media streamer, Termux-native, OpenClaw-integrated)
```

---

## STATUS SUMMARY BY READINESS

| Repo | Language | Status | Role |
|------|----------|--------|------|
| Omo-Koda2 | Rust | **PRODUCTION** (759 tests) | Agent kernel |
| Vantage | Python | **PRODUCTION** (live) | Civilization layer |
| Vantage-Voice | TypeScript | **PRODUCTION** (live PWA) | Voice interface |
| BIPON39 | Rust | **PRODUCTION** v0.1.0 | Key derivation root |
| minipae | Python | **PRODUCTION** phases 1-3 | Agent memory |
| mycelium-tools | Python | **PRODUCTION** pip packages | Substrate tools |
| ares-control | Python | **PRODUCTION** | Daemon fleet control |
| vanity-cloakseed | React | **PRODUCTION** | Seed security |
| Twelve-thrones | TypeScript | **PRODUCTION** v1.0.0 | Epistemology engine |
| Blocksim | Python | **PRODUCTION** API | PoSim chain |
| franken-stream | Python/Rust | **PRODUCTION** v1.0 | Media utility |
| buzz-OG | Rust (28 crates) | **NEAR-COMPLETE** (WF-08 gap) | Sovereign workspace |
| If-Script | Rust | **NEAR-COMPLETE** (compiler partial) | Divination engine |
| mycelium | Python/Go | **ACTIVE** | Stigmergic substrate |
| Koodu | Julia/JS | **COMPLETE** (data) | Temporal resonance |
| agentic-waggle | Go+Rust+Python | **ACTIVE** | Swarm coordination |
| agent-phone | Python | **ACTIVE** 8/8 tests | Agent comms stack |
| Triune-Memory | TypeScript | **ACTIVE** | Memory orchestration |
| Axiom | TypeScript | **ACTIVE** | 3D agent visualization |
| Synapse | TypeScript | **DRAFT** | NIP-30 skill/trust layer |
| Portent | Python | **SPEC COMPLETE** pre-launch | Prediction market |
| Zangbeto | Rust/Node.js | **v0.1.8 DEVNET** | Red-team audit |
| Witness-firmware | Python | **MVP** | DePIN LoRa witness |
| Scarabswarm | Julia | **DEMO-READY** | Drone racing sim |
| omokoda-mesh-firmware | C++ | **FORK ACTIVE** | Meshtastic firmware |
| omokoda-smithers | TypeScript | **EARLY** functional | SkillForge approval |
| larql | Rust | **CORE WORKING** | Model-as-database |
| zerolang | C | **v0.3.4** pre-1.0 | Agent language |
| organism-core | TypeScript | **WIRED** (sim mode) | Nervous system bridge |
| ip-layer | Schemas | **SCHEMA-DRAFT** | IP provenance |
| agent-hub | TypeScript | **UNKNOWN** (empty README) | Unknown |
| **sovereign-types** | Rust | **PRODUCTION** (306 tests) | Shared primitives for all crates |
| **dip** | Rust | **PRODUCTION** (19 tests) | DIP/1 interoperability protocol |
| **vcp** | Rust | **PRODUCTION** (17 tests) | VCP/1 device capture protocol |
| **twin-protocol** | Rust | **PRODUCTION** (22+ tests) | TSP spatial twin + Àṣẹ economy |
| **sovereign-runtime** | Rust | **PRODUCTION** | Execution primitives |
| **sovereign-pipeline** | Rust | **PRODUCTION** | Gaussian splat capture pipeline |
| **sovereign-node** | Rust | **REFERENCE DAEMON** (82 integration tests) | Protocol glue — NOT an app server |

---

## KEY WIRING GAPS (what's not yet connected)

### Original 10 (from 2026-09-07)

1. **ip-layer implementation** — schemas done, no code, not wired into Omo-Koda2 birth flow
2. **organism-core real mode** — Julia binary mismatch on ARM/Termux blocks OSOVM real execution; Sui CLI not installed
3. **Buzz-OG WF-08** — Workflow approval gate executor not wired (schema exists)
4. **Synapse → real signing** — NIP-30 events are mock (no BIP-340 yet)
5. **Blocksim ↔ Scarabswarm** — Sim engine exists, PoSim chain exists, not yet wired end-to-end
6. **larql ↔ Omo-Koda2** — Local model inference not yet consumed by the agent kernel
7. **Portent oracle agents** — Resolution oracle not yet wired to any agent framework
8. **zerolang ↔ agent workflows** — Compiler exists but Buzz/Waggle invocation not wired
9. **Vantage broadcast-intent trigger** — Referenced in minipae docs as missing (wD/Vantage gap)
10. ~~**Sovereign device birth → ip-layer**~~ **FULLY FIXED 2026-09-11** —
    Both publication paths are now wired:
    - **sovereign-node**: publishes kind 31900 IP Root to the configured Nostr relay at startup
      when `dip.nostr_nsec` is set (`nostr_publisher::publish_nostr_event`).
    - **Omo-Koda2**: `ip_layer::publish_ip_root()` is called at every agent birth in
      `interpreter.rs:1616` — fail-open, stores the returned event id in the agent snapshot.
      `ip_layer::publish_twin_binding()` is available for on-demand VeilSim binding after
      a real twin exists. The "first-boot-birth.py" reference was stale; the birth flow is
      entirely in Rust.

### Sovereign-stack integration gaps (added 2026-09-11)

11. ~~**Witness-firmware ← ReceiptKind::Observation**~~ **FIXED 2026-09-11** —
    `twin-protocol/src/observation.rs` now exports `FirmwareObservationReceipt` — the Rust
    struct matching the CanonicalReceipt shape `sovereign_witness.py` actually produces.
    Three key changes:
    - `FirmwareObservationReceipt` struct added (kind=31040, physical_attestation block,
      identity/action/witness_attestations as `serde_json::Value` for firmware flexibility)
    - `FirmwarePhysicalAttestation` struct (rssi, frequency_hz, node_did)
    - `FirmwareObservationReceipt::KIND = 31040` const — single source of truth
    `sovereign_witness.py` updated:
    - `RECEIPT_KIND_OBSERVATION = 31040` constant added
    - `ledger_entry_to_canonical_receipt` now emits `kind: 31040` (integer), not `"observation"` string
    - `SovereignWitnessNode.submit_to_sovereign_node()` added — POST to `/proofs/observation`
    3 new tests in `observation.rs`: kind constant, JSON round-trip, kind-is-not-string.

12. ~~**Vantage DIP ingest schema mismatch**~~ **FIXED 2026-09-11** —
    `Vantage/backend/routers/dip_ingest.py` updated:
    - `DipAddress.did` is `Option<String>` → null accepted for Nostr/Meshtastic (was wrongly required)
    - `_opt_str()` helper prevents `"None"` string storage for null DIDs
    - Full `routing Vec<DipHop>` stored as JSON (was only counting hops)
    - `kind` validated against the 6 canonical `DipKind` variants (snake_case)
    - `origin_address` / `dest_address` columns added to schema
    - `GET /api/dip/outbound?did=<did>` endpoint added — sovereign-node behind NAT
      polls this to drain its inbound queue (acknowledged atomically, no duplicates)
    - Schema migration added for old `routing_hops` column
    - 13 tests covering all cases including null-did, outbound drain, and old-format rejection

13. ~~**Omo-Koda2 VCP/DIP tools are mocks**~~ **FIXED 2026-09-11** — `Omo-Koda2/omokoda-core/src/tools/sovereign_node.rs`
    now has all 12 MCP tool structs. The 6 new tools (`vcp_body_session_open`, `vcp_body_session_command`,
    `vcp_body_session_close`, `sovereign_timeline`, `sovereign_timeline_diff`, `sovereign_ip_root`) delegate
    to sovereign-node `/mcp` JSON-RPC 2.0 — same pattern as the original 6. No hand-rolled VCP/DIP structs.
    Tests updated: `tool_count_is_twelve`, all 12 names asserted, write-op and tier coverage extended.

14. ~~**Scarabswarm trajectory proofs → SimulationReceipt**~~ **FIXED 2026-09-11** —
    `Scarabswarm/src/validator.jl` now has:
    - `proof_to_simulation_proof_payload(proof, agent_id, principal_id; kwargs...)` — builds the
      `sovereign_types::SimulationProof` JSON from a `TrajectoryProof`:
        trajectory_hash → trajectory_hash, imu_hash → sensor_hash,
        hash(trajectory_hash + imu_hash) → checkpoint_root,
        execution_time → metrics.execution_time_ms, energy_used → metrics.energy_estimate
    - `submit_trajectory_proof(proof, agent_id, principal_id; node_url, kwargs...)` — HTTP POST
      to `{SOVEREIGN_NODE_URL}/proofs/simulation` using the `HTTP.jl` package already in
      Project.toml. Fail-open: returns nothing on any network error.
    Both functions exported from `ScarabSwarm.jl`. Trajectory proofs now flow directly
    from swarm sim runs to the sovereign-node proof engine.

15. ~~**sovereign-node contains code that belongs elsewhere**~~ **DOCUMENTED 2026-09-11** —
    Scope boundary is now explicit. Two changes:
    - `sovereign-node/ARCHITECTURE.md` added: defines the 5 legitimate concerns (VCP,
      DIP routing, capture pipeline, TSP receipt publishing, PoSim evaluation), lists the
      8 misplaced modules with their migration targets (Vantage/OSOVM/Omo-Koda2/Scarabswarm),
      and states the scope boundary rule: "if it doesn't touch a physical device, protocol
      wire format, or capture pipeline — it doesn't belong here."
    - `node.rs` module doc updated to reference ARCHITECTURE.md and state the scope boundary.
    Code not moved (89 tests still pass). This is a migration guide for future sessions,
    not an immediate refactor. No new application logic should be added to sovereign-node.

16. ~~**Vantage twin-protocol receipt indexer**~~ **FIXED 2026-09-11** —
    `Vantage/backend/routers/twin_receipt_index.py` added:
    - `POST /api/twin-receipts/ingest` — validates kind against {31020, 31030, 31040, 31050},
      enforces F1 quality gate (>= 0.777) on Capture and Scene receipts, rejects string
      `"observation"` for kind (must be integer 31040), stores full raw JSON
    - `GET /api/twin-receipts` — list with `kind`, `twin_id`, `agent_id`, `f1_min` filters
    - `GET /api/twin-receipts/{receipt_id}` — single receipt with `receipt` (decoded JSON)
    - `twin_receipts` table: `receipt_id`, `kind`, `kind_name`, `twin_id`, `agent_id`,
      `merkle_root`, `f1_score`, `outcome`, `raw_json`, `received_at`
    - Indexed on `kind`, `twin_id`, `agent_id`, `(kind, f1_score)` for explorer queries
    Registered in `main.py`. 24 tests in `test_twin_receipt_index.py` covering happy path,
    kind filtering, F1 gate enforcement, duplicate idempotency, string-kind rejection, and
    invalid filter rejection. Smoke-tested via direct TestClient — all 5 core behaviours pass.

### Phase completion — sovereign-stack build sequence (2026-09-11)

All 4 phases of the build-sequence plan are functionally implemented and tested:
- **Phase 4.1** — VCP→TSP: `handle_body_session_close` auto-queues capture job on camera session success
- **Phase 4.2** — DIP→TSP: inbound `twin_license_request` issues `TwinLicenseGrant` via DIP Receipt
- **Phase 4.3** — DIP→VCP: inbound `vcp_command` validates DIP principal against body session agent_id
- **Phase 4.4** — Full loop: 9-step integration test (VCP session → auto-capture → proof → obs receipt → Merkle → gossip)
- **Mycelium feedback loop**: `emit_mycelium_finding()` appends sim/obs delta to `{data_dir}/mycelium/sim-obs-findings.jsonl`
- **4D timeline diff**: `GET /twins/:id/timeline/diff` — change detection between first/last snapshot
- **IP Root publish**: 31900 fires at sovereign-node boot (`dip.nostr_nsec` configured) AND at every Omo-Koda2 agent birth (`ip_layer::publish_ip_root` in interpreter.rs:1616) — gap #10 fully closed
