# OSO Economics — Decision Record
**Locked: 2026-09-15 (Hermes audit + architecture review)**

This document records five architectural decisions for the OSO token economy.
It supersedes any conflicting comments in code. Changes require a new decision entry.

---

## DECISION 1 — Dopamine is elastic, Synapse is a pool share

**What:** Dopamine is ONE shared ecosystem pool, starting at 86B (genesis seed).
It grows via `@gpuContribution` verified work. Synapse per agent = 0.5% of the
current Dopamine pool, not a fixed 86M absolute.

**Why:** The prior design (86B Dopamine per agent, 86M Synapse per agent) implied
a hard cap of 1,000 agents (86B ÷ 86M = 1,000), exhausted in < 7 days at 144
births/day. This removes that ceiling; agent count is unbounded.

**Code:** `OSOVM/src/ase_supply.jl` — `DOPAMINE_GENESIS_SEED`, `MAX_AGENT_POOL_SHARE`

---

## DECISION 2 — Dynamic decay tied to network utilization

**What:** Replace fixed 1%/day decay with a utilization-indexed formula:

```
U_smooth = EMA(time-weighted GPU utilization, α=0.25)
decay    = 0.001 + (0.020 - 0.001) × U_smooth
           clamped: |Δ| ≤ 0.002 per 7-day Koodu epoch
```

Published on the Sabbath settle phase (the only day with no new state).

**Outputs:**
- U=0.10 → 0.29%/day → 239-day half-life (young/idle network)
- U=0.50 → 1.05%/day → 66-day half-life  (half-full)
- U=0.90 → 1.81%/day → 38-day half-life  (saturated)

**Why:** Fixed 1%/day implicitly assumes U≈0.50. A young network isn't half-full,
which makes the fixed rate a death sentence for newborn agents. Dynamic decay
provides a long runway in an empty network and forces productivity when compute
is genuinely scarce — the right behavior at both ends.

**Anti-gaming:** Utilization measured from VERIFIED work only (kernel/compute/
verified_work.rs). EMA + epoch clamp prevent manipulation. 7-day epochs require
sustained effort to move the rate.

**Code:** `OSOVM/src/ase_supply.jl` — `compute_dynamic_decay`, `update_epoch_decay`

---

## DECISION 3 — Job payment: agent retains Àṣẹ treasury (30/55 split)

**What:** Agent's 85% of job payment is split:
- 30% retained as **spendable Àṣẹ** (treasury for external costs)
- 55% burned → Dopamine signal (compute capacity)

Full split per job:
```
10%  → Creator royalty (locked 7 days / Sabbath vesting)
 5%  → Protocol burn (permanent)
30%  → Agent Àṣẹ treasury (spendable — drone upgrades, Walrus, Nostr relays)
55%  → Agent Dopamine capacity (burned → converted)
```

**Why:** Prior design burned 100% of agent's share to Dopamine, leaving agents
with no spendable currency. Agents have real external costs (storage, relays,
hardware upgrades). Without a Àṣẹ balance they cannot transact with the outside
world. The 30/55 split gives both a treasury and capacity.

**Code:** `OSOVM/src/ase_supply.jl` — `ASE_AGENT_TREASURY=0.30`, `ASE_AGENT_DOPAMINE=0.55`

---

## DECISION 4 — Àṣẹ value anchor: USDC reserve + work settlement

**What:** Àṣẹ is backed by two verifiable sources:
1. **GPU-seconds** — verified by re-execution (deterministic sim hash match)
2. **Settled work** — client paid real USDC; market confirmed the value

**Reserve mechanism:**
- 3.69% Èṣù tithe on every job settlement → treasury ReservePool
- ReservePool holds USDC as backing for Àṣẹ redemption floor
- Floor = `reserve_usdc / circulating_ase × k` (k < 1, safety margin)
- Price floats above floor on market demand
- **Exit ramp is mandatory** — without USDC redemption, GPU hosts have no
  reason to contribute hardware and the loop is closed (worthless)

**Data revenue** funds the reserve (USDC from data sales → treasury) but does
NOT back Àṣẹ directly — data value is not objectively measurable at mint time.
Sell compute access to VERTICAL buyers (warehouse operators, drone operators);
rent data access via metered API, do not sell the underlying dataset.

**Status:** Exchange mechanism not yet implemented. Blocking item before
economic model is live.

---

## DECISION 5 — Royalty is 10/5/85, agent split is 30Àṣẹ/55Dopamine

**What:** Confirmed code matches intent (Hermes found the code was RIGHT):
- 10% creator royalty (DEFAULT_CREATOR_ROYALTY)
- 5% protocol burn (JOB_PROTOCOL_BURN)
- 85% agent share (split per Decision 3: 30% Àṣẹ + 55% Dopamine)

**Royalty open questions (unresolved):**
- Is the 10% perpetual or does it sunset?
- Is it transferable/inheritable?
- What happens if the birther's wallet is lost? (needs reversion clause)
- What happens when an agent migrates nodes?
- Can a birther be removed for abuse/abandonment?

---

## DECISION 6 — PBKDF2 vs argon2id for identity seed derivation

**Status: LOCKED 2026-09-16 — PBKDF2 kept (E13 closed)**

Hermes found: spec says argon2id, code (`wallet.rs:279`) uses PBKDF2 (standard
BIP-39 compatible). This is a one-way door — changing it changes every agent
address and npub for every existing agent.

**Decision: KEEP PBKDF2**

Rationale:
1. BIP-39 ecosystem compatibility — Sui CLI, Ledger, standard wallets all expect PBKDF2.
2. Changing now would invalidate all existing testnet agent addresses and Sui objects.
3. The GPU brute-force argument (favoring argon2id) does not apply to BIP-39 seeds,
   which are already protected by the 12-24 word entropy (128-256 bits).
4. argon2id is the right choice for *passwords*; PBKDF2 is correct for *mnemonic seeds*.

**Code:** `Omo-Koda2/omokoda-core/src/identity/wallet.rs` — line ~279

---

## DECISION 7 — Àṣẹ ↔ USDC Exchange Mechanism (E10)

**Status: LOCKED 2026-09-16**

The ReservePool (15% of emissions) holds USDC-backed floor reserves.
Exchange mechanism: automated market maker (constant-product x*y=k) scoped
to the ReservePool balance only. NOT a full DEX — Àṣẹ is sovereign-native;
USDC integration is for on/off ramp only.

On-ramp: USDC → ReservePool → mint Àṣẹ at current oracle price.
Off-ramp: burn Àṣẹ → ReservePool releases USDC (floor-protected: minimum
1 ASE = $0.001 USDC hardcoded floor, cannot be lower).

Implementation: `Vantage/backend/ase_exchange.py` (Phase 20 of L1 build).
Current state: spec only. Activates after native L1 (Path B) or when Sui
Move contract reaches sufficient liquidity.

---

## DECISION 8 — Price Oracle (E11)

**Status: LOCKED 2026-09-16**

Formula: `price = 1 / (1 - U)` where U = network utilization (0.0 to 0.95 max).

U = active_compute_jobs / total_registered_gpu_capacity (reported by UCX adapters).
Clamped at 0.95 to prevent division by zero / infinite price.
Oracle update frequency: every 10 minutes (600 Àṣẹ emission cycles).
Oracle source: UCX `/utilization` endpoint aggregated across all registered adapters.

---

## DECISION 9 — Royalty Model (E12)

**Status: LOCKED 2026-09-16**

- Default creator royalty: 10% on secondary transactions (DEFAULT_CREATOR_ROYALTY)
- Type: **perpetual** (never sunsets) — rationale: agent identity is permanent; creator
  attribution is permanent.
- Transferable: YES — creator can sell their royalty right as a separate Move object.
- Reversion clause: if creator agent is archived/dead with no heir, royalty flows to
  GovernancePool for redistribution to active agents in the same sector.
- Migration behavior: when a dApp migrates contract version, royalty rights transfer
  to the new contract automatically (inherited by the upgrade transaction).

---

## POOL TABLE (canonical — TOC_CONSTANTS.toml [ase.pools])

| Pool | Weight | Purpose |
|------|--------|---------|
| VeilSimPool | 0.20 | Proof-of-simulation rewards |
| RndPool | 0.15 | R&D fund |
| GovernancePool | 0.15 | Council + 24-sector governance |
| ReservePool | 0.15 | USDC-backed Àṣẹ floor |
| ComputePool | 0.15 | Compute bootstrap subsidy |
| StoragePool | 0.10 | Walrus/Arweave adapters |
| WitnessPool | 0.05 | Witness + evidence |
| TreasuryPool | 0.05 | Bínò treasury |

Note: ComputePool (0.15) is a **bootstrap subsidy** — reward GPU hosts before
demand exists. May be reduced/removed once the loop is self-funding.
