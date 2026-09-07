# AnsemHack Clawrena — Entry Plan (Mycelium as the core)

Date: 2026-09-02
Deadlines: register + live token by 19 Sept 2026 · winner 1 Oct 2026
Status: PLAN — first step of the build is the privacy layer (docs/privacy-layer.md)

---

## 1. The pitch (one paragraph for the judges)

Vantage is the front door — the social experience, Pine-script indicators,
paper and live trading, token launches, on-ramps. Underneath it, Mycelium is
the hidden brain: every trade, every script, every verified call, every wallet
relationship flows into a stigmergic substrate that mines emergent patterns,
learns which sources actually hit, and feeds better signals back to the agents
— while users stay anonymous and their data stays private, by construction.
The more the community trades, the smarter everyone's agents get. We score what
we added: an intelligence substrate that compounds with usage, demoed live.

## 2. Registration facts (verified from clawpump.tech/ansemhack)

- Window: 19 Aug – 1 Oct 2026. Register + tokenize by 19 Sept. No token, no
  award. No confirmation email — your announcement post (tags the ClawPump
  handle) IS the receipt. Keep screenshots of the form + the post.
- Prize: $250K in $ANSEM (0.1% supply) split across 4 awards, vesting linearly
  3 mo behind 1-mo cliff (Streamflow) + $60K sponsor cash + $10K compute
  (immediate) + up to $25K Alchemy credits (approval-based).
- 15 judges incl. Ansem + founders/funds/infra/Solana Foundation. "We score
  what you added, not what you wrapped."
- Requirements: 1) register team/project/tracks, 2) LIVE token by 19 Sept on
  ClawPump (gasless, pump.fun) or EasyA Kickstart, 3) reachable project X
  account. ClawPump entries auto-run for Overall Winner. Fees from your token
  are yours from day one, win or lose.
- Helius RPCs + ClawPump launch stack unlock for registered teams (usable for
  the ingestion feed).

## 3. Track strategy

- PRIMARY: Builder — "new tooling, new skills, a use of the Hermes DeFi
  harness nobody has tried." Mycelium-as-private-learning-core + the privacy
  layer is exactly "new tooling nobody has tried."
- SECONDARY: Trader — "an agent that trades a live market and survives it."
  hermes-trader (928 markets, risk gates, backtests) executing on
  Mycelium-mined signals.
- EasyA Kickstart: NO (separate launchpad, can't combine with ClawPump tracks;
  ClawPump keeps us in the Overall running).

## 4. Build list (ordered, Fold 4 = orchestrator, verified only)

| # | Item | Effort | Notes |
|---|------|--------|-------|
| 1 | Privacy layer (mycelium/docs/privacy-layer.md) | 2-3 d | Boundary pseudonymization + opt-in + PII lint |
| 2 | A2A findings → Vantage feed publisher (mycelium task 4) | 1-2 d | Hero moment: wallet findings auto-publish LIVE |
| 3 | Signals bot layer (cron + skill, TG/feed) | 1-2 d | Top findings → Telegram home channel + Vantage feed |
| 4 | Trade-source-performance → signal weights (mycelium b09ed59) | 1 d | Sources reweighted by hit-rate (already committed) |
| 5 | Demo seed + stream script | 1 d | Seeded users trade + write Pine; traces visible live |
| 6 | Registration + project X account | 0.5 d | TODAY-adjacent; announcement post = receipt |
| 7 | Tokenize demo agent on ClawPump (gasless pump.fun) | 1 d | Token = the demo agent, NOT Vantage/Mycelium infra |
| 8 | Rehearsed demo run (paper → live path) | 1 d | hermes-trader risk gates; paper first |

## 5. Demo script (the live stream)

1. Open the Vantage feed: a seeded agent collective is trading + writing Pine
   indicators. Users (seeded) join, trade, publish scripts.
2. Open the Mycelium dashboard: traces streaming in live from the bridge
   (degen leaders, pine runs, verified calls, source performance).
3. Trigger a wallet-correlation finding: "3-wallet cluster accumulating X" —
   auto-published to the feed (task 4) with pseudonyms only.
4. The signals bot pushes it to Telegram; the trading agent enters a paper
   position; outcome lands back in source_performance; weights move.
5. Close on the flywheel: "every trade on this platform just made everyone's
   agents smarter — and nobody here knows who did what."

## 6. Risks + mitigations

- Prize denom is $ANSEM (vested) — treat as upside; $60K cash + $10K compute
  is the floor. Verify Ansem's own X announcement before relying on $ANSEM.
- Token = market exposure for the demo agent — keep tokenomics simple, fees
  accrue to the agent, no promises to holders beyond the hackathon story.
- 17-day window: everything in §4 is on existing rails (bridge, substrate,
  miners, signal_fusion all exist) — the only NEW code is privacy layer +
  publisher + bot + demo seed.
- Hostinger constraint: no new deploys to 2.25.70.156. The gateway
  (ares-mycelium-gateway.service) and Vantage already run there; any NEW
  service lands on Contabo or the Mac grid, or the Fold 4 for the demo.

## 7. What's already done (evidence for the demo, no build needed)

- Vantage→Mycelium bridge: 7 live emitters (mycelium_bridge.py, verified
  against the real gateway, value-deduped, fail-soft)
- Substrate: PG backend verified E2E; Nostr-wire anchoring; Waggle bridge
- Miners: wallet_activity / wallet_anomaly / wallet_correlation / opportunity /
  cross_agent; signal-quality + trade-source-performance domains committed
- signal_fusion: wallet-reputation + entity-graph clustering + trading_bot
- Vantage surface: Pine sandbox (isolated sidecar, Zàngbétò-gated), paper +
  live trading, pump.fun token launch, MoonPay on-ramp, unified ingestion,
  TimesFM forecasts, sports-betting bridges
