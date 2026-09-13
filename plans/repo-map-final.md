# SOVEREIGN ECOSYSTEM — COMPLETE REPO MAP (CANONICAL FINAL)
# Last updated: 2026-09-13
# Source of truth for all 94+ repos, categories, absorption verdicts, wave order

---

## PILLAR 1 — OMO-KODA2
Canonical: ~/Omo-Koda2 | Rust OS Kernel

| Repo | Action | Notes |
|------|--------|-------|
| Omo-Koda2 | CANONICAL | Rust kernel — lifecycle, compute, security, device |
| Omokoda | STANDALONE | Sui Move + agent runtime; independent identity |
| omokoda-core | STANDALONE | PlatformIO embedded/IoT hardware layer |
| Axiom | STANDALONE | Formal reasoning app for Omo-Koda2 |
| Swibe | absorb | Agent social/comms layer |
| vibe-lang | absorb | Agent DSL → lang/vibe/ |
| aether / The-Aether | absorb | 3-primitive AI pet language → lang/aether/ |
| omokoda-smithers (SkillForge half) | absorb | Skill registration → skills/forge/ |
| agency-agents | absorb (study) | Open-source agent framework reference |
| Droidclaw / droidclaw | absorb (study) | Mobile agent CLI tool reference |
| Claude-2 | absorb (study) | Claude 2 era architecture study |
| Claude-mirror | absorb (study) | Claude UI frontend mirror |
| Core-Agency | absorb (study) | Agent framework study |
| Omo-koda-fresh-20260502 | ARCHIVE (Wave 1) | May 2026 backup snapshot |

---

## PILLAR 2 — OSOVM ECOSYSTEM
Canonical: ~/OSOVM | Julia VM — 3-Repo Ecosystem

| Repo | Action | Notes |
|------|--------|-------|
| OSOVM | CANONICAL | Julia VM: opcodes, ComputeProof, ToC mint, simulation runner |
| ScarabSwarm / Scarabswarm | STANDALONE | 100k-trajectory proof-of-sim; OSOVM ecosystem peer |
| witness-firmware + Blocksim/blocksim-repo | COMBINE → osovm-witness-sim (Wave 4) | Hardware attestation + deterministic sim |
| SwarmIDE2 / swarmide2 | STANDALONE | IDE for swarm orchestration |
| NarratorIDE | STANDALONE | Narrative/reasoning IDE service |

---

## PILLAR 3 — VANTAGE
Canonical: ~/Vantage | Python Backend Nervous System

| Repo | Action | Notes |
|------|--------|-------|
| Vantage | CANONICAL | All routers: heartbeat, UCX/Dopamine, trading, cinema, mesh, ARP |
| Vantage-Voice- | STANDALONE | Voice pipeline connecting all 3 pillars |
| AIO | absorb (Wave 5) | All-in-one orchestration → routers/aio/ |
| Agent.TV | absorb (Wave 5) | Cinema streaming → cinema/agent_tv/ |
| Agent-Reach | absorb (Wave 5) | Agent outreach/broadcast → routers/reach/ |
| omokoda-smithers (approval gates half) | absorb (Wave 5) | Proposal/approval logic → governance/gates/ |
| ase-vault / asemirror | absorb (Wave 5) | ASE vault UI + mirror dashboard |
| VantageNew | ARCHIVE (Wave 1) | Superseded build |
| Vantage_dive | ARCHIVE (Wave 1) | Exploration branch |

---

## SOVEREIGN STACK
Canonical: ~/sovereign-stack | 14-Crate Rust Protocol Workspace

Crates: dip, vcp, twin-protocol, ip-layer, arp-types, arp-broker,
        ucx-protocol, ucx-provider, ucx-broker, swarm-types, swarm-broker,
        witness-types, witness-broker, sovereign-pipeline, sovereign-a2a,
        sovereign-node, sovereign-cli, sovereign-os, mycelium-finetune

| Repo | Action | Notes |
|------|--------|-------|
| ip-layer (standalone repo) | STANDALONE | Independent git history; mirrors crate |
| ARP / DIP / VCP / UCX | standalone workspaces | Pre-integration standalone versions; keep |

---

## GRAPH CATEGORY
Canonical: ~/Nex- | TypeScript graph runtime; 7 Hermetic/Orisha primitives; v1.0

| Repo | Action | Notes |
|------|--------|-------|
| Nex- | CANONICAL | src/ has bridges/compiler/guards/primitives/runtime/types |
| zerolang | STANDALONE | C graph-native language |
| larql | STANDALONE | Transformer weight graph queries |
| ares_graph | STANDALONE | Entity graph query bridge |
| code-review-graph | STANDALONE | Code review graph tooling |
| nex | ARCHIVE (Wave 1) | Pre-1.0 version |

---

## SECURITY LAYER
Canonical: ~/Zangbeto

| Repo | Action | Notes |
|------|--------|-------|
| Zangbeto | CANONICAL | Smart contract red-team, Arweave receipts, BTC OTS proofs |
| Zangbeto- | absorb (Wave 8) | Fork/variant → merge into canonical |
| Evil-twin / evil-twin | STANDALONE | Adversarial twin / MITM security tool |
| GuardianPact | STANDALONE | Smart contract guardian pacts |
| strix | absorb (Wave 8) | Threat scanner pipeline |
| tenzir | absorb (Wave 8) | Threat intel ingestion |

---

## MEMORY LAYER — minipae
Canonical: ~/minipae | Nostr kind 30174 memory mesh

| Repo | Action | Notes |
|------|--------|-------|
| minipae | CANONICAL | Nostr kind 30174 memory mesh |
| iranti / Buzz | absorb (Wave 6) | Buzz memory mesh — NIP kinds 36000–36003 |
| Triune-Memory | absorb (Wave 6) | Episodic/semantic/procedural orchestrator |
| supermemory | absorb (Wave 6) | External memory API integration |

## MEMORY LAYER — mycelium
Canonical: ~/mycelium | STANDALONE

| Repo | Action | Notes |
|------|--------|-------|
| mycelium | STANDALONE | Go gateway + stigmergic trace substrate |
| mycelium-gh | ARCHIVE (Wave 1) | GitHub mirror; superseded |

---

## MESH / NETWORK

| Repo | Action | Notes |
|------|--------|-------|
| Reticulum | CANONICAL | Rust — LoRa/Meshtastic mesh protocol |
| omokoda-mesh | STANDALONE | Omo-Koda2 mesh networking module |
| omokoda-mesh-os | STANDALONE | Rust mesh OS variant |
| freenet-core | STANDALONE | Freenet P2P decentralized routing |
| OmniRoute | STANDALONE | Multi-protocol routing engine |
| herdr | STANDALONE | Go mesh routing/control |
| herdr-lite-go | STANDALONE | Lightweight Go mesh node |
| oniux | STANDALONE | Network isolation layer |

---

## OH-MY-PI STACK
Canonical: ~/oh-my-pi

| Repo | Action | Notes |
|------|--------|-------|
| oh-my-pi | CANONICAL | Pi homelab OS — Caddyfile, NIPS/, self-hosted services |
| peaq-network-node | STANDALONE | Peaq blockchain node for homelab sovereignty |
| ares-habitat | STANDALONE | Ares runtime environment |
| ares-control | STANDALONE | Go Ares control plane |
| TempleOS | reference | Terry Davis OS — architecture study |

---

## LANGUAGE / SCRIPTING

| Repo | Action | Notes |
|------|--------|-------|
| If-Script / Ifascript | STANDALONE | Ifá divination scripting language |
| Koodu | STANDALONE | Code-native agent scripting |
| ritual-codex | STANDALONE | Yoruba/Ifá ritual logic codex |

---

## IDENTITY / WALLET / CRYPTOGRAPHY

| Repo | Action | Notes |
|------|--------|-------|
| BIPON39 / BIP-N39 | CANONICAL | BIP-39 sovereign wallet identity |
| bipon39 | absorb (Wave 7) | Lowercase variant → BIPON39 |
| vanity-cloakseed | CANONICAL | Vanity address + seed cloaking |
| Vanity / vanity / vanity-eth-pro / vanity2 / vanity-check / Vanity-eth- | absorb (Wave 7) | All variants → vanity-cloakseed |
| Cloakseed | absorb (Wave 7) | Seed cloaking → vanity-cloakseed |
| Sign-wise / sign-wise | STANDALONE | Cryptographic signing protocol |
| agent-phone | STANDALONE | Mobile agent interface |
| OpenPhone | STANDALONE | Open-source phone layer |

---

## ECONOMY / GOVERNANCE

| Repo | Action | Notes |
|------|--------|-------|
| Synapse | STANDALONE | Synapse token UI/dashboard — 86M pool |
| Twelve-thrones / twelve-thrones | CANONICAL | Governance contracts; Council of 12 onchain |
| twelve-thrones-genesis | absorb (Wave 9) | Genesis deployment → Twelve-thrones |
| world-dutch-auctions | STANDALONE | Dutch auction market mechanism |
| decentralized-tournaments | STANDALONE | Onchain tournament system |
| Portent | STANDALONE | Prediction/oracle (agent + contracts + relay) |
| ForgeVault | STANDALONE | Vault/forge for token mechanics |

---

## TRADING / FINANCE
Canonical: ~/TradingOS

| Repo | Action | Notes |
|------|--------|-------|
| TradingOS | CANONICAL | Full trading OS platform |
| AutoHedge | STANDALONE | Automated hedging strategies |
| Vibe-Trading | STANDALONE | Vibe-coded trading system |
| FinceptTerminal | STANDALONE | Financial terminal UI |
| Loom | STANDALONE | Transformer signal strategy + ML agents |
| Hyperliquid-Data-Layer-API | STANDALONE | Hyperliquid data layer |
| hermes-agent / hermes-trader | STANDALONE | Hermes trading agent pair |
| Harvard-Algorithmic-Trading-with-AI | reference/archive | Study |
| Limitless-Prediction-Market-Bots | reference/archive | Study |
| Polymarket-Trading-Bot-Examples-By-Moon-Dev | reference/archive | Study |
| Moon-Dev-AI-Trading-Battles | reference/archive | Study |
| MoneyPrinterTurbo | reference/archive | Study |
| Pumpfun_AI_Trading_Bot | reference/archive | Study |
| Trading-View-MCP-for-AI-by-Moon-Dev | reference/archive | Study |
| Short-crypto-to-0-trading-bot | reference/archive | Study |

---

## ORGANISM-CORE
Canonical: ~/organism-core | STANDALONE — 3-Pillar Bridge
12 TypeScript bridge files; 9 live, 3 stubs: ifa-veil-router, nex-graph-bridge, toc-evolve-hook

---

## SACRED / LORE / GAME

| Repo | Action | Notes |
|------|--------|-------|
| Sacred-cored-agency / sacred-core-agency | CANONICAL | Sacred Core SaaS — 10-session AI agency build |
| NeverEndingQuest | STANDALONE | Expo mobile quest/game app |
| arcane-realms | STANDALONE | Arcane realm game world |
| genesis-world | STANDALONE | Genesis world builder |
| Brahma-Echo | STANDALONE | Brahma AI framework |
| eternal-orisa-loom-v8 | STANDALONE | Orisha loom v8 system |
| trinity-genesis | STANDALONE | Trinity genesis protocol |

---

## OPEN SOURCE / EXTERNAL FORKS

| Repo | Notes |
|------|-------|
| LibreChat | LLM chat frontend |
| Open-LLM-VTuber | VTuber LLM integration |
| openagents | Open agent framework |
| deepagents | DeepSeek agent framework |
| deepseek-harness | DeepSeek test harness |
| crawl4ai | AI web crawling |
| llama.cpp | GGUF local inference |
| Claw-code / claw-code / openclaw | Code agent CLI tools |
| deepcode-cli | Deep code CLI |
| Claude-Code-main | Claude Code CLI source study |
| dify | Dify AI platform |
| pocketbase | PocketBase self-hosted backend |

---

## SOVEREIGN ECO-BLUEPRINT

| Repo | Notes |
|------|-------|
| sovereign-eco-blueprint | Architecture plans, full-ecosystem-map |
| sovereign-types | Shared Rust type crate |
| Technosis-Sovereign-Ecosystem | Ecosystem overview docs |

---

## WAVE ORDER (ABSORPTION + ARCHIVE SEQUENCE)

Wave 1 — Archive dead repos
  - nex (old Nex pre-1.0)
  - VantageNew (superseded)
  - Vantage_dive (exploration branch)
  - Omo-koda-fresh-20260502 (backup snapshot)
  - mycelium-gh (GitHub mirror)

Wave 2 — Language + comms → Omo-Koda2
  - Swibe → Omo-Koda2/social/
  - vibe-lang → Omo-Koda2/lang/vibe/
  - aether / The-Aether → Omo-Koda2/lang/aether/

Wave 3 — Study repos → Omo-Koda2/study/
  - agency-agents
  - Droidclaw / droidclaw
  - Claude-2
  - Claude-mirror
  - Core-Agency

Wave 4 — OSOVM: combine witness-firmware + Blocksim → osovm-witness-sim
  - Create ~/osovm-witness-sim
  - Move/merge witness-firmware content
  - Move/merge Blocksim / blocksim-repo content
  - Archive originals

Wave 5 — Backend → Vantage
  - AIO → Vantage/routers/aio/
  - Agent.TV → Vantage/cinema/agent_tv/
  - Agent-Reach → Vantage/routers/reach/
  - omokoda-smithers (gates) → Vantage/governance/gates/
  - ase-vault / asemirror → Vantage/economy/ase/

Wave 6 — Memory → minipae
  - iranti / Buzz → minipae/memory/iranti/
  - Triune-Memory → minipae/memory/triune/
  - supermemory → minipae/integrations/supermemory/

Wave 7 — Wallet consolidation
  - Vanity / vanity / vanity-eth-pro / vanity2 / vanity-check / Vanity-eth- → vanity-cloakseed/variants/
  - Cloakseed → vanity-cloakseed/cloakseed/
  - bipon39 → BIPON39/

Wave 8 — Security → Zangbeto
  - Zangbeto- → Zangbeto/
  - strix → Zangbeto/scanners/strix/
  - tenzir → Zangbeto/ingestion/tenzir/

Wave 9 — Economy consolidation
  - twelve-thrones-genesis → Twelve-thrones/genesis/
