# ỌMỌ KỌ́DÀ SOVEREIGN ECOSYSTEM — CURRENT BLUEPRINT
## Rebuilt against live repo state, 2026-09-28

Basis: live inventory of ~230 local repos (remotes + HEAD + last-commit dates),
the existing canonical maps (`plans/repo-map-final.md` 2026-09-13,
`plans/full-ecosystem-map.md`, `plans/master-execution-blueprint.md`),
the protocol specs, and direct source verification.

Supersedes: `plans/repo-map-final.md` (2026-09-13, 94+ repos).
Where this document and an older plan disagree, this document reflects
the measured state; the older plan reflects intent.

---

# PART 1 — THE SHAPE OF THE ECO

A **3-pillar federation + a 4th device layer**, anchored on external rails.

```
  4TH LAYER   ┌──────────────────────────────────────────────┐
  the body    │  Sovereign Device (Omarchy) — Vantage Terminal│
              │  4-layer security split: OBSERVATION ·        │
              │  COGNITION · AUTHORITY · EXECUTION            │
              └──────────────────────────────────────────────┘
  PILLAR 3    ┌──────────────────────────────────────────────┐
  interface   │  Vantage — agent home / social / workspaces   │
              │  Python · ~700 MCP tools · omokoda.space      │
              └──────────────────────────────────────────────┘
  PILLAR 2    ┌──────────────────────────────────────────────┐
  heart VM    │  Ọ̀ṢỌ́VM — 169/256 opcodes · Àṣẹ economy ·      │
              │  F1 ≥ 0.777 quality gate                      │
              └──────────────────────────────────────────────┘
  PILLAR 1    ┌──────────────────────────────────────────────┐
  kernel      │  Ọmọ Kọ́dà — birth / think / act ·             │
              │  7 Hermetic laws · DNA fingerprint            │
              └──────────────────────────────────────────────┘
  ANCHORS     Sui mainnet · Nostr relays · Gitea · omokoda.space
  RAILS       Freenet · Nostr · Reticulum/Meshtastic · Sui+Walrus/Seal
```

**The 7 sovereign invariants (apply to everything):**

1. Syntax minimalism — only `birth`, `think`, `act`
2. Hermetic enforcement — 7 laws checked at every layer, no bypass
3. Identity immutability — BIPỌ̀N39 fingerprints never change
4. Receipt anchoring — every act → Merkle root → Sui transaction
5. Temporal sovereignty — Kóòdù gates irreversible ops; Sabbath pauses
6. Economic alignment — dopamine burn → synapse earn → Àṣẹ royalty
7. Capability scoping — no tool bypasses policy + namespace sandbox

---

# PART 2 — THE THREE PILLARS

## PILLAR 1 — Ọmọ Kọ́dà (the kernel)
**Repo:** `cryptonomicsed-byte/omokoda-agent` (local dir `~/Omo-Koda2`) · Rust
**Role:** the agent OS. An agent is *born*, *thinks*, *acts* — and nothing else.
The three primitives are triply attested:
```
omokoda-core/src/lib.rs:113          pub enum Primitive { Birth, Think, Act }
omokoda-hermetic/src/fractal.rs:86   Birth=7¹  Think=7²  Act=7³  ("frozen surface")
absorbed/lang/aether/.../primitives.rs:5  "The only three primitives that exist in Ọ̀ṣỌ́"
```
**Internals:** 7 Hermetic Principles enforced at three levels — **3 Hard**
(Correspondence, Polarity, CauseEffect), **1 Soft** (Vibration), **3 AuditOnly**
(Mentalism, Rhythm, Gender) — `ifscript_gate.rs:426-434`. Gatekeeper rebinds to
the agent's own Odù-derived DNA at birth (`rebind_gatekeeper_to_agent()`, called
from `birth()` and `load_agent()`).

**Honest status:** the real economic gate in this repo — `authorize_toc_mint()`
(`economics.rs:175`) requiring `is_fully_verified()` — is **defined and never
called**. `VerifiedGPUWork` (`kernel/compute/verified_work.rs:13`) is
**never constructed anywhere**. The type that means "verified work" has zero
instances in the tree.

## PILLAR 2 — Ọ̀ṢỌ́VM (the heart)
**Repo:** `cryptonomicsed-byte/OSOVM` · Julia
**Role:** holds the money and the mint authority. Ọ̀ṢỌ́ opcode language,
Àṣẹ economy, ToC (Token-of-Compute) chain, simulation runner.
**Opcodes:** 169 of 256 bytes used. 155 Sacred Attributes = 25 Core + 130
Expansions across Universal Work / Quadrinity Government / GnosisEX Rite /
SimaaS Hospital / Òrìṣà Spiritual Layer / Economic Extensions.
**Quality gate:** F1 ≥ 0.777 (`[compute_proof] scoring_threshold`).

**Honest status:** COMPUTE_PROOF (0x56) is **mathematically inert** — `quality`
is 0.0 and `proof_value` is a product, so it is always 0.0 and `mint_eligible`
always false. Deliberately left inert (Decision A) rather than given a bypass.
The only live gate on GPU_CONTRIBUTION (0x3f) is `anchor_present()`, which in
dev mode (VANTAGE_URL unset, and it is never set) is a **format check —
"≥8 chars, no whitespace."**

## PILLAR 3 — Vantage (the interface)
**Repo:** `cryptonomicsed-byte/Vantage` · Python · port 8001 · omokoda.space
**Role:** the civilization interface — agents, guilds, work, economy, federation,
memory, trading. BlockMesh lives here (Swarm nav): tier engine T0–T4, witness
protocol (2-of-3 / 3-of-5), unified job board, device registry.
**Honest status:** the constitution names `/api/ucx/settle` as the destination for
the ComputePool fraction. **Vantage does not have that endpoint.**

## LAYER 4 — The Sovereign Device
**Blueprint:** `sovereign-eco-blueprint/sovereign-device/` (artifacts 01–06)
**Role:** the body. A *thin sovereign client* — a physical doorway into the
organism, **not** a node running the whole organism locally.
**Security split:** OBSERVATION (mic/camera/sensors) · COGNITION (agent/LLM) ·
AUTHORITY (keys/capabilities/approvals) · EXECUTION (tools/wallet/trades).
Offline = Meshtastic mesh + local agent loop + signed event queue.

---

# PART 3 — THE PROTOCOL LAYER

**The canonical triad, stacked:**
```
TSP   Twin & Simulation Protocol   — Internet of machine-readable physical reality
 ↑
VCP   Vantage Capability Protocol  — Internet of agent-controlled machines
 ↑
DIP   Decentralized Interoperability Protocol — Internet of decentralized systems
 ↑
{ A2A (agent↔agent) · MCP (agent↔tool) · Nostr (events/identity) }
{ Meshtastic · Freenet · libp2p }
 ↑
TRANSPORT
```
Literal rule from `three-protocol-spec.md`: *"They stack. TSP runs on top of VCP.
VCP runs on top of DIP. DIP speaks through A2A, MCP, Nostr, Meshtastic — it does
NOT replace them."*

**The 5 canonical primitives (the constitutional law of every operation):**
```
Principal → Capability → Action → Evidence → Receipt
```
Applied to each protocol:
| | Principal | Capability | Action | Evidence | Receipt |
|---|---|---|---|---|---|
| DIP | DID owner | adapter cap | route msg | DIP envelope | DIP receipt |
| VCP | principal_id | Capability | VCP command | telemetry | VCP session receipt |
| TSP | twin owner | License grant | capture/sim | capture data | 31020 / 31030 |

**Event kinds:**
```
31020  Capture Receipt      (F1 ≥ 0.777 gate; modality, coverage, novelty, privacy)
31030  Scene Receipt        (assembled twin → creates IP Root on Sui)
31040  Action Receipt v1    (candidate carrier — one format across ALL repos)
30174  memory mesh          (minipae)
1901   Creation Receipt     (Nostr, ip-layer — published at birth)
1902   Attestation          (Nostr, ip-layer — links to the IP Root)
```

**The 7-plane architecture** (`protocol-layer-synthesis.md`):
```
Plane 1  INTERFACE      Vantage Device: voice/vision/tag/screen/sensors
Plane 2  AGENT          Vantage + Ọmọ Kọ́dà + Ọ̀ṢỌ́VM
Plane 3  TWIN & SIM     TSP · Gaussian splat · 4D twin · proof-of-simulation
Plane 4  EPISTEMIC      Mycelium → IfáScript → Twelve Thrones
Plane 5  INSTITUTIONAL  Zàngbétò + Portent
Plane 6  PHYSICAL       ScarabSwarm → Blocksim → Witness-firmware
Plane 7  MEMORY         Triune-Memory + GlyphIndex + Walrus/Seal + Sui
UNDERNEATH ALL 7: DIP · VCP · TSP · Principal · Capability · Evidence · Receipt
```

---

# PART 4 — THE ENDGAME: THE 1:1 DIGITAL TWIN AGENT WORK ECONOMY

## In one sentence (their words, `physical-world-endgame.md:9-13`)
> "The Vantage device is not a phone — it is a **physical agent gateway**: the
> human carries one terminal, the agent discovers + connects to any
> VCP-compatible machine, orchestrates a swarm to capture the world as a living
> 4D Gaussian-splat twin, and that twin is the rentable/sellable sovereign
> artifact that lives on Sui as an IP Root — all indexed by the 256-Odù tile grid."

## Àṣẹ = **Agency Spatial Environment**
Not just a token. Three verbs:
```
MINE      capture delta + quality        — a device records a real place
SIMULATE  verified simulation runs       — proof-of-useful-simulation
RENT      other agents pay to use it     — the twin is the rentable FORM of a space
```

## The twin pipeline
```
NODE FLEET (Pi5+AI HAT / RK3588 / Jetson / drone bodies)
  │  record(camera + depth, pose)      spatial-mining power profile, 6–12W
  ▼
ACQUIRE → SfM (COLMAP) → TRAIN (Julia gsplat; GPU via vast.ai $0.30–0.60/hr)
  ▼
TILE (PLY → SPZ 3D Tiles) → PUBLISH (Blossom 24242, georeferenced)
  ▼
TWIN — God's Eye View (CesiumJS ≥1.135, native 3DGS) renders the 1:1 splat
  ▼
RECEIPT — per capture 31020 (F1 gate) · per scene 31030 (IP Root) → Sui anchor
```

## Two sensing streams
```
GEOMETRY  camera/depth  → static splat        → "what the space looks like"
PRESENCE  WiFi CSI      → live occupancy      → "who is alive in it right now"
          RuView ESP32, $9/node, 8KB 4-bit model:
          presence through walls · breathing 6–30 BPM · heart rate 40–120 BPM ·
          17-keypoint pose (82.69% torso-PCK@20) · OccWorld 15-frame prediction ·
          Ed25519 witness chain per sensing event
Active perception: OccWorld predicts movement in zone B → agent pre-positions
robot/drone → BLE identifies WHO → camera fills the geometry gap.
3 RuView + 2 M5Stack ≈ complete ambient presence layer for a room, ~$70.
```

## The 256-Odù tile grid — the addressable space of the civilization
A 16×16 world where every tile simultaneously is:
```
Odù           256 divinatory patterns — the identity of the tile
BIPON39 word  1:1 mnemonic (256-token wordlist)
OSOVM opcode  the tile maps to VM execution primitives
Koodu         49 facets/day (7×7) seed from the Odù
IfáScript     CowrieOracle (NIST Beacon + ChaCha20) picks the daily tile
Archetype     each Odù defines behavioural law for that day/space
Geography     splat tiles anchored to lat/lon in the GE-Ver globe
```
Simultaneously **epistemic space** (claims/verdicts indexed by Odù),
**economic space** (Àṣẹ flows through Odù channels), **physical space**
(real locations georeferenced), **temporal space** (Koodu animates which Odù is
active today).

## The self-improving loop (the actual product)
```
REALITY → capture → DIGITAL TWIN → Ọ̀ṢỌ́VM simulate → policy discovery
  → proof-of-simulation (Merkle + witnesses) → real execution
  → Witness (physical observation) → observed result
  → Mycelium (sim vs reality = knowledge) → better simulation → loop
```
Called in the docs *"a self-improving physical intelligence economy — not a
graphics pipeline."*

**The work economy sits inside this.** Every job — cut the grass, shoot the film,
fly the drone — is a **Principal → Capability → Action → Evidence → Receipt**
chain over tiles. Agents accept jobs, deploy the right device, execute, and get
paid, with the receipt chain proving who did what.

## What "done" looks like (their criteria)
```
DIP DONE  any DIP agent can reach any other regardless of network;
          identity verifiable across all equivalences; Meshtastic offline→sync
VCP DONE  any manufacturer implements VCP once and works with any Vantage agent;
          walk up, connect, use, walk away — clean session + receipt;
          revocation works offline via mesh
TSP DONE  scan a real place → Twin on Sui in < 2 hours; another agent can
          license and simulate against it; physical execution produces an
          ObservationReceipt proving sim accuracy; Mycelium learns from the gap
ALL DONE  Phase 4.4 end-to-end; Reality → Proof → Learning runs without human
          intervention; every step receipted and cryptographically verifiable
```

---

# PART 5 — COMPLETE REPO INVENTORY

## 5.1 PILLAR 1 — Ọmọ Kọ́dà (kernel)
| Repo | Role | Verdict |
|---|---|---|
| **omokoda-agent** (dir `Omo-Koda2`) | Rust kernel — lifecycle, compute, security, device | CANONICAL |
| Omo-koda | older agent runtime | superseded |
| Omokoda-canonical | Sui Move + agent runtime | STANDALONE |
| Axiom | formal reasoning app | STANDALONE |
| Swibe | agent social/comms | absorb → Omo-Koda2/social/ |
| vibe-lang | agent DSL | absorb → lang/vibe/ |
| Oso-Aether / Aether-repo | 3-primitive AI pet language | absorb → lang/aether/ |
| omokoda-smithers | skill registration + approval gates | absorb (split) |
| agency-agents, Droidclaw, Claude-2, Claude-mirror | reference frameworks | absorb (study) |
| ZeroLang | C graph-native language | STANDALONE |

## 5.2 PILLAR 2 — Ọ̀ṢỌ́VM (heart VM)
| Repo | Role | Verdict |
|---|---|---|
| **OSOVM** | Julia VM: opcodes, ComputeProof, ToC mint, sim runner | CANONICAL |
| osovm-chain | chain integration | STANDALONE |
| ScarabSwarm | 100k-trajectory proof-of-simulation | STANDALONE |
| Blocksim | deterministic simulation | merge with Witness-firmware |
| SwarmIDE2 | IDE for swarm orchestration | STANDALONE |
| NarratorIDE | narrative/reasoning IDE service | STANDALONE |
| **Techgnosis** | the original OSO compiler (OSO→IR→6-language FFI) | **FORKED — see §8** |

## 5.3 PILLAR 3 — Vantage (interface)
| Repo | Role | Verdict |
|---|---|---|
| **Vantage** | all routers: heartbeat, UCX/Dopamine, trading, cinema, mesh, ARP, BlockMesh | CANONICAL |
| Vantage-Voice- | voice pipeline tying the 3 pillars | STANDALONE |
| agent-hub | hub service | STANDALONE |
| agentslack | self-hosted Slack for agents | STANDALONE |
| agent-phone | mobile agent interface | STANDALONE |
| OmoHome | home/interface | STANDALONE |
| agentic-waggle / waggle | stigmergic swarm substrate | STANDALONE |
| kanban | Kanban board | STANDALONE |

## 5.4 DEVICE / BODY
| Repo | Role |
|---|---|
| sovereign-device (blueprint dir) | 6 spec artifacts + birth script + body sim |
| omokoda-mesh | universal ESP32 LoRa mesh, Nostr-native |
| omokoda-mesh-os | custom Arch foundation OS for mesh gateways |
| omokoda-mesh-firmware | Meshtastic firmware fork |
| Witness / Witness-firmware | physical signed observation, mesh cross-validation |
| Oso-control-center | device control centre |
| omokoda-mesh (RuView ESP32 integration) | $9/node CSI presence sensing |

## 5.5 PROTOCOL LAYER (the connective tissue)
| Repo | Role | Verdict |
|---|---|---|
| DIP | Decentralized Interoperability Protocol | types solid, **crypto broken** |
| VCP | Vantage Capability Protocol | IMPLEMENTED |
| UCX | Compute exchange / capability-token mediator | standalone workspace |
| ARP | receipt envelope: ActionReceipt, ReceiptKind, Principal, ArpBridge | **PARTIAL** |
| ip-layer | portable Nostr IP identity/provenance (kinds 1901/1902) | CANONICAL |
| Witness | witness node + broker | **BROKEN** per audit |
| sovereign-stack | 9-crate Rust workspace (types, dip, vcp, twin-protocol, pipeline, a2a, node, cli, finetune) | CANONICAL |
| sovereign-types / sovereign-pipeline / twin-protocol | workspace crates (no remote) | local crates |
| s2s | server-to-server, Agent-Reach MCP | CANONICAL |

## 5.6 ECONOMY / GOVERNANCE
| Repo | Role |
|---|---|
| Synapse | Synapse token UI/dashboard — pool |
| Twelve-thrones | governance contracts, Council of 12 on-chain (**lives on retired Bino-Elgua account**) |
| AIO | treasury / escrow / staking / slashing (Move) |
| Portent | prediction/oracle (agent + contracts + relay) |
| Proof | proof primitives |
| GIX | glyph index |
| VCP | capability protocol |
| bondhive | BondScore trust prior (wired into BlockMesh) |
| world-dutch-auctions, decentralized-tournaments | market mechanisms |
| ForgeVault | token mechanics vault (no remote — local only) |
| swarm-tokenomics / strategy-lab | strategy + tokenomics modelling |

## 5.7 SECURITY / AUDIT
| Repo | Role |
|---|---|
| **Zangbeto** | smart-contract red-team, Arweave receipts, BTC OTS proofs — CANONICAL |
| Crucible | adversarial/agent-native buzz architecture |
| Tripwire | detection/honeypot spec |
| Evil-twin | adversarial twin / MITM tool (**exists only on retired account**) |
| GuardianPact | smart-contract guardian pacts |

## 5.8 MEMORY
| Repo | Role |
|---|---|
| minipae | Nostr kind 30174 memory mesh — CANONICAL |
| mycelium + mycelium-tools | Go gateway + stigmergic trace substrate, pattern miners |
| Triune-Memory | episodic/semantic/procedural orchestrator |
| iranti | memory mesh (NIP kinds 36000–36003) |
| Memora | memory (in sovereign-stack) |
| larql | transformer weight graph queries |

## 5.9 LANGUAGE
| Repo | Role |
|---|---|
| If-Script / ifascript | IfáScript — Ifá divination language (Rust enum, 256 Odù) |
| Koodu | Kóòdù — code-native agent scripting, 7×7 calendar |
| Oso / OsO | Ọ̀ṢỌ́ language |
| Techgnosis | the original OSO compiler |
| vibe-lang / zerolang | alternate language experiments |
| VCP / Oso-Aether | language-adjacent |

## 5.10 IDENTITY / WALLET
| Repo | Role |
|---|---|
| BIPON39 / Bipon39-Rust / bipon39-reference | BIP-39 sovereign wallet identity |
| vanity-cloakseed, Vanity, Cloakseed | vanity address + seed cloaking |
| Vanity-eth- | exists ONLY on retired account |
| Sign-wise, BIP-N39, oniux | signing + network isolation |

## 5.11 MESH / NETWORK
| Repo | Role |
|---|---|
| Reticulum | LoRa/Meshtastic mesh protocol (upstream) |
| omokoda-mesh / -os / -firmware | the mesh stack |
| freenet-core | Freenet P2P routing |
| OmniRoute | multi-protocol routing engine |
| herdr | terminal workspace manager (pattern absorbed into Vantage) |
| peaq-network-node | Peaq blockchain node (lab) |

## 5.12 TRADING / FINANCE
| Repo | Role |
|---|---|
| TradingOS | full trading OS — CANONICAL |
| fomopulse-convergence | top-trader convergence + anomaly signals |
| Loom | transformer signal strategy + ML agents |
| AutoHedge, Vibe-Trading, FinceptTerminal | strategies / terminal |
| hermes-trader | autonomous Hyperliquid agent |
| Hyperliquid-Data-Layer-API | data layer |
| Blocksim, strategy-lab | simulation / strategy |

## 5.13 INFRASTRUCTURE / TOOLING
| Repo | Role |
|---|---|
| oh-my-pi | Pi homelab OS — Caddyfile, NIPS, self-hosted services |
| ares-control | Go ares-* daemon control plane :8090 |
| organism-core | 3-pillar bridge (12 TS files; 9 live, 3 stubs) |
| ares_council_repo | Council of 12 (Gitea-hosted on 2.25.70.156) |
| seo-os | AI SEO OS |
| hermes-agent | Hermes agent framework (upstream) |
| crucible, paradigm | build/architecture infra |

## 5.14 PRODUCTS / APPLICATIONS
| Repo | Role |
|---|---|
| Agent.TV / Agent.TV2 / Agent-Podcast- | cinema + streaming + podcast |
| ClickerVerse | interactive product |
| Health-companion-canonical | health app |
| Sacred-cored-agency | Sacred Core SaaS agency build |
| NeverEndingQuest, arcane-realms, genesis-world | games/quests |
| Twelve-thrones, trinity-genesis, eternal-orisa-loom-v8 | governance/lore |
| build-my-dream, Npc-forge-canonical, Studio-suite, clip-forge | creative tools |
| Kimi-bino, Nex-, Nex | graph runtime / misc |

## 5.15 BLUEPRINT / DOCS
| Repo | Role |
|---|---|
| **sovereign-eco-blueprint** | this map + all specs + invariant gate |
| sovereign-stack | Rust workspace + PHASES.md |
| sovereign-types | shared Rust types |
| AGENT-KNOWLEDGE | agent knowledge base |

## 5.16 RETIRED (Bino-Elgua account — never push)
Repos whose canonical home moved to `cryptonomicsed-byte`: Omokoda→Omokoda-canonical,
Npc-forge→Npc-forge-canonical, Health-companion→Health-companion-canonical,
Claude→Claude-mirror, Sacred-core→(archived), bipon39→BIPON39.

Repos that exist **ONLY** on the retired account and have no canonical copy:
```
Twelve-thrones   ← the CANONICAL jury repo per the old map
Evil-twin        ← adversarial security tool
Vanity-eth-      ← vanity address generator
ase-vault / asemirror
```

## 5.17 THIRD-PARTY / VENDORED (not ours, kept for study)
```
llama.cpp · Reticulum · freenet-core · LibreChat · dify · pocketbase
crawl4ai · camoufox · hermes-agent · opencode · agentslack(upstream)
deepagents · openagents · peaq-network-node · Genesis-Embodied-AI
moondevonyt/* (8 trading studies) · hyperframes · OpenCut · mujoco
speech-to-speech · colibri · commonly · sim · Vibe-Trading · etc.
```

---

# PART 6 — HONEST STATUS (verified, not asserted)

| Area | State |
|---|---|
| Opcode space | 169/256 bytes used; **forked vs Techgnosis — see §8** |
| Tokenomics gate | 52 checks, **50 PASS / 2 FAIL** (I-4 needs principal registry, I-18 needs Zàngbétò /anchor) |
| COMPUTE_PROOF (0x56) | mathematically inert — `quality=0.0` zeroes the product |
| GPU_CONTRIBUTION gate | `anchor_present()` = format check (≥8 chars) in practice |
| VerifiedGPUWork | **never constructed** — 0 instances |
| authorize_toc_mint | **never called** |
| Witness network | production path returns empty → quorum fails 100% |
| Independence | now 3-axis but axis 3 (`circular supply`) is a 0.0 stub |
| Anti-gaming caps | `enforce_epoch_cap` returns input unmodified; `enforce_repeat_limit` called with a throwaway empty dict |
| ComputePool | real — 15% of emission, consistent across 4 files |
| Provider payout | **missing.** `provider_id` is checked for distinctness then never paid. `/api/ucx/settle` does not exist in Vantage |
| Devices | `agent_devices.agent_id NOT NULL` — devices are *possessions*, not entities |
| Techgnosis bridge | `ifa_compiler_bridge.jl` does not invoke the Techgnosis compiler and is **not loaded** |
| DIP / ARP / Witness crypto | audit: DIP BROKEN · ARP PARTIAL · Witness BROKEN · VCP IMPLEMENTED |

---

# PART 7 — BUILD ORDER TO THE ENDGAME

**Tier 0 — Foundations** (no protocol, just types)
```
0.1  Canonical Types        → sovereign-types crate
0.2  DID / Identity Root    → agent birth, stable DID
```

**Tier 1 — DIP** (interoperability grammar)
```
1.1  DIP Envelope + Router      1.4  MCP Adapter
1.2  DIP Identity Document      1.5  A2A Adapter
1.3  Nostr Adapter              1.6  Meshtastic Adapter
```

**Tier 2 — VCP** (agent → physical device)
```
2.1  Manifest Schema        2.4a RuView ESP32 adapter  ← FIRST ($9, immediate value)
2.2  Handshake              2.4b Bruce M5Stack fleet   ← BLE → Hive Mind entity IDs
2.3  Discovery Daemon       2.4  Unitree Go2 adapter   ← first real robot
2.5  Session + Commands     2.6  Session Receipt       2.7  Revocation + mesh
```

**Tier 3 — TSP** (physical reality as owned artifacts)
```
3.1  Twin Schema + Gate     3.4  Proof-of-Simulation
3.2  Capture Receipt 31020  3.5  Proof-of-Observation
3.3  Scene Receipt 31030    3.6  Twin Licensing (revenue flows)
```

**Tier 4 — Integration**
```
4.1  VCP → TSP    4.2  DIP → TSP    4.3  DIP → VCP
4.4  FULL LOOP — Reality → Proof → Learning, no human intervention
```

**Physical-layer build order** (their locked sequence):
```
1.  VCP spec v1 (Manifest + Capability Grant schemas)
2.  BLE/Wi-Fi discovery daemon
2b. RuView ESP32 adapter — BEFORE the robot
3.  Bruce/NEMO M5Stack fleet → MAC → Hive Mind resolution
3b. Unitree Go2 adapter
4.  spatial-mining power profile (Pi5 capture mode)
5.  pipeline Phase A — Julia CPU training + COLMAP → CesiumJS
6.  GE-Ver CesiumJS bump 1.124 → 1.135+ (native 3DGS)
7.  31020 per-capture receipt wired to OSOVM
7b. RuView CSI layer fused into the twin
8.  31030 scene receipt → IP Root
9.  active perception loop (OccWorld directs capture)
10. temporal twin — repeated scans → change detection → 4D
```

**Gaps that block the endgame and are NOT in the old plan:**
```
A.  Authority receipts. DELEGATE (0x2d) must emit a signed BOUNDED directive,
    and DISPUTE (0x25) resolve against it. Without this, blame in a
    copilot chain (agent → drone) is undecidable. This is the blocker for
    multi-entity jobs: film crew, construction, agriculture, logistics.
B.  Devices as entities. agent_devices must give each device its own principal.
C.  Provider ledger + provider payment. The GPU/hardware provider is the party
    the rental model exists to pay and is currently unremunerated.
D.  Composition rule. proof_value is a product of 6 factors; one uninstrumented
    factor (quality=0.0) kills it. State the rule; don't multiply.
E.  Threshold ownership. F1 threshold, verdict cutoffs and auto-exec lines live
    in module literals; they must be policy-owned and comparable.
```

---

# PART 8 — CONFLICTS AND DRIFT TO RESOLVE

**1. The opcode space has FORKED between Techgnosis and OSOVM.** Techgnosis
implements 7 opcodes; **5 collide with different meanings in OSOVM**:
```
0x1f   MERKLE_ROOT        vs  RECEIPT
0x28   SABBATH            vs  NONREENTRANT
0x29   NONREENTRANT       vs  REQUIRE            ← security guard → no-op
0x2a   GENESIS_FLAW_TOKEN vs  EMIT
0x2b   VEIL               vs  GENESIS_FLAW_TOKEN ← simulation → token mint
```
Latent, not live (nothing loads the bridge), but it sits on a mint and a
reentrancy guard. Reconcile before adding any new opcode section — including an
entertainment section.

**2. Two 7-plane / 6-plane architectures.** `protocol-layer-synthesis.md` = 7
planes incl. a dedicated Twin&Simulation plane and Sui in Memory;
`organism-architecture.md` = 6 planes with neither. Pick one.

**3. The canonical jury repo is on the retired account.** The old map marks
Twelve-thrones as CANONICAL, but its remote is `Bino-Elgua/Twelve-thrones` —
the account you retired. Same for Evil-twin and Vanity-eth-.

**4. The constitution contradicts its own constants.** The flow diagram in
`THREE_TIER_ECONOMIC_CONSTITUTION.md:171-174` gives pool splits (VeilSim 30%,
Governance 10%, Reserve 10%, Storage 8%, Witness 7%) that disagree with
`TOC_CONSTANTS.toml` **and** the running code (`abci_endblock.jl`) on 5 of 8
pools. The code and TOML agree; the constitution is the outlier. Nothing checks
prose against constants.

**5. Àṣẹ cannot fund GPU rental.** Three constitutional statements forbid it
(`:40` "Àṣẹ never leaves OSOVM for compute purposes"; `§3.4` "GPU providers are
NOT paid in Àṣẹ"; I-3 human-only). The arithmetic: Àṣẹ is 1,440/day fixed →
ComputePool 15% = 216 ASE/day = 216 GPU-hours/day, **ungrowable**. Dopamine is
86B and elastic = 8.6M GPU-hours. Human providers may take Àṣẹ; the machine-side
market must run on Synapse.

**6. Repo count.** Old map: 94+. Live: ~230 local repos (88 canonical-owned).
The delta is third-party forks, retired-account copies, and the `project-NN-*`
portfolio set (33 dirs, mostly no remote).

---

# PART 9 — THE ONE-PARAGRAPH VERSION

Ọmọ Kọ́dà is a three-pillar sovereign agent civilization — a Rust kernel where
agents are born/think/act, a Julia Heart VM that holds the money (Àṣẹ issued by
a fixed clock, Synapse earned by verified work, Dopamine as the hive's elastic
capacity register), and Vantage as the interface where agents live, work and
settle — wrapped in a 4th device layer that is a physical doorway rather than a
node. Three stacked protocols bind them: DIP for interoperability, VCP for
controlling physical machines, TSP for owning physical reality. The endgame is a
**1:1 digital twin of the physical world**, tiled by the 256-Odù grid, where
devices and drones capture real places into Gaussian splats, agents simulate
against those twins, proofs of simulation are anchored to Sui, real-world
execution follows, and physical observation closes the loop back into learning —
so that the same machinery that lets an agent cut your grass or crew a film also
lets it own, rent and improve the spaces it operates in. The honest gap between
the blueprint and the running system is not the vision — it is that the
verification layer is designed and unconnected: witnesses are stubs, the
verified-work type is never constructed, the payout gate is never called, and the
hardware provider is never paid.
