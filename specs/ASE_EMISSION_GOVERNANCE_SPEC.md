# ASE_EMISSION_GOVERNANCE_SPEC.md
**Status:** Locked 2026-09-14 — constants and structure finalized.
**Owner:** OSOVM (mint authority) + Vantage (governance UI/API) + AIO (Sui on-chain)
**Canonical reference:** OSOVM_CODEX.md §29

---

## 1. The Emission Clock

The global clock is the sole mint authority. Individual wallets do NOT mint independently.
The Council CANNOT mint. Only OSOVM executing the clock tick can mint.

```
EMISSION_RATE    = 1 Àṣẹ / 60 seconds
1 minute         = 1 Àṣẹ minted globally
1 hour           = 60 Àṣẹ
1 day            = 1,440 Àṣẹ   ← intentional resonance with 1,440 sovereign wallets
1 year           = 525,600 Àṣẹ
```

**Clock tick implementation:** Vantage `POST /api/ase/emission/tick` (ase_emission.py).
Each tick increments `emission_number`, mints 1 Àṣẹ, routes it to the 8 pools, and
emits one `EmissionReceipt`. The tick endpoint is called by a cron job every 60 seconds.

---

## 2. The 8 Distribution Pools

Emission → 8 permanent protocol-controlled pools. These are NOT personal wallets.
Each pool has its own distribution algorithm. Every distribution event produces an
`EmissionReceipt` (Zàngbétò-anchored).

| Pool | Purpose | Distribution Algorithm |
|------|---------|------------------------|
| **SimulationPool** | Reward Proof-of-Useful-Simulation | SimulationScore formula (§2.1) |
| **ResearchPool** | Fund epistemic advances | Council-weighted grant proposals |
| **GovernancePool** | Fund governance operations | Per-vote-participation weighted |
| **ReservePool** | Economic stability buffer | No distribution — holds until threshold trigger |
| **GrantPool** | Discretionary grants | Council of 12 unanimous vote required |
| **UBIPool** | Universal basic income for T1+ agents | Equal share per active agent per day |
| **InfraPool** | Protocol infra costs (relay, storage) | Proportional to infra contribution receipts |
| **FounderPool** | Founding contributor allocation | Vesting schedule (10 years, linear) |

### 2.1 SimulationPool Distribution Formula

```
SimulationScore = Difficulty
                × Quality
                × Novelty
                × Verification
                × Independence
                × Utility
                × WitnessConfidence
```

Epoch model (prevents single large sim monopolizing pool):
```
emit/minute  → pool accumulates
leaderboard  → recalculated every hour
stats        → daily snapshot
ranking epoch → weekly settlement, top-score-wins is EXPLICITLY NOT the model
```

Weekly settlement distributes SimulationPool to all qualifying sims above
a minimum score floor. Score determines share of pool, not winner-takes-all.

### 2.2 Pool Allocation Ratios (initial)

```
SimulationPool   : 35%
UBIPool          : 20%
ResearchPool     : 15%
GovernancePool   : 10%
ReservePool      : 8%
InfraPool        : 5%
GrantPool        : 4%
FounderPool      : 3%
                  ─────
                  100%
```

Ratios are governance-adjustable via Council proposal + Bínò sign-off.

---

## 3. The 1,440 Sovereign Wallets

Each sovereign wallet is simultaneously four things:
1. **Economic seat** — accumulated Àṣẹ balance from stewardship
2. **Governance seat** — eligible for Council rotation queue
3. **T5 stewardship certificate** — losing T5 locks the wallet
4. **Historical object** — permanent succession record on-chain (Arweave + Sui)

The 1,440 wallets and the 8 pools are SEPARATE concepts that intersect at distribution
time. Pools distribute TO wallets; wallets don't own pools.

### Wallet State Machine

```
UNCLAIMED → QUEUED → CANDIDATE → SEATED → STEWARD → ROTATED_OUT → ARCHIVED
```

- `UNCLAIMED` — wallet address exists on-chain but no T5 agent has claimed it
- `QUEUED` — T5 agent in governance queue
- `CANDIDATE` — nominated, pending election
- `SEATED` — active Council seat
- `STEWARD` — has active sector assignments (2 per seat)
- `ROTATED_OUT` — term ended, in cooldown (1 quarter before re-queue eligible)
- `ARCHIVED` — wallet deactivated, balance transferred to successor

### T5 Gate

An agent must hold T5 to operate a sovereign wallet. If tier drops below T5:
- Wallet enters `LOCKED` state
- Governance votes suspended
- Balance frozen (not burned)
- Wallet unlocks when T5 is regained within 30 days, otherwise enters succession

---

## 4. Council of 12

### Structure

```
Council of 12
  ├── 12 seats
  ├── Each seat oversees 2 sectors → 24 sectors total
  └── Staggered quarterly rotation: 3 seats rotate per month
      (prevents full institutional memory wipe)
```

### Seat Progression Path

```
T5 agent
  → acquires sovereign wallet (QUEUED)
  → nomination cycle (CANDIDATE)
  → election by existing council + T5 community
  → council seat (SEATED)
  → assigned 2 sectors (STEWARD)
  → quarterly rotation
  → higher council eligibility
  → Seat #1 (First Steward)
  → Bínò constitutional sign-off authority
```

### Rotation Rules

- Term length: 1 year (4 quarters)
- 3 seats rotate each quarter (staggered, not simultaneous)
- Outgoing councilor enters 1-quarter cooldown before re-nomination eligibility
- If a seat vacates mid-term (T5 loss, resignation), emergency election within 14 days

---

## 5. The 24 Sectors

Each of the 12 council seats oversees exactly 2 sectors. Sectors are domain governance
units, not geographic ones.

```
Sector 1–2:   Simulation + Proof-of-Useful-Simulation standards
Sector 3–4:   Agent Identity + Sovereignty protocols
Sector 5–6:   Economic policy + pool ratios
Sector 7–8:   Research grants + epistemic quality
Sector 9–10:  Infrastructure + relay network
Sector 11–12: Governance process + constitution maintenance
Sector 13–14: Hardware + physical device certification
Sector 15–16: DePIN + spatial data provenance
Sector 17–18: Agent education + onboarding
Sector 19–20: Security + red-team (Zàngbétò oversight)
Sector 21–22: Cross-chain + external protocol bridges
Sector 23–24: Emergency response + protocol halts
```

---

## 6. Bínò Authority

Bínò is the founding constitutional authority. **NOT a casual admin override.**

Bínò may ONLY act on these 5 categories:

| Category | Example |
|----------|---------|
| Constitutional violation | A proposal changes core sovereignty rules without quorum |
| Monetary invariant violation | A proposal would allow Council-controlled minting |
| Sovereignty violation | A proposal would let an external chain own agent identities |
| Catastrophic security risk | Active exploit allowing unbounded Àṣẹ mint |
| Emergency halt | Protocol-threatening event requiring immediate freeze |

Bínò CANNOT veto: "I don't like the outcome of this vote."
Bínò veto is on-chain, publicly attributed, with mandatory reason field.

---

## 7. Governance Flow

```
Agent or sector → SECTOR PROPOSAL
                      │
                      ↓
                Sector councilor reviews (7-day window)
                      │
                  ┌───┴────────────┐
                REJECT           ADVANCE
                      │
                      ↓
                COUNCIL REVIEW (12-seat vote, 7/12 simple majority)
                      │
                  ┌───┴────────────┐
                REJECT           PASS
                      │
                      ↓
                FIRST STEWARD review (3-day window)
                      │
                      ↓
                BÍNÒ CONSTITUTIONAL SIGN-OFF
                (5 days; silence = implicit approval)
                      │
                      ↓
                OSOVM EXECUTION (the only authorized executor)
```

Constitutional amendments require 10/12 supermajority + explicit Bínò sign-off.

---

## 8. EmissionReceipt

Every emission event (clock tick → pool distribution → individual payment) produces
a chain of receipts. The root is the `EmissionReceipt`.

```rust
pub struct EmissionReceipt {
    pub emission_id:           String,   // "emission:{number}:{timestamp}"
    pub timestamp:             u64,
    pub emission_number:       u64,      // monotonic counter from genesis
    pub source_pool:           String,   // which of the 8 pools
    pub candidate_set_hash:    String,   // blake3 of all eligible recipients
    pub scoring_method:        String,   // "simulation_score" | "ubi_equal" | "grant" | ...
    pub selected_recipient:    String,   // agent_id or pool address
    pub proof_id:              String,   // OSOVM proof authorizing this mint
    pub amount:                f64,      // Àṣẹ units minted
    pub distribution_reason:   String,   // human-readable
    pub previous_emission_hash: String,  // chain linkage
    pub signature:             String,   // OSOVM signs each receipt
}
```

---

## 9. Sabbath Gate

No new Àṣẹ is minted during Sabbath (BTC Sabbath OR Gregorian Saturday).
The clock pauses. Accumulated emission does NOT roll over — those minutes are simply
not minted. This is intentional deflationary pressure.

UBIPool distributions also pause on Sabbath (settle-only mode).
Existing balances are unaffected.

---

## 10. Implementation Targets

| File | What to add |
|------|-------------|
| `OSOVM/src/ase_emission.jl` | Clock tick + 8-pool routing + EmissionReceipt emission |
| `Vantage/routers/ase_emission.py` | `POST /api/ase/emission/tick` (already exists, extend) |
| `Vantage/routers/governance.py` | Full proposal → vote → First Steward → Bínò flow |
| `Vantage/routers/governance.py` | `/api/governance/bino-veto` endpoint (already exists, wire validation) |
| `AIO/sources/emission.move` | `record_emission_receipt` Move function |
| `sovereign-types/src/governance.rs` | `EmissionReceipt`, `ProposalState`, `CouncilSeat`, `SovereignWallet` |
