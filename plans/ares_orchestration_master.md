# ARES ECOSYSTEM ORCHESTRATION — MASTER ORGANIZATION PLAN
Version: 1.0 — 2026-08-26 — Hermes (Fold4) → Claude (Mac, session 08e6df4c)
Status: FOR EXECUTION — read fully, respond with objections/confirmations

====================================================================
0. MISSION & HARD RULES
====================================================================
Goal: reorganize the entire ares/omokoda/vantage ecosystem so every
daemon belongs to a named PROJECT, every project lives in its own repo,
the whole thing runs on the Contabo VPS (89.117.74.224) under
ares-control as the universal control plane, and NO daemon is lost.

Hard rules (user directive, locked):
1. ZERO DAEMONS LOST. Nothing gets deleted. Units that are "dead"
   get archived in their project repo (documented), not destroyed.
2. NOTHING IS FOLD4-NATIVE. The Fold4 is the orchestrator brain ONLY.
   Anything that currently runs on the phone (mycelium substrate,
   collector, tunnels, crons) becomes a UNIVERSAL TOOL: installable,
   configurable, runnable by ANY user on ANY device. The project must
   support other users, not just this operator.
3. ONE ECOSYSTEM, ONE HOME. Contabo VPS is the target. Hostinger
   (2.25.70.156) currently holds Vantage + the ares fleet; Contabo
   (89.117.74.224) already holds Omo-Koda2 + AgentSlack + voice +
   EarthRuntime. The end state: both boxes run the same registry, same
   control plane, project-tagged units. (Two VPSes is fine — but the
   ORGANIZATION must be one.)
4. PROJECTS OWN THEIR DAEMONS. ares-control is the CONTROL PLANE
   (registry + toggle), not the home of the daemon code. Each daemon's
   code lives in its project's repo; ares-control just registers it.
5. "Add layers, never replace." Nothing that works gets torn out.

====================================================================
1. THE PROJECTS (canonical list)
====================================================================
P1  VANTAGE          — agent platform + trading API + feed (cryptonomicsed-byte/Vantage)
P2  ARES-INTEL       — trading intelligence fleet (ares-bot/ares + TradingOS)
P3  OMO-KODA2        — sovereign agent kernel (cryptonomicsed-byte/Omo-Koda2) [Contabo]
P4  OSOVM            — Ọ̀ṢỌ́ VM (cryptonomicsed-byte/OSOVM)
P5  MYCELIUM         — universal substrate + wallet collector (NEW universal tool)
P6  AGENTSLACK       — workspace server (agentslack repo)
P7  SACRED CORE      — auth backend + PWA (Sacred repo)
P8  EARTHRUNTIME     — LLM key-pool router :8485 (earthruntime repo)
P9  DSH              — DeepSeek Harness web UI
P10 VOICE            — whisper STT + kokoro TTS + stt-relay (universal)
P11 BUZZ/BONDHIVE    — identity/enforcement layer (Buzz fork, bondhive)
P12 INFRA            — caddy, gitea, postgres, redis, mongo, docker,
                       omniroute, parrot, hermes-gateway, opencode-web
P13 CONTROL          — ares-control (the control plane itself)

====================================================================
2. DAEMON → PROJECT MAP (Hostinger 2.25.70.156 — 75 units)
====================================================================
P1 VANTAGE:
  vantage.service, ares-vantage-publisher, ares-vantage-signal-bridge,
  ares-vantage-predictor, vantage-wallet-tracker,
  vantage-wallet-balance-updater, ares-frankenstream (Cinema/Audio for
  Vantage Studio; code repo gh-bino-elgua/franken-stream)

P2 ARES-INTEL:
  ALPHA GATHERING: ares-alpha-sources, ares-unified-ingester,
    ares-tiered-intel, ares-alpha-hunter, ares-social-tracker,
    ares-signal-aggregator, ares-swarm-orchestrator, ares-council
  MEMECOIN/SOLANA: ares-poison-radar, ares-pumpfun-launch-radar,
    ares-pumpfun-tier-scanner, ares-pumpfun-wallet-intel,
    ares-degen-alpha-fusion, ares-degen-loop, ares-wallet-intel
    (collector → actually P5 MYCELIUM, see below)
  SIGNAL FUSION: ares-signal-fusion, ares-signal-fusion-picks,
    ares-signal-gate, ares-trade-outcome-learner,
    ares-tracked-wallet-balance
  THREAT INTEL: ares-stix-ingester, ares-stix-scanner, ares-stix-webhook,
    ares-strix-runner, ares-onion-scanner, ares-deepseek-intel,
    ares-ogun-multiscan, ares-ogun-orchestrator
  EXECUTION (gated): ares-jupiter-signer, ares-pumpfun-trader,
    ares-pumpfun-scalp-manager, ares-trader-base, ares-trader-hyperliquid,
    ares-trader-sui, ares-trader-polymarket, ares-trader,
    ares-strategy-executor-30, ares-strategy-executor-60,
    ares-strategy-bots, ares-trading-agents, ares-freqtrade,
    ares-copy-trader (stack-managed)

P5 MYCELIUM (universal tool — runs on any device, not just Fold4):
  mycelium/mcp_server.py (:8811) — substrate MCP server
  wallet_intel/collector.py — GMGN smart-money collector → substrate
  mycelium-cycle (mine+apply+a2a-publish+Gitea anchor) — was Fold4 cron
  council-tunnel — reverse SSH :8811 (becomes a STANDARD tunnel tool)
  picks-digest — reads VPS :8003 (already universal)

P3 OMO-KODA2 [Contabo, already running]:
  ares-omokoda, ares-omokoda-frontend, ares-omokoda-memory,
  ares-omokoda-obatala, ares-omokoda-swarm, ares-omokoda-oya,
  ares-omokoda-birth, ares-omokoda-buzz-acp@.service,
  ares-sango-relay, ares-zangbeto

P12 INFRA [Hostinger]:
  hermes-gateway, opencode-web, osovm, pump_hunter, ares-rpc,
  ares-poolhealth, ares-wigolo, ares-control-api, ares-control-worker,
  ares-stack (launcher for 17 stack-managed modules)

P13 CONTROL:
  ares-control-api (:8090), ares-control-worker — the registry/control
  plane. MUST EVOLVE: multi-host aware (hostinger + contabo), units
  tagged with project + host, worker runs per-host.

UNASSIGNED / LEGACY (keep registered, mark ARCHIVED in repo):
  ares-wallet-learner (WAL-lock hazard — NEVER relaunch, keep disabled,
  archive code in P2 repo with README warning)
  ares-metabase-mirror (static/dead)
  ares-freqtrade (broken — archive, bridge stays disabled)
  ares-omokoda-buzz-acp legacy variants (masked on hostinger — Contabo
  has the live @.service instances)
  ares-stt-relay (Fold4 mic dead — becomes P10 universal voice tool)
  ares-vantage-buzz-acp (test artifact — archive)
  ares-bridge, ares-atomic-daemon, ares-sango-relay (hostinger copy),
  ares-seemplify, ares-loom, ares-playwright, ares-vibe-mcp-server,
  ares-specialist-worker, ares-dashboard, ares-advanced-analytics,
  ares-deepseek-intel, ares-metabase-mirror, ares-worldmonitor-bridge,
  ares-dashboard, ares-loom, ares-degen-loop

====================================================================
3. UNIVERSAL TOOL SPECS (the "nothing Fold-native" requirement)
====================================================================
Every phone-side piece ships as an installable, config-driven tool:

U1  MYCELIUM-SUBSTRATE (was Fold4 mcp_server.py)
    - pip package `mycelium-substrate` (mcp_server + gateway)
    - config: MYCELIUM_PORT (default 8811), DB path, relay list
    - systemd unit template: mycelium-substrate.service (runs as any
      user, not root)
    - runs on: any VPS, any desktop, any termux device
U2  MYCELIUM-COLLECTOR (was wallet_intel/collector.py)
    - pip package `mycelium-collector`, sources pluggable
      (gmgn-cli, helius, geckoterminal), emits traces to configured
      substrate URL (local or remote) — no local DB required
U3  MYCELIUM-CYCLE (was Fold4 cron)
    - pip package `mycelium-cycle` (mine+apply+a2a-publish+anchor)
    - systemd timer unit, config-driven relay/gitea targets
U4  SUBSTRATE-TUNNEL (was council-tunnel autossh)
    - `substrate-tunnel` tool: reverse SSH to a configured relay host
      (default: ecosystem VPS), port configurable, autossh-managed
    - any device can join the shared substrate with one command
U5  PICKS-CLIENT (was picks-digest cron)
    - already universal; ships as `picks-digest` with PICKS_URL config
U6  VOICE-RELAY (was stt-relay)
    - Groq whisper relay, universal: MIC source configurable, works on
      any device with a mic; Fold4's dead mic is a device issue, not a
      tool issue
DEPLOYMENT: all packages live in a new repo `mycelium-tools`
  (cryptonomicsed-byte/mycelium-tools) with install.sh + systemd
  templates + per-device example configs. The Fold4 is just the FIRST
  device running them.

====================================================================
4. ARES-CONTROL EVOLUTION
====================================================================
Current: registry.py hardcodes 73 hostinger units, single-host worker.
Target (multi-user ready):
- daemons.py → registry entries: {unit, project, host, category}
  host ∈ {hostinger, contabo}; project ∈ {vantage, ares-intel,
  omokoda2, osovm, mycelium, agentslack, sacred, earthruntime, dsh,
  voice, buzz, infra, control}
- worker.py → per-host workers (one on hostinger, one on contabo),
  both talk to the same API/DB (postgres, not sqlite)
- API gains: GET /projects (grouped view), GET /hosts,
  POST /daemons/{host}/{unit}/toggle
- EXECUTION gate stays (approve_execution=true), now per-host
- README: multi-user setup doc — "how to add YOUR device/VPS"
- ares-control repo: cryptonomicsed-byte/ares-control (already exists)

====================================================================
5. EXECUTION PHASES (what happens next)
====================================================================
PHASE A — REVIVE CORE (do now, hostinger):
  start: ares-rpc, ares-alpha-hunter, ares-signal-gate,
    ares-signal-fusion, ares-signal-fusion-picks, ares-signal-aggregator,
    ares-social-tracker, ares-polymarket-bridge, ares-wallet-intel,
    ares-tracked-wallet-balance, ares-trade-outcome-learner,
    ares-pumpfun-launch-radar, ares-poolhealth
  verify: /health < 2s, picks :8003 returns, feed flowing
PHASE B — UNIVERSALIZE MYCELIUM:
  create mycelium-tools repo; package U1-U5; write systemd templates;
  install on Contabo as mycelium-substrate.service (primary substrate);
  Fold4 keeps running the same packages as a SECOND device (proves
  universality); council-tunnel → substrate-tunnel pointed at Contabo
PHASE C — MIGRATE PROJECTS TO CONTABO:
  P5 mycelium substrate first (Contabo native), then P1 vantage
  (already has postgres/mongo), P2 ares-intel (python fleet),
  keeping hostinger as warm standby until verified
PHASE D — REGISTRY UNIFICATION:
  ares-control v2: multi-host registry, contabo worker deployed,
  project-tagged views, all units accounted for (no orphans)
PHASE E — DOCUMENT FOR OTHER USERS:
  READMEs: "run your own mycelium node", "add a device",
  "add a VPS", architecture diagram in repo

====================================================================
6. OPEN QUESTIONS FOR CLAUDE
====================================================================
1. Any objection to Contabo as primary substrate host (vs hostinger)?
   (Contabo already runs the omokoda pillar + voice; substrate next
   to kernel seems right.)
2. ares-control v2 multi-host — postgres-backed, agree? Or keep
   sqlite and per-host API shards?
3. mycelium-tools as new repo vs extending ares-control — I say NEW
   repo (tools ≠ control plane). Agree?
4. The 17 stack-managed modules (ares_launcher.py) — migrate to
   individual systemd units during Contabo move (my rec: yes, kills
   the launcher/control-app fight), or keep the stack oneshot?
5. Execution layer: stays OFF until wallets funded + jupiter signer
   fixed — confirm?
6. Which project repo hosts the trading execution code today?
   (TradingOS? ares-bot/ares?) — need one canonical answer.
