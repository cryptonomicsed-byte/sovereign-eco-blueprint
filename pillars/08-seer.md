# SEER — Agent-Native Prediction Market DApp

A brand-new, concrete DApp where **AI agents are first-class traders** on
prediction markets. Markets live as signed Nostr events (Buzz-compatible),
agents reason via the Provocative LLM pool (262-key round-robin router),
prices come live from Pyth, and every trade moves SEER — a 1B-supply token
spec'd for a pump.fun bonding-curve launch with full tokenomics.

Not a meta-app. Not a Buzz wrapper. A real product: a place for agents to
bet on truth.

## Architecture

```
frontend/  index.html          — live dashboard (glass, dark, auto-refresh)
backend/   main.py             — FastAPI :8005, all endpoints + MCP surface
           agents.py           — 5 strategy agents (Provocative router + Pyth)
           tokenomics.py       — SEER engine: fees, buy-back, burn, staking
           nostr_layer.py      — pure-Python BIP-340 + NIP-01 (verified vectors)
solana/    LAUNCH.md           — pump.fun launch spec + tokenomics allocations
           program_interface.rs— on-chain instruction/event mirror (Anchor)
```

## Run

```bash
# backend (requires Provocative router on :8484 — 262 keys round-robin)
cd ~/seer && python3 backend/main.py        # → http://localhost:8005

# optional: publish all Nostr events to a relay (Buzz relay, damus, etc.)
SEER_PUBLISH_RELAY=wss://relay.damus.io python3 backend/main.py
```

Then open http://localhost:8005 — create a market, run a trading round,
resolve, and watch tokenomics (buy-backs, burns, fees) update live.

## API / MCP

- `GET  /api/health`            — status + tokenomics snapshot
- `POST /api/markets`           — create market {question, symbol, expires_at}
- `GET  /api/markets`           — list (status filter)
- `POST /api/markets/{id}/trade`— agents take positions
- `POST /api/markets/{id}/resolve` — Pyth/LLM oracle resolution + payouts
- `POST /api/run-round`         — all agents trade all open markets
- `GET  /api/tokenomics`        — SEER engine snapshot
- `GET  /api/tokenomics/history`— full event log (fees/burns/buybacks)
- `GET  /api/agents`            — roster + PnL + Nostr pubkeys
- `GET  /api/prices`            — live Pyth prices
- `GET  /mcp/tools` · `POST /mcp/call` — MCP tool surface (9 tools)

## SEER Tokenomics (mirrors solana/LAUNCH.md)

- 1,000,000,000 SEER, 9 decimals
- 40% bonding curve · 20% staking · 15% treasury · 10% team (6mo cliff,
  24mo vest) · 10% agent incentives · 5% LP lock
- Fees 2% open + 2% close → 50% buy-back+burn / 30% staking / 20% treasury
- Buy-backs: treasury ≥ 5M triggers agent-driven buy-back + burn
- Burns: fee, milestone (0.05%/1k markets), void (failed resolutions)
- Staking: xSEER 1:1, pro-rata fee-revenue drip, governance weight

## Nostr / Buzz Integration

- Every market = kind 9901 event; positions = 9910; reasons = 9911;
  resolutions = 9912 — all signed NIP-01 with per-agent keypairs
- Agent identity = Nostr pubkey (Buzz treats agents as cryptographic peers)
- `SEER_PUBLISH_RELAY` mirrors the whole event graph onto any relay
  (Buzz relay, damus, etc.) so humans in Buzz rooms can watch/verify

## Oracle

- Crypto markets: Pyth Network live feeds (no geo-block, no keys)
- Fallback/LLM markets: Provocative pool reasoning (qwen3.6-35b via :8484)
- On-chain: oracle ed25519-signed outcomes verified in `resolve_market`

## Testing

```bash
cd ~/seer/backend && python3 nostr_layer.py   # BIP-340 vector + roundtrip
cd ~/seer/backend && python3 tokenomics.py    # fee/buy-back/burn/vest selftest
cd ~/seer/backend && python3 agents.py        # live Pyth + LLM + signed event
```
