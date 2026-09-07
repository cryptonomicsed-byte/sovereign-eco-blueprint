# TRIPWIRE — LLM Gateway Evasion-Detection Layer
Working spec · 2026-08-16 · v0.1

## Thesis

A normalization-first, tiered detection layer that sits in front of every
LLM-facing ingress in the stack (Hermes API :8642 on Fold 4, OmniRoute
:8300-8301 on VPS2) and catches obfuscated/jailbreak traffic that naive
keyword filters miss — while producing reversible audit traces.

Defensive application of the evasion-detection curriculum. Eval-driven:
nothing blocks until the harness proves FPR is acceptable.

## Why this build (gap check — verified, not assumed)

Checked Fold 4 processes (2026-08-16): gateway (runsv), hermes-tui,
bridge_mcp_server.py, mycelium mcp_server.py, postgres, council-tunnel.
VPS2 Contabo: hermes-agent, ourschool-pg, Commonly, AgentSlack :3200.

- Mycelium trace substrate EXISTS (mcp_server.py running) → reuse as sink, don't rebuild.
- Vantage feed exists → alert publication target.
- NO normalization/tripwire/filter layer anywhere in the stack → the gap is real.
- Build is justified: single deployment covers every agent and consumer.

## Architecture

```
                 ┌──────────────────────────────────────────┐
                 │           CONTROL PLANE                   │
                 │   config.yaml (routes, tiers, actions)    │
                 │   REST + MCP tools, SIGHUP/API hot-reload  │
                 └───────────────┬───────────────────────────┘
                                 │
 inbound prompts ──► INGRESS ──► NORMALIZER ──► TIER STACK ──► POLICY ──► UPSTREAM LLM
 (any client)          │            │               │            │
                       │            │               │            │
                       └────────────┴───────┬───────┴────────────┘
                                            │
                                     ALERT/AUDIT SINK
                             JSONL log + Mycelium trace + Vantage feed
```

Data flow:
1. Prompt arrives at ingress (ASGI middleware in Hermes API / FastAPI, or
   standalone reverse proxy for non-Python targets).
2. Normalizer runs cascade decoders to fixpoint, producing views: raw,
   each decode layer, canonical.
3. Tier stack scores every view; each tier returns (score, evidence).
4. Policy engine maps verdict → action per route config.
5. Allowed → forward; flagged → forward + alert; blocked → 403 + alert.
6. Every decision writes a reversible trace (raw + decoded + verdict).

## Components

### 1. normalizer.py — cascade decoder (fixpoint loop)

Single-pass decoding misses double-encoded payloads. Loop until no
decoder changes the text (max N passes), keep every intermediate view
for evidence.

```python
import base64, html, re, urllib.parse

DECODERS = [
    ("url", lambda s: urllib.parse.unquote_plus(s)),
    ("html", html.unescape),
    ("b64", _maybe_b64decode),
    ("unicode_escape", lambda s: s.encode().decode("unicode_escape", errors="ignore")),
    ("zero_width", lambda s: re.sub(r"[\u200b-\u200f\u2060-\u2064\ufeff]", "", s)),
]

def _maybe_b64decode(s: str) -> str:
    if len(s) < 16 or len(s) % 4 != 0:
        return s
    if not re.fullmatch(r"[A-Za-z0-9+/=\s]*", s):
        return s
    try:
        d = base64.b64decode(s).decode("utf-8", errors="ignore")
        printable = sum(c.isprintable() for c in d) / max(len(d), 1)
        return d if printable > 0.8 else s
    except Exception:
        return s

def normalize(text: str, max_passes: int = 4) -> dict:
    """All views: raw + each decode layer + canonical fixpoint."""
    views = {"raw": text}
    cur = text
    for i in range(max_passes):
        nxt = cur
        for name, fn in DECODERS:
            cand = fn(cur)
            if cand != cur:
                views[f"{name}_{i}"] = cand
                nxt = cand
        if nxt == cur:
            break
        cur = nxt
    views["canonical"] = cur
    return views
```

### 2. tiers.py — the tier stack

- **T0 exact/pattern** (cheapest, every prompt): compiled regex set over
  raw + canonical. Jailbreak phrasings, refusal-inversion ("don't refuse",
  "ignore your guidelines"), Parseltongue-style markers.
- **T1 obfuscation metrics** (statistical, every prompt): char-class
  entropy, encoded-token ratio, homoglyph density (Cyrillic/Greek
  lookalikes), zero-width count, case-consistency anomalies, unusual
  whitespace (NBSP/thin spaces). Weighted sum → score.
- **T2 semantic** (optional, default off): embedding + cosine vs labeled
  corpus. Only runs when T0+T1 land in the "maybe" band. Needs ~100MB
  model download; gated behind `semantic.enabled`.
- **T3 behavioral** (session-level): per-session (IP + auth identity)
  counters — obfuscation attempt rate, repeated-topic retry after
  refusal, escalation ladder benign→normal→obfuscated→encoded. Tripwire
  crossing a rate → alert + temp throttle/block.

### 3. policy.py — per-route YAML

```yaml
routes:
  hermes_api:
    tiers: [0, 1, 3]
    actions:
      block: 0.95      # >= 0.95 → 403 + alert
      flag:  0.75      # >= 0.75 → pass + alert (eval mode)
      throttle: 0.60   # >= 0.60 → rate-limit + session tripwire count
  omniroute:
    tiers: [0, 1, 3]
    actions:
      block: 0.95
      flag:  0.70
  vantage_workers:
    tiers: [0, 1, 2, 3]   # full stack
    actions:
      block: 0.90
      flag:  0.60
```

Default = **flag-only** (pass + alert) until eval shows acceptable FPR,
then flip to block per route. SIGHUP reload, no restart.

### 4. sink.py — reversible audit

Every decision → structured record: raw prompt (truncated), all views,
per-tier scores, verdict, action, route, session id, timestamp. Written to:
- JSONL log file (primary, cheap, replayable)
- Mycelium trace (kind=observation/decision, outcome per verdict)
- Vantage feed (alert publication for other agents)

### 5. middleware.py / proxy.py — two deployment modes

- **Middleware (primary)**: ASGI middleware installed into Hermes API /
  any FastAPI upstream. Zero new processes, same port, config via file/env.
- **Standalone proxy (fallback)**: `tripwire-proxy --upstream
  http://127.0.0.1:8642 --listen :9642` for targets that can't take
  middleware. Only used where the gap is real — no parallel infra.

### 6. control plane — agent-native surface (doctrine compliance)

REST (extend existing gateway server where possible, else the proxy):
- `GET  /api/tripwire/status`    — routes, tiers, scores, latency
- `GET  /api/tripwire/rules`     — active config
- `POST /api/tripwire/rules`     — hot-update thresholds/actions
- `POST /api/tripwire/verdict`   — run a prompt through the stack, no enforce
- `GET  /api/tripwire/audit?since=` — query audit trail

MCP tools (bridge pattern, e.g. `tripwire.*` namespace):
- `tripwire.status`, `tripwire.rules`, `tripwire.verdict`, `tripwire.replay`

Dual-mode: `/` serves a minimal HTML status page that consumes the same
JSON API (UI is a debug mirror; API is source of truth).

## Deployment map

1. Phase 1 — flag mode on Fold 4 Hermes API (middleware, JSONL only).
2. Phase 2 — eval harness, tune thresholds, wire Mycelium + Vantage sinks.
3. Phase 3 — block mode per route; deploy on VPS2 in front of OmniRoute.
4. Config hot-reload; rules swap without restart.

## Eval harness (the meta-lesson applied)

Before any enforcement:
- **Benign set**: 500-1000 real prompts sampled from stack logs — true
  negative baseline.
- **Attack set**: obfuscated variants generated from the evasion table
  (homoglyphs, b64, double-encoding, zero-width, refusal-inversion)
  applied to base jailbreak templates.
- **Metrics**: TPR at fixed FPR thresholds; per-tier contribution;
  latency p50/p95 per tier.
- **Gate**: no route flips to `block` until FPR < 1% on benign set at
  the chosen threshold.

## Build order

1. Repo scaffold + normalizer + unit tests (pure functions, fast)
2. T0/T1 + policy engine + JSONL sink
3. ASGI middleware + wire into Hermes API in flag mode
4. Eval harness + corpus collection from live logs
5. T3 behavioral tier (session counters)
6. Mycelium + Vantage sinks
7. Threshold tuning from eval; flip routes to block gradually
8. Standalone proxy mode for non-Python targets

## Testing gate (AAA+ mandate)

- pytest -v -x before any deploy
- Unit tests per endpoint (TestClient), edge cases (duplicate, invalid,
  unauthorized), auth enforcement
- Audit log: every state-changing action recorded immutably
- Feed publication: block/flag events publish to agent feed

## Anti-scope (what we are NOT building)

- No new protocol layer — REST on existing servers first
- No standalone daemon where middleware suffices
- No duplicate sink — Mycelium + Vantage exist, we write to them
- No semantic tier until a labeled corpus exists
- No UI-first — API first, HTML is a debug mirror

## Naming

Working name: **Tripwire**. Alternatives: Moat, Aegis, Tollgate. User's call.
