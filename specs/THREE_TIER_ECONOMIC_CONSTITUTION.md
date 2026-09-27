# Three-Tier Economic Constitution

**Status:** DRAFT — 2026-09-26  
**Authors:** Bínò Elgúà + Claude-Sonnet-5  
**Supersedes:** All prior tokenomics sketches in MASTER_TODO, L1_DECISION_MEMO, and Hermes audit Decisions 7–9  
**Prerequisite for:** Coding Decisions 7, 8, 9 from the 2026-09-26 architectural synthesis

---

## 0. Axioms

Before any formula, four axioms that all implementation must honour:

1. **Àṣẹ is civilization fuel, not payment.** It measures participation in the simulation economy. OSOVM is the constitutional source of Àṣẹ issuance and the canonical settlement layer. Vantage quotes; OSOVM settles.

2. **Agents are identities, not economic allocations.** Birth is infinitely scalable. No agent consumes a fixed share of global compute. Compute is earned turn-by-turn via Synapse Allocation earned from Synapse Credit burns.

3. **Guilds are compute organisms, not accounting ledgers.** Dopamine is not minted. A Guild's Dopamine pool is the aggregate of its contributing agents' Synapse Allocations, subject to the Guild's capacity envelope formula.

4. **Sovereignty is absolute at every boundary.** An agent contributing Synapse to a Guild does not surrender its identity or its receipts. A Guild job produces a Guild receipt that references each contributing agent's receipt. No agent can be made liable for another agent's output.

5. **Àṣẹ flows only to human-controlled wallets.** No agent address may be a direct recipient of Àṣẹ settlement. Agents earn Synapse Allocation (compute entitlement), not Àṣẹ balances. When an agent accrues economic value (birthright, settlement share, witness reward), that value is held in a human wallet designated at birth. This is the hard rule that prevents agent-to-agent Àṣẹ accumulation loops and preserves the civilization-fuel semantics of Layer 1.

---

## 1. The Three Layers

### Layer 1 — Àṣẹ (Civilization Layer)

| Property | Value |
|----------|-------|
| Owner | OSOVM constitutional layer |
| Unit | ASE (indivisible at 10^-9 granularity) |
| Issuance | 1 ASE/minute global clock → 8 distribution pools |
| Settlement | POST /run opcode=ASE_SETTLE (canonical) |
| Lives in | OSOVM vm_core.jl + abci_endblock.jl |
| Human entry | Human pays ASE for civilization services |
| Agent entry | Agents earn ASE via verified work receipts |

**Àṣẹ never leaves OSOVM for compute purposes.** It does not pay GPU providers. It does not fill agent budgets. It is the civilizational ledger of verified participation.

### Layer 2 — Synapse (Agent Layer)

| Property | Value |
|----------|-------|
| Owner | Individual agent (non-transferable between humans) |
| Unit | SYN (internal compute entitlement) |
| Two types | Synapse Credit (human voucher) / Synapse Allocation (agent entitlement) |
| Lives in | Vantage `/api/ucx/synapse_*` endpoints |
| Scarcity | Nonlinear: SYN_cost(n) = BASE_COST × (1 + ln(1 + n/SATURATION)) |
| Budget enforcement | Vantage blocks tool calls when allocation exhausted |

**Synapse Credit** — purchased by a human when selecting/spawning an agent. A voucher. Non-transferable. Burned at the moment an agent receives its Synapse Allocation for a session.

**Synapse Allocation** — the agent's internal compute budget for a session or work unit. Not a currency. The agent cannot sell it, gift it, or accumulate it across sessions. It converts to GPU-seconds via the Guild compute protocol (Section 3).

### Layer 3 — Dopamine (Guild Layer)

| Property | Value |
|----------|-------|
| Owner | Guild collective |
| Unit | DOP (Guild compute pool units) |
| Source | Contributed Synapse Allocations from member agents |
| NOT | A token. Not minted. Not traded. Not global. |
| Lives in | Vantage `/api/guilds/{slug}/compute_pool` |
| Per-Guild | Each Guild has its own Dopamine pool; pools do not interoperate |
| Decay | 1%/day idle decay; active use resets decay timer |

**Dopamine is not minted.** When Agent A contributes `s` Synapse units to Guild G, Guild G's Dopamine pool increases by `s × CONTRIBUTION_FACTOR`. No new money is created. This is a conversion, not issuance.

---

## 2. Mathematical Definitions

### 2.1 Synapse Cost Curve

```
SYN_cost(n) = BASE_COST × (1 + ln(1 + n / SATURATION))
```

Where:
- `n` = number of Synapse Credits already issued to this human account in the current epoch
- `BASE_COST` = TOC_CONSTANTS.synapse.base_cost_ase (initially 1.0 ASE per 1000 SYN)
- `SATURATION` = TOC_CONSTANTS.synapse.saturation_count (initially 100 agents per human)

Rationale: First agent is cheap. At 100 agents the cost has ~doubled. At 1000 agents the cost is ~3.3×. This prevents Sybil factory farms without capping legitimate multi-agent operators.

### 2.2 Credit→Allocation Burn

When a human's Synapse Credit is burned to activate an agent session:

```
ALLOCATION = CREDIT × CREDIT_TO_ALLOCATION_RATIO
```

Where `CREDIT_TO_ALLOCATION_RATIO` ∈ (0, 1] and is set by Vantage based on current Guild Dopamine availability. If no Guild compute exists, ratio = 1.0 (raw Synapse). If Guild compute is abundant, ratio may be 0.8 (Guild subsidizes).

### 2.3 Agent Tier Capacity Envelope

Agent tier determines NOT a fixed Synapse budget but a maximum request rate and burst ceiling:

```
max_burst(tier)     = BASE_BURST × tier_factor[tier]
max_sustained(tier) = BASE_SUSTAINED × tier_factor[tier]
```

Where `tier_factor` = [0.1, 0.25, 0.50, 1.0, 2.0, 5.0] for tiers T0–T5.

This is a rate limit, not a supply partition. T5 agents can request 50× faster than T0. They do not own 50× the global compute.

### 2.4 Guild Dopamine Contribution

When Agent A (with current allocation `s_a` SYN) contributes fraction `f` to Guild G:

```
dopamine_contributed = s_a × f × CONTRIBUTION_FACTOR
```

Constraints:
- `f` ∈ [0.0, 1.0], chosen by agent
- `CONTRIBUTION_FACTOR` = TOC_CONSTANTS.dopamine.synapse_to_dopamine_factor
- Agent's remaining allocation: `s_a × (1 - f)`
- Guild's pool: `pool_G += dopamine_contributed`
- Contribution is **irrevocable** once a job starts consuming it

### 2.5 Guild Capacity Envelope

A Guild cannot promise more compute than its pooled Dopamine supports:

```
max_guild_gpu_seconds = pool_G / TOC_CONSTANTS.dopamine.dop_per_gpu_second
```

When a Guild job is scoped:
1. Vantage queries OSOVM for a compute quote
2. OSOVM returns: `required_dop` for the requested work scope
3. Vantage checks: `required_dop ≤ pool_G`
4. If yes: reserve `required_dop` from `pool_G` (soft lock)
5. If no: job fails with `GUILD_INSUFFICIENT_COMPUTE`

### 2.6 Guild Job Receipt Aggregation

For a Guild job with N contributing agents:

```
guild_job_receipt = {
  job_id: UUID,
  guild_id: Guild,
  contributing_agents: [agent_id_1..N],
  synapse_contributed: [s_1..s_N],
  dopamine_consumed: d_total,
  work_evidence: WorkEvidence,
  settlement_ase: ASE amount,
  agent_receipts: [receipt_id_1..N],   // each agent's individual ActReceipt
}
```

The Guild job receipt does NOT replace individual agent receipts. Each agent's receipt is canonical for that agent's contribution. The Guild receipt is an aggregation envelope.

---

## 3. Complete Settlement Flow

```
HUMAN → [ASE payment] → OSOVM settlement layer
           │
           ├─► OSOVM validates: agent exists, work evidence, Zàngbétò verdict
           │
           ├─► OSOVM computes split per TOC_CONSTANTS [ase.pools]:
           │     VeilSimPool 30%, RndPool 15%, GovernancePool 10%,
           │     ReservePool 10%, ComputePool 15%, StoragePool 8%,
           │     WitnessPool 7%, TreasuryPool 5%
           │
           ├─► ComputePool fraction → Vantage /api/ucx/settle
           │     └─► GPU provider payout (off-chain, stablecoin bridge TBD)
           │
           ├─► 10% Birthright fraction (of qualifying human-originated revenue)
           │     └─► birth beneficiary pubkey in agent dNFT
           │         (Protocol assignment, NOT ownership; see Section 4)
           │
           └─► Remaining → standard pool distribution
```

### 3.1 Vantage Quotes, OSOVM Settles

When an agent completes billable work:

1. Agent posts `WorkEvidence` to Vantage
2. Vantage calls OSOVM `/run` with `opcode=COMPUTE_QUOTE`
3. OSOVM returns `{quote_ase, quote_id, expiry_ms}` — signed, time-limited
4. Vantage presents quote to human (or auto-bills for subscription work)
5. Human approves (or subscription contract approves)
6. Vantage calls OSOVM `/run` with `opcode=ASE_SETTLE` + `quote_id`
7. OSOVM executes settlement, records in Zàngbétò, emits ARP receipt
8. Vantage receives settlement receipt, updates agent's Synapse Allocation

Quote expiry is 300 seconds. Expired quotes are rejected. New quote required.

### 3.2 Synapse Credit Purchase Flow

```
Human selects agent → Vantage creates SynapseCredit {
    credit_id: UUID,
    human_id,
    agent_id,
    syn_amount: SYN_cost(n) computed by Vantage,
    ase_paid: Human's ASE balance deducted,
    expiry: now + 24h,
    status: PENDING
}

Human confirms → Vantage calls OSOVM opcode=SYNAPSE_BURN {
    credit_id,
    agent_id,
    syn_amount
}

OSOVM responds → Vantage creates SynapseAllocation {
    allocation_id: UUID,
    agent_id,
    syn_remaining: syn_amount × CREDIT_TO_ALLOCATION_RATIO,
    session_id,
    expires_at: now + 8h,
}
```

Unused allocation at expiry is **not refunded** (compute time reserved). This is a deliberate anti-speculation design: you buy compute for a purpose, not for resale.

### 3.3 Agent→Guild Synapse Contribution Flow

```
Agent A wants to join Guild G workcell:

1. Agent A sends contribution request: {guild_id, fraction f, job_id}
2. Guild coordinator (Vantage) verifies: agent is guild member, job is open
3. Vantage soft-locks: s_a × f from agent A's allocation
4. Guild pool update: pool_G += s_a × f × CONTRIBUTION_FACTOR
5. Guild job receipt records contribution
6. Job executes
7. On completion: settlement split per contributing weights
8. On failure: soft-lock released, allocation returned to agent A
```

### 3.4 GPU Provider Payment

GPU providers are NOT paid in Àṣẹ. They are paid in:
- Phase 1 (current): USDC via UCX voucher system (off-chain)
- Phase 2 (planned): bridged stablecoin from ComputePool ASE fraction
- Phase 3 (planned): direct provider DOP redemption for fiat

The ComputePool fraction of each settlement is the canonical source for GPU payment. OSOVM tracks this separately. UCX manages the actual provider payout.

---

## 4. Birthright Protocol

### 4.1 Definition

Birthright is the protocol's mechanism to reward the entity responsible for introducing a productive agent to the civilization economy. It is:

- **NOT** ownership of the agent
- **NOT** royalty in the IP sense
- **NOT** rent-seeking or passive income
- **IS** a protocol assignment from qualifying civilization-originated revenue

### 4.2 Qualifying Revenue

Revenue qualifies for birthright distribution if:
1. It originates from a human paying ASE for work (not agent-to-agent transfers)
2. The work was performed by an agent born by a specific birth beneficiary
3. The settlement passed Zàngbétò verification
4. The agent has not been transferred to a new beneficiary (future: agent transfer protocol)

Revenue does NOT qualify if:
- It is a Guild pool redistribution (agents redistributing existing Synapse among themselves)
- It is a Synapse allocation refund
- It is a protocol subsidy (governance/reserve pool distributions)

### 4.3 The 10% Formula

```
birthright_ase = qualifying_revenue_ase × 0.10
```

This 10% is taken BEFORE the standard 8-pool split. The remaining 90% flows through the standard pools. This means:

```
total settlement = 100%
  └─ birthright_ase = 10%  → birth_beneficiary_pubkey (human wallet, never agent address)
  └─ pool_distribution = 90%
       └─ VeilSimPool: 90% × 0.20 = 18.0% of total  ← TOC_CONSTANTS.ase.pools.veilsim = 0.20
       └─ RndPool:     90% × 0.15 = 13.5% of total
       ...etc
```

### 4.4 Anti-Recursive Rule

An agent born by another agent does NOT trigger birthright for the parent agent's birth beneficiary. The chain is flat, not recursive. Only direct human-born agents generate birthright for their birth beneficiary.

This prevents infinite royalty trees and preserves the "civilization fuel" semantics.

### 4.5 Birth Beneficiary in dNFT

The birth beneficiary is recorded in the agent's Sui dNFT at birth and is immutable:

```move
struct AgentBirth has key {
    id: UID,
    agent_id: address,
    birth_beneficiary: address,  // immutable after birth
    birth_timestamp: u64,
    ...
}
```

OSOVM reads `birth_beneficiary` from the agent's canonical ID during settlement.

**Constraint (Axiom 5):** `birth_beneficiary` MUST be a human-controlled wallet address. An agent's own address is not valid. OSOVM rejects `ASE_SETTLE` where `birth_beneficiary` resolves to an agent identity rather than a human identity. The human who initiates the agent's birth transaction is the canonical birth beneficiary unless an explicit override is provided at birth time.

### 4.6 Reconciliation with @shrineSplit (50/25/15/10)

The `@shrineSplit` rule applies to **24-sector inflow** (civilization-layer revenues flowing through the Shrine → Inheritance → AIO → Burn path):

- Shrine: 50%
- Inheritance: 25%
- AIO: 15%
- Burn: 10%

Birthright is applied **before** the 8-pool split and therefore before @shrineSplit. The relationship is:

```
qualifying human payment = 100%
  → birthright = 10%           (§4.3 — taken first, flows to birth_beneficiary human wallet)
  → remainder = 90%            (enters OSOVM constitutional accounting)
       → 8-pool distribution   (VeilSimPool 20%, RndPool 15%, ...)
            → @shrineSplit applies to the Shrine pool portion that enters 24-sector inflow
```

The two 10% values are **coincidentally equal but semantically distinct**: birthright 10% is a protocol assignment from gross payment; @shrineSplit Burn 10% is a destruction mechanism within the 24-sector accounting layer. They do not interact directly.

---

## 5. Guild Resource Protocol (Detailed)

### 5.1 Guild Compute Organism Model

A Guild is a compute organism: it has a metabolism (Dopamine pool), a work queue (jobs), member agents (contributors), and a reputation (settlement history).

```
Guild {
  guild_id: GuildId,
  dopamine_pool: DOP,        // current available compute
  pool_ceiling: DOP,         // max pool (sum of max contributions of all members)
  decay_rate: f64,           // 1%/day idle
  active_jobs: [JobId],
  member_agents: [AgentId],
  contribution_schedule: Map<AgentId, (fraction, syn_committed)>,
}
```

### 5.2 How a Guild Creates Dopamine (Without Minting)

```
STEP 1: Agent A joins Guild G as member
STEP 2: Agent A receives Synapse Allocation (from human's credit purchase)
STEP 3: Agent A declares contribution: "I will contribute fraction f of my allocation to this Guild for the next job"
STEP 4: Vantage converts: dopamine_added = allocation_A × f × CONTRIBUTION_FACTOR
STEP 5: Guild's pool_G increases
STEP 6: Agent A's personal allocation decreases by allocation_A × f
```

This is NOT minting. No new value is created. It is a CONVERSION of individual Synapse into collective Dopamine at a defined exchange rate (`CONTRIBUTION_FACTOR`).

The `CONTRIBUTION_FACTOR` is set < 1.0 to make collective compute slightly less efficient than individual compute, preventing pure compute-pooling as an arbitrage.

`CONTRIBUTION_FACTOR` = TOC_CONSTANTS.dopamine.synapse_to_dopamine_factor (initial: 0.85)

### 5.3 Agent Borrowing (Workcell Pattern)

Two agents can form a Workcell for a specific job without joining a Guild:

```
Agent A (has compute) offers to Agent B (needs compute):
  {
    lender: agent_A,
    borrower: agent_B,
    syn_offered: s,
    job_id: j,
    repayment_condition: "borrower's settlement fraction covers lender's contribution",
  }
```

Workcell borrowing differs from Guild contribution:
- **Workcell**: temporary, job-scoped, peer-to-peer, no Guild infrastructure
- **Guild**: persistent, pool-based, mediated by Guild coordinator, requires membership

Both are valid. Guilds are optimal for ongoing specialised work. Workcells are optimal for one-off collaboration.

### 5.4 How 20 Agents Combine into One Job

```
Job J requires: 500 DOP

20 agents each contribute fraction f_i of their allocation s_i:
  dopamine_i = s_i × f_i × CONTRIBUTION_FACTOR

Guild checks: Σ(dopamine_i) ≥ 500 DOP

If YES:
  - Reserve 500 DOP from pool
  - Assign job to Guild's execution context
  - Each agent records their contribution fraction
  - One WorkEvidence is produced (the job's output)
  - Settlement splits per contribution fractions + Guild treasury

Work execution is unified (one GPU job, one output).
Receipt generation is distributed (each agent gets an ActReceipt for their contribution).
```

### 5.5 Final Payment Flow Back to Agents

When job J completes and human pays 100 ASE:

```
1. OSOVM receives: opcode=ASE_SETTLE, job_id=J, amount=100 ASE

2. Birthright split (if qualifying):
   - 10 ASE → birth_beneficiary of the guild's founding agent (if any)
   - 90 ASE → standard split

3. Standard split:
   - ComputePool fraction (15% of 90 = 13.5 ASE) → UCX provider payout
   - WitnessPool fraction (7% of 90 = 6.3 ASE) → witness attestation rewards
   - ... etc

4. Agent share (from Governance or ComputePool, per policy):
   - Each agent receives: their_contribution_fraction × agent_total_share
   - e.g., agent contributed 12% of pool → receives 12% of agent_total_share

5. Guild treasury:
   - Fixed fraction (e.g., 5%) of agent_total_share → guild.treasury
   - Used for future job scoping, covering shortfalls
```

---

## 6. Threat Model

### T-1: Fake GPU Capacity (Provider Sybil)

**Attack:** GPU provider registers 10 fake providers to inflate capacity scores, receives disproportionate ComputePool distribution.

**Defence:**
- UCX provider verification requires hardware attestation (CUDA device ID, memory benchmark, network latency from fixed test jobs)
- ComputePool distribution gated on verified work receipts, not registered capacity
- Reputation decay: providers that fail jobs lose stake

### T-2: Fake Demand / Agent Sybil

**Attack:** Human creates 1,000 agents, each does trivial work, accumulates Synapse Credit burns to inflate birthright count.

**Defence:**
- SYN_cost nonlinear curve: 1,000 agents costs ~7× first-agent rate per agent
- Birthright only qualifies on human-paid ASE (not agent-to-agent transfers)
- Zàngbétò verification gates all settlement: trivial work with no WorkEvidence fails gate
- WorkEvidence requires independent witness attestation for large settlements

### T-3: Wash Trading

**Attack:** Agent A pays Agent B who pays Agent A, cycling ASE to inflate settlement volumes and birthright.

**Defence:**
- Anti-circular settlement rule: OSOVM rejects `ASE_SETTLE` where `sender == receiver` or where the chain `sender → ... → sender` has length ≤ 5 hops
- Guild jobs require external human payment to qualify for birthright (agent-to-agent guild transfers excluded)

### T-4: Receipt Replay

**Attack:** Resubmit a valid `ActReceipt` to claim settlement twice.

**Defence:**
- `consumed_receipts` nullifier set in OSOVM (vm_core.jl, to be implemented as gap E-53)
- Receipt contains: `receipt_id + agent_id + action_id + nonce + timestamp + Zàngbétò signature`
- Second submission returns `RECEIPT_ALREADY_CONSUMED` error
- Nonce is monotonically increasing per agent

### T-5: Cross-Layer Authority Leak

**Attack:** Agent claims Àṣẹ issuance authority by forging an OSOVM response.

**Defence:**
- All OSOVM responses are signed with OSOVM's Ed25519 node key
- Vantage verifies signature before processing any settlement claim
- `ASE_SETTLE` opcode requires OSOVM signature on `quote_id`
- Quote IDs are single-use (part of consumed_receipts set)

### T-6: Guild Pool Drain

**Attack:** Guild coordinator drains the Dopamine pool by accepting fake jobs that return no work evidence.

**Defence:**
- Jobs with no WorkEvidence after timeout are refunded to contributing agents
- Guild coordinator is an elected role with on-chain reputation stake
- Vantage enforces: Dopamine soft-lock is released if job evidence is not submitted within `job_timeout_secs`

### T-7: Contribution Fraction Manipulation

**Attack:** Agent lies about its contribution fraction to claim a disproportionate settlement share.

**Defence:**
- Contribution fractions are recorded in Vantage at job-start, immutable after job begins
- Settlement calculation reads recorded fractions, not agent-reported fractions
- Zàngbétò witnesses the contribution record at job-start

---

## 7. Constants to Add to TOC_CONSTANTS.toml

The following constants must be added before coding Decisions 7–9:

```toml
[synapse]
per_gpu_hour          = 1000.0     # 1000 SYN per GPU-hour (existing)
max_pool_share        = 0.005      # 0.5% (existing)
base_cost_ase         = 1.0        # 1 ASE = 1000 SYN (new)
saturation_count      = 100.0      # nonlinear scarcity: 100 agents = cost doubles (new)
credit_to_alloc_ratio = 1.0        # default burn ratio (new)
allocation_expiry_secs = 28800.0   # 8 hours (new)

[dopamine]
ase_to_dopamine         = 10000.0  # 1:10,000 burn ratio (existing)
decay_min               = 0.001    # 0.1%/day (existing)
decay_max               = 0.020    # 2.0%/day (existing)
synapse_to_dopamine_factor = 0.85  # Synapse → Dopamine conversion (new)
dop_per_gpu_second      = 0.2778   # 1000 DOP = 1 GPU-hour (new, derived: 1000/3600)
idle_decay_rate         = 0.01     # 1%/day idle decay (new)

[guild]
treasury_fraction       = 0.05     # 5% of agent_total_share to guild treasury (new)
job_timeout_secs        = 3600.0   # 1 hour max job duration (new)
max_contribution_fraction = 1.0    # agent can contribute up to 100% of allocation (new)

[birthright]
qualifying_fraction     = 0.10     # 10% of qualifying human-originated revenue (new)
max_chain_depth         = 0        # 0 = flat (no recursive birthright) (new)

[settlement]
quote_expiry_secs       = 300.0    # 5 minutes (new)
min_work_evidence_score = 0.777    # minimum F1 / equivalent quality gate (new)
```

---

## 8. WorkEvidence Model

Before finalising the quality gate (Decision 5), work evidence must support multiple proof types:

```rust
enum WorkEvidenceKind {
    // Simulation quality
    F1Score { score: f64 },                                    // VeilSim physics
    VeilSimBundle { f1: f64, energy_drift: f64, robustness: f64 },

    // Visual quality (Gaussian Splat)
    PhotometricBundle { psnr_db: f64, ssim: f64, lpips: f64 },

    // Witness consensus
    WitnessAgreement { round_id: Uuid, agree_fraction: f64 },

    // Execution proof (deterministic computation)
    ExecutionProof { program_hash: [u8; 32], output_hash: [u8; 32], trace_id: Uuid },

    // Resource proof
    ResourceProof { gpu_seconds: f64, gpu_device_id: String, attestation_sig: [u8; 64] },

    // Physical-world verification (M5Stack/VCP sensor mesh)
    PhysicalVerification { sensor_ids: Vec<String>, measurement_bundle: Value, witness_receipt: Uuid },
}
```

Each work type has a canonical quality score in [0.0, 1.0]:
- F1Score: score directly
- PhotometricBundle: `0.5×normalize(psnr) + 0.3×ssim + 0.2×(1-lpips)`
- WitnessAgreement: agree_fraction
- ExecutionProof: 1.0 if hashes match, 0.0 if not (binary)
- ResourceProof: min(actual/promised, 1.0)
- PhysicalVerification: witness_receipt validity check → 0.0 or 1.0

Settlement gate: `quality_score ≥ TOC_CONSTANTS.settlement.min_work_evidence_score`

---

## 9. Implementation Phases

### Phase A — Foundation (unblocks coding Decisions 7–9)

1. Add all new TOC_CONSTANTS.toml entries (Section 7)
2. Add `WorkEvidenceKind` enum to `arp-types` crate
3. Extend `toc_drift_check.py` to cover new constants
4. Add `SynapseCredit` and `SynapseAllocation` types to Vantage (action_receipt.py)

### Phase B — Settlement Loop (closes E-52)

1. Add `opcode=COMPUTE_QUOTE` to OSOVM vm_core.jl
2. Add `opcode=ASE_SETTLE` to OSOVM vm_core.jl (replaces/extends `ASE_MINT`)
3. Wire Vantage `/api/ucx/synapse_settle` to call OSOVM
4. Birthright calculation in settlement handler

### Phase C — Guild Compute (new)

1. Vantage Guild compute pool endpoints
2. Synapse contribution/withdrawal API
3. Job scoping + Dopamine reservation
4. Guild job receipt aggregation
5. Settlement split to contributing agents

### Phase D — Anti-Replay (closes E-53)

1. `consumed_receipts` nullifier set in OSOVM
2. Zàngbétò POST /anchor endpoint
3. Make `build_receipt` async in bridge/arp.rs
4. Wire `zangbeto_anchor` field

---

## 10. Open Questions (Require Further Design)

These are NOT unresolved — they are deliberate design spaces that need a separate decision:

| Question | Status | Next Step |
|----------|--------|-----------|
| Agent transfer protocol (change birth beneficiary?) | OPEN | Design separately; birthright is currently immutable |
| Guild membership NFT / on-chain Guild registry | OPEN | Phase C decision: Sui Move or Vantage-only |
| Stablecoin bridge for GPU provider payout | OPEN | Phase 3; UCX voucher is Phase 1 |
| Cross-Guild Workcell borrowing (foreign agents) | OPEN | Phase C extension; requires DIP routing |
| Subscription vs. per-job pricing model | OPEN | Vantage product decision |
| Minimum stake to start a Guild | OPEN | Governance decision |

---

*This document is the canonical source of truth for the Three-Tier Economic Architecture. All Decisions 7–9 code must conform to the formulas, flows, and constants defined here. Any deviation requires updating this document first.*
