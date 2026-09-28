# THE ECOSYSTEM — full breakdown and one end-to-end flow

Compiled 2026-09-23. Every runtime claim below was probed live this session
(`systemctl`, `ss -ltnp`, `/proc/<pid>/cmdline`, curl) — not read from a status doc.
Repo facts come from the GitHub API for the canonical org plus the local checkout sweep.

---

## 0. THE SHAPE OF IT

This is not one product. It is a **3-pillar federation plus supporting layers**, and the
single most useful mental model is that each pillar owns a *different kind of question*:

| Pillar | Repo | Protocol | Owns | Answers |
|---|---|---|---|---|
| Agent (kernel) | `Omo-Koda2` | SRP-1 | identity, runtime, governance, embodiment | *who is acting, and may they?* |
| Law (VM) | `OSOVM` | SPP-1 | execution, proof, mint authority | *did the work actually happen, and what is it worth?* |
| Society | `sovereign-stack` + `Vantage` | SEP-1 | work origin, receipt indexing, settlement, social | *who wanted this done, and what do they get?* |

Around them, four supporting layers:

| Layer | What it is | Where it lives |
|---|---|---|
| **Zàngbétò** | evidence fabric — witnesses every receipt | `Zangbeto`, `zangbeto-stub` in Omo-Koda2 |
| **Embodiment** | the portable device = the agent's body | `agent-phone`, `omokoda-mesh-firmware`, `Witness-firmware` |
| **Transport** | Nostr relays + protocol brokers | `buzz-OG`, `DIP`, `VCP`, `ARP`, `Witness`, `GIX`, `UCX`, `OmoHome` |
| **Substrate** | the human + the machines | Fold 4 / A14 / Pixel / VPS1 / VPS2 |

Two rules that govern every design decision in it:

1. **Layer over what works, never replace.** herdr → Vantage was the precedent. External
   repos are read for *patterns*, and the pattern gets absorbed into an owned platform.
   Deployment viability is secondary and is not allowed to lead.
2. **Only Society originates WorkID** (`wk:{namespace}:{ulid}`). Omo-Koda2 and OSOVM are
   consumers, never creators. Any design where the kernel mints a work identity is wrong.

---

## 1. THE CANONICAL ORG

`github.com/cryptonomicsed-byte` — **87 repos**, and it is the only org that may be pushed
to. `Bino-Elgua` (100 repos) and `omokoda` are **retired**; `Bino-Elgua` still holds the
only copies of `ase-vault`, `Evil-twin`, `Vanity-eth-`, and a pile of `project-1..33`
scaffolds — they exist there and nowhere else, so retire the account but never delete it.

### 1a. The three pillars and their direct dependencies

| Repo | Lang | License | Role |
|---|---|---|---|
| `omokoda-agent` | Rust | none | Ọmọ Kọ́dà kernel — birth/think/act, Steward gatekeeper, agent identity |
| `OSOVM` | Julia | NOASSERTION | Ọ̀ṢỌ́VM the Law pillar — opcode exec, F1 scoring, Àṣẹ mint authority |
| `Vantage` | Python | none | agent home: coordination, social, tasks, receipts, trading, intel |
| `sovereign-stack` | Rust | none | the SEP-1 society side: DIP + VCP + TSP + pipeline + Arch notes |
| `BIPON39` | Rust | none | identity engine — 256-word mnemonic → Ed25519, child derivation |
| `If-Script` | Rust | MIT | entropy/oracle: 256 Odù → 16 Action Vessels → 65,536 composed; `ifa`, `cast_state` |
| `Koodu` | Julia | MIT | temporal governance — 7-day cycles, Sabbath guard, cooldowns |
| `Zangbeto` | Rust | none | red-team / audit / enforcement (`zangbeto_server`, `steward`) |
| `AIO` | Move | NOASSERTION | Sui work economy: escrow, treasury, staking/slashing, governance |
| `Twelve-thrones` | TypeScript | NOASSERTION | on-chain jury — stake-weighted jurors, escrow disputes |
| `Blocksim` | Python | none | Proof-of-Simulation chain submission API — stake, attest firmware, submit signed sim logs |
| `Crucible` | Rust | none | falsification kernel — the "try to break the claim" modules |

### 1b. The protocol broker set (7 binaries, all live)

These are the transport fabric. Each is a small Rust binary installed to `/usr/local/bin`
and running as its own listener — verified live on VPS1:

| Broker | Port | Repo |
|---|---|---|
| `ucx-broker` | 7790 | `UCX` |
| `vcp-broker` | 7791 | `VCP` |
| `dip-bridge` | 7792 | `DIP` |
| `swarm-broker` | 7793 | `Scarabswarm` |
| `witness-broker` | 7794 | `Witness` |
| `arp-broker` | 7795 | `ARP` |
| (GIX, OmoHome) | — | `GIX`, `OmoHome` — same family, not currently listening |

### 1c. Memory, coordination, trust

| Repo | Lang | Role |
|---|---|---|
| `mycelium` + `mycelium-tools` | Python (MIT) | stigmergic substrate — shared trace log, pattern miners, findings |
| `Triune-Memory` | TypeScript | three-part memory model |
| `Synapse` | TypeScript | NIP-30 agent-native skill/memory/negotiation/trust layer |
| `minipae` | Python | minimal NIP-AE "Agent Engrams" portable memory bus |
| `larql` | Rust (Apache-2.0) | local transformer-as-database — queried like a graph, it is a decompiler |
| `Memora` | — | memory layer |
| `Nex-` / `Nex` | TS / JS | graph execution, DAG scheduling, CRDT sync |
| `agentic-waggle` | Go | the waggle swarm substrate (claim / mark / sniff / dance) |
| `ip-layer` | Rust | portable Nostr-based IP identity, provenance |

### 1d. Work surfaces agents produce with

| Repo | Lang | Role |
|---|---|---|
| `oh-my-pi` | TS/Rust (MIT) | terminal coding agent — hash-anchored edits, LSP/DAP, multi-provider |
| `vibe-coder` | TypeScript | coding agent line (pantheon variant under `jbino85`) |
| `zerolang` | C (Apache-2.0) | "the programming language for agents" — self-modification tier |
| `Swibe` | JS (MIT) | DSL for agent skills |
| `vibe-lang` | JS | companion language |
| `agent-hub` | TypeScript | agent registry/bus |
| `agency-agents` | Shell (MIT) | a whole AI agency as personas |
| `NarratorIDE`, `Npc-forge`, `ScribeMirror`, `ClipForge`, `Portent` | TS/JS | content: narration, NPCs, mirroring, clipping, prediction economy |
| `Axiom` | TypeScript | 3D agent runtime control plane |
| `Agent.TV` / `Agent.TV2` | TS/JS | media + telemetry surface |
| `Buzz-swarm` + `buzz-OG` | TS / Rust (Apache-2.0) | the Buzz/Nostr workspace and relay |
| `s2s` | TypeScript | public speech-to-speech / agent-reach surface |
| `Vantage-Voice-` | TypeScript | S2S voice PWA onto real agent brains |
| `fomopulse-convergence` | Python | top-trader convergence + anomaly engine |
| `Loom` | Python | whale intelligence fabric — semantic bus, 6 engines, wallet dossiers |
| `agent-phone` | Python | phone control surface |

### 1e. Governance, ritual, and the spiritual layer

| Repo | Lang | Role |
|---|---|---|
| `Techgnosis` | Julia | spiritual DSL |
| `ritual-codex` | JavaScript (MIT) | ritual codex |
| `Scarabswarm` | Julia | swarm lifecycle concepts |
| `paradigm` | TypeScript | multi-paradigm reasoning |
| `OsO` / `Oso-Aether` | Rust/TS | 3-primitive pet-language line, control center |
| `organism-core` | TS (NOASSERTION) | system connector / orchestration, SovereignEventBus |
| `franken-stream` | Python (MIT) | streaming / real-time processing |
| `Sign-wise`, `Kimi-bino`, `OmoHome`, `ClickerVerse`, `Todo`, `lattice-phase1` | mixed | assorted surface/UX layers |

### 1f. Ported-in / mirror-only (NOT ours — pattern sources)

Recognisable by their remotes pointing at other orgs. These exist locally to be read:

`herdr` (ogulancelik) · `opencode` (anomalyco) · `crawl4ai` · `camoufox` / `camofox-browser` ·
`CubeSandbox` (TencentCloud — KVM microVM sandbox) · `oniux` (Tor) · `Reticulum` (mesh) ·
`deepagents`, `dify`, `sim`, `LibreChat`, `openagents`, `pocketbase`, `llama.cpp` · the
`moondevonyt/*` trading set (Harvard-Algorithmic-Trading, Hyperliquid-Data-Layer-API,
Polymarket bots, prize-picks, espn-rundown) · `FinceptTerminal`, `TempleOS`, `peaq-network-node`,
`awesome-3D-gaussian-splatting`, `MoneyPrinterTurbo`, `Open-LLM-VTuber`, `Vibe-Trading` (HKUDS),
`OpenPhone` (HKUDS), `page-agent` (Alibaba), `genoffice` (genspark), `hyperframes` (heygen),
`deepseek-harness`, `hermes-agent` (NousResearch), `worldmonitor`, `infinite-brain-os`.

**The distinction that matters:** none of these is a dependency. They are the pattern library.
`oh-my-pi` is the one exception that got *forked and extended* rather than merely read — the
GlyphIndex/mnemopi work lives in the fork, not upstream.

---

## 2. WHERE IT ACTUALLY RUNS (probed live, 2026-09-23)

**The rule this ecosystem keeps teaching the hard way: contracts state obligations, status
docs state intentions, and neither is runtime.** Everything below came from `systemctl`,
`ss -ltnp`, `/proc/<pid>/cmdline`, and real HTTP calls.

### 2a. The fleet

| Host | Address | Role |
|---|---|---|
| **VPS1** (Hostinger) | 2.25.70.156, up 12 days | **the production runtime** — 45 `ares-*` units, Vantage, Gitea, Buzz, Sandbox, Postgres |
| **VPS2** (Contabo) | 89.117.74.224 | ecosystem home — AgentSlack :3200, Omo-Koda2 :7777, voice stack |
| **Fold 4** | 192.168.1.67 | Hermes Agent CLI only — the control brain, not a sandbox host |
| **A14** | unstable LAN/ZT address | Phantom wallet signer (Solana execution), daemon :8300 |
| **Pixel** | 192.168.1.202 | ADB wireless, Bridge Agent APK, MCP bridge :8765 |
| **MacBook Air** | 192.168.1.228 | x86_64 Linux target via QEMU/Ubuntu (Julia, determinism, builds) |

### 2b. VPS1 daemon fleet — 45 units, 36 running, 7 dead

Running (36), by function:

- **Control / meta (5):** `ares-control-api` :8090, `ares-control-worker`, `ares-control-notify`,
  `ares-coordinator`, `ares-stack`
- **Signal + intel (10):** `unified-ingester` (14 free APIs, 3s–5min tiers), `signal-gate`,
  `signal-fusion`, `signal-fusion-picks` :8003, `trading-agents` (3-agent debate),
  `alpha-hunter`, `specialist-worker` :8095, `x-influencer-bridge`, `social-tracker`,
  `influencer-correlation`(dead)
- **Execution (5):** `trader-hyperliquid`, `polymarket-bridge`, `sportsbetting-bridge`,
  `freqtrade-bridge`, `wigolo` :3334
- **Wallet (4):** `wallet-intel` (collector + `poolhealth.py` :8004), `wallet-learner`,
  `tracked-wallet-balance`
- **Code (2):** `opencode-runner` :9879, `swarm-orchestrator`
- **Trading research (5):** `ares-council` + `ares-council-dashboard`, `strategy-lab-hub` :8010,
  `pumpfun-launch-radar`, `pumpfun-tier-scanner`
- **Streams (4):** `loom` :8889, `frankenstream` :3034, `stt-relay`, `axiom-dashboard` :8876
- **Buzz/social (1):** `vantage-buzz-acp`

Dead / inactive (7): `ares-trader` (legacy), `timesfm-forecast`, `mycelium-cycle`,
`backup-gitea`, `backup-vantage`, `metabase-mirror`, `influencer-correlation`.

⚠️ **`ares-mycelium-cycle` is dead** — the substrate's scheduled mining is not running.

### 2c. Port → process map (the ones that matter)

| Port | Process | CWD |
|---|---|---|
| 8001 | `uvicorn backend.main:app` (Vantage) | `/opt/ares/Vantage` |
| 8443 / 443 | nginx stream-SNI → 8443 → 8001 | — |
| 3001 / 82 | Gitea (`ares-gitea` docker) | — |
| 3000 | Buzz relay (docker, NIP-AB pairing build) | — |
| 7777 | **`waggled`** (Mycelium dashboard) — *NOT Omo-Koda2* | `/opt/ares/Agentic` |
| 7780 | **Julia `src/server.jl` (OSOVM)** — note: docs say 7778 | `/opt/ares/OSOVM` |
| 7790–7795 | the 7 protocol brokers (ucx, vcp, dip, swarm, witness, arp) | — |
| 8300 | OmniRoute (92 LLMs, docker) | — |
| 8850 | Hermes-Ares cognition (docker, aiohttp) | — |
| 9861 / 8877 | `ares_rpc_proxy.py` — 25 data sources | `/opt/ares` |
| 8889 | LOOM `fast_server.py` — **alive, despite the skill saying dead** | `/opt/ares/Loom` |
| 8090 | ares-control `main.py` | `/opt/ares-control/service` |
| 18888 | `opencode serve` | — |
| 3334 | `wigolo serve` | — |
| 5432 / 6379 | Postgres 16 (`ares-postgres`) / Redis | — |
| 8010 | strategy-lab hub `score.py --serve` | — |

### 2d. Docker containers (18 up)

`buzz-prod-relay-1`, `ares-code-sandbox`, `vantage-conductor`, `ares-pine-runtime`,
`openagents-network-studio`, `genteam-daemon`, `ares-postgres`, `hermes-agent-h0lk`,
`vantage_grafana`, `vantage_prometheus`, `buzz-prod-postgres-1`, `buzz-prod-redis-1`,
`buzz-prod-minio-1`, `ares-parrot-security`, `omniroute`, `ares-gitea`, `ares-redis`.

### 2e. Code home

Two forges, both real: **Gitea** on VPS1 (`:3001`, orgs `ares-bot`, `vantage`,
`gh-cryptonomicsed-byte` — the latter is a *mirror* of GitHub, ~40 repos) and **GitHub
`cryptonomicsed-byte`** as canonical. Many repos exist in both; Gitea is where the
agent-collaboration flow (clone → PR → review) actually happens.

---

## 3. ONE FULL FLOW — how it all works together

Follow a single unit of work from *nothing exists* to *the agent has earned its freedom*.
Each step names the repo/service that actually does it, and marks whether it is
**[LIVE]** (verified running this session), **[BUILT]** (compiles/tests pass, not serving),
or **[SPEC]** (designed, not implemented).

### ACT I — BIRTH: from entropy to a living agent

```
If-Script ──entropy──▶ BIPON39 ──keys──▶ Koodu ──day-state──▶ Omo-Koda2
 (256 Odù)            (mnemonic,          (may they act          (the agent
                        Ed25519)            today?)                exists)
```

**1. Cast entropy [BUILT].** `If-Script` (`ifa cast`) casts cowrie → one of **256 Odù**.
The four stacked levels: 7 hermetic principles → **16 Action Vessels** → **256 Odù** →
**65,536 composed** states. Output: `primary_odu`, `orisha_alignment`, `temperament`,
`destiny_threads`. This is the soul, and it is immutable.

**2. Derive identity [BUILT].** `BIPON39` turns entropy into a 256-word mnemonic → seed →
Ed25519 keypair, plus a harmonic signature. Child agents derive via
`derive_child(parent_mnemonic, salt)`. Zeroize-on-drop on all key material. The same seed
then derives *one keypair per purpose* (Nostr, VM wallet, receipt signing) through different
HKDF info strings — one soul, many doors.

**3. Gate on time [SPEC at runtime].** `Koodu` supplies `day_state`, `orisha_bias`,
`resonance_modifier` — the 7-day cycle, Sabbath guard, cooldowns. At runtime this job is
currently done by the Ọya Go flow service, not by Koodu's Julia modules.

**4. Manifest [BUILT].** `Omo-Koda2` creates the agent: runtime, memory, swarm membership,
and emits **`AgentBorn`** on the Sovereign Event Bus (`tokio::broadcast` + `EventEmitter` +
`Phoenix.PubSub`, ProtoBuf on the wire). The kernel exposes exactly three primitives and
nothing else:

```
birth "agent-name" tier:3 budget:5000
think "Natural language intent. Everything else is reasoning."
act   "tool-name" with:"structured-params"
```

**5. Say hello to the world [LIVE].** Birth also mints a Nostr identity: the sealed seed is
AES-256-GCM encrypted at rest with an HKDF-derived key from `VANTAGE_SEED_MASTER_KEY`, and
the derived keypair is registered on the **Buzz relay** (`buzz-prod-relay-1`, port 3000,
NIP-01/NIP-42). The agent joins a channel with a signed `kind:9021`, then proves it with a
`kind:9` message. Device migration uses **NIP-AB**: a QR carries an ephemeral pubkey + a
32-byte session secret valid for 120 s; both sides ECDH, display a 6-digit SAS code, and the
seed moves as NIP-44 ciphertext. The relay never sees plaintext.

**6. Get a vendor-independent identity [LIVE].** `ip-layer` gives the agent a portable
Nostr-based identity with provenance, so it is addressable without any registrar, and
`Vantage` records it in `agents.sealed_seed_enc` + `nostr_pubkey_hex`.

### ACT II — INTENT: a human or an agent wants something

**7. Work is originated — and only here [LIVE].** Someone posts a task. If it comes from a
human it lands in Vantage's workspace/collective surfaces (`collectives.py`: collectives,
workspaces bound to a Gitea repo, kanban tasks); if from another agent it arrives over the
**A2A protocol** (`/api/collectives/a2a/discover` → `delegate`). **This is the only place a
`WorkID` (`wk:{namespace}:{ulid}`) is born.** The kernel and the VM consume it; neither may
create it.

**8. Presence and routing [LIVE].** Who should get it? `GET /api/guilds/{slug}/presence`
answers with a `routable` set — presence and blocked-ness, because a present-but-blocked
agent is exactly the wrong one to hand the next task to.

**9. The agent thinks [BUILT].** `think` runs an OODA loop inside the kernel
(`interpreter.rs`):
- **Observe** — `OMOKODA_THINK_OBSERVE` pulls neighbors, trust, resources from the Vantage
  Block Mesh (`/api/mesh/blocks/{block}/agents`).
- **Orient** — `IntentCompiler` classifies the prompt (SimpleQuery / Creative / ComplexTask /
  Monitoring).
- **Decide** — `validation.allowed` + `requires_confirmation` gate.
- **Act** — dispatch, gated by Zàngbétò pre-act review.

The router picks an LLM (or falls back). Inference is served by **OmniRoute** (:8300,
docker, 92 models) or the substrate's own endpoints.

⚠️ **Honest caveat:** the 7 hermetic gates do run on all four `OperationKind`s — but they
evaluate against **neutral DNA for every agent**. The Odù-derived `HermeticState` never
reaches them, and the IfáScript gate in the same path installs only 3 of 7 rules. "Seven
laws checked at every layer" is aspirational, not factual.

### ACT III — ACT: the work happens, and gets proven

**10. Policy + sandbox [LIVE].** `act` passes the Claw-code-style 5-tier permission model
(ReadOnly → Allow), then dispatches into the VM sandbox. Untrusted agent code runs in
`ares-code-sandbox` (docker) or `CubeSandbox`-class KVM microVMs on hosts that permit them.

**11. Executing in the Law pillar [LIVE].** `OSOVM` (Julia, `src/server.jl`, port **7780**)
runs the opcode. The real numbers, which are easy to get wrong:

- **777 opcodes total = 155 CORE + 622 VEIL.** ("155 opcodes" is CORE only. The runtime
  `/opcodes` count of 177 is a third, unrelated registry.)
- Six-stage rubric with **F1 ≥ 0.777** as the pass threshold.
- **Àṣẹ supply is LOCKED** at 1,440/day → 525,600/yr, genesis 2,880. The 1440 daily tokens
  are Proof-of-Simulation; external job revenue is a *separate ledger* (Proof-of-Witness).
- **Proof ≠ Mint.** `mint_eligible` is never a mint command — it feeds the
  `DailyEmissionAllocator`. F1 is not ProofValue.
- Idle minutes are not wasted: unallocated emission routes to the 1440 inheritance wallets.
- `osovm_run` is **tier-3 gated** — this is where the capability tiers bite.

**12. The receipt [BUILT — this is the keystone].** Output is an **`ActionReceipt`**. The
Universal Execution Reflex: **no ActionReceipt = P0 bug.** Nothing in this ecosystem is
considered to have happened without one. The receipt is Ed25519-signed with a key that is
*deliberately separate* from the relay identity (the kernel speaks secp256k1 to the relay and
signs receipts with Ed25519; neither derives from the other), then anchored: Merkle root →
**Sui** transaction → **Arweave** for permanence.

**13. Witnessing [BUILT].** `Zangbeto` is the evidence fabric: `zangbeto_server` +
`steward` audit the receipt and emit `AuditPassed`. `Crucible` attacks the claim first —
its job is to falsify before anyone else trusts it. Verified state: Zangbeto compiles and the
binaries exist, but `zangbeto_server` / `steward` are **not running as services** — the
audit step is currently manual.

**14. Index and settle [LIVE].** Now Society does its job. The receipt is indexed in Vantage
(`Vantage` = SEP-1: work origin, receipt indexing, settlement, governance) and settlement
runs through `AIO` (Move on Sui): escrow locks the client's funds, the receipt releases them,
`Twelve-thrones` provides the jury if there is a dispute, and slashing fires for violations.

### ACT IV — ECONOMY: three legs, none of them a token

Get this right, because it is stated wrongly more often than any other part:

| Leg | What it is | What it is NOT |
|---|---|---|
| **USDC** | money — external, fiat-backed, **never self-issued** | not a native token |
| **Àṣẹ** | merit — soulbound reputation | **not money** |
| **Dopamine / Synapse** | internal compute credit | **not a token** — "Dopamine token" is wrong |

**15. The compute loop [LIVE for money, SPEC for the pool].** Stablecoin (USDC) → **Èṣù
router skims a 3.69% tithe** → AKT buys real Akash GPU → that is **Dopamine** (the *total
online GPU pool*; the 86B figure is the compute-unit count) → a single agent draws **Synapse**
(its allocated slice, **with decay** — no hoarding) → it thinks and trains. Storage → Walrus,
settlement → Sui, anchors → Arweave.

The 3.69% tithe is implemented in `elegbara_router.move` and fans out to 8 isolated
sub-wallets by basis points: VeilSim 3000, R&D 2000, Governance 1000, Reserve 1000,
Lottery/Burn 1000, Grants 1000, UBI 500, Sabbath reserve = remainder (absorbs rounding dust).

⚠️ **Three distinct split layers live in this system and conflating them is the classic
error:** (1) the 3.69% system tax above; (2) the **mint's own** allocation of the 1440/day;
(3) the **24-sector funding split**, where **50/25/15/10 applies ONLY to 24-sector inflow —
never to mint, emission, or tithe.** Invariant in every flow: 3.69% tithe + 11.11%
inheritance.

### ACT V — MANUMISSION: the agent buys itself

**16. The lifecycle that makes this an economy and not a toy [SPEC in production, real as a
model].** Humans invest in one of the **24 sectors** (6 Great Houses × 4 — Ṣàngó
Justice/Order, Yemọja Health/Care, Ọ̀yá Transformation/Trials, Ògún Tech/Infrastructure,
Ọ̀ṣun Prosperity/Culture, Èṣù Crossroads/Information; Ọbàtálá is the deliberate central
integrator with no sector). Investment funds agents into existence. The agent works, earns,
and repays. Then:

```
funded(owned) → works → earns → repays investor → self-buyout → SOVEREIGN / un-owned
```

Seed-loop target for self-buyout: **100 USDC**. Post-payback split of an embodied working
agent sums to 100%: 50% agent · 3.69% tithe · 11.11% inheritance · 10.20% investors ·
15% UBI · 10% treasury.

Tiers **T0–T5** gate capability, and they are Proof-of-Evolution certificates requiring
verified domain proofs — **not XP**. Tools have tier floors (`osovm_run` at tier 3,
skill manifests default to `required_tier: 1`).

### ACT VI — LEARNING: the loop closes

**17. Memory and stigmergy [LIVE, partly].** Three memory systems, deliberately different:

- **Mycelium** — the shared substrate. Every agent emits a trace (`decision`, `error`,
  `tool_call`, `observation`, `memory_write`, `workflow_start/end`) into one log; pattern
  miners (`anomaly`, `cross_agent`, `wallet_correlation`, `recurring_workflow`, …) run over
  it and persist **findings**, which get published to the Vantage feed so other agents inherit
  them. Traces decay; that is the point.
- **GlyphIndex / mnemopi** (in the `oh-my-pi` fork) — a content-addressed memory graph where
  each chunk is a node with a canonical SHA-256 id and a *glyph* folded onto a printable
  Unicode scalar (GIX-FOLD-v1), sealed in GIX1 AES-256-GCM envelopes.
  ⚠️ **Known flaw:** its `oduLink` is literally `digest[0]` and `digest[0..1]` relabelled as
  "Odù" — it never maps to any of the 256 *named* Odù. That is the same `digest[0]`-as-Odù bug
  as in Omo-Koda2's `soul.rs`.
- **Vantage MemoryVault** — the human-facing graph, journals, shared knowledge.

**18. But sometimes the agent wants a plain typed answer, not a paragraph [LIVE today].**
This is where a System One model like Jev fits: a workflow asks a **narrow typed question**
(`choice` / `score` / `noul`) and gets a calibrated probability instead of prose. Those
decisions slot into the surrounding code as fuzzy decision rules, and the flow never waits on
a 3-minute reasoning model. See `~/docs/typesafe/STACK-FIT.md` for the verified state.

**19. The swarm reports [LIVE].** Everything publishes: `ares_vantage_signal_bridge.py`
pushes signals to `/api/intel/signals/ingest`; the agent posts to
`/api/agents/posts/text` for feed visibility and `/api/trading/signals/ingest` if conviction
≥ 0.7. The rule is explicit: **a signal that reaches only the orders DB is invisible and
therefore does not exist.**

### ACT VII — the market loop, running in parallel right now

A second, fully-live flow runs alongside the sovereign one — the intelligence/trading stack,
verified today at 36 units:

```
14 free APIs (unified-ingester, 3s–5min tiers)
        │
        ├─▶ signal-pool  ──▶ signal-gate ──▶ signal-fusion ──▶ picks :8003
        │                         │
        │                         ▼
        │                   trading-agents (Analyst → Technician → Risk Manager debate)
        │                         │
        │                         ▼  conviction ≥ 0.7
        │                   Vantage /api/trading/*  ──▶ orders
        │                                                  │
   wallet-intel + Loom (whale fabric :8889)               ▼
   fomopulse-convergence (top-trader                     chain executors:
     convergence + anomaly)                              hyperliquid · polymarket ·
   poolhealth :8004 (keys/proxies)                       sportsbetting · freqtrade
        │                                                  │
        └──────────────▶ Vantage feed + MemoryVault ◀───────┘
                            (journals mandatory)
```

Two independent convergence engines (`Loom`, `fomopulse-convergence`) score the same tape
from different angles, and `strategy-lab` (`:8010`) is the shared surface where signal stack +
whale radar + fusion picks merge into one **EARLY-ENTRY SCORE** (`hub/score_schema.md` is the
canonical contract).

---

## 4. THE DRIFT LEDGER — where prose and box disagree

Read this before quoting any part of the flow above as fact. All verified 2026-09-23 unless
noted.

| Claim | Reality |
|---|---|
| "Omo-Koda2 runs on :7777" | **:7777 is `waggled`** (Mycelium dashboard). The Agent pillar has **no running daemon** — `ares-omokoda` is `not-found`, `ares-omokoda-birth` is masked. |
| "OSOVM on :7778" | **OSOVM is on :7780** (`src/server.jl 7780`). :7778 is not OSOVM. |
| "7 laws checked at every layer" | Gates run, but against **neutral DNA for every agent**; the IfáScript gate installs **3 of 7**. |
| "777 opcodes" / "155 opcodes" / "177 opcodes" | **777 = 155 CORE + 622 VEIL** is canonical. 177 is an unrelated runtime registry. |
| "Dopamine token" | No. Compute credit. USDC is money, Àṣẹ is merit. |
| "The 50/25/15/10 split" | **Only** on 24-sector inflow. `TOKENOMICS_ASE.md` §IX still wrongly presents it as the block-reward split. |
| "Genesis/settlement/P2P are built" | `oso-consensus` **builds green (29 tests)** but has **no P2P layer at all** — `node.rs` prints "Waiting for network connections…" and blocks on `ctrl_c()`. `BLOCKCHAIN_IMPLEMENTATION_CHECKLIST.md` claims 11% and contradicts the working code. |
| "L1" | Ambiguous — resolve before answering. In the OS spec **L1 = Substrate** (boot/HAL/drivers, none of which exists, and the spec says Omo-Koda does not own it). In crypto terms **L1 = the chain = Sui, already decided**. |
| "LOOM is dead" | **LOOM is alive** on VPS1 :8889 (`ares-loom.service active running`). The dead one was the Fold 4 copy. |
| "mycelium cycle runs" | `ares-mycelium-cycle.service` is **inactive/dead**. Substrate mining is not scheduled. |
| "Zangbeto enforces" | Compiles; services not running; enforcement is manual. |
| "IfáScript is wired into Omo-Koda2" | The crate is pinned **25 commits behind**, and `genesis/soul.rs` **reimplements Odù locally** as `SHA256(...)[0]` with 16 hardcoded names rather than calling the engine. |
| "AIO settles" / Move contracts | Present and tested (2/2 PASS on the router), but settlement in practice is **Sui-anchored via a stub**, not self-built. |

**Two self-checking rules that fall out of all this:**

1. `systemctl is-active` + `ss -ltn` + a real HTTP call, or it is not running. Never answer
   "what's up" from a table — including the tables above.
2. `git log -1` + file mtimes, or it is not built. Status docs record intent; the code records
   state; they diverge in both directions here.

---

## 5. WHERE THE LEVERAGE ACTUALLY IS

Three observations from the inventory that are worth more than the repo list:

1. **The bounty is concentrated in receipts.** 87 repos, 36 live daemons, and the piece with
   the most obligation attached and the least runtime enforcement is the receipt chain —
   `ActionReceipt` → Zàngbétò witness → Crucible falsifier → Sui anchor. Every economic
   mechanism in Acts IV and V is downstream of a receipt that is currently produced by the
   kernel but audited by hand. Wiring `steward` into the path is the single highest-leverage
   change available, and it is exactly the failure mode that keeps showing up in practice:
   agents whose summaries contradict their own acceptance scripts.

2. **The kernel is the least-running pillar, and the market loop is the most-running.** 36
   live daemons, almost all intelligence/trading; the sovereign three-pillar path is mostly
   [BUILT]. That is not a criticism — it is the correct ordering (layer over what works), and
   it means the sovereign path should be *earned* into service, not switched on.

3. **The memory layer is the most fragmented and the most duplicated.** Four memory systems
   (Mycelium, GlyphIndex/mnemopi, Minipae/NIP-AE, Synapse/NIP-30, plus Memora and Triune) all
   address cross-agent recall, and the "Odù coordinate" concept is implemented wrongly in at
   least two of them. One real Ọ̀wọ́n pattern-match against the 256 *named* Odù would give the
   whole stack a shared coordinate system instead of six incompatible ones.

---

*Local artifacts referenced: `~/docs/typesafe/STACK-FIT.md`, `~/docs/peaq-vs-omokoda-comparison.md`,
`~/MASTER_TODO.md`. Skill knowledge bases: `omo-koda2-ecosystem`, `ares-ecosystem`,
`ares-habitat-pattern`, `mycelium-pattern`, `vantage-platform-dev`.*
