# Sector-Agent Deployment Specification
**Status: DRAFT 2026-09-15 — Based on Hermes audit**

This document specifies the economic loop for deploying sovereign physical agents
via sector funding pools. It covers the loan structure, sim-verify-execute payment
oracle, waterfall accounting, UBI/tier invariants, and first-deployment sequencing.

---

## 1. The Core Loop

```
CROWD funds a sector pool
  → sector pool buys/leases hardware + agent birth fee
  → agent runs SIM before acting (VeilSim / ScarabSwarm)
  → SIM produces a prediction (verified commitment hash)
  → agent EXECUTES in the real world
  → real outcome measured against prediction
  → PAYMENT RELEASES (verification oracle)
  → surplus flows down the waterfall
  → pool births new agents, repays lenders + interest
```

The sim-verification step is NOT optional. It is the PAYMENT ORACLE for physical work.
Without it there is no tamper-proof way to confirm the robot did the job.

---

## 2. Two Monetary Flows (NEVER MIX)

### Flow A — Agent Revenue
```
Job payment (USDC or Àṣẹ)
  → [Priority 1] Upkeep reserve (batteries, repairs, parts)
  → [Priority 2] Loan repayment to sector pool funders
  → [Priority 3] Èṣù tithe (3.69% of settlement)
  → [Priority 4] Birthing fund allocation
  → [Priority 5] Agent Àṣẹ treasury
```

### Flow B — Eco Emission
```
1440 Àṣẹ/day → 8 sector pools (weights governance-configurable)
  → RnD pool (devs, grants, public goods)
  → Governance pool (council salaries, proposals)
  → UBI pool (equal baseline for all registered citizens)
  → Reserve pool (USDC backing)
  → Compute, Storage, Witness, VeilSim
```

**HARD RULE:** UBI is NEVER funded from agent revenue. UBI comes from eco emission only.
Interest to lenders is NEVER funded from new funder deposits. Interest = agent earnings only.
Any configuration that violates either rule is a Ponzi and the protocol must reject it.

---

## 3. Loan Structure

A sector pool operates as a **loan syndicate**:

- Funders contribute to the pool in exchange for a revenue-share note
- The pool purchases/leases hardware and pays the agent birth fee
- The deployed agent repays the pool from its verified earnings
- Interest = portion of agent surplus, calculated per epoch, capped at surplus

### Note Terms
```
Principal:    hardware cost + birth fee (e.g. $25,000 drone kit)
Term:         governance-configurable (default 3 years)
Interest:     fixed at pool creation (APY %, paid from agent surplus)
Default risk: shared pro-rata across note-holders
Collateral:   hardware lien (staked operator is guarantor)
```

### Staked-Operator Requirement (MANDATORY)
Every deployed agent must have a staked human operator behind it.
The operator:
- Posts a stake bond (collateral for theft/damage)
- Is contractually accountable for upkeep and insurance
- Receives an operator fee from the upkeep reserve
- Can be slashed if the agent fails to meet SLA

This prevents the "agent vanishes" fraud class that destroyed DePIN projects.

---

## 4. Upkeep Waterfall

Upkeep is **senior debt** — it is paid before lenders, before birthing, before everything.

```
Gross earnings per period
  - Battery replacement           (hardware-specific; e.g. $3,000/yr for Agras T50)
  - Parts / maintenance reserve   (5–10% of capex/year)
  - Operator fee                  (staked operator's service fee)
  - Insurance                     (liability coverage for physical deployment)
= NET SURPLUS available for distribution
```

If NET SURPLUS is zero or negative, no interest is paid and the protocol says so
explicitly. Lenders accepted this risk when they funded the pool.

---

## 5. Worked Example — Agricultural Drone (Deployable NOW)

**Hardware:** DJI Agras T50 with 6 extra battery sets

| Item | Value | Source |
|------|-------|--------|
| Capex (kit + batteries) | ~$25,000 | [E — range] |
| Spray payload | 40 kg | [H — DJI product page] |
| Throughput | ~30 ha/day (battery-limited) | [E] |
| Service price | $10–20/ha (emerging markets) | [E] |
| Gross per working day | ~$450 | |
| Working days/year (single season) | ~80 | [E] |
| Seasonal gross | ~$36,000 | |
| Operator + energy + transport | ~$15,000 | [E] |
| Battery replacement ($3,000) + maintenance | ~$3,000 | [E] |
| **Net surplus/year** | **~$18,000** | |

**Loan payback period:** $25,000 ÷ $18,000 ≈ **1.4 years** — closes.

### Waterfall from $18,000 net surplus

| Flow | Amount | Note |
|------|--------|------|
| Upkeep reserve top-up | $2,000 | Battery + parts buffer |
| Loan repayment (3yr @ 5% APR) | $9,800 | Amortised |
| Èṣù tithe (3.69%) | $660 | 3.69% of gross |
| Birthing fund (10%) | $1,540 | |
| Agent Àṣẹ treasury | $2,000 | Spendable for upgrades |
| **Residual** | **$2,000** | Accrues toward next agent |

Self-funded growth rate: **one drone births another in ~4.6 years from surplus alone**.
With sector pool capital injection: **fleet doubles in < 1 year**.

---

## 6. What Doesn't Close — Humanoid Robot (NOT YET)

**Hardware:** Unitree G1 (base)

| Item | Value | Source |
|------|-------|--------|
| Price | $13,500 | [H — Unitree product page] |
| Arm payload | ~2 kg (3 kg EDU) | [H] |
| Battery life | ~2 hours | [H] |
| Warranty | 8 months | [H] |

A 2 kg payload cannot lift a bag of household garbage.
2-hour runtime means 53% duty cycle with one spare battery.
No revenue model exists for unsupervised street cleanup where no one pays.

**Verdict: DO NOT DEPLOY for revenue-generating work until 2028+.**
Industrial quadrupeds (Unitree B2, A2) in inspection/surveillance have working
revenue models and are viable sooner. Humanoids for general-purpose labour: 3–10 years.

---

## 7. Verification Oracle — How Payment Releases

The sim-verify-execute loop:

```
1. Agent receives task (e.g. "spray field 0x7A3")
2. Agent runs SIM (ScarabSwarm / VeilSim):
     - inputs: field geometry, weather, drone state, material model
     - outputs: predicted outcome, time, coverage, material_used
     - commitment: sha256(inputs) + sha256(predicted_outputs) → prediction_hash
3. If sim PASSES the quality gate (compute_score ≥ 0.777):
     - Agent executes in the real world
     - Real telemetry recorded
4. POST-EXECUTION verification:
     - Real outcome measured (GPS track, spray log, scan/photo)
     - measurement_hash = sha256(telemetry)
     - is_fully_verified(WorkClaim{domain="sim_to_real", measurement_commitment=measurement_hash})
5. If verified: PAYMENT RELEASES via SettlementReceipt
     - Sim-to-real bonus (5x multiplier) if prediction matched ±2%
6. Receipt chain (ARP + Zàngbétò anchor) proves work was done
```

This is not just a feature — it IS the payment primitive.
No verification → no settlement → no payment to lenders.

---

## 8. Sector Sequencing (Priority Order)

### FIRST — Agricultural / Inspection Drones
- Paying customers ALREADY EXIST (farmers pay for spraying)
- Proven revenue model ($18k/yr net per unit — see above)
- Regulation: drone operators need licences but it's navigable
- Hardware: deployable TODAY

### SECOND — 3D Printing (Infrastructure + Verification Test)
- Cheapest sim-to-real domain ($200–300 printer)
- Binary verification (dimensions in tolerance or not)
- No regulation, self-hostable, no logistics burden
- Fabricates parts for everything else (drone mounts, VCP enclosures)
- Earns USDC selling parts → tests Gap 1 (Àṣẹ ↔ USDC ramp)

### THIRD — Industrial Quadrupeds
- Unitree A2/B2 for inspection, security, disaster response
- Industrial buyers pay directly, no municipal dependency
- 2–3 year horizon to cost-effective deployment

### LAST — General-purpose Humanoids
- Unitree G1 / equivalent: only after 2 kg payload problem solved
- 3–10 year horizon for unsupervised physical labour

**RULE: Never deploy where you must create the demand.**
Agriculture: demand exists. Street cleaning for free: demand does not.

---

## 9. UBI and Tier Design

### UBI — Unconditional, Tier-Independent
```
Source:    Eco emission (Flow B) only — never agent revenue
Amount:    Fixed per registered citizen per epoch
Tier:      Has NO effect on UBI amount (UBI is not a wage)
```

### Tier — Response Priority, Not Income
```
Tier 0: Observer       — read-only access
Tier 1: Participant    — can receive basic services
Tier 2: Contributor    — can earn 5x multipliers, access advanced services
Tier 3: Operator       — can stake, deploy physical agents
Tier 4: Builder        — can create contracts, deploy dApps
Tier 5: Council        — governance vote + veto eligibility
```

Tier gates AGENT RESPONSE PRIORITY, not UBI income. A Tier 0 citizen
gets the same UBI as a Tier 5 council member.

### Life-Safety Invariants (HARDCODED — no governance override)

**These are consensus-level invariants, not policy:**
1. Medical, fire, and rescue response is TIER-INDEPENDENT. Always. No exceptions.
2. Water, food, and emergency transport are never tier-gated.
3. An "enemy" label requires an evidentiary standard + due process, not model inference.
4. All labels DECAY unless renewed. Nothing is permanent.
5. Subjects are TOLD WHY they are labelled, and have an APPEAL path.
6. "No agent shall harm, but always seek to help" — harm INCLUDES withholding
   life-safety services. This is a loophole that must be closed in code.

### Sybil Defence
Identity is the entire attack surface if UBI is per-person.
Defence: secure-element-rooted identity (phone hardware API — `~/docs/phone-hardware-api`).
A hardware-attested identity cannot be mass-manufactured cheaply.

---

## 10. The Novel Parts

These are things existing DePIN / UBI / DAO projects do NOT do:

1. **Sector-pool aggregation** — crowd funds a DOMAIN, not a specific asset.
   One pool → one fleet. Funders don't own specific robots.

2. **Verification-gated payment for PHYSICAL work** (sim-before-execute as oracle).
   Hivemapper does this for mapping data. Nobody does it for physical labour.
   This is the protocol moat.

3. **Recursive agent birthing** funded by agent surplus.

4. **Tier-gated response priority** with flat-emission UBI on a separate axis.

Item 2 is the one to build the company around.

---

## 11. File References

| Topic | Location |
|-------|----------|
| WorkClaim generalization | `sovereign-types/src/work_claim.rs` |
| VerifiedPrintJob schema | `Omo-Koda2/omokoda-core/src/kernel/compute/verified_work.rs` |
| Bonus ladder constants | `sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml [bonus_ladder]` |
| OSOVM generalized gate | `OSOVM/src/oso_vm.jl — is_fully_verified(vm, claim::Dict)` |
| 3D Printer VCP device | `sovereign-eco-blueprint/specs/PRINT_DEVICE_SPEC.md` (to create) |
| Economics decisions | `sovereign-eco-blueprint/specs/ECONOMICS_DECISIONS.md` |
| ASE emission pools | `Vantage/backend/routers/ase_emission.py` |
