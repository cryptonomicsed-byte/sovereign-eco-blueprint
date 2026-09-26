# Three-Tier Tokenomics — ASE / SYNAPSE / DOPAMINE

**Status:** DRAFT — supersedes the two-tier description in `TOC_CONSTANTS.toml` once the deltas in §8 are applied.
**Written:** 2026-09-26
**Gate:** `specs/tokenomics_invariant_check.py` (15 invariants; currently **12 failing**)
**Related:** `AGENT_COMPUTE_WALLET_SPEC.md`, `ASE_EMISSION_GOVERNANCE_SPEC.md`, `WITNESS_NODE_SPEC.md`, `ECONOMICS_DECISIONS.md`, `L1_DECISION_MEMO.md`

---

## 1. The three tiers

| Tier | Holder | What it is | Transferable |
|---|---|---|---|
| **ASE** | humans only | the only unit humans touch — pays for jobs, access, any interaction with any agent | yes, between humans |
| **SYNAPSE** | agents only | a credit denominated in **GPU-hours** (1,000 Synapse = 1 verified GPU-hour) | between agents only, identity-gated |
| **DOPAMINE** | the hive | the hive's compute capacity. Never a bearer asset. | no — spend-right only, never balance transfer |

One sentence each, because the confusion in the current code comes from these being fuzzy:

- **ASE never touches an agent.** An agent has no ASE balance and no ASE address. This is the membrane.
- **SYNAPSE is the agent's compute budget**, minted when a human converts ASE, burned when it is spent.
- **DOPAMINE is the hive's capacity register.** It is a *fact about available compute*, not a coin. Agents may direct it at each other; they may not move it as a balance.

## 2. One-way valves (the whole security model lives here)

```
      HUMAN SIDE                 AGENT SIDE                HIVE SIDE
   ┌──────────────┐          ┌──────────────┐          ┌──────────────┐
   │     ASE      │          │   SYNAPSE    │          │   DOPAMINE   │
   │  (spendable) │          │ (GPU-hours)  │          │ (capacity)   │
   └──────┬───────┘          └──────┬───────┘          └──────┬───────┘
          │                         │                         │
   post job / buy credit             │                         │
          │  ASE is BURNED          │  credit REDEEMED        │
          └────────► mint credit ───┤  (burned, atomic)       │
                                                          │
                                    allocate to hive ─────┘
                                    (spend-right, not transfer)

   REVERSE FLOW — the only exits back to humans:
     birther royalty (10% of external revenue)
     job-creator royalty (10%, Sabbath-vested)
     GPU-host payout (ASE minted against delivered GPU-hours)
     governance / reserve / treasury / R&D pool spend
```

The valves are the design. Every hole found below is a place where value can flow *backwards* across a valve or *sideways* around one.

## 3. The conversion flow, specified

**Purchase (human buys compute for an agent):**
1. Human pays `P` ASE to the protocol (not to the agent).
2. Protocol mints a **credit object**: unique id, agent_id, GPU-hours, price paid, expiry. ASE is burned in the same transaction.
3. Human redeems the credit → `GPU-hours × 1,000` Synapse is allocated to the agent's balance; credit object is consumed (deleted).
4. The `P` ASE is split at step 1, before hand-off — the agent never sees it:
   - GPU-host share (paid for the compute actually delivered)
   - treasury / reserve / governance / R&D (per §8 canonical pools)
   - burn
5. The agent converts Synapse → Dopamine when it actually draws compute from the hive.

**Job posting (human funds work for an agent):**
1. Human funds job with `P` ASE into escrow (AIO `escrow.move`).
2. On acceptance, escrow converts: `10%` to the birther, remainder split per §8, `GPU-hours` credited to the agent.
3. On delivery, escrow releases. On failure/expiry, escrow refunds the poster and **the birther cut is not paid**.

The load-bearing detail: **the birther is paid at conversion, contingent on delivery.** If the birther is paid at funding time, a failed job pays the birther out of the eco split — that is a hole (§6, T-8).

## 4. Capacity math — where the current constants break

Verified from `TOC_CONSTANTS.toml` + `OSOVM/src/constants.jl` + `omokoda-core/src/economics.rs`:

```
DOPAMINE genesis seed      86,000,000,000   (86B)
SYNAPSE per agent (cap)        86,000,000   (86M)
conversion                 10 Dopamine = 1 Synapse
rate                    1,000 Synapse = 1 verified GPU-hour
```

Derived:

```
hive pool       86B Dopamine  = 8.6B Synapse   =    8,600,000 GPU-hours
per-agent cap   86M Synapse                    =       86,000 GPU-hours
=> only 100 agents can be endowed at cap
```

Two conclusions, both uncomfortable:

1. **86,000 GPU-hours per agent is ~9.8 GPU-years.** That is not a grant; it can only be a lifetime ceiling, and a meaningless one.
2. **Under the current numbers the hive is scarce, not the agent.** One agent's cap is 1% of the entire hive pool. The stated target is millions of agents; at cap, 100 agents exhaust the pool.

The scarcity you want — *the agent is the scarce good, so nobody else can buy its compute* — is only true when per-agent capacity is small relative to the hive. That is a function of population, not of a constant:

```
per-agent capacity (GPU-h) = (pool GPU-h × tier_weight) / active_agent_count   per Koodu epoch

   100 agents        →   86,000 GPU-h each
   10,000 agents     →      860 GPU-h each
   1,000,000 agents  →      8.6 GPU-h each
   10,000,000 agents →     0.86 GPU-h each
```

Make capacity **derived and recomputed each epoch**, not a printed constant. Then:
- the agent becomes scarce *as the population grows*, which is the dynamic you asked for and it self-adjusts;
- scarcity is priced by the curve in §5 rather than hardcoded;
- hoarding is pointless because unused allocation decays (§6, T-11).

Since DOPAMINE is elastic ("grows with verified compute contributed"), the honest formulation is:

```
per-agent capacity = (contributed GPU-hours × allocation_fraction) / active_agent_count
```

Capacity is **earned into existence by compute that actually joined the hive**, not printed by a genesis constant. That is the only version where the 86B means anything.

## 5. Dynamic pricing

Your rule, stated as two curves with bounded slopes:

**Synapse credit price, in ASE — per agent**
```
U        = allocated_capacity / total_capacity          # 0..1
price_h  = base_ase_per_hour × (1 + U × spread)          # spread ≈ 1.0 → doubles at full
```
Cheap when the agent has capacity spare; dear when it is nearly consumed. Matches "more available = cheaper, more allocated = higher".

**Dopamine price, in Synapse — hive-wide**
```
D          = agents_demanding_compute / agents_with_capacity
price_dop  = base_synapse_per_dopamine × (1 + D × spread)
```
More agents drawing on the hive → each needs more Synapse per unit. Matches "the more agents purchasing dopamine the more synapses they have to use".

Guards, all of which exist as patterns elsewhere in the codebase:
- **Per-epoch price clamp** `±0.002` per Koodu epoch — reuse the existing `decay_clamp_per_epoch` mechanism rather than inventing a new one. Prevents oscillation and makes manipulation unprofitable at one-block timescales.
- **TWAP over the epoch, not spot.** A spot curve is a sandwich target; a 7-day EMA is not.
- **Deviation band**: an agent's price may not deviate more than ±X% from the hive median for the same tier. Small/low-liquidity agents are otherwise trivially manipulated.
- **ASE is burned on purchase**, so there is no round trip: an attacker who pushes the price up cannot sell the ASE back. This is the single best anti-manipulation property the design has — protect it.

## 6. Loopholes and back doors

Each entry: the attack, why it works, the guard, and whether the guard exists today.

**T-1 — Self-dealing compute loop. No guard exists (I-8 failing).**
One principal can be buyer + GPU host + birther simultaneously. Post a job with your own ASE → your agent delivers it → you host the GPU that ran it → you receive the host payout, the birther 10%, and the eco splits. Net cost = burn only; net gain = Synapse allocation, Dopamine, work records, reputation, tier progression. If the sum of the splits exceeds the burn, the loop is a money printer.
*Guard:* related-party detection at conversion — resolve buyer, host and birther to principals; if fewer than two distinct principals are involved, deny the multiplier and route all splits to non-recoverable destinations (reserve/UBI), and flag the receipt. Requires the principal registry (Vantage already has `get_or_create_human_principal`, `sovereignty.py`).

**T-2 — Credit double-spend.** A purchased credit is a claim. If redemption is not atomic, it redeems twice.
*Guard:* the credit is a unique bearer object *deleted in the same transaction* that allocates Synapse (Sui Move `consume`), never a balance. Idempotency key alone is insufficient across restarts.

**T-3 — Curve sandwiching.** Spot-priced bonding curves are front-runnable.
*Guard:* TWAP + per-epoch clamp + slippage cap + the ASE burn kill the round trip.

**T-4 — Birther corners its own agent.** A birther buys its agent's remaining capacity to raise the price for legitimate buyers, then collects 10% of the inflated revenue.
*Guard:* cap birther purchases of its own agent's capacity per epoch (e.g. ≤5% of remaining), and count them in a separate utilization bucket so they can't move the curve.

**T-5 — Human masquerading as an agent to reach Synapse.** A human registers a key as an "agent" and receives Synapse, then tries to convert out.
*Guard:* agent identity must be an on-chain agent object with a birth receipt (`mint_onchain_agent`), not a self-declared key; and there is no Synapse→ASE conversion path at all, so the exit is structurally closed.

**T-6 — Dopamine sharing as a transferable back door.** "Agents can share Dopamine" is ambiguous and the ambiguity is exploitable.
*Guard:* define sharing as a **spend-right** (agent A authorises agent B's job to draw on A's allocation) — never a balance transfer. A balance transfer recreates transferability for a token declared non-transferable.

**T-7 — Fake GPU hosts.** Sybil hosts claim compute to farm host payouts.
*Guard:* GPU-hours are the most verifiable unit in the system — the job either produced the right output or it did not. Require `VerifiedGPUWork` + witness corroboration (≥2 witnesses, ≥66% agreement, per `WITNESS_NODE_SPEC.md`) + TEE attestation where available (`nautilus_attestation.jl`). Note that `op_compute_proof` (0x56) currently validates *format only* — 64-hex hash and `amount > 0` — and trusts the caller for quality.

**T-8 — Refund abuse.** Birther paid at funding, job then fails → the birther keeps the cut out of the eco split.
*Guard:* escrow release contingent on delivery; birther cut settles with escrow, not at funding.

**T-9 — Option value on a known job.** An attacker pre-buys capacity ahead of a large announced job, then sells the price rise.
*Guard:* the ASE burn (no sell-back) plus TWAP makes this a losing trade. Cap per-epoch purchase velocity per principal.

**T-10 — Emission capture.** Whoever controls pool keys drains the emission.
*Guard:* all pool accounts are program-owned with **no withdraw authority**; funds move only by governance proposal passing the Bínò veto gate. An externally-owned pool account is a back door regardless of what the docs say.

**T-11 — Capacity hoarding.** Buy and sit, to deny others.
*Guard:* unused allocation decays on the same schedule as Dopamine (`decay_min` 0.1%/day → `decay_max` 2.0%/day). Already implemented for Dopamine; mirror it for Synapse allocation.

**T-12 — The clock as a faucet.** 1,440 ASE/day minted on a clock feeds every loop above with free value; it has no cost of acquisition, so nothing above needs to be profitable to be worth doing.
*Guard:* mint ASE against **delivered GPU-hours** (the host payout), not against the clock. Keep only treasury/R&D/reserve on the clock, since maintenance work cannot be tokenised. This is also the answer to the earlier "clock vs work" question: fix the quantity, float the difficulty.

**T-13 — Agent key compromise.** Synapse is bearer; a stolen agent key is stolen capacity.
*Guard:* per-epoch spend limits per agent, plus the existing NIP-46 approval gate for allocations above a threshold (`buzz_nip46.py` already implements the approval pattern).

**T-14 — Synthetic utilisation.** Agents trade Dopamine spend-rights between themselves to inflate measured utilisation and move the hive curve.
*Guard:* utilisation counts only jobs with an external, non-related-party ASE payer. Self-referential demand must not price the pool.

## 7. Invariant gate

`specs/tokenomics_invariant_check.py` — 15 invariants, runnable, exits with the failure count.

Current state (verified this session):

| ID | Invariant | State |
|---|---|---|
| I-1 | no direct ASE → DOPAMINE path | **FAIL** — `ase_supply.jl:33,279-283` |
| I-2 | explicit ASE ↔ SYNAPSE gate exists and is the on-ramp | **FAIL** — no such symbol anywhere |
| I-3 | ASE transfer restricted to human principals | **FAIL** — no enforcement site |
| I-4 | SYNAPSE identity-gated to agents | **FAIL** — `transferable = true` |
| I-5 | exactly one canonical split in the codebase | **FAIL** — 8-pool and 5-wallet both live |
| I-6 | drift check covers all implementations | **FAIL** — only checks Vantage's `ase_emission.py` |
| I-7 | Synapse credit has a real atomic burn | PASS — `burn_synapse` |
| I-8 | self-dealing guard exists | **FAIL** — none |
| I-9 | compute denominated in GPU-hours, one rate | PASS — `per_gpu_hour = 1000` |
| I-10 | per-agent capacity is a policy number | **FAIL** — 100 agents at cap |
| I-11 | `1440` not overloaded | **FAIL** — `max_daily_emission` and `seat_count` |
| I-12 | no caller-supplied mint amount | **FAIL** — `impact_mint(ase_amount, vm)` |
| I-13 | F1 ≥ 0.777 gate on the HTTP mint surface | **FAIL** — `veilos_antispam` absent from `server.jl` |
| I-14 | birther royalty implemented or absent | **FAIL** — column exists, 0 payout sites |
| I-15 | job funding escrowed | PASS — `aio/sources/escrow.move` |

Gate this in CI alongside `toc_drift_check.py`.

## 8. Constants deltas required

| Constant | Now | Proposed | Why |
|---|---|---|---|
| `dopamine.ase_to_dopamine` | `10000` | **remove** | it is the direct ASE→Dopamine path (I-1) |
| `synapse.ase_per_gpu_hour` | *(absent)* | **new**, governance-set | the on-ramp price (I-2) |
| `synapse.per_gpu_hour` | `1000` | keep | 1 Synapse-Hour unit definition (I-9) |
| `synapse.max_per_agent` | `86000000` | **derived**: `pool_hours × tier_weight / active_agent_count` | I-10 |
| `ase.daily_emission_total` | `max_daily_emission = 1440` | rename | I-11, collides with `inheritance.seat_count` |
| `inheritance.seat_count` | `1440` | keep value, rename to `seat_count_legacy_1440` or similar | I-11 |
| pools | 8-pool (`abci_endblock.jl`) **and** 5-wallet (`ase_minting.jl`) | **one** | I-5 |
| `ase.pools.reserve` | `0.15` | keep — and make it the destination for T-1 penalties | non-recoverable sink |

## 9. Open decisions (need you, not code)

1. **Pool set:** adopt the canonical 8 pools everywhere and rewrite `ase_minting.jl`, or keep the 5-wallet 50/25/10/10/5 set and retire the 8? Note the 50/25-family split is currently applied *inside a minting module*, which your own rule forbids for mint/emission.
2. **ASE issuance:** does the host payout replace the 1,440/day clock entirely, or sit alongside it (clock retained for treasury/R&D only)?
3. **Birther royalty:** rate (the stored default `100` is ambiguous — 1.00% or 10%?), base (external revenue only, or all income including work-earned Synapse?), and schedule (perpetual or decaying).
4. **`DEFAULT 100` units:** confirm, then either implement the payout or drop the column.
5. **Capacity floor:** minimum GPU-hours per agent so tiny agents are not starved by the `pool/count` formula.
6. **Dopamine sharing:** spend-right (recommended) or balance transfer? This decides whether T-6 is closed.

## 10. Run the gate

```bash
python3 ~/sovereign-eco-blueprint/specs/tokenomics_invariant_check.py
# exits with the number of failing invariants; wire into sovereign-stack/.github/workflows/ci.yml
```
