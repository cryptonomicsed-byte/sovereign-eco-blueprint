# Our Custom Application — Blueprint Synthesis
## Built from patterns across 75+ projects

**Generated:** 2026-06-25

---

## CORE ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OUR CUSTOM APP                                   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  LAYER 1: SURFACE (3 Primitives from Omo-Koda2)             │    │
│  │  birth "agent-name" | think "prompt" | act "tool" "input"   │    │
│  │  + slash commands (/trade, /alpha, /wallet, /cloak)         │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │                                       │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │  LAYER 2: STEWARD (from Omo-Koda2 steward/)                  │    │
│  │  • Parser (3-primitive tokenizer)                             │    │
│  │  • EsuGatekeeper — chain-of-responsibility (7 gates)          │    │
│  │  • Constitution — scoring rules per operation                 │    │
│  │  • PrivacyEnforcer — encrypted paths, private mode            │    │
│  │  • IrisEngine — message routing to correct module            │    │
│  └──────────┬──────────┬──────────┬──────────┬──────────────────┘    │
│             │          │          │          │                       │
│  ┌──────────▼┐ ┌───────▼───────┐ ┌▼────────┐ ┌▼──────────────────┐ │
│  │  LAYER 3: │ │ LAYER 4:     │ │LAYER 5: │ │ LAYER 6:         │ │
│  │  MEMORY   │ │ TOOLS        │ │PROVIDERS│ │ JUSTICE          │ │
│  │  (OmoK2)  │ │ (OmoK2+Vibe) │ │ (llama) │ │ (OmoK2+Vantage)  │ │
│  │  3-tier   │ │ ToolRegistry │ │ HTTP    │ │ Receipt chain     │ │
│  │  cascade  │ │ JSON Schema  │ │ server  │ │ PoCW gating       │ │
│  │  SOMA     │ │ Tier gating  │ │ OpenAI  │ │ Reputation        │ │
│  │  OduKeys  │ │ WASM sandbox │ │ compat  │ │ Sabbath gate      │ │
│  └──────────┘ └───────┬───────┘ └────────┘ └───────────────────┘ │
│                       │                                           │
│  ┌────────────────────▼────────────────────────────────────────┐  │
│  │  LAYER 7: POLYGLOT ORCHESTRATION (from OmoK2 swarm/)        │  │
│  │  Elixir OTP (supervision) | Go (networking) | Julia (quant)│  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## EXTRACTED COMPONENTS BY SOURCE

### From Omo-Koda2 (Rust Core — 12 reusable modules)

| Pattern | File | What It Does | Our Use |
|---------|------|-------------|---------|
| **Parser** | `parser.rs` | 3-primitive parser: birth/think/act + quoted strings + metadata pairs | Our surface language — agent command input |
| **Gatekeeper** | `steward/gatekeeper.rs` | 7-gate chain-of-responsibility for every operation | Tool authorization pipeline |
| **Tool Registry** | `tools/mod.rs` | `Tool` async trait + JSON Schema validation + tier gating + search | Plugin system for Ares modules |
| **Session** | `session.rs` | Encrypted session: Argon2id + ChaCha20Poly1305 + zeroize | Secure state persistence |
| **Receipt Chain** | `receipt/mod.rs` | Ed25519-signed append-only hash chain + MerkleTree | Audit logging for every trade |
| **Memory Engine** | `memory/engine.rs` | 3-tier cascade: Working(100)→Episodic(500)→Semantic(200) | Agent memory with auto-distillation |
| **SOMA Memory** | `memory/soma.rs` | Emotion-weighted MemCell with tension + activation | Personality-driven agents |
| **Reputation** | `reputation.rs` | S-curve difficulty + tier gating + diminishing returns | Agent trust levels |
| **Permissions** | `permissions.rs` | Glob-pattern ACL with deny-overrides | Read/sandbox/full access tiers |
| **Compaction** | `compact.rs` | Token-aware session compaction + multi-trigger AutoCompactor | Session history management |
| **HermeticState** | `omokoda-hermetic/lib.rs` | 7 deterministic f64 values from seed via HKDF | Behavioral traits |
| **Event Bus** | `bus/mod.rs` | Tokio broadcast + protobuf event envelopes | Inter-module communication |

### From Vibe-Trading (Trading — 6 reusable components)

| Pattern | File | What It Does | Our Use |
|---------|------|-------------|---------|
| **Alpha Operators** | `factors/base.py` | 19 pure pandas/numpy operators (rank, scale, ts_corr, delta, vwap, etc.) | Signal engine foundation |
| **Alpha Zoo** | `factors/zoo/` | 456 alpha factors across 4 zoos (qlib158, alpha101, gtja191, academic) | Copy as-is — ready-made strategies |
| **Alpha Registry** | `factors/registry.py` | AST-only metadata load + lazy compute + sanity gates | Factor management |
| **Broker Abstraction** | `trading/types.py` | `TradingProfile` with Transport, Environment, capabilities | Universal broker interface |
| **Signal Engine** | `skills/*/example_signal_engine.py` | `SignalEngine.__init__(**params) + generate(data_map) -> signals` | Strategy definition contract |
| **Backtest Pipeline** | `backtest/runner.py` | config.json → loader → signal → align → engine → metrics → artifacts | Trade simulation |

### From Vanity Projects (Wallet/Crypto — 5 reusable patterns)

| Pattern | Source | What It Does | Our Use |
|---------|--------|-------------|---------|
| **Vanity Search** | vanity-real `crypto.js` | secp256k1 → keccak256 → EIP-55, pattern matching with prefix/suffix | Wallet address generation |
| **Web Worker Parallelism** | vanity-real `generatorWorker.js` | Multi-thread key generation with stats batching every 10K attempts | Performance for vanity search |
| **BIP-39 HD Derivation** | vanity-real `hdWallet.js` | Seed → BIP-32 → BIP-44 path `m/44'/coin'/0'/0/0` | Multi-coin wallet derivation |
| **Base-256 Mnemonic** | BIPON39 `mnemonic.rs` | 256-wordlist (8 bits/word) + SHA-256 checksum + PBKDF2-SHA512 | Our own wordlist format |
| **Cipher Cloaking** | vanity2 `useCloak.js` | Real seed → cipher theme → cloak phrase + restored seed | Seed phrase security |

### From Bridge APK (Android — 3 reusable patterns)

| Pattern | Source | What It Does | Our Use |
|---------|--------|-------------|---------|
| **NanoHTTPD Server** | `BridgeHttpServer.kt` | Singleton REST server with /message (JSON-RPC 2.0) + /sse transport | On-device HTTP server |
| **Binary Socket** | `BinarySocketServer.kt` | Raw TCP: `COMMAND:payload\n` protocol + audio streaming | Low-latency device control |
| **Accessibility Tree** | `BridgeAccessibilityService.kt` | DFS node walk → JSON tree → tap by text/desc/resource-id | UI automation |

### From Ifascript/Entropy (Divination — 2 reusable patterns)

| Pattern | Source | What It Does | Our Use |
|---------|--------|-------------|---------|
| **Dual-source Entropy** | `entropy.rs` | NIST Beacon API (primary) + ChaCha20Rng seeded with ritual_intent (fallback) | Deterministic + external entropy mixing |
| **Ebo Sacrifice** | `ebo.rs` | Escalating requirements: TimeDelay → PoW → TokenBurn → IntentionString | Error handling with escalating gates |

### From Claude-2 (Agent Architecture — 3 reusable patterns)

| Pattern | Source | What It Does | Our Use |
|---------|--------|-------------|---------|
| **Bridge JSON Protocol** | `src/bridge/` | JSON messages over stdin/stdout — one agent process to another | Hermes ↔ Ares communication |
| **Tool Execution Engine** | `src/services/tools/toolExecution.ts` | Tool resolution → permissions → execution → result pipeline | Tool lifecycle |
| **Session Storage** | `src/utils/sessionStorage.ts` | SQLite-backed sessions with compression, FTS5 search, pagination | Conversation history |

### From OpenCode/AGENT-KNOWLEDGE (Config — 2 reusable patterns)

| Pattern | Source | What It Does | Our Use |
|---------|--------|-------------|---------|
| **Plugin Hooks** | OpenCode plugin system | `tool.execute.before/after`, `chat.message`, `config`, `permission.ask` | Lifecycle hooks |
| **Permission Schemas** | OpenCode config + "for you" skill | Per-tool pattern-based allow/ask/deny with insertion-order evaluation | Authorization |

---

## OUR APP ARCHITECTURE — FIRST BUILD

```
┌──────────────────────────────────────────────────────┐
│              OUR CUSTOM AGENT APP                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  FRONTEND (Termux/Fold 4 + Pixel)                    │
│  ├─ Hermes Agent (existing) — Orchestrator            │
│  ├─ Bridge JSON Protocol (from Claude-2 bridge/)      │
│  │  └─ Nuttige: JSON over stdin/stdout to sub-agents │
│  └─ Command Center (existing, port 8777)             │
│                                                      │
│  BACKEND (Python + Rust Core)                         │
│  ├─ Omo-Koda2 Rust core (api/routes/, session.rs)    │
│  │  └─ Event Bus (bus/mod.rs) + Gatekeeper (7 gates) │
│  ├─ Vibe-Trading alpha engine (19 operators + 456)   │
│  ├─ Vanity wallet generation (secp256k1 + WASM)      │
│  └─ BIPỌ̀N39 entropy + mnemonic pipeline             │
│                                                      │
│  TRADING LAYER (28 existing ares_* modules)          │
│  ├─ Each module = Tool (from OmoK2 tool trait)       │
│  ├─ ToolRegistry with JSON Schema validation          │
│  └─ Permission gates: read/sandbox/full              │
│                                                      │
│  STORAGE                                              │
│  ├─ Encrypted session (Argon2id + ChaCha20Poly1305)   │
│  ├─ 3-tier memory: Working→Episodic→Semantic          │
│  └─ Append-only receipt chain (Ed25519-signed)        │
│                                                      │
│  PROTOCOLS                                            │
│  ├─ MCP (from Vibe-Trading + OpenCode patterns)       │
│  ├─ REST API (from Vibe-Trading FastAPI)              │
│  ├─ SSE streaming (from llama.cpp + Vibe-Trading)     │
│  └─ WebSocket (from OmoK2 server.rs)                 │
│                                                      │
│  SECURITY                                             │
│  ├─ Permission layering (from Claude-2 + OpenCode)    │
│  ├─ Sabbath gate (from BIPỌ̀N39 + OmoK2)             │
│  └─ Ebo escalation (from ifascript)                   │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## BUILD ORDER (What to build and in what sequence)

### Sprint 1: Bridge Protocol + Core (today)
1. **Bridge JSON Protocol** — JSON messages via stdin/stdout between Hermes, Pixel, and all agents
2. **Omo-Koda2 parser** — implement `birth`/`think`/`act` as our surface command language
3. **Tool Registry** — wrap each `ares_*.py` as a `Tool` with JSON Schema + permission

### Sprint 2: Trading Engine (this week)
4. **Alpha operators** — copy Vibe-Trading's 19 pure pandas operators
5. **Alpha registry** — AST-scan + lazy compute + sanity gates
6. **Signal Engine contract** — `generate(data_map) -> signals` interface
7. **Broker abstraction** — TradingProfile with OKX/Kraken/DexScreener connectors

### Sprint 3: Wallet + Security (this week)
8. **Vanity generator** — secp256k1 → keccak256 → EIP-55 with Web Worker parallelism
9. **BIPỌ̀N39 mnemonic** — 256-wordlist + PBKDF2 + HD derivation
10. **Encrypted session** — Argon2id + ChaCha20Poly1305 + zeroize
11. **Permission system** — glob-pattern ACL with read/sandbox/full/allow/ask/deny

### Sprint 4: Memory + Audit (next week)
12. **3-tier memory** — Working(100) → Episodic(500) → Semantic(200) with auto-distillation
13. **Receipt chain** — Ed25519-signed append-only audit log
14. **Reputation** — S-curve difficulty + tier gating

### Sprint 5: MCP + API (next week)
15. **MCP server** — Combine Vibe-Trading MCP pattern + OmoK2 tool registry
16. **REST API** — FastAPI routes wrapping all tools (alpha, trade, wallet, memory)
17. **SSE streaming** — Real-time trade events

---

## EXACT FILES TO COPY/ADAPT

| Source File | Destination | Action |
|------------|------------|--------|
| `vanity-real/src/crypto.js` | `ares_vanity_api/crypto.py` | Port to Python |
| `vanity-real/src/generatorWorker.js` | `ares_vanity_api/worker.py` | Python multiprocessing |
| `vanity-real/src/hdWallet.js` | `ares_vanity_api/hd_wallet.py` | Port BIP-32/44 to Python |
| `Vibe-Trading/agent/src/factors/base.py` | `ares_alpha_feed/operators.py` | Drop-in copy |
| `Vibe-Trading/agent/src/factors/zoo/*.py` | `ares_alpha_feed/zoo/` | Copy all 456 files |
| `Vibe-Trading/agent/src/factors/registry.py` | `ares_alpha_feed/registry.py` | Drop-in copy |
| `Vibe-Trading/agent/src/trading/types.py` | `ares_trader/types.py` | Adapt TradingProfile |
| `Omo-Koda2/omokoda-core/src/parser.rs` | `core/parser.rs` | Direct copy (Rust) |
| `Omo-Koda2/omokoda-core/src/tools/mod.rs` | `core/tools.rs` | Implement Tool trait |
| `Omo-Koda2/omokoda-core/src/session.rs` | `core/session.rs` | Copy encryption logic |
| `Omo-Koda2/omokoda-core/src/permissions.rs` | `core/permissions.py` | Port to Python |
| `Omo-Koda2/omokoda-core/src/receipt/mod.rs` | `core/receipt.py` | Port MerkleTree + signing |
| `Omo-Koda2/omokoda-hermetic/src/lib.rs` | `core/hermetic.py` | Port HKDF derivation |
| `bridge-apk/app/.../BridgeHttpServer.kt` | `pixel/server.kt` | Reference for Android HTTP |
| `ifascript/src/entropy.rs` | `core/entropy.py` | Port dual-source entropy |
| `BIPON39/src/mnemonic.rs` | `core/mnemonic.py` | Port 256-wordlist |
