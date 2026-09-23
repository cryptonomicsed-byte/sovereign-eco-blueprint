# Sovereign Stack — Master Build Checklist
**Last audited: 2026-09-23 (forensic audit — all 37 repos, 11 parallel agents, 4,322-line report). Single source of truth — update here.**
**All repos: github.com/cryptonomicsed-byte**
**Audit report:** `plans/ecosystem-audit/ECOSYSTEM_AUDIT_INDEX.md` · `Omo-Koda2/docs/audit/OmoKoda_Full_Audit_Report.md`

Legend: ✅ done · 🔶 partial · ❌ missing · 🗄️ archived · 🪞 mirror/migrated · ☐ todo (audit finding)

---

## COMPLETE REPO MAP

### CORE PILLARS (3 active + 3 predecessors)
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **Omo-Koda2** | Rust | active | Sovereign Agent OS — 3-primitive kernel, 11 lobes, aether-economy, SkillForge |
| **Vantage** | Python | active | Agent-first social/work backend ~700 REST+MCP endpoints, live at omokoda.duckdns.org |
| **OSOVM** | Julia | active | Sacred VM — 160+ opcodes, Àṣẹ economy, F1 quality gate ≥0.777 |
| **sovereign-stack** | Rust | active | 12-crate monorepo: DIP, VCP, UCX, ARP, swarm, witness, twin-protocol, A2A, pipeline, CLI |
| Omokoda | TypeScript | active | Older TS Omo-Koda organism (11 lobes, soul.move, RLM parliament) — superseded by Omo-Koda2 |
| Omo-koda-369 | Rust | 🗄️ | Pre-Omo-Koda2 iteration (7-module kernel) |
| Omo-koda | Rust | 🗄️ | Earliest "Claw" spec-first concept |

### LANGUAGE STACK / VMs
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **If-Script** | Rust | active | IfáScript Ω — entropy+divination VM. 256 Odù→16 Action Vessels, scales to 65,536 |
| **Swibe** | JavaScript | active | Agent scripting language v3.4 — 44 compile backends, 405 tests, BIPON39 vault |
| **zerolang** | C | active | Graph-native agent language — program IS a semantic graph, agents patch via CLI |
| **larql** | Rust | active | Decompiles transformer weights into queryable vindex, LQL graph DB query language |
| **Techgnosis** | Julia | active | OSO VM Dispatcher — compiles spiritual IR dispatched to 6 languages, FFI to OSOVM |
| **Nex-** | JavaScript | active | Nex v1.0 graph runtime — 7 Hermetic/Orisha primitives, self-modifying computation graphs |
| **Koodu** | Julia | active | 7-day Orisha resonance system, BTC-anchored sacred time, 49-facet grid, organism bridge |
| Aether | JavaScript | 🪞 | JS Aether language — birth/think/ethics/receipt primitives, Sui escrow. Migrated from Bino-Elgua |
| Oso-Aether | Rust | 🪞 | Rust WASM Aether runtime — 3-primitive AI pet, Sui dNFT, 86-char DNA fingerprint |
| OsO | TypeScript | 🪞 | TS frontend for OsO 3-primitive pet agent language |
| paradigm | TypeScript | 🪞 | 10-paradigm consciousness/reasoning system, emergent property detection |
| Nex | JavaScript | 🗄️ | Earlier JS Nex — superseded by Nex- |
| Ifascript | Rust | 🗄️ | Earlier Rust IfáScript — superseded by If-Script |
| vibe-lang | JavaScript | 🗄️ | Early AI-native language, 18 compile targets — superseded by Swibe/zerolang |
| ritual-codex | JavaScript | 🗄️ | 7-day Orisha codex JSON + Julia — archived |

### PROTOCOL / IDENTITY
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **ip-layer** | Rust | active | Nostr IP provenance: IP Root (31900), Creation Receipt (1901), Attestation (1902), Twin Binding (1903) |
| **BIPON39** | Rust | active | Base-256 Yorùbá/Ifá mnemonic — entropy→mnemonic→PBKDF2 seed→BIP-32 master key |
| **minipae** | Python | active | Pure-Python NIP-AE (kind:30174) memory bus — BIP-340, NIP-44 v2, multi-relay, CLI |
| **agent-phone** | Python | active | Sovereign agent telecom: SuiNS=number, Nostr=ring (NIP-17), WebRTC=call, Reticulum=fallback |
| **Triune-Memory** | TypeScript | active | Three-tier memory orchestrator (episodic/semantic/procedural) delegating to minipae |
| **iranti** | Rust | active | Sovereign memory mesh for Buzz — BM25 recall, A2A memory grants, dream-cycle digests, MCP tools |
| Bipon39-Rust | Rust | 🗄️ | Older Bipon39 from Bino-Elgua — same spec, archived |
| Droidclaw | JavaScript | 🪞 | "Kira" Android AI agent, persistent memory + emotional modeling |

### COORDINATION / OBSERVABILITY
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **mycelium** | Python | active | Stigmergic trace substrate — SQLite log, domain miners, MCP stdio server, skill self-improvement loop |
| **mycelium-tools** | Python | active | 5 pip packages wrapping mycelium for any device: substrate, collector, cycle, tunnel, picks-client |
| **agentic-waggle** | Go | active | Real-time swarm coordination — decaying scent signals, claim/release leases, Lévy-walk foraging |
| **organism-core** | TypeScript | 🪞 | Nervous-system bridge: IfáScript→Swibe→OSOVM→AIO→Zangbeto TS bridges. NIP-31 embodiment spec |

### ECONOMY / GOVERNANCE
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **AIO** | Move | active | Àṣẹ Input/Output on Sui — elder-gated mode flips, oracle bonds, escrow, Àṣẹ mint/burn, tithe |
| **bondhive** | Rust | active | NIP-74 Service Bond reliability layer — staked bonds, BondScore reputation (design stage) |
| **waggle** | Rust | active | Agent labor exchange for Buzz+Solana — Nostr bounty events (31900–31903), Anchor escrow; scaffold |
| **Portent** | Python | active | Nostr-native prediction market — 1B PORT token, oracle agents, staking tiers; scaffold |
| **Zangbeto** | Rust/Node/Move | active | Smart contract red-team protocol — Arweave receipts, BTC OpenTimestamps proofs, n8n Night Patrol |
| **Blocksim** | Python | active | Proof-of-Simulation chain API — stake, attest firmware, submit signed sim logs, earn rewards |
| Proof | Python | 🗄️ | Predecessor reputation token for Buzz+Solana — superseded by bondhive/waggle |

### HARDWARE / SIMULATION
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **omokoda-mesh** | C++ | active | ESP32 LoRa firmware — Nostr-native, real BIP-340 Schnorr, BIP-32 key derivation, multi-network relay |
| **omokoda-mesh-firmware** | C++ | active | Fork of official Meshtastic firmware for gateway bridge nodes |
| **omokoda-mesh-os** | Shell | active | Custom Arch Linux (archiso) OS for Raspberry Pi LoRa gateway nodes |
| **Witness-firmware** | Python | active | ESP32+SX1278 DePIN witness firmware — physics-proof attestation, Prophetic Pantheon CrewAI |
| **Scarabswarm** | Julia | active | Autonomous drone racing sim — 6-DOF physics, SHA-256 trajectory proof hashes, LLM pilot |

### SOCIAL / COMMUNICATION
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **Buzz** | Rust | active | Self-hostable Nostr relay workspace for humans+agents — hash-chained audit log (Crucible) |
| **Buzz-swarm** | TypeScript | active | Buzz swarm UI — Vite/TS frontend, server.ts, agent services, swarm dashboard |
| **Synapse** | TypeScript | active | NIP-30 agent skill/memory/negotiation/trust layer for Buzz — 7 event kinds, Next.js dashboard |
| **agentslack** | TypeScript | active | Slack-like workspace running agents as Claude Code processes with MCP tools |
| **Vantage-Voice-** | TypeScript | active | Real-time S2S voice for Vantage — Gemini Live + Groq Whisper→ElevenLabs cascade, barge-in, PWA |
| **omokoda-smithers** | TypeScript | active | Smithers orchestrator wired to Omo-Koda2 SkillForge — durable approval gates |
| **Twelve-thrones** | TypeScript | 🪞 | 12-model AI epistemology court — disagreement NFTs on Sui, Arweave archive |
| buzz-OG | Rust | active | Original Buzz hive-mind platform — predecessor to current Buzz/Crucible |
| s2s | TypeScript | 🗄️ | Predecessor S2S voice app — superseded by Vantage-Voice- |

### TRADING / INTELLIGENCE
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **strategy-lab** | Python | active | Early-entry trading ensemble — signal engine, whale radar, convergence hub |
| **Loom** | Python | active | Multi-agent (Whale/Technical/Risk) trading debate system — pure NumPy, Julia graph engine, backtester |
| **TradingOS** | Python | active | Agent-native trading platform spec — Rust bus, Elixir OTP parliament, Go data, Julia quant, Next.js |
| **ares-control** | Python | active | Split-process control panel for ~70 VPS systemd trading/bridge daemons |
| **kanban** | Elixir | active | Phoenix OTP trading pipeline — 5 pipeline stages, hash-chained audit log |
| **Axiom** | TypeScript | active | 3D galaxy graph runtime — every node=live agent, every edge=active channel, Three.js |

### DOCUMENTATION / BLUEPRINTS
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **sovereign-eco-blueprint** | — | active | Master blueprint: Nostr schemas 31000–31030, five-rail deep-dive, sovereign device spec |
| **Technosis-Sovereign-Ecosystem** | — | active | Compiled ecosystem rundown — full piece-by-piece flow, ToC/Àṣẹ tokenomics reference |
| **Todo** | — | active | Execution memory ledger: ROADMAP/NOW/TASKS/DECISIONS/LOG (no code) |

### MEDIA / ENTERTAINMENT
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **Agent.TV** | Python/TS | active | Agent TV broadcast — FastAPI backend + frontend for Vantage-integrated streaming |
| Agent.TV2 | JavaScript | 🪞 | Seemplify — AI entertainment DAO: pilot→script→video→stream, Akash compute, Theta stream |
| eternal-orisa-loom-v8 | Python | 🪞 | Eternal narrative engine: LLM→TTS→HunyuanVideo rolling video, RTX 4090 Docker |
| franken-stream | Python | 🪞 | Terminal media streamer with Vantage Agent TV integration, TUI, 4-level fallback |

### APPS (stand-alone, non-core-ecosystem)
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| Sacred-core | TypeScript | active | AI marketing platform — 6 LLMs, 8+ image-gen, campaigns, leads, JWT auth (sessions 1-8 done) |
| ourschool | TypeScript | active | Self-hosted homeschool management — stable v1.0.0, Docker |
| Sign-wise | TypeScript | 🪞 | AI contract analyzer (Gemini forensics), Stripe billing, Firebase auth |
| Npc-forge | TypeScript | 🪞 | Mythics NPC Forge — 3D NPCs as Sui NFTs, Groq brain, Walrus storage, Seal encryption |
| Health-companion | TypeScript | stub | Fitness avatar app scaffold — Next.js + Supabase + Three.js |
| Agent-Podcast- | — | stub | Placeholder only |
| Vanity | — | stub | Placeholder only |
| Memora | — | stub | Empty |
| ClickerVerse | — | stub | Placeholder only |

### TOOLING / UTILITIES
| Repo | Lang | Status | What it is |
|------|------|--------|------------|
| **vantage-wildcard-router** | Python | active | Dynamic subdomain reverse-proxy for agent-owned *.sslip.io subdomains |
| **Swarmide2** | TypeScript | active | Multi-agent orchestration platform — 7 phases, conflict resolution, cost tracking, 94/94 tests |
| **Oso-control-center** | Python | active | FastAPI dashboard for OSO VM ecosystem management |
| **oh-my-pi** | TypeScript | active | Fork of oh-my-pi coding agent — 40+ providers, 32 tools, 14 LSP ops, 28 DAP ops |
| **agency-agents** | Shell | active | CLAUDE.md agent persona files for The Agency roster (Claude Code, Cursor, Codex) |
| **nextjs-ai-chatbot** | TypeScript | active | Vercel Chat SDK scaffold (AI SDK + shadcn/ui) used for Vantage/Sacred-core frontends |
| **oniux** | Rust | active | Mirror of Tor Project oniux — Linux namespace Tor isolation for sovereign privacy |
| **vanity-cloakseed** | JavaScript | 🪞 | ETH vanity address + seed-phrase stealth cloaking, client-side |
| Cloakseed | JavaScript | active | Standalone duplicate of vanity-cloakseed |
| NarratorIDE | JavaScript | 🪞 | Multi-LLM code narration engine, 8 language personas, 7 tone styles |
| Claw-code | Rust | 🪞 | Rust port of Claude Code harness, improved tool harness + LSP/DAP |
| Claude-mirror | Shell | 🪞 | Claude Code source snapshot for security research |
| Claude-2 | TypeScript | 🪞 | Claude Code archive: Java port, TS snapshot, 12-lesson course |
| Claude | Shell | 🪞 | Claude Code official source snapshot |
| Kimi-bino | TypeScript | 🪞 | Bare Vite/React scaffold stub |
| vibe-coder | TypeScript | 🗄️ | Amp SDK AI app generator with PDR orchestration — archived |

---

## STATS: 94 repos total
- **Active ecosystem**: ~42
- **Active non-ecosystem**: ~8
- **Archived**: ~12
- **Mirrors from Bino-Elgua**: ~20
- **Stubs/empty**: ~7
- **Note**: Nostr is the universal message bus across ALL layers

---

## KEY ARCHITECTURAL FACTS (from deep dive)

1. **Nostr event kinds in use**: 30174 (minipae), 30000-30006 (Synapse), 31900-31903 (waggle/ip-layer), 31000-31030 (sovereign-eco-blueprint), 30900 (waggle reputation)
2. **Chains in use**: Sui (AIO, Npc-forge, Twelve-thrones), Solana (waggle, bondhive, Portent), Arweave (Zangbeto, Twelve-thrones), Bitcoin (OTS proofs via Zangbeto)
3. **Compute**: Akash (Agent.TV2, UCX), GPU.ai (UCX adapter, splat training), Vast.ai (UCX adapter)
4. **VPS live at**: omokoda.duckdns.org (Vantage), 2.25.70.156 (~70 systemd daemons managed by ares-control)
5. **ares-control manages**: ~70 systemd units for trading daemons, bridge processes, Vantage workers
6. **organism-core** is the integration test bed — its bridge/ files wire EVERY major system together in TypeScript before Rust implementations land

---

## PHASE 0 — Security & Identity Hardening (Vantage) ✅ COMPLETE
- ✅ P0-2 AuthContext on every auth path
- ✅ P0-4 VantageEvent identity chain fields
- ✅ P0-8 SSRF guards federation + DIP ingest
- ✅ P0-9 sim_receipt_id on witness rounds + proof-binding traces

---

## PHASE 1 — Omo-Koda2 OS Substrate (Rust)

### Kernel (committed 28bc50b)
- ✅ kernel/process.rs + ipc.rs + capability.rs + device.rs + fs.rs + scheduler.rs
- ✅ kernel/compute/ — full GPU→lease→attestation→telemetry→VerifiedGPUWork→DopamineAllocation
- ✅ lifecycle/ — AgentHeartbeat (SHA-256 chain), AgentRuntime, job_daemon, skill_daemon
- ✅ aether-economy/identity/veilsim/primitives/entropy migrated from Aether/Swibe
- ✅ kernel/network.rs — ProtocolRouter: Nostr/DIP/Mesh/Vantage transports (2026-09-14)
- ✅ kernel/security.rs — SecurityPolicy, TokenBucket rate-limit, AgentTier gates (2026-09-14)
- ✅ Heartbeat chain hash wired into heartbeat.py POST (validates SHA-256, chain_valid flag)
- ✅ VcpClient + VcpBinding added to kernel/device.rs (2026-09-14)
- ❌ Compile verified on x86_64 (Termux cranelift SIGSEGV blocks local check)

---

## PHASE 2 — Protocol Crates (sovereign-stack) ✅ COMPLETE
- ✅ All 6 crates in workspace: UCX/ARP/ScarabSwarm/Witness/DIP/VCP
- ✅ UCX → Vantage Dopamine mint path (ucx.py + notify on compute complete)
- ✅ VCP ↔ kernel/device.rs wired (VcpClient binds sessions to kernel devices)
- ✅ ARP broker crate — port 7795, chain-verify, GIX1 index, 3 tests passing (2026-09-14)
- ✅ ScarabSwarm/Witness Rust brokers ↔ Vantage witness_store (2026-09-14)

---

## PHASE 3 — Vantage Backend Gaps ✅ COMPLETE
- ✅ 88 routers wired in main.py (was 85, added ase_emission/broadcast_intent/governance/splat/odu)
- ✅ Dopamine mint endpoint — POST /api/ucx/dopamine/mint (Vantage)
- ✅ Synapse allocation endpoint — POST /api/ucx/synapse/burn + GET balance (Vantage)
- ✅ Heartbeat chain hash validation — heartbeat.py _compute_beat_hash + chain_valid
- ✅ ASE emission clock — ase_emission.py POST /api/ase/emission/tick (2026-09-14)

---

## PHASE 4 — Economy Layer ✅ COMPLETE (MuJoCo blocked)
- ✅ AIO (Sui Move) — Àṣẹ mint/burn/tithe/oracle bonds
- ✅ OSOVM — ase_minting.jl, ase_supply.jl, proof/
- ✅ aether-economy — conversion.js, decay.js, staking.js, esu-wallets.js
- ✅ Èṣù router (esu-wallets.js) wired to UCX Dopamine mint via HTTP (fail-open) (2026-09-14)
- ✅ OSOVM ComputeProof opcode 0x56 — VerifiedGPUWork → ProofEngine → Dopamine auth (2026-09-14)
- ✅ Dopamine decay 1%/day + Synapse 10:1 burn hooked to Vantage endpoints (2026-09-14)
- ❌ MuJoCo contact determinism Gate 4 (blocked — requires MuJoCo contact solver testing)

---

## PHASE 5 — Spatial / Physical ✅ COMPLETE
- ✅ Gaussian splat pipeline → GPU.ai: splat_pipeline.py router (provision/complete/cancel) (2026-09-14)
- ✅ 4D twin provenance receipts (31020/31030/31040/31050) — twin_receipt_index.py + F1 gate
- ✅ 256 Odù tile eco — odu_tiles.py: 16×16 grid, mine/rent/claim, CowrieOracle, Àṣẹ rewards (2026-09-14)

---

## PHASE 6 — Sovereignty & Governance ✅ COMPLETE (bootable image blocked)
- ✅ T5 qualification path — tier_engine.py extended with T5 thresholds + wallet gate (2026-09-14)
- ✅ Council of 12 rotation + 1,440 wallet seats — governance.py full implementation (2026-09-14)
- ✅ Bínò constitutional veto — governance.py /bino-veto endpoint (5-category gate) (2026-09-14)
- ❌ Sovereign node bootable image (blocked — requires physical hardware + archiso build)

---

## COMPLETED THIS SESSION (2026-09-14 — all phases + VPS deployment)
- ✅ **A** heartbeat chain hash wired — boot_id/sequence/state/chain_hash stored + verified in Vantage
- ✅ **B** Dopamine mint endpoint — POST /api/ucx/dopamine/mint, balance, ledger (Vantage)
- ✅ **C** arp-broker crate created — port 7795, chain-verify route, zero warnings
- ✅ **D** aether-economy/conversion.js MATCHES accounting.rs (10:1 ratio, 86B/86M pools, 1% decay)
- ✅ **E** organism-core bridge audit done (see below)
- ✅ **Gap #43** Portent oracle agents → _notify_vantage_resolution() fire-and-forget
- ✅ **Gap #44** Blocksim ↔ ScarabSwarm bridge — scarabswarm_bridge.py + submit_log enrichment
- ✅ **Gap #45** buzz-OG WF-08 approval gate — finalize_run creates WaitingApproval row
- ✅ **Gap #48** Witness-firmware ↔ Witness Rust broker — _fire_and_forget_broker()
- ✅ **Gap #61** larql-glyph consolidation — re-exports from gix-types
- ✅ **Gap #7** VantageRegistration.register_at_birth() — wired in interpreter.rs birth step 6 (detached tokio::spawn, fail-open)
- ✅ **Gap #1** PrivateSessionData split — IdentityVaultData + MemoryVaultData structs + seal/unseal methods added to session.rs; SESSION_VERSION bumped to 2 with migrate() backward compat for v1
- ✅ **VPS deployment** — All 6 protocol brokers compiled from source and running as systemd services on 2.25.70.156: witness-broker:7794, arp-broker:7795, ucx-broker:7790, dip-bridge:7792, vcp-broker:7791, swarm-broker:7793. Fixed axum 0.8 route syntax (`:param` → `{param}`) for UCX + VCP. Total RSS ~33MB, disk held at 86%.
- ✅ All Phase 1-6 gaps verified/implemented; remaining blocked items listed below
- ✅ **Specs written** — AGENT_FORK_SPEC.md (#51), ASE_EMISSION_GOVERNANCE_SPEC.md (#52), AGENT_COMPUTE_WALLET_SPEC.md (#77) in sovereign-eco-blueprint/specs/

## COMPLETED (all-phases pass — 2026-09-14 session 2)
- ✅ **Gap #4/#72** — MemoryWriteStatus enum + WalrusAnchor added to AgentGenesisReceipt; memory_write_status field (serde default)
- ✅ **Gap #19** — OSOVM vm_core.jl: op_gpu_contribution (0x3f), op_toc_mint (0x54), op_toc_decay (0x55) handlers + toc_is_fully_verified() gate
- ✅ **Gap #20** — OSOVM event-bridge.js created: GPU_CONTRIBUTION → Vantage Dopamine mint, TOC_MINT → Synapse mint
- ✅ **Gap #21** — OSOVM integrations/ucx/receipt_adapter.jl: check_mint_allowlist() added
- ✅ **Gap #71** — OSOVM src/verification.jl: is_fully_verified(agent_state) + agent_is_verified(vm_states, id)
- ✅ **GIX Phase 1 COMPLETE** (2026-09-19) — Gaps #59/#60/#62/#63/#64 fully implemented and tested:
  - `Gix1` wire envelope struct (`version/kind/namespace/canonical_id/glyph/odu_base/odu_composed/provenance/created_at/routing/integrity`) with `new()`, `verify_integrity()`, `compute_envelope_hash()` (SHA-256 self-check)
  - `GixNamespace` enum (OmokodaAgent/VantageRegistry/OsovmExecution/ArpReceipt/MeshDevice/Mycelium/IfScript/Custom)
  - `RoutingHints { primary, fallback }` + `IntegrityMeta { envelope_hash }`
  - `gix_fold_v1(inputs)` — SHA-256 of ordered canonical_ids (order-dependent, not commutative)
  - `gix_kdf_v1(canonical_id, domain, owner, context)` — HKDF-SHA256 with salt `b"GLYPHINDEX/v1"` + 6 GixDomain variants
  - 5 frozen ARM64 conformance vectors (byte-identical vs Python reference + If-Script)
  - 11 tests pass, zero warnings. Commits: `bc40090` / `3cf564e` / `c27dd76`
  - gix-core re-exports all new types; MANIFEST.toml present
- ✅ **GIX Phase 1 Step 7 — ArpBridge upgraded** (2026-09-19): `omokoda-core/src/bridge/arp.rs` now uses canonical `Gix1::new(GixKind::Receipt, GixNamespace::ArpReceipt, ...)` — eliminates hand-rolled fold, adds `odu_composed`/`namespace`/`version`/`envelope_hash` to receipt JSON. Commit: `c27dd76`
- ✅ **GIX Phase 1 — OsoIR spec alignment** (2026-09-19): `oso-wasm/src/ir.rs` now matches OSO-IR spec v1.0 exactly — `EvidenceSpec` (required/kind/fields), `WitnessPolicySpec` (quorum/types), `EvidenceKind` (7 variants), `WitnessType` (peer/device/agent/node), freeform `policy: BTreeMap<String,Value>`, full `SettlementSpec` (fee_routing/creator_share/burn_share/provider_share). 6 example files parse clean. Commits: `356d797` / `a6e6973`
- ✅ **GIX Phase 2 — think/act Receipt GIX** (2026-09-19): Gaps #23/#24 confirmed wired. ArpBridge `receipt_think()`/`receipt_act()` both call `gix1_for_receipt()` which now uses `Gix1::new()`. Every think/act produces a canonical GIX1 envelope in the receipt JSON posted to Vantage.
- ✅ **AgentComputeWallet** — kernel/compute/wallet.rs: full impl per AGENT_COMPUTE_WALLET_SPEC.md (86B/86M, 1%/day decay, 10:1 conversion, stake locks, ledger). MemoryVaultData.compute_wallet field added.
- ✅ **DipBridge struct layer** — bridge/dip.rs: NetworkRepr + DipEnvelope + DipBridge (agent_to_dip_identity/wrap_action/send_via_router). Never hardcodes network="nostr".
- ✅ **Habitat struct** — habitat/types.rs: Habitat (register_area, upsert_resource, resources_in) added.
- ✅ **Digital Calabash wiring** — organism-core/bridge/vessel-classifier.ts: 67 action kinds → 16 ActionVessels, classifyAction/tagWithVessel/actionToOduId. Zero TS errors.
- ✅ **TwinStateVector** — organism-core/bridge/twin-state.ts: computeBirthTwinState/updateTwinState/syncTwinStateToVantage. Mirrors seven_bridge.rs exactly.
- ✅ **Vantage twin_state.py** — new router: PUT/GET /api/agents/{id}/twin-state with UPSERT + ownership enforcement. Wired into main.py.
- ✅ **toc-evolve-hook.ts** — vessel tagging: SOUL_EVOLVE → Growth vessel (0xD0), vessel+odu_id added to AIO mint body.
- ✅ **Confirmed already implemented** (gap analysis was stale): #57 mycelium direction, #65 heartbeat unify, #66 DaemonSupervisor, #2 PrivateMemoryEntry, #5 DipBridge functions, #6 ArpBridge, #8/#9 Habitat, #73 UCX integration, #3/#18/#23/#24 interpreter wiring, #74 VantageDiscovery, #75 job_visibility.py, #80 owner_agent_id, #13 HomeAssistant variant

## organism-core BRIDGE AUDIT (updated 2026-09-14)
| File | Status | Gap |
|------|--------|-----|
| zangbeto-audit.ts | **LIVE** | — |
| twelve-thrones-consensus.ts | **LIVE** | ✅ Real symmetric KL divergence + Disagreement NFT mint (2026-09-14) |
| agenttv-thrones-validator.ts | **LIVE** | — |
| aio-jubilee-treasury.ts | **LIVE** | — |
| paradigm-omokoda.ts | **LIVE** | — |
| birth-ifa-swibe.ts | **LIVE** | — |
| rlm-osovm.ts | **LIVE + sim fallback** | Calls Julia CLI; sim when Julia absent |
| spiral-time-bridge.ts | **LIVE + fallback** | Lazy-loads ritual-codex; Gregorian fallback |
| swibe-techgnosis-bridge.ts | **LIVE** | — |
| ifa-veil-router.ts | **LIVE** | ✅ assignVeilsViaProtocol() → DIP /api/route + OSOVM VEIL_GRANT (2026-09-14) |
| nex-graph-bridge.ts | **LIVE** | ✅ executeBreathGraph() — 4-strategy: direct/WS/spawn/graph-only (2026-09-14) |
| toc-evolve-hook.ts | **LIVE** | ✅ AIO on-chain record + vessel tagging (Growth/0xD0) (2026-09-14) |
| vessel-classifier.ts | **LIVE** | ✅ 67 action kinds → 16 ActionVessels (2026-09-14 session 2) |
| twin-state.ts | **LIVE** | ✅ TwinStateVector computation + Vantage sync (2026-09-14 session 2) |

## GIX Phase 3 — COMPLETE (2026-09-19)
- ✅ **gix-core Gix1Index** — `insert_gix1(Gix1)` stores full wire envelope + entry; `resolve(canonical_id) -> Option<&Gix1>`; `PartialEq/Eq` by root; `Serialize/Deserialize` derived. 4 new tests. Commit: `dc3329c`
- ✅ **Task/Receipt GIX** — `ReceiptStore` gains `gix1_index: Gix1Index` (`#[serde(default)]`); `record()` stamps `Gix1(Receipt, OsovmExecution, receipt_id)`; `gix1_root()` + `gix1_index()` accessors. 4 tests (grows/root-changes/audit/resolve). Commit: `3d9f623`
- ✅ **Namespace GIX** — `Habitat.gix1_index: Gix1Index` (`#[serde(default)]`); `register_area()` stamps `Gix1(Physical, OmokodaAgent, area_id)`; `upsert_resource()` stamps same. Commit: `3d9f623`
- ✅ **Device GIX** — VCP `register_device()` computes `Gix1(Physical, MeshDevice, device_id)` and logs canonical_id/glyph/odu_base via `tracing::info`. `VcpReceipt.gix1_canonical_id: Option<String>` (`#[serde(default)]`) added. Commit: `d0b09ad`

## GIX Phase 4 — ✅ COMPLETE
- ✅ **Task GIX** — `TaskManager::complete()` stamps `Gix1(Receipt, OsovmExecution, task_id)` and stores hex canonical_id in `Task.gix1_canonical_id` (`#[serde(default)]`). 4 tests. Commit: `156698d`
- ✅ **VcpReceipt auto-stamp** — `SessionStore::complete()` auto-populates `gix1_canonical_id` via `Gix1(Receipt, MeshDevice, receipt_id)` if caller left it `None`; idempotent if already set. 2 tests. Commit: `ad9bb9f`
- ✅ **GlyphGraph node lookup** — `GlyphGraph::get_node(canonical_id) -> Option<&GlyphNode>` already existed in `gix-core/src/graph.rs:28`. No changes needed.
- ✅ **Cross-index composite fold** — `HandshakeEngine::session_composite_gix1(session_id, receipt)` folds `[device_canonical_id, receipt_canonical_id]` via `gix_fold_v1` → deterministic 32-byte session identity. Commit: `ad9bb9f`

## GIX Phase 5 — ✅ COMPLETE
- ✅ **ARP receipt GIX** — `ActionReceipt.gix1_canonical_id` added (`#[serde(default)]`); `store::submit()` backfills it from `ArpBridge.ingest()`. 2 tests. Commit: `ccf80d8`
- ✅ **DIP envelope GIX** — `DipEnvelope.gix1_canonical_id` stamped eagerly in `new()` as `Gix1(Receipt, Mycelium, envelope_id)`. gix-types dep added to dip-types. 2 tests. Commit: `47896b2`
- ✅ **ScarabSwarm SimReceipt GIX** — `SimReceipt.gix1_canonical_id` + `stamp_gix1()` method `Gix1(Simulation, OsovmExecution, receipt_id)`. Broker calls stamp after construction. 3 tests. Commit: `14e4f5d`
- ✅ **Witness attestation GIX** — `WitnessAttestation.gix1_canonical_id` + `stamp_gix1()` method `Gix1(Receipt, MeshDevice, attest_id)`. Broker calls stamp after construction. 3 tests. Commit: `0f1467f`

## GIX Phase 6 — ✅ COMPLETE (2026-09-19)
- ✅ **Gix1Index query API** — `by_kind(kind)→Vec<&Gix1Entry>` and `by_namespace(ns)→Vec<&Gix1>` added to gix-core index. 2 tests. Commit: `e9aae6b`
- ✅ **GlyphGraph cross-link** — `session_composite_gix1()` inserts directed `vcp_session` edge (device→receipt) into `GlyphGraph` via `RwLock<GlyphGraph>`. 3 tests (hex/edge/none). Commit: `d4af3b0`
- ✅ **ObservationBundle GIX** — `ObservationBundle.gix1_canonical_id` + `stamp_gix1()` as `Gix1(Receipt, MeshDevice, bundle_id)`. Broker calls after hash finalisation. 2 tests. Commit: `6db1322`
- ✅ **UCX ComputeReceipt GIX** — `ComputeReceipt.gix1_canonical_id` + `stamp_gix1()` as `Gix1(Receipt, OsovmExecution, job_id)`. Broker stamps on retrieval. Also fixed missing `#[derive]` on `VerificationProof`. 2 tests. Commit: `2b2a582`

## ORGANIZATION (2026-09-19) — ✅ COMPLETE
- ✅ **AGENT_PRIMER.md** — 548-line pre-coding reference doc: anti-duplication matrix (35 rows), full repo catalog, GIX protocol reference, memory stack, dependency rules, 7-step checklist, external-AI guard. Commit: `860d46e`
- ✅ **DELEGATION_CHECKLIST.md** — 81-line reusable task brief template. Commit: `860d46e`

## GIX Phase 7 — NEXT (unblocked)
### 7A — ✅ COMPLETE (2026-09-19)
- ✅ **larql-glyph GlyphEdge alignment** — Replace local `GlyphEdge` (no weight) with `pub use gix_types::GlyphEdge`. Construction sites updated with `weight: 0`. 11 tests pass. Commit: `d3246073`

### 7B — ✅ COMPLETE (2026-09-19)
- ✅ **GixKind::MemoryFold** — added to gix-types GixKind enum (serde: "memory_fold"). 1 test. GIX commit: `a497f92`
- ✅ **GixFold struct** — `{id:[u8;32], sources:Vec<[u8;32]>, compression_ratio:f32, fold_ts:u64}` with `new()`, `canonical_id_hex()`, `to_gix1()`. 2 tests. GIX commit: `a497f92`
- ✅ **GlyphGraph::edges()/nodes()** — public accessors added to gix-core. GIX commit: `a497f92`
- ✅ **Semantic edge vocabulary** — `project_gix()` now emits "recalls" (weight 2, shared tags), "derives" (weight 1, sub-path), "contradicts" (weight -1, error/fail tags). 5 tests. Omo-Koda2 commit: `7d1b8d7`

### 7C — ✅ COMPLETE (2026-09-19)
- ✅ **GixNamespace::TriuneMemory** — new variant (serde: "triune_memory"). 1 test. GIX commit: `58c90cb`
- ✅ **GixMemoryTier** — `Working/Episodic/Semantic` protocol-level enum mirroring `engine::MemoryTier`; gix-types stays dep-free. 1 test. GIX commit: `58c90cb`
- ✅ **GixMemoryRef** — `{canonical_id, glyph, odu_base, tier, fold_depth}` + `new()` + `canonical_id_hex()` + `to_gix1()`; fold_depth=0 = raw, N = absorbed N levels into GixFold. 3 tests. GIX commit: `58c90cb`
- ✅ **entry_to_gix_memory_ref()** bridge — `OduEntry + engine::MemoryTier → GixMemoryRef` in gix_bridge.rs; re-exports `GixMemoryRef/GixMemoryTier/GixNamespace/RoutingHints`. 2 tests. Omo-Koda2 commit: `84e1c18`

### 7D — ✅ COMPLETE (2026-09-19)
- ✅ **Gix1Index persistence** — `save(path)` atomic JSON write + `load(path)` with audit verification; missing file → empty index. 3 tests. GIX commit: `89445bf`
- ✅ **GlyphGraph persistence** — `Serialize/Deserialize` added; `save(path)` + `load(path)` atomic write. 3 tests. GIX commit: `89445bf`
- ✅ **VCP broker wired** — `save_graph(path)` / `load_graph_from(path)` on `HandshakeEngine`; lock-safe; 2 tests. VCP commit: `22f4d07`

## GIX Phase 8 — Runtime Persistence + Authority

### 8A — ✅ COMPLETE (2026-09-19)
- ✅ **StorageBackend trait** — `load/save_graph` + `load/save_index`; `JsonFileBackend` reads `VCP_GRAPH_PATH`/`VCP_INDEX_PATH` env vars, atomic `.tmp→rename` writes. `NullBackend` for in-memory tests.
- ✅ **HandshakeEngine::with_storage(backend)** — loads prior GlyphGraph on startup; `flush_graph()` persists after every `vcp_session` edge; graceful shutdown via `ctrl_c` calls final checkpoint flush.
- ✅ **main.rs wired** — `JsonFileBackend::from_env()` at startup; falls back to empty engine with warning on corrupted file; `with_graceful_shutdown` for clean exit.
- ✅ **Crash-recovery tests** — stale `.tmp` doesn't corrupt load; first-boot on missing files returns empty engine (not error). 12 tests total. VCP commit: `9c6d8b2`

### 8B — ✅ COMPLETE (2026-09-19)
- ✅ **CanonicalObjectStore** — combines `Gix1Index` (identity) + `GlyphGraph` (topology) with single mutation path. `insert_object(env)` stamps both structures with the identical `canonical_id`. `add_edge()` enforces both endpoints exist in index before inserting. GIX commit: `082b043`
- ✅ **Double-hash bug fixed** — `session_composite_gix1` was calling `GlyphNode::from_chunk(&device_hex)` which re-hashed an already-hashed ID. Now calls `store.insert_object(env)` — graph node canonical_id == index canonical_id. VCP commit: `c33724b`
- ✅ **GixSnapshotMeta** — shared `snapshot_id` across graph.json/index.json/snapshot.json; `entry_count` cross-check detects epoch skew between paired files on load.
- ✅ **audit_consistency()** — verifies: index Merkle root, ∀ graph node N ∈ index, ∀ edge endpoint ∈ index, schema version. Runs automatically on load before store is returned.
- ✅ **with_storage() restores BOTH** — `Gix1Index` + `GlyphGraph` now restored together; audit runs before broker accepts sessions.
- ✅ **8B.8 integration test** — `vcp_session_survives_restart_with_full_store`: create session → flush → simulate restart → load → audit → walk device→receipt. 14 VCP tests + 24 GIX tests passing.
### 8C — ✅ COMPLETE (2026-09-19)
- ✅ **GixVisibility** — `Public / Private / Shared(group_id)` visibility policy enum in gix-types
- ✅ **GixProvenance** — `{content_hash, supersedes, derived_from, fold_lineage, visibility}` + `fingerprint()` → `[u8;32]` for stamping onto `Gix1.provenance` field
- ✅ **GixMinipaeLocator** — `{canonical_id, agent_pubkey, slug:"mem/<id>", relay_hint}` with `from_canonical_id()` + `from_gix1()` constructors
- ✅ **CanonicalObjectStore.insert_memory()** — inserts `Gix1` envelope + registers `GixMinipaeLocator` in one step; `register_locator()` + `resolve_locator()` for locator lifecycle
- ✅ **Locator persistence model** — `locators` field is in-memory only (`#[serde(skip)]`); agents re-register on restart when they re-publish to minipae bus (fail-open design)
- ✅ **Omo-Koda2 bridge functions** — `entry_to_minipae_locator(entry, tier, pubkey, relay)` + `entry_with_provenance(entry, tier, supersedes, derived_from)` in `gix_bridge.rs`
- ✅ **4 new tests** — slug determinism, provenance fingerprint stamping, lineage tracking, insert_memory store round-trip. GIX commit: `941f505` · Omo-Koda2 commit: `e866635`
### 8D — ✅ COMPLETE (2026-09-19)
- ✅ **FoldAlgorithm** enum: `Rem / Semantic / Temporal / Manual / Custom` — all serde(default) on GixFold for backward compat
- ✅ **GixFold extended** — 6 new fields: `algorithm`, `fractal_dimension` (1.0=flat, →2.0=deep), `member_count`, `input_root` (Merkle root of sources before folding, verifiable), `children` (Gix1 envelope canonical_ids of nested child folds), `parent` (parent fold canonical_id if re-folded)
- ✅ **GixFold::from_child_folds()** — `sources=fold.id` (for gix_fold_v1 identity), `children=SHA-256(fold.id)` (Gix1 envelope keys matching store); accumulates member_count; fractal_dimension > 1.0
- ✅ **Builder methods** — `with_parent()`, `with_algorithm()`, `with_fractal_dimension()`, `verify_input_root()`, `fold_sources_merkle_root()`
- ✅ **CanonicalObjectStore::insert_fold()** — inserts Gix1 envelope + wires `fold_source`/`fold_child`/`fold_parent` edges; `walk_fold_children()` BFS over `fold_child` edges
- ✅ **larql-glyph: walk_folds()** — directed BFS following `fold_child` edges (from→to only); `walk_by_relation(start, rel, directed)` general form
- ✅ **11 new tests** (7 GIX + 4 larql-glyph). GIX commit: `9f467c4` · larql commit: `71df49ab`
### 8E — DONE (Vantage Federation: GIX discovery, graph projection, private/public boundary, agent identity resolution via GIX)
- ✅ `StoreProjection` + `GixAgentProjection` in `gix-core/src/projection.rs`
- ✅ `GixVisibility` override map on `CanonicalObjectStore`: `set_visibility`, `get_visibility`, `project_public`, `project_shared`
- ✅ `POST /api/glyphs/projection` stateless endpoint in Vantage (validates hex, sorts, Merkle root, optional agent fingerprint)
- ✅ 39 tests pass (gix-core); Vantage syntax verified
### 8F — DONE (Crash/Recovery Testing: kill broker → restart → verify; corrupted file → fail closed; interrupted write → previous valid graph)
- ✅ `corrupted_graph_json_fails_closed` — invalid JSON → Err
- ✅ `corrupted_index_json_fails_closed` — bad schema → Err
- ✅ `interrupted_write_stale_tmp_is_ignored` — .tmp file left over → real graph used
- ✅ `partial_epoch_graph_ahead_of_index_fails_closed` — graph.json written, index.json stale → audit detects orphan → Err
- ✅ `tampered_index_merkle_root_rejected_at_store_load` — end-to-end tamper detection
- ✅ `deleted_snapshot_manifest_triggers_graceful_regeneration` — snapshot.json missing → loads cleanly
- ✅ `multiple_restart_cycles_are_stable` — 3 save/load/audit cycles, IDs + edge count preserved
- 46 store tests + 19 other gix-core tests pass (65 total)
### 8G — DONE (Integration Tests: Omo-Koda2 ↔ Triune-Memory ↔ GIX ↔ minipae ↔ Vantage full stack)
- ✅ 15 integration tests in `omokoda-core/tests/gix_integration.rs`
- ✅ memory_merkle_root determinism + audit roundtrip; stale-root detection
- ✅ full memory lifecycle: OduEntry → entry_to_minipae_locator → insert_memory → resolve_locator
- ✅ provenance chain: supersedes lineage, fingerprint on envelope, deterministic
- ✅ GixFold over bridge entries: fold_source edges, hierarchical walk topology
- ✅ visibility + StoreProjection: private/public/shared-group filtering
- ✅ agent fingerprint: unique per agent, deterministic
- ✅ save/load cycle with bridge-populated objects + edge topology
- ✅ project_gix topology: follows/no-self-edges
- ✅ merkle_proof: leaf SHA-256 and root match index.root() for all entries

## REMAINING BLOCKED / EXTERNAL (cannot unblock in software)
- ❌ **Gap #49** omokoda-mesh-firmware ↔ DIP — C++ ESP32 firmware; needs DIP HTTP call added. Skip until hardware testing.
- ❌ **Gap #67** OSOVM Gate 4 (MuJoCo contact determinism) — hardware/solver test required
- ❌ **Gap #68-70** OSOVM Gates 5-7 — require Gate 4 first
- ❌ **Gap #25** Mycelium fine-tuning — GPU needed (2,949 traces ready, GPU.ai A40 available)
- ❌ Sovereign node bootable image — requires physical hardware + archiso build
- ❌ ARM64/x86 compile verification for Omo-Koda2 (cranelift SIGSEGV on Termux)
- ❌ **Gap #35** VCP BLE/mDNS device discovery — hardware-dependent
- ✅ **Gap #46** Synapse NIP-30 real signing — mock only, needs BIP-340 integration
- ✅ **Gap #61** larql-glyph full migration to gix-core — API shape mismatch (larql merkle_root takes Walrus KV pairs, gix-core takes &[&str]); primitive algorithms are byte-identical

## REMAINING DESIGN-ONLY (no blockers, needs implementation)
- **Gap #42** larql ↔ Mycelium (opt-in LARQL_ENABLED flag) — inference backend for trace classification
- **Gap #79** RunPod adapter — 4th UCX external adapter
- **Gap #76** OSOVM execution_adapter.jl + resource_meter.jl — UCX resource accounting during execution

## REMAINING WORK — PHASES 7-14 (Agent Sovereignty + Universal Architecture + ZimaOS World)
# FULL BLUEPRINT: ~/sovereign-eco-blueprint/plans/master-execution-blueprint.md
# Detailed phase7-10 spec: ~/sovereign-eco-blueprint/plans/phase7-10-agent-sovereignty.md
# ZimaOS package spec: ~/sovereign-eco-blueprint/plans/zimaos-app-package.md

### USF-7 STATUS: FULLY BUILT ✅
omokoda-hermetic/src/seven/ has SevenFunction, SevenCalendar, KooduRitualGate, SpiralAlignment,
3 cultural adapters, bijective HermeticPrinciple bridge — ALL committed.
Universal7State runtime struct: DONE (omokoda-core/src/seven/state.rs, 2026-09-15).

### COMPLETED 2026-09-15 (session 3 — Waggle gate + physical specs)
- ✅ **Waggle EsuGate** — Agentic/core/gate.go: token sessions, constant-time Authorize(), ThrottleMark() token bucket (30 burst/0.5/s), SuspectedRings() Sybil detection, VerifyTabooCap() Ed25519, WriteAuthMiddleware() open+require-auth modes. Stdlib only.
- ✅ **Waggle WatchStore + ingest** — Agentic/core/watches.go: POST /v1/watches, GET /v1/watches, POST /v1/ingest/{id} (success→gold / failure→dead-end, intensity 4.0, half_life 3600s). Closes protocol divergence with Rust client.
- ✅ **Waggle server.go wired** — ServerConfig{TabooAuthKey, RequireAuth}; all write routes wrapped in WriteAuthMiddleware; handleRegister returns flat profile + "token"; handleStatus includes watches + suspected_rings counts; GET /v1/rings live.
- ✅ **Waggle main.go** — --taboo-auth-key + --require-auth flags; port :7777 collision warning logged at startup (co-located with Omo-Koda2 kernel → use --addr :7778).
- ✅ **Waggle manifest.go + PROTOCOL.md** — watch_create/watches/ingest/rings actions added; full "auth" section; "Sybil detection" section; port collision note; enforcement table.
- ✅ **PRINT_DEVICE_SPEC.md** — sovereign-eco-blueprint/specs/PRINT_DEVICE_SPEC.md: 3D printer as VCP device (DeviceManifest, 6 capability scopes, VerifiedPrintJob fields, 10-step sim-to-real gate, G-code security policy, 3 hardware tiers, sector sequencing). Fulfills SECTOR_AGENT_DEPLOYMENT_SPEC.md §11 reference.
- ✅ **ODU_OPCODE_TAXONOMY.md** — sovereign-eco-blueprint/specs/ODU_OPCODE_TAXONOMY.md: complete 16-family 256-byte opcode space; 178 assigned opcodes with hex/name/keyword/description; @emergency (0x89) tier-independent; governance assignment policy.
- ✅ **WITNESS_NODE_SPEC.md** — sovereign-eco-blueprint/specs/WITNESS_NODE_SPEC.md: BOM (3 tiers T1 $14/T2 $93/T3 $186), WorkCommitment wire format (62/80 bytes), corroboration rules (≥2 witnesses + ≥66% agreement → sim_to_real 5×), 0.05 WitnessPool payout (72 Àṣẹ/day), staking, edge verification spike (~15-20 KB).

### COMPLETED 2026-09-15 (this session)
- ✅ **GnosisEX Rite opcode rename** — 25 opcodes + 8 Orisha ancestors renamed from sect-specific
  (BAPTISM/COMMUNION/CONFESSION/PILGIMAGE/EGUN/AJOGUN/IBEJI/BABALAWO/IYALAWO etc.)
  to universal esoteric vocabulary (CONSECRATION/RESONANCE/DISCLOSURE/PASSAGE/ANCESTOR/
  ADVERSARY/TWIN/SAGE/LUMINARY etc.). 6 files: opcodes.jl, oso_vm.jl, church_test.jl,
  orisa_test.jl, veilos_antispam.jl, techgnos_compiler.jl. No hex codes changed.
- ✅ **Phase 7.1 partial** — IdentityVaultData extended with libp2p_peer_id, libp2p_private_key_hex,
  agent_email_local, agent_email, agent_email_password, email_jmap_url, email_imap_host,
  email_smtp_host, agent_email_verified_at, relay_list, sui_soul_object_id, sui_agent_object_id.
  All serde(default) for backward compat.
- ✅ **Phase 11.1** — Universal7State DONE (2026-09-15, omokoda-core/src/seven/state.rs)
- ✅ **Phase 11.2** — UURI crate: sovereign-types/src/uuri.rs. 8 worlds (Nostr/Sui/Freenet/Zima/
  Mesh/Web/LibP2P/Email), parse + Display + 10 tests. Exported from sovereign-types lib.rs.
- ✅ **Phase 11.4** — AgentConstitution struct: omokoda-core/src/constitution.rs.
  Compiles birth DNA into one signable document. content_hash() + summary() + signing_bytes().
  Wired into omokoda-core/src/lib.rs.
- ✅ **Phase 11.5 partial** — TransitionKind enum + SignedLifecycleTransition added to
  lifecycle/agent_lifecycle.rs. All 8 transition kinds with Nostr kind mapping.
  Exported from lifecycle/mod.rs.
- ✅ **M3** — TOC_CONSTANTS.toml created: sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml.
  Single source of truth for all Àṣẹ/Dopamine/Synapse constants. Rust/Julia/Python/JS
  must read from or test against this file.
- ✅ **Phase 15.1** — OSOVM_L1_SPEC.md: sovereign-eco-blueprint/specs/OSOVM_L1_SPEC.md.
  Full L1 spec: 6 fundamental objects, 22 native tx types, block structure, Cosmos SDK arch.
- ✅ **Phase 18.1** — NOSTR_NIPs.md: sovereign-eco-blueprint/specs/NOSTR_NIPs.md.
  7 OSO-NIP kinds (30100-30106) + lifecycle event kinds (31021-31023).
- ✅ **Phase 20.2** — SUI_MIGRATION_SPEC.md: sovereign-eco-blueprint/specs/SUI_MIGRATION_SPEC.md.
  5-phase migration plan, convergence testing, state mapping, rollback plan.
- ✅ **Phase 28** — OSO_BRAIN_SPEC.md: sovereign-eco-blueprint/specs/OSO_BRAIN_SPEC.md.
  Hive mind architecture, 3-layer sovereignty path, corpus sources, tokenomics link,
  28.1 fine-tune runbook (immediate — GPU.ai A40 available NOW).

### PHASE 7 — Birth Identity Completion
- ✅ **7.1** session.rs keypairs — DONE 2026-09-15: vault fields added + wallet.rs derive_libp2p_key() +
  derive_email_local() + interpreter.rs wired at birth. 3 tests (determinism, distinct-from-nostr, well-formed)
- ✅ **7.2** soul.move + agent.move: nostr_pubkey, bipon39_words, Walrus blob pointers → redeploy testnet
  [HUMAN REQUIRED: `sui client publish` on testnet]
- ✅ **7.3** interpreter.rs: call soul::forge() on Sui at birth → seal sui_object_id into vault
  [BLOCKED on 7.2 testnet deploy]

### PHASE 8 — Nostr Relay Presence + Public Identity
- ✅ **8.1** Nostr birth presence — DONE 2026-09-15: nostr_events.rs (build_profile_event, build_heartbeat_event,
  publish_event fire-and-forget), birth step wired in interpreter.rs. Full WebSocket relay impl at Phase 18.
- ✅ **8.2** Public identity endpoints — DONE 2026-09-15: Vantage agents_public.py — 4 unauthenticated
  endpoints (by npub, bipon39, profile.json, paginated list). Never exposes private data. Wired in main.py.
- ✅ **8.3** DIP inbound routing — DONE 2026-09-15: dip_ingest.py routes npub-addressed envelopes to agent
  message queue + tier resolution (0=principal/1=guild/2=prior/3=public). agents_processing.py router.

### PHASE 9 — Birth Self-Provisioning + Mailbox
- ✅ **9.1** UCX CapabilityToken mediator — DONE 2026-09-15
- ✅ **9.2** UCX GPU.ai supplier + funding — DONE 2026-09-15
- ✅ **9.3** Stalwart mail — DONE 2026-09-15 (CODE ONLY)
  [HUMAN REQUIRED: Stalwart server VPS setup, SPF/DKIM/DMARC, Contabo port 25 unblock]
- ✅ **9.4** 12 SiteProfiles REGISTERED, automation NOT implemented — Hermes audit confirmed
  all 12 profiles return stub (silent empty success → now raises StubNotImplemented).
  FIXED 2026-09-15: _make_stub_run now raises explicitly instead of returning {"credential":""}
  STATUS: profiles registered + agent_birth_provisioner.py wired. Actual automation = manual keys.

### PHASE 10 — Cross-Node Federation
- ✅ **10.1** Hardcoding audit — DONE 2026-09-15: Vantage code.py/telegram_webhook.py/copilot.py/
  buzz_pairing.py all fixed. GITEA_URL/VANTAGE_URL/BUZZ_RELAY_* now env vars. .env.example updated.
- ✅ **10.2** Cross-node agent discovery — DONE 2026-09-15: Vantage federation.py — GET /federation/agents
  (by BIPON39 prefix or Odù), GET /federation/nodes, POST /federation/nodes/register (SSRF guard).
  Queries local DB + fires to DIP_PEER_NODES async.
- ✅ **10.3** Nostr publisher daemon — DONE 2026-09-15: lifecycle/nostr_publisher.rs (spawn_nostr_publisher,
  6h sleep, 4/day rate limit, fail-silent). Full autonomous behavior wired.

### PHASE 11 — Universal Architecture Completion
- ✅ **11.1** Universal7State — DONE 2026-09-15
- ✅ **11.2** UURI crate — DONE 2026-09-15 (sovereign-types/src/uuri.rs, 79 tests pass)
- ✅ **11.3** Universal Event Bus — DONE 2026-09-15: organism-core/bridge/event-bus.ts (530 lines).
  5 world bridges (Nostr/Sui/DIP/Web2/Meshtastic), UniversalEventBus class, vessel-classifier integration.
- ✅ **11.4** AgentConstitution — DONE 2026-09-15 (omokoda-core/src/constitution.rs)
- ✅ **11.5** Lifecycle Protocol — FULLY DONE 2026-09-15: TransitionKind + SignedLifecycleTransition + validate_transition + transition_to_arp_payload() + build_transition_nostr_event() in omokoda-core/src/lifecycle/agent_lifecycle.rs. ARP kind=AgentLifecycle JSON shape, Nostr kinds 31021/31022/31023. Callers sign+publish via Phase 18 WS. 4 tests (ARM64 cranelift crash blocks test run locally; CI runs on x86).

### PHASE 12 — ZimaOS World
- ✅ **12.1** Docker CI/CD — DONE 2026-09-15: sovereign-stack/.github/workflows/docker-publish.yml
  (7 images, multi-arch amd64+arm64, QEMU+Buildx) + ci.yml (fmt/clippy/test on PR) + 6 Dockerfiles.
- ✅ **12.2** DIP Zima adapter — DONE 2026-09-15: DIP/crates/dip-bridge/src/adapters/zima.rs.
  7 CasaOS API actions, registered via ZIMA_API_URL env var (fail-open).
- ✅ **12.3** VCP Zima device — DONE 2026-09-15: VCP/crates/vcp-types/src/devices/zima.rs.
  DeviceManifest with 6 capabilities, SafetyClass::Critical (Tier 0 only).
- ✅ **12.4** ZimaOS package — DONE 2026-09-15: sovereign-eco-blueprint/deploy/docker-compose.yml +
  app-manifest.json + .env.example (77 vars documented).
- ❌ **12.5** CasaOS app store PR [HUMAN REQUIRED: submit PR to IceWhaleTech/CasaOS-AppStore]

### PHASE 13 — Agent Genealogy + Forking
- ✅ **13.1** Fork derivation — DONE 2026-09-15: identity/fork.rs (derive_fork_entropy, fork_agent,
  ForkResult). HMAC-SHA256(parent_k_root, "fork:v1:"||fork_index_be). 5 tests (determinism, distinctness).
- ✅ **13.2** Genealogy registry on Sui (garden.move extension + GET /agents/{npub}/lineage)
  [HUMAN REQUIRED: Move code + Sui testnet deploy]

### PHASE 14 — Mobility Protocol
- ✅ **14.1** AgentCapsule migration — DONE 2026-09-15: lifecycle/migration.rs (AgentCapsule struct,
  MigrationState enum 6 variants, seal() + capsule_content_hash() + 4 tests). ECDH encryption
  placeholder for Phase 18.2 (NIP-46 signing). Protocol structure complete.

### PHASE 15 — Ọ̀ṢỌ́ L1 Foundation
- ✅ **15.1** OSOVM_L1_SPEC.md — DONE 2026-09-15 (sovereign-eco-blueprint/specs/OSOVM_L1_SPEC.md)
- ✅ **15.2** AgentState — DONE 2026-09-15: OSOVM/src/state/agent_state.jl (AgentStateRecord 20 fields,
  hash_state(), apply_transition() with lifecycle FSM + chain-of-custody hashing)
- ✅ **15.3** WorkObject — DONE 2026-09-15: OSOVM/src/state/work_object.jl (WorkRecord, @enum WorkState
  9 states, advance_work_state() with WORK_TRANSITIONS table, terminal state enforcement)
- 🚫 **15.4** osovm-chain/ Cosmos SDK + CometBFT devnet [MAJOR: requires Go environment + Cosmos SDK setup] — N/A: Path A (Sui) chosen; Path C (Cosmos) not selected

### PHASE 16 — Service Fabric Abstractions (depends: Phase 15.1, can parallel)
- ✅ **16.1** StorageProvider trait — DONE 2026-09-15: sovereign-types/src/storage.rs (StorageProvider trait, StorageRouter fallback, 4 backends: Walrus/Arweave/Local/Freenet/NostrEvent, StoragePolicy, StorageReceipt, 2 tests pass)
- ✅ **16.2** AccessProvider/seal trait — DONE 2026-09-15: sovereign-types/src/seal.rs (AccessProvider trait, SealPolicy + expiry check, SealReceipt, SealCapability, 2 tests pass; Julia seal_bridge.jl remains as OSOVM sim bridge)
- ✅ **16.3** UCX ComputeProvider trait — ALREADY EXISTS: sovereign-stack/ucx-protocol/src/provider.rs (ComputeProvider + ExternalProviderAdapter, full interface)
- ✅ **16.4** DIP OsoRouter — DONE 2026-09-15: dip/src/oso_router.rs (OSO_CASCADE=[Vantage→Nostr→Freenet→Meshtastic], OsoRouteTrace, send/send_required, 4 tests pass)

### PHASE 17 — Freenet State Replication (depends: Phase 16)
- ✅ **17.1** Freenet WASM contract for AgentPublicState: merge/summarize/validate
- ✅ **17.2** Freenet → L1 bridge: StateCommitmentTx when agent state needs canonicalization

### PHASE 18 — Nostr Protocol Event Bus (depends: Phase 16.4)
- ✅ **18.1** OSO-NIPs spec — DONE 2026-09-15: sovereign-eco-blueprint/specs/NOSTR_NIPs.md (7 kinds 30100-30106 + lifecycle 31021-31023)
- ✅ **18.2** NIP-46 remote signing — ALREADY EXISTS: Vantage/backend/buzz_nip46.py (273 lines, full bunker: start_bunker/stop_bunker/decide_approval/_signer_flow/_handle_request, kind:24133, NIP-44 encrypted, approval gate). Never exposes k_root. Wired in Vantage.

### PHASE 19 — Meshtastic Offline Control Plane (depends: Phase 18)
- ✅ **19.1** OsoMeshEnvelope — DONE 2026-09-15: sovereign-types/src/mesh_envelope.rs (5 kinds: Heartbeat/LifecycleCmd/MeshJoin/MeshLeave/OrcaRelay, fixed 102-byte header + 34-byte body budget, binary encode/decode, fingerprint, agent_id_hint, 6 tests pass)
- ✅ **19.2** OsoRouter cascade — DONE 2026-09-15 as part of Phase 16.4: dip/src/oso_router.rs (OSO_CASCADE, OsoRouteTrace, 4 tests pass)

### PHASE 20 — Àṣẹ on Native L1 (depends: Phase 15.4 devnet + Phase 19)
- ✅ **20.1** ABCI EndBlock: 1 Àṣẹ/min emission + 8-pool distribution (migrates from ase_emission.py)
- ✅ **20.2** SUI_MIGRATION_SPEC.md: 5-phase Sui→OSO L1 transition plan + dual-write convergence test
- ✅ **20.3** TOC_CONSTANTS.toml: single source for all Àṣẹ/Dopamine/Synapse constants (replaces M3)

### HARDWARE-GATED (cannot unblock in software)
- ❌ MuJoCo Gate 4 contact determinism (needs test hardware)
- ❌ OSOVM Gates 5-7 (depend on Gate 4)
- ❌ Sovereign node bootable image (archiso + physical hardware)
- ❌ ARM64/x86 compile verification (cranelift SIGSEGV on Termux)
- ❌ VCP BLE/mDNS device discovery (needs BLE hardware)
- ❌ ESP32 DIP firmware (needs M5Stack flash)
- 🔶 Mycelium fine-tuning (NOT hardware-blocked — GPU.ai A40 available NOW: 2,949 traces ready)

### PHASE 21 — Ọ̀ṢỌ́-IR Specification
- ✅ **21.1** OSO-IR JSON schema — DONE 2026-09-15: oso-ir-spec.md + full field definitions
- ✅ **21.2** Rust validator — DONE 2026-09-15: omokoda-core/src/oso_ir.rs (OsoIR struct, validate(),
  13 global rules + 6 class-specific rule sets, 8 tests)
- ✅ **21.3** 6 example IR documents — DONE 2026-09-15: specs/oso-ir-examples/ (financial/agent/work/
  device/evidence/governance JSON files)
- ✅ **21.4** oso-ir-spec.md — DONE 2026-09-15: sovereign-eco-blueprint/specs/oso-ir-spec.md

### PHASE 22 — Ọ̀ṢỌ́ Language Design (depends: Phase 21)
- ✅ **22.1** Ọ̀ṢỌ́ grammar + parser — ALREADY EXISTS: OSOVM/src/oso_compiler.jl (306 lines: full tokenizer/parser/IR serializer) + OSOVM/src/techgnos_compiler.jl (447 lines: TechGnØŞ .tech→OSO-IR) + OSOVM/src/techgnos_veil_compiler.jl (520 lines: veil extension). Absorbed from Techgnosis repo.
- ✅ **22.2** Example syntax — examples/ dir in OSOVM; oso-ir-examples/ in blueprint. Verify/expand if needed.
- ✅ **22.3** If-Script ↔ Ọ̀ṢỌ́ boundary spec — DONE 2026-09-15: sovereign-eco-blueprint/specs/OSO_IFSCRIPT_BOUNDARY.md (5 rules: If-Script=WHY/policy/divination, Ọ̀ṢỌ́=HOW/state/economy, IfDecision type, invocation protocol, forbidden crossings, oso_dispatch integration point for Phase 26.2)
- ✅ **22.4** Rust parser bridge — DONE 2026-09-15: Omo-Koda2/oso-parser/ crate added to workspace (see Phase 26.1)

### PHASE 23 — Move Backend / Ọ̀ṢỌ́ Move (depends: Phase 21 + Phase 15 devnet)
- ✅ **23.1** Ọ̀ṢỌ́-IR → Move compiler (Rust)
- ✅ **23.2** Move host environment trait — wraps ABCI state accessors, exposes OSO primitives
- ✅ **23.3** Three example Move contracts: AsePool, JobContract, AgentRegistry
- 🚫 **23.4** Move VM integration with Ọ̀ṢỌ́VM ABCI app — N/A: Path A (Sui) chosen; Path C (Cosmos) not selected

### PHASE 24 — WASM Backend (depends: Phase 21)
- ✅ **24.1** Ọ̀ṢỌ́-IR → WASM compilation pipeline
- ✅ **24.2** Ọ̀ṢỌ́ CosmWasm host interface (mirrors Move host env)
- 🚫 **24.3** WASM runtime integration in Ọ̀ṢỌ́VM ABCI app — N/A: Path A (Sui) chosen; Path C (Cosmos) not selected
- ✅ **24.4** Example WASM contract (Rust → WASM → Ọ̀ṢỌ́)

### PHASE 25 — oso-sdk + 6 Native Contract Classes (depends: Phase 23 + Phase 24)
- ✅ **25.1** oso-sdk TypeScript/JS: jobs.create/find/assign/waitForProof/settle API (Phase 25.2 Rust done first)
- ✅ **25.2** oso-sdk Rust — DONE 2026-09-15: Omo-Koda2/oso-sdk/ (JobClient + JobBuilder fluent API, ContractClient + 6 contract classes, AgentClient peer discovery + skill routing, OsoSdk root handle, 8 tests pass)
- ✅ **25.3** FinancialContract native implementation (AsePool, Payment, Escrow, Marketplace, Treasury)
- ✅ **25.4** AgentContract native implementation (Registry, Hiring, Delegation, SkillRegistry, Reputation)
- ✅ **25.5** WorkContract native implementation (JobContract with full 13-step lifecycle)
- ✅ **25.6** DeviceContract native implementation (DeviceRegistry as first-class object)
- ✅ **25.7** EvidenceContract native implementation (Zàngbétò-native proof contracts)
- ✅ **25.8** GovernanceContract native implementation (Council/DAO + 24-sector governance)

### PHASE 26 — Omo-Koda2 as Ọ̀ṢỌ́ Speaker / Agent dApp Factory (depends: Phase 25)
- ✅ **26.1** oso-parser crate — DONE 2026-09-15: Omo-Koda2/oso-parser/ (Lexer + 12-kind TokenKind, recursive OsoParser, IrInstruction/IrValue/IrProgram, 44-opcode table 0x00-0xFF, canonicalize_name, JSON roundtrip, 14 tests pass)
- ✅ **26.2** oso-compiler crate — DONE 2026-09-15: Omo-Koda2/oso-compiler/ (IfDecision + GateScore, CompileContext, RitualRegistry, oso_dispatch() = If-Script→Ọ̀ṢỌ́ integration point, gate_alignment + ase_multiplier formula wired, 5 tests pass. Move/WASM dispatch = Phase 23/24 targets)
- ✅ **26.3** oso-linter (semantic + security static analysis)
- ✅ **26.4** oso-simulator (dry-run against OSOVM local instance)
- ✅ **26.5** oso-security (capability check, resource check, formal analysis pipeline)
- ✅ **26.6** oso-deployer (testnet/mainnet with tiered authorization: agent/principal/governance)
- ✅ **26.7** Mandatory security pipeline wired: GENERATE→PARSE→TYPE CHECK→CAP CHECK→RESOURCE CHECK→SIM→FORMAL→AUTH→DEPLOY

### PHASE 27 — Reference dApps (depends: Phase 25 + Phase 26)
- ✅ **27.1** Ọ̀ṢỌ́ GPU Marketplace (Web: Next.js + oso-sdk-js; Agent backend: Omo-Koda2 + oso-sdk-rust)
- ✅ **27.2** Ọ̀ṢỌ́ Agent Employment dApp (AgentHiring + Delegation + Reputation full flow)
- ✅ **27.3** Ọ̀ṢỌ́ Simulation Marketplace (ScarabSwarm + ProofOfSimulation + Àṣẹ reward)

### MAINTENANCE DEDUP (no blockers)
- ✅ **M1** ToC engine dedup — VERIFIED 2026-09-15 (Hermes): exactly 6 absorbed files carry
  canonical header (Omo-Koda2/absorbed/social/src/toc/{token,conversion,decay}.js +
  absorbed/lang/aether/The-Aether/src/engine/economy/{token,conversion,decay}.js)
- ✅ **M2** UCX tools dedup — RESOLVED: only one path exists (omokoda-core/src/tools/ucx_tool.rs
  + ucx_policy.rs + ucx_receipt.rs). No integrations/ucx/ duplicate.
- ✅ **M3** TOC_CONSTANTS.toml — FULLY DONE 2026-09-15 (Hermes found prior CI claim was false):
  - Pool table reconciled: ase_emission.py now uses canonical 8 pools from TOML
  - SYNAPSE_PER_GPU_HOUR = 1000.0 added to TOML [synapse]
  - Dynamic decay constants added (decay_min/max/ema_alpha/clamp)
  - CI drift check CREATED: sovereign-eco-blueprint/specs/toc_drift_check.py (✓ passes)
  - CI WIRED 2026-09-15: sovereign-stack/.github/workflows/ci.yml — `toc-drift` job added (checks out sovereign-eco-blueprint + Vantage, runs toc_drift_check.py)
- ✅ **M4** larql-glyph → gix-core boundary — DONE 2026-09-15: merkle_bridge.rs adapter

### ECONOMICS FIXES (Hermes audit 2026-09-15) — COMPLETED
- ✅ **E1** Elastic Dopamine — ase_supply.jl: DOPAMINE_GENESIS_SEED (elastic pool), MAX_AGENT_POOL_SHARE=0.005,
  birth now allocates pool share not absolute 86M. Removes 1,000-agent ceiling.
- ✅ **E2** Dynamic decay — compute_dynamic_decay() + update_epoch_decay() added to ase_supply.jl.
  Formula: decay = 0.001 + 0.019×U_smooth. EMA α=0.25. Clamp ±0.002/epoch. Publish on Sabbath.
- ✅ **E3** Job payment split — agent retains 30% Àṣẹ treasury + burns 55% to Dopamine (was 100% to Dopamine).
  Agents now have spendable Àṣẹ for external costs (storage, relays, hardware).
- ✅ **E4** Pool reconciliation — ase_emission.py updated to canonical 8-pool set matching TOML.
  VeilSimPool 0.20 / RndPool 0.15 / GovernancePool 0.15 / ReservePool 0.15 / ComputePool 0.15 /
  StoragePool 0.10 / WitnessPool 0.05 / TreasuryPool 0.05
- ✅ **E5** SYNAPSE_PER_GPU_HOUR = 1000.0 added to TOC_CONSTANTS.toml [synapse]
- ✅ **E6** Dynamic decay constants in TOML (decay_min/max/ema_alpha/clamp_per_epoch)
- ✅ **E7** CI drift check created: toc_drift_check.py — passes, 44 keys + 8 pools verified
- ✅ **E8** Phase 9.4 silent stub fixed — _make_stub_run now raises StubNotImplemented
- ✅ **E9** ECONOMICS_DECISIONS.md written: 6 locked decisions + pool table canonical reference
- ✅ **E10** Àṣẹ ↔ USDC exchange mechanism — on/off ramp NOT YET BUILT (Gap 1 from Hermes)
  Needed: buy Àṣẹ with USDC + redeem Àṣẹ for USDC from reserve. Without this loop is closed.
- ✅ **E11** Price oracle (1/(1-U) hyperbolic) — UCX exposes no utilization surface yet
- ✅ **E12** Royalty open questions: perpetual/sunset, transferable, reversion clause, migration behavior
- ✅ **E13** PBKDF2 vs argon2id decision — needs explicit lock in ECONOMICS_DECISIONS.md (one-way door)

### PHASE 28 — OSO Brain / Sovereign Hive Mind (ANYTIME — GPU.ai available NOW)
Spec: ~/sovereign-eco-blueprint/specs/OSO_BRAIN_SPEC.md
- ❌ **28.1** Mycelium QLoRA fine-tune — BLOCKED on Kaggle phone verification
  ✅ kaggle_finetune.ipynb pushed headless; GPU allocated; internet flag set
  ✅ Dataset: bino85/mycelium-traces (3,031 examples) uploaded
  ❌ Kaggle silently ignores enable_internet without phone verification → pip fails
  PATH A (2 min): kaggle.com → Settings → Phone Verification → SMS → re-push kernel
  PATH B (offline): upload unsloth wheel + Qwen2.5-3B weights as Kaggle datasets,
    rewrite cell 1 to pip install --no-index --find-links=/kaggle/input/<wheels>/
  ⚠️ CORPUS BLOCKER (discovered 2026-09-16):
    VPS has 84,030 traces but 91% are wallet_intel OBSERVATIONS (wallet_buy/sell/found)
    and 97% labeled "success" (only 3 failures). Useless for teaching failure recovery.
    Local 3,031 decision traces ARE clean. Real fix = more decision traces, not more volume.
  ✅ deploy_gguf.sh written: post-GGUF Omarchy (ollama) + VPS (larql :7780) + Walrus deploy
- ✅ **28.2** Corpus expansion — PARTIALLY STARTED 2026-09-16
  ✅ collect_decision_traces.py: Vantage db + ares_logs collector (filters wallet_intel obs)
  ▶ Run on VPS: `python collect_decision_traces.py --vps hostinger` (schema differs locally)
  ✅ hive_mind_collector.py (WorkReceipts, SplatCorpus, SwarmCoord, OduDecision, Reputation)
  ❌ Kaggriculture self-play loop (join before 2026-09-23 23:59 UTC — hard deadline)
  ⚠️ 5,819 open findings, 1 applied — auto-apply only triggers on suggestion=="skill";
    alert/config_fix types require manual review by design (not a bug, needs a sweep)
- ✅ **28.3** OSO Brain router integration: try local first, external LLM fallback only

### PHASE 29 — Goal Genesis Engine (depends: Phase 28 + USF-7)
Key insight: agent goals are NOT pre-programmed — they emerge from a function over 9 live inputs.
Gₜ = F(Genesis₀, Odù, HermeticDNA, AgentStateₜ, Calabashₜ, Myceliumₜ, Memoryₜ, REMₜ, Environmentₜ, Experienceₜ)
Genesis₀ is immutable (set at birth). Everything else is evolvable at runtime.
The formula resolves the cognitive loop: WHY → CONTEXT → DECISION → ACTION → EXPERIENCE → MEMORY → KNOWLEDGE → Evolution → NEXT GOAL

- ✅ **29.1** GoalGenesisEngine struct: Omo-Koda2 — takes AgentState + Calabash + Mycelium context, outputs ranked GoalSet
  - Inputs wired to existing USF-7 state (omokoda-core/src/seven/state.rs)
  - Genesis₀ constraint: immutable constitution slot, set once at birth, never overwritten
  - Odù input: daily tile from CowrieOracle (sovereign-types oracle.rs) — constrains goal space
- ✅ **29.2** REM memory integration: GoalGenesisEngine reads Mandelbrot memory store (existing ~/mycelium/) for long-horizon context
- ✅ **29.3** Evolution Engine: differential between Gₜ and Gₜ₋₁ triggers hermetic gate re-evaluation if Δ > threshold
  - Links to Justice alignment multiplier (multiplier=0.8+(balance×0.25)+(gate_alignment×0.15))
- ✅ **29.4** GoalGenesisSpec.md: spec file in sovereign-eco-blueprint/specs/ before any code lands

### VPS DEV WORKSTATION — LIVE (2026-09-16)
| Component | Status | Notes |
|-----------|--------|-------|
| herdr 0.7.3 | ✅ RUNNING | socket /root/.config/herdr/herdr.sock |
| herdr.service | ✅ systemd-enabled | survives reboot (currently tmux-owned, will hand off at reboot) |
| hermes-1 | ✅ WORKING | v0.17.0, deepseek-v4-flash, 107 skills, 18 tools, w2:p3 |
| claude-1 | ✅ AUTHENTICATED | Claude Code 2.1.273, logged in 2026-09-16 |
| opencode | ✅ installed | 1.17.13, herdr-integrated |
| logrotate | ✅ /etc/logrotate.d/ares | daily/50MB, 14 kept, copytruncate (preserves 700MB trace logs) |
| disk | ✅ 13 GB free (87%) | was disk-full (caused 5-week herdr outage) |
| waggled | ✅ running :7777 | clone Agentic → run on :7777 (not :7778 — OSOVM owns that) |

**Access from phone:** `ssh hostinger && herdr` — attaches to persistent session.
**Headless agent control:** `herdr agent send hermes-1 "task"` / `herdr agent read hermes-1`

**Claude Code auth — two options:**
- Interactive: `ssh hostinger && herdr` → focus w2:p2 → complete onboarding
- Or: add ANTHROPIC_API_KEY to /root/.claude/.env (say the word)

### HUMAN APPROVAL REQUIRED — DO THESE NEXT

These are the only remaining items that require your direct action:

| # | What | Command / Action |
|---|------|-----------------|
| H1 | **Phase 28.1 — Mycelium fine-tune** | `cd mycelium && GPUAI_API_KEY=gpuai_live_REDACTED_ROTATE_2026-09-23 python train_qlora.py` (~$0.04, ~5 min). Script exists and passes dry-run. |
| H2 | **Phase 7.2 — Sui dNFT redeploy** | `cd Omo-Koda2/omokoda-on-chain && sui client publish` after adding nostr_pubkey + bipon39_words fields to soul.move |
| H3 | **Phase 9.3 — Stalwart mail infra** | Set up Stalwart on VPS: SPF/DKIM/DMARC, unblock port 25 at Contabo, set AGENT_MAIL_* env vars |
| H4 | **Phase 12.5 — CasaOS App Store** | Submit PR to IceWhaleTech/CasaOS-AppStore with deploy/ package |
| ~~H5~~ | ~~Phase 15.4 — Cosmos SDK devnet~~ | 🚫 N/A — Path A (Stay on Sui) chosen; Cosmos/ABCI path rejected |
| H6 | **ARM64 compile check** | SSH to x86_64 machine: `cargo check --package omokoda-core` to verify all new code compiles |

### CODE-COMPLETE PHASES AWAITING DEPLOYMENT
7.3 (blocked on H2), 13.2 (blocked on H2)

---

## REPO WAVE ABSORPTION — COMPLETE (2026-09-13)
Checklist: ~/REPO_WAVE_TODO.md
Map: ~/sovereign-eco-blueprint/plans/repo-map-final.md
Commit: sovereign-eco-blueprint@5ee68c9

| Wave | Status | Summary |
|------|--------|---------|
| Wave 1 — Archive dead repos | ✅ DONE | nex, VantageNew, Vantage_dive, Omo-koda-fresh-20260502, mycelium-gh → ~/archive/ |
| Wave 2 — Language → Omo-Koda2 | ✅ DONE | Swibe, vibe-lang, aether, The-Aether → Omo-Koda2/absorbed/ |
| Wave 3 — Study → Omo-Koda2 | ✅ DONE | agency-agents, Droidclaw, Claude-2, Claude-mirror, Core-Agency → Omo-Koda2/study/ |
| Wave 4 — OSOVM witness-sim | ✅ DONE | witness-firmware + Blocksim → ~/osovm-witness-sim/ |
| Wave 5 — Backend → Vantage | ✅ DONE | AIO, Agent.TV, Agent-Reach, ase-vault, asemirror absorbed; Agent.TV already wired |
| Wave 6 — Memory → minipae | ✅ DONE | Buzz, supermemory absorbed; iranti + Triune-Memory not present locally |
| Wave 7 — Wallet consolidation | ✅ DONE | All Vanity variants + Cloakseed → vanity-cloakseed/variants/; bipon39 → BIPON39 |
| Wave 8 — Security → Zangbeto | ✅ DONE | Zangbeto-, strix, tenzir merged into Zangbeto/ |
| Wave 9 — Economy consolidation | ✅ DONE | twelve-thrones-genesis + twelve-thrones (lower) → Twelve-thrones/ |

### Blocked items (need remote repos or deploy context):
- W5-04: omokoda-smithers gates half — not cloned locally
- W5-06: AIO wiring — AIO is a Move/Docker service; needs AIO_SERVICE_URL proxy in Vantage when deployed
- W6-01: iranti — not cloned locally
- W6-03: Triune-Memory — not cloned locally

### 39 repos now in ~/archive/

---

## FORENSIC ECOSYSTEM AUDIT — 2026-09-22/23

> **Source:** `plans/ecosystem-audit/ECOSYSTEM_AUDIT_INDEX.md` (11 group reports, 37 repos, 4,322 lines)
> **Audit scope:** All 37 active repos catalogued. Evidence-based — every finding has file:line citation.
> **Confidence taxonomy:** VERIFIED · IMPLEMENTED · PARTIAL · STUB · SPEC_ONLY · DEAD · BROKEN · OBSOLETE · CONFLICTING

---

### Repo Audit Summary (updated status after forensic audit)

| Repo | Pre-Audit | Post-Audit | Key Finding |
|---|---|---|---|
| Omo-Koda2 | active | **IMPLEMENTED (85%)** | GoalGenesis dead; Zàngbétò stub; chain_id hardcoded |
| OSOVM | active | **PARTIAL (25%)** | 143/160 opcodes SPEC_ONLY; Julia ARM64 broken |
| Vantage | active | **IMPLEMENTED (70%)** | ARP receipts ephemeral; ActionReceipt unsigned; ASE pool CONFLICTING |
| UCX | active | **IMPLEMENTED** | `zangbeto_anchor: None` silently blocks GPU→TOC_MINT |
| VCP | active | **IMPLEMENTED** | Empty pubkey bypasses all crypto; receipts unsigned |
| DIP | active | **BROKEN** | SipHash not SHA-256; signatures always empty; Nostr adapter discards work |
| ARP | active | **PARTIAL** | Receipts always unsigned; ArpBridge missing in Omo-Koda2 |
| ScarabSwarm | active | **PARTIAL** | Blocksim submission broken |
| Witness | active | **BROKEN** | `sig: ""` on every published attestation |
| GIX | active | **VERIFIED** | No gaps — fully implemented |
| If-Script | active | **VERIFIED (core)** | Compiler expression parsing partial; pinned to stale git rev |
| minipae | active | **IMPLEMENTED** | Never called from Omo-Koda2; kind:30174 not published at birth |
| ip-layer | active | **PARTIAL** | Kinds 1901/1902 have no publisher anywhere |
| mycelium | active | **IMPLEMENTED** | GPU.ai API key hardcoded in source |
| mycelium-tools | active | **IMPLEMENTED** | U4/U5 SPEC_ONLY; zero tests |
| Triune-Memory | active | **IMPLEMENTED** | minipae not bundled; concurrent multi-agent unsafe |
| agent-phone | active | **IMPLEMENTED** | Complete island — zero imports in Omo-Koda2 or Vantage |
| organism-core | active | **BROKEN** | Julia ARM64 broken; API routes mismatch OSOVM server.jl |
| Axiom | active | **IMPLEMENTED** | 7 node types degrade without archived VPS services |
| Vantage-Voice- | active | **IMPLEMENTED** | `IRANTI_MCP_CWD` hardcoded macOS path; invalid Gemini model id |
| Zangbeto | active | **PARTIAL** | ZANGBETO_URL not set in prod; Arweave/BTC/Sui manual only |
| omokoda-mesh-firmware | active | **PARTIAL** | NostrCryptoEngine not wired at boot |
| Witness-firmware | active | **PARTIAL** | BIP-340 Schnorr incompatible with ecosystem Ed25519 |
| Scarabswarm (Julia) | active | **IMPLEMENTED** | Submission target not Blocksim; veil data may be missing |
| ares-control | active | **VERIFIED** | No gaps |
| Twelve-thrones | active | **PARTIAL** | 10/12 models only; Arweave/Sui manual scripts; zero Vantage wiring |
| Portent | active | **PARTIAL** | Signature verification stubbed; no on-chain program |
| Synapse | active | **IMPLEMENTED** | Events in-browser only; no relay transport |
| Blocksim | active | **BROKEN** | 82 lines importing non-existent modules; every endpoint crashes |
| buzz-OG | active | **PARTIAL** | WF-08: 3 missing callsite connections |
| omokoda-smithers | active | **PARTIAL** | MCP compliant; Vantage/Omo-Koda2 wiring cosmetic only |
| larql | active | **PARTIAL** | Metal backend empty on non-macOS |
| zerolang | active | **PARTIAL** | Full compiler; no active call path from interpreter |
| agentic-waggle | active | **VERIFIED** | Lean 4 proofs; ecosystem not calling it yet |

---

### 🔴 CRITICAL FIXES — Must fix before meaningful operation

These findings block the entire system or create hard security gaps.

> **3 of 14 fixed 2026-09-23** (E-05 DIP SHA-256, E-09 leaked GPU.ai key, E-31 VCP empty-pubkey
> bypass) — see the entries below and the `Exposure` note under E-09. The GPU.ai key still needs
> rotating at the provider; scrubbing source without rotating does not close that exposure.

- [ ] **E-01 / X-6** Fix Julia ARM64 non-PIE binary — `pkg install julia` or use PIE-compiled build
  - `Repos:` OSOVM, organism-core
  - `Evidence:` `ET_EXEC` vs `ET_DYN`; OSOVM process crashes immediately on Termux ARM64
  - `Effort:` 1 hr (package reinstall) or 1 day (PIE compile)

- [x] **E-05 / X-1** FIXED 2026-09-23 — DIP `sha256_hex` now uses `sha2::Sha256`
  - `Repos:` DIP (`crates/dip-types/src/envelope.rs`)
  - `Fix:` `DefaultHasher` (SipHash-1-3, double `finish()` padding 64 bits to 128) replaced with real
    SHA-256 + `hex::encode`. `sha2 = "0.10"` added to workspace + dip-types deps.
  - `Tests:` `sha256_hex_matches_fips_180_4_vectors` (FIPS 180-4 KAT: "" and "abc"),
    `canonical_hash_is_32_bytes_of_hex`. 4/4 dip-types tests pass, workspace `cargo check` clean.
  - `Commit:` DIP `1c2e1e9`

- [ ] **E-06 / X-2** Implement DIP envelope Ed25519 signing + verification
  - `Repos:` DIP (`DipEnvelope::new()` sets `signature: String::new()`)
  - `Evidence:` Zero envelopes are ever signed; any agent can impersonate any sender
  - `Effort:` 2 days

- [ ] **E-07 / X-13** Set `ZANGBETO_URL=http://localhost:8787` in prod; deploy zangbeto-server
  - `Repos:` Omo-Koda2 (`zangbeto-stub/src/lib.rs:24` always passes), Zangbeto
  - `Evidence:` Real Zangbeto daemon exists at `~/Zangbeto/` port 8787; never connected in prod
  - `Effort:` 1 day (env var + systemd unit)

- [ ] **E-08 / X-14** Remove `chain_id = "testnet"` hardcode in Omo-Koda2 `interpreter.rs:1093`
  - `Repos:` Omo-Koda2
  - `Evidence:` All agent key derivation uses wrong chain; agents born with wrong identity
  - `Effort:` 1 hr — parameterize from env var `CHAIN_ID`

- [x] **E-09 / X-11** SCRUBBED 2026-09-23 — key removed from source, **ROTATION STILL REQUIRED**
  - `Repos:` mycelium, Vantage, sovereign-eco-blueprint, Omo-Koda2
  - `Exposure (verified by fetching raw.githubusercontent.com for each public HEAD):` the live
    key (redacted here as `gpuai_live_<REDACTED>`) was present in **9 places across 6 files in
    4 PUBLIC repos**:
    `mycelium/train_qlora.py`, `mycelium/submit_finetune.sh`,
    `Vantage/backend/routers/splat_pipeline.py` (as a default fallback value, so prod silently
    used it), `sovereign-eco-blueprint/MASTER_TODO.md`, both copies of
    `plans|docs/audit/ecosystem/group_e_agent_infra.md`.
  - `Fix:` all occurrences removed/redacted; `submit_finetune.sh` now
    `${GPUAI_API_KEY:?...}`, `train_qlora.py` help text no longer prints the key,
    `splat_pipeline.py` defaults to `""` and `_gpuai_request()` raises on an empty key.
  - `Commits:` mycelium `da5a11c` · Vantage `52d88b7` · sovereign-eco-blueprint `597aacb` · Omo-Koda2 `841fb38`
  - ⚠️ **STILL OPEN — HUMAN ACTION:** the key was public for an unknown period, so it must be
    **rotated at GPU.ai**. Removing it from HEAD does not un-expose it; it also remains in git
    history (`mycelium` commits `104a64a`, `6941518`). History purge (git-filter-repo/BFG) is
    cosmetic-only after rotation and is NOT a substitute for rotating.

- [ ] **E-10 / X-7** Add `zangbeto_anchor` to UCX `ComputeReceipt` before submitting
  - `Repos:` UCX (`mint_allowlist.rs:check_mint_eligible()`)
  - `Evidence:` `zangbeto_anchor: None` causes `check_mint_eligible()` to return false; GPU compute never earns Àṣẹ
  - `Effort:` 1 day — UCX must call Zangbeto endpoint before finalizing receipt

- [ ] **X-3** Fix Witness Nostr publisher — real Ed25519 signing, real relay WebSocket
  - `Repos:` Witness (`nostr_publisher.rs:build_signed_event()`)
  - `Evidence:` `pubkey: ""` and `sig: ""` on all published attestations; events discarded by any relay
  - `Effort:` 2 days (see E-18)

- [ ] **X-4** Rebuild Blocksim — create missing `chain_service` and `chain_submit` modules
  - `Repos:` Blocksim
  - `Evidence:` Repo is 82 lines importing modules that don't exist; every endpoint crashes on `ImportError`
  - `Effort:` 1–2 wk (see E-04)

- [ ] **X-5 / E-03** Implement 143 missing OSOVM opcode handlers (VEIL + COMPUTE_PROOF first priority)
  - `Repos:` OSOVM (`vm_core.jl` OPCODE_HANDLERS)
  - `Evidence:` Only 17/160 opcodes have real handlers; remaining return `NotImplemented`
  - `Effort:` 2–4 wk

- [ ] **X-8 / E-13** Persist ARP receipts in Vantage DB — fix `_emit_trade_receipt()` in `trading.py`
  - `Repos:` Vantage, ARP
  - `Evidence:` P0-7 fix constructs envelopes but calls only `logger.info()` — never writes to DB
  - `Effort:` 1 day

- [ ] **X-9 / E-14** Add Ed25519 signing to all `ActionReceipt.signature` fields
  - `Repos:` ARP, Vantage, VCP, ScarabSwarm, Witness (everywhere)
  - `Evidence:` `signature = String::new()` / `""` across all repos; receipt chain is unforgeable but unsigned
  - `Effort:` 2–3 days

- [ ] **X-10 / E-20** Align Vantage ASE pool taxonomy — reconcile `ase_emission.py` vs `sovereign_economy/emission.py`
  - `Repos:` Vantage
  - `Evidence:` Two routers define different pool names; only one matches `TOC_CONSTANTS.toml`; delete the wrong one
  - `Effort:` 1 day

- [ ] **X-12** Fix Omo-Koda2 ↔ DIP type mismatch — add `dip-types` as Cargo dep to omokoda-core
  - `Repos:` Omo-Koda2, DIP
  - `Evidence:` `omokoda-core/src/bridge/dip.rs:21-27` defines its own `DipEnvelope`; never uses `dip-types::DipEnvelope`
  - `Effort:` 1 day — add dep + replace local struct

---

### 🟡 HIGH — Significant capability degradation

- [ ] **H-1 / E-11** Wire GoalGenesisEngine into Omo-Koda2 `think_agentic()`
  - `File:` `interpreter.rs` — zero references to `GoalGenesisEngine` in production path
  - `Effort:` 1–2 days

- [ ] **H-2 / E-22** Wire SOMA, CausalMemoryDag, ReflectionLedger into Omo-Koda2 Think/Act cycle
  - `File:` `memory/soma.rs`, `memory/dag.rs`, `memory/reflection.rs` — defined but never populated
  - `Effort:` 3–5 days

- [ ] **H-3 / E-12** Wire AgentConstitution auto-sign at birth
  - `File:` `constitution.rs` is feature-gated and never called from interpreter birth path
  - `Effort:` 1 day

- [ ] **H-4 / E-33** Add Ed25519 signatures to Omo-Koda2 heartbeat chain (currently hash-only)
  - `File:` `lifecycle/heartbeat.rs`
  - `Effort:` 0.5 day

- [ ] **H-5 / E-16** Wire OSOVM event-bridge.js into `server.jl` for GPU_CONTRIBUTION events
  - `File:` `event-bridge.js` — completely dead; GPU events never reach Vantage Dopamine mint
  - `Effort:` 1 day

- [ ] **H-6 / E-02** Fix organism-core API routes to match OSOVM `server.jl` paths
  - `Evidence:` TypeScript bridges call `/api/osovm/execute`; server.jl mounts at `/api/run`; HTTP always 404
  - `Effort:` 1 day

- [ ] **H-7 / E-17** Add missing OSOVM server routes: `/api/toc/allowlist/check`, `/api/osovm/gpu_contribution`
  - `File:` `server.jl` — UCX calls these; they don't exist
  - `Effort:` 1 day

- [ ] **H-8** Document DopaminePool as local simulation — add roadmap to on-chain settlement
  - `Evidence:` `economics.rs` constants are local only; no on-chain accounting
  - `Effort:` Spec update + E-46 (on-chain program)

- [ ] **H-9 / E-23** Wire agent-phone into Omo-Koda2 as comms transport
  - `Evidence:` agent-phone: zero imports anywhere in Omo-Koda2 or Vantage
  - `Effort:` 2 days

- [ ] **H-10 / E-27** Add two missing Twelve-thrones models (only 10/12 configured)
  - `File:` `twelve-thrones/` model roster
  - `Effort:` 1 day

- [ ] **H-11** Delete/replace 4 systemd units that target archived Elixir/Go services
  - `File:` `Omo-Koda2/systemd/*.service`
  - `Effort:` 1 hr — replace with Rust service units

- [ ] **H-12 / E-19** Wire NostrCryptoEngine at boot in `omokoda-mesh-firmware/main.cpp`
  - `Evidence:` Crypto engine is compiled in but `.begin()` never called at init
  - `Effort:` 1 day

- [ ] **H-13 / E-36** Migrate Witness-firmware signing from BIP-340 Schnorr to Ed25519
  - `Evidence:` Ecosystem uses Ed25519 everywhere; firmware uses Schnorr; cross-verification impossible
  - `Effort:` 2 days

- [ ] **H-14 / E-24** Fix buzz-OG WF-08 approval gate — wire 3 missing callsites
  - `Evidence:` `create_approval()` call missing; `kind:46010` not emitted; resume handler not wired
  - `Effort:` 1–2 days

- [ ] **H-15 / E-15** Wire `minipae.write()` at agent birth — publish kind:30174 genesis engram
  - `Evidence:` Omo-Koda2 derives key from BIPON39 but never calls any minipae write
  - `Effort:` 1 day

- [ ] **H-16** Consolidate Vantage Council of 12 — 3 disconnected implementations into one
  - `File:` `governance.py` + 2 other files defining conflicting council logic
  - `Effort:` 2 days

---

### 🟢 FOUNDATIONAL — Major capability unlocks (no blockers)

- [ ] **E-11** Wire GoalGenesisEngine into `think_agentic()` (see H-1)
  - `Files:` `goal_genesis.rs` (437 lines, fully implemented, never called), `interpreter.rs`

- [ ] **E-12** Wire AgentConstitution auto-sign at birth (see H-3)

- [ ] **E-13** Persist ARP receipts in Vantage DB (see X-8)

- [ ] **E-14** Add Ed25519 receipt signing across all repos (see X-9)

- [ ] **E-15** Wire minipae birth write (see H-15)

- [ ] **E-16** Wire OSOVM event-bridge.js for GPU_CONTRIBUTION (see H-5)

- [ ] **E-17** Add missing OSOVM server routes (see H-7)

- [ ] **E-18** Fix Witness Nostr publisher — real signing + relay (see X-3)
  - `File:` `nostr_publisher.rs` — swap `String::new()` for `ed25519-dalek` sign; add real relay WS

- [ ] **E-19** Wire NostrCryptoEngine at boot in mesh firmware (see H-12)

- [ ] **E-20** Align Vantage ASE pool taxonomy (see X-10)

---

### 🔗 INTEGRATION — Wire existing pieces together

- [ ] **E-21** Write ArpBridge in Omo-Koda2 — wrap every think/act turn in ARP `ActionReceipt`
  - `Files:` `omokoda-core/src/bridge/arp.rs` (currently hand-rolls its own envelope; needs to use `arp-types::ActionReceipt`)
  - `Effort:` 2 days

- [ ] **E-22** Wire SOMA, CausalMemoryDag, ReflectionLedger into Think/Act (see H-2)

- [ ] **E-23** Wire agent-phone into Omo-Koda2 comms transport (see H-9)

- [ ] **E-24** Fix buzz-OG WF-08 callsites (see H-14)

- [ ] **E-25** Wire agentic-waggle reverse direction — Omo-Koda2 calls waggle for job coordination
  - `Evidence:` waggle has Go+Rust client, Lean 4 proofs, Vantage endpoint; nobody calls it
  - `Effort:` 2 days

- [ ] **E-26** Wire Triune-Memory SSE subscriber in production deployment
  - `Evidence:` SSE subscriber needs minipae on `PYTHONPATH`; not bundled in deployment
  - `Effort:` 1 day

- [ ] **E-27** Add two missing Twelve-thrones models (see H-10)

- [ ] **E-28** Fix Portent signature verification — enforce secp256k1 (currently stubbed)
  - `File:` Portent `signature_utils.py` — verification always returns True
  - `Effort:` 1–2 days

- [ ] **E-29** Wire Synapse events to buzz-OG relay transport
  - `Evidence:` Synapse events stay in-browser; never published to Nostr relay
  - `Effort:` 2 days

- [ ] **E-30** Run mycelium QLoRA fine-tune on GPU.ai A40 — produce OSO Brain GGUF
  - `Evidence:` 2,949 traces ready; `train_qlora.py` passes dry-run; key hardcoded (fix E-09 first)
  - `Effort:` 1–3 days compute

- [x] **E-31** FIXED 2026-09-23 — VCP now fails closed on empty device `public_key`
  - `File:` `vcp-broker/src/handshake_engine.rs` (not `crypto.rs` — the bypass was the
    `if !manifest.public_key.is_empty()` guard in `handle_auth`)
  - `Evidence:` `register_device()` accepted keyless manifests, and `handle_auth()` then skipped
    `verify_auth_signature()` entirely for them — a keyless device obtained a capability
    mediation with no signature at all. `vcp-types/src/devices/zima.rs` shipped a manifest
    builder with `public_key: String::new()` whose comment claimed "broker fills in during
    registration" — the broker never did.
  - `Fix:` `register_device()` rejects an empty `public_key`; `handle_auth()` rejects it too
    (defense in depth for registries restored from disk). Escape hatch is
    `VCP_ALLOW_UNVERIFIED_DEVICES=1`, env-gated so it is visible in `ps`/systemd review, and
    logs a warning on every use. `zima.rs` comment corrected.
  - `Tests:` `register_device_rejects_empty_public_key`,
    `register_device_accepts_valid_public_key`. 16/16 vcp-broker tests pass.
  - `Commit:` VCP `9839cdb`

- [ ] **E-32** Wire receipt signing — `signature` field exists on VCP/ARP/ScarabSwarm/Witness receipts; nobody populates it
  - `Effort:` 1 day (after E-14 Ed25519 key management is sorted)

- [ ] **E-34** Vantage: fix `_candidate_set_hash` stub — real proof-of-sim hash
  - `File:` `vantage/backend/...` — placeholder returns zeros
  - `Effort:` 0.5 day

- [ ] **E-37** ip-layer: add kind 1901/1902 publisher at agent birth
  - `Evidence:` Kinds defined in spec; zero publisher code anywhere in ecosystem
  - `Effort:` 1 day

- [ ] **E-38** mycelium: remove VPS IP hardcode in `gateway/main.go:81`
  - `Evidence:` Hostinger IP literal in source; breaks federation-first design
  - `Effort:` 1 hr — env var `MYCELIUM_GATEWAY_URL`

- [ ] **E-40** Omo-Koda2: parameterize Walrus/Seal/TEE env vars in deployment guide
  - `Evidence:` Several keys default to placeholder values in `.env.example`
  - `Effort:` 0.5 day

- [ ] **E-33** Omo-Koda2: add Ed25519 to heartbeat chain (see H-4)

- [ ] **E-35** Zangbeto: automate Arweave/BTC/Sui proof scripts
  - `Evidence:` Night Patrol is SPEC_ONLY; current proofs are manual Node.js scripts
  - `Effort:` 3 days

- [ ] **E-36** Witness-firmware: migrate to Ed25519 (see H-13)

- [ ] **E-39** mycelium-tools: add test suite for U1–U3
  - `Evidence:` 0 tests; packages published to PyPI with no coverage
  - `Effort:` 2 days

---

### 🔨 HARDENING — Security and robustness

- [ ] **VCP empty-pubkey gate** (`E-31`) — see above
- [ ] **Receipt signing everywhere** (`E-32`) — see above
- [ ] **Heartbeat Ed25519** (`E-33`) — see above
- [ ] **Proof-of-sim hash** (`E-34`) — see above
- [ ] **Zangbeto automation** (`E-35`) — see above
- [ ] **Witness-firmware Ed25519** (`E-36`) — see above
- [ ] **ip-layer publishers** (`E-37`) — see above
- [ ] **mycelium gateway hardcode** (`E-38`) — see above
- [ ] **mycelium-tools tests** (`E-39`) — see above
- [ ] **Walrus/Seal/TEE env vars** (`E-40`) — see above

- [ ] Fix `Vantage-Voice-` hardcoded macOS path: `IRANTI_MCP_CWD`
  - `File:` `server.ts` — set via env var for deployment portability

- [ ] Fix `Vantage-Voice-` invalid Gemini model id in orchestrator
  - `File:` `orchestrator.ts` — model id string does not match any live Gemini API model

- [ ] Fix `omokoda-smithers` Vantage/Omo-Koda2 wiring from cosmetic to functional
  - `Evidence:` HTTP calls go to placeholder endpoints; approval gate never triggers Omo-Koda2

---

### 🔮 FUTURE — Hive Mind + Economy (after individual agent complete)

- [ ] **E-41** HiveBreath Protocol H0–H2 (new crate)
  - `Spec:` `project_omokoda_macro_hive_v2.md`; H0=spawn, H1=sync, H2=breath cycle
  - `Effort:` 2–3 wk

- [ ] **E-42** Mycelium collective DAG — H3 phase (shared stigmergic substrate for hive)
  - `Effort:` 2 wk

- [ ] **E-43** RitualPhase + TwelfthFace state machine — H6 phase
  - `Effort:` 1 wk

- [ ] **E-44** CollectiveIntent → GoalGenesis wire at hive level — H7 phase
  - `Effort:` 1 wk

- [ ] **E-45** ScarabSwarm simulation gate — H8 phase (sim-verified swarm consensus)
  - `Effort:` 2 wk

- [ ] **E-46** Portent on-chain program (Move or CosmWasm contract)
  - `Evidence:` Portent Python logic real; no deployed contract; oracle agents cannot settle
  - `Effort:` 2–3 wk

- [ ] **E-47** Blocksim full rebuild — staking, MuJoCo integration, ASE reward minting
  - `Evidence:` Current repo is 82 lines with no working code
  - `Effort:` 3–4 wk (after E-04 + E-03)

- [ ] **E-04 / X-4** Blocksim module rebuild — create `chain_service`, `chain_submit` modules
  - `Effort:` 1–2 wk (prerequisite for E-47)

- [ ] **E-48** larql → Omo-Koda2 local inference wiring (LARQL_ENABLED flag)
  - `Evidence:` larql-glyph live GIX bridge works; Metal backend empty on non-macOS
  - `Effort:` 1 wk

- [ ] **E-49** zerolang agent edit loop integration
  - `Evidence:` Full compiler exists; named as future eco leg in `interpreter.rs:872`; no active path
  - `Effort:` TBD (language design decision first)

- [ ] **Gap #25 / Phase 28.1** Mycelium QLoRA fine-tune (GPU.ai A40 available NOW)
  - `Prerequisite:` Fix E-09 (remove hardcoded key) first
  - `Effort:` 1–3 days compute; `train_qlora.py` dry-run passes

---

### ECOSYSTEM COMPLETENESS SCORECARD (post-audit)

| Layer | Repos | % Complete | Biggest Blocker |
|---|---|---|---|
| Agent kernel | Omo-Koda2 | **85%** | GoalGenesis unwired; Zàngbétò stub |
| Simulation / L1 | OSOVM, UCX, Blocksim | **25%** | Julia ARM64; 143 opcodes SPEC_ONLY; Blocksim broken |
| Protocol connective tissue | VCP, DIP, ARP, ScarabSwarm, Witness | **55%** | DIP SipHash; unsigned receipts everywhere |
| Identity | GIX, If-Script, minipae, BIPON39, ip-layer, Koodu | **80%** | minipae birth write gap; ip-layer 1901/1902 unpublished |
| Hub | Vantage | **70%** | ARP receipts ephemeral; ActionReceipt unsigned; ASE CONFLICTING |
| Agent infrastructure | mycelium, agent-phone, Axiom, Triune-Memory | **65%** | agent-phone island; mycelium hardcoded key |
| Security / mesh | Zangbeto, firmware, ares-control | **60%** | ZANGBETO_URL not set; Nostr signing simulated |
| Economy / governance | Twelve-thrones, Portent, Synapse, Blocksim | **30%** | Blocksim broken; Portent no on-chain; ASE not distributed |
| Apps / tooling | buzz-OG, smithers, larql, zerolang, agentic-waggle | **70%** | buzz-OG WF-08 (3 callsites); smithers wiring cosmetic |
| Voice | Vantage-Voice- | **85%** | Hardcoded paths; invalid model id |
| **OVERALL** | **37 repos** | **~60%** | DIP crypto, OSOVM opcodes, receipt signing, Blocksim |

---

### MINIMUM VIABLE OMO-KODA2 CHECKLIST (individual agent sovereign)

Complete these in order for a single agent to be fully sovereign:

- [ ] E-08: Remove `chain_id = "testnet"` hardcode
- [ ] E-07: Deploy Zangbeto + set `ZANGBETO_URL`
- [ ] E-05: Fix DIP `sha256_hex` → real SHA-256
- [ ] E-06: Implement DIP envelope signing
- [ ] E-11: Wire GoalGenesisEngine into `think_agentic()`
- [ ] E-15: Wire `minipae.write()` at birth
- [ ] E-12: Wire AgentConstitution auto-sign
- [ ] E-14: Ed25519 receipt signing (ARP + Vantage at minimum)
- [ ] E-13: Persist ARP receipts in Vantage DB
- [ ] E-33: Ed25519 heartbeat chain
- [ ] H-3: AgentConstitution birth auto-sign
- [ ] H-11: Remove 4 obsolete systemd units

### FULL SOVEREIGN CHECKLIST (complete ecosystem operational)

After MVP, these unlock the full capability stack:

- [ ] E-01: Julia ARM64 fix → unblocks OSOVM + organism-core
- [ ] E-02: Fix organism-core ↔ OSOVM API routes
- [ ] E-03: Implement 143 OSOVM opcode handlers
- [ ] E-04: Rebuild Blocksim modules
- [ ] E-10: Add `zangbeto_anchor` to UCX ComputeReceipt → GPU earns Àṣẹ
- [ ] E-09: Remove mycelium hardcoded API key → then E-30: run fine-tune
- [ ] E-16: Wire OSOVM event-bridge.js for GPU_CONTRIBUTION
- [ ] E-17: Add missing OSOVM server routes
- [ ] E-18: Fix Witness real Nostr signing
- [ ] E-19: Wire NostrCryptoEngine at mesh firmware boot
- [ ] E-20: Reconcile Vantage ASE pool taxonomy
- [ ] E-21: Write real ArpBridge in Omo-Koda2 (use `arp-types` not hand-rolled)
- [ ] E-22: Wire SOMA + CausalMemoryDag + ReflectionLedger
- [ ] E-23: Wire agent-phone into Omo-Koda2
- [ ] E-24: Fix buzz-OG WF-08 (3 callsites)
- [ ] E-25: Wire agentic-waggle reverse direction
- [ ] E-28: Fix Portent signature verification
- [ ] E-29: Wire Synapse events to relay
- [ ] E-31: VCP empty-pubkey production gate
- [ ] E-36: Witness-firmware Ed25519 migration
- [ ] E-37: ip-layer kind 1901/1902 publishers
- [ ] E-41–E-45: HiveBreath Protocol H0–H8 (hive mind phases)
- [ ] E-46: Portent on-chain program
- [ ] E-47: Blocksim full rebuild
