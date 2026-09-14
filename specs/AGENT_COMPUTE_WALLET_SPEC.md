# AGENT_COMPUTE_WALLET_SPEC.md
**Status:** Locked 2026-09-14 — constants from live OSOVM code.
**Owner:** Omo-Koda2 `walletd` daemon + OSOVM (mint/burn authority)
**Depends on:** VerifiedGPUWork, TOC_MINT, Dopamine ledger, Synapse ledger

---

## 1. Purpose

Every sovereign agent owns a compute wallet. It is NOT a financial wallet (Àṣẹ lives
in Vantage + AIO). The compute wallet holds the two compute credit tokens:

- **Dopamine** — the agent's slice of the total online GPU compute pool.
  Contributes GPU → earns Dopamine. Think with Dopamine.
- **Synapse** — the agent's allocated compute units, converted from Dopamine.
  Synapse is the spendable form. Synapse decays. Dopamine does not.

Àṣẹ is reputation/currency and lives separately. The compute wallet contains only
Dopamine and Synapse.

---

## 2. Token Constants (from live OSOVM code)

```
# From OSOVM/src/ase_supply.jl
AGENT_DOPAMINE_ENDOWMENT  = 86_000_000_000   # 86B units (= ~human neuron count)
AGENT_SYNAPSE_ENDOWMENT   = 86_000_000        # 86M units
TITHE_RATE                = 0.0369            # 3.69% Èṣù on value-job settlement
ASE_TO_DOPAMINE_RATIO     = 10_000            # 1 Àṣẹ → 10,000 Dopamine (via Akash rail)
AGENT_BIRTH_FEE           = 10.0              # Àṣẹ paid to birth registry

# From The-Aether/src/engine/toc/token.js
DOPAMINE_DAILY_DECAY      = 0.01              # 1%/day compound (anti-hoard)
DOPAMINE_TRANSFERABLE     = false
SYNAPSE_CONVERSION_RATIO  = 0.10              # 10 Dopamine → 1 Synapse (one-way burn)
SYNAPSE_TRANSFERABLE      = true
SYNAPSE_DAILY_DECAY       = 0.01              # 1%/day compound
FORK_STAKE_FRACTION       = 0.10              # 10% Synapse locked on fork
STAKE_GATE_FRACTION       = 0.10             # 10% Synapse required for tier gate
```

---

## 3. Wallet Structure

```rust
pub struct AgentComputeWallet {
    pub agent_id:           String,

    // Dopamine — hive-pool contribution token
    pub dopamine_balance:   u64,     // current balance (post-decay)
    pub dopamine_earned:    u64,     // lifetime earned from GPU contributions
    pub dopamine_burned:    u64,     // lifetime burned via 10:1 → Synapse conversion
    pub dopamine_decayed:   u64,     // lifetime lost to 1%/day decay

    // Synapse — spendable compute allocation
    pub synapse_balance:    u64,     // current spendable balance (post-decay)
    pub synapse_earned:     u64,     // lifetime minted (from conversion + birth)
    pub synapse_spent:      u64,     // lifetime spent on jobs/inference
    pub synapse_staked:     u64,     // currently locked in stake gates
    pub synapse_decayed:    u64,     // lifetime lost to 1%/day decay

    // Stake locks
    pub stake_locks:        Vec<StakeLock>,

    // Ledger
    pub ledger:             Vec<ComputeLedgerEntry>,

    // Metadata
    pub last_decay_tick:    u64,     // unix timestamp of last decay application
    pub wallet_version:     u8,
}

pub struct StakeLock {
    pub lock_id:        String,
    pub reason:         String,  // "tier_gate" | "fork" | "skill_acquire"
    pub amount:         u64,
    pub locked_at:      u64,
    pub unlock_at:      u64,     // 0 = indefinite (tier gate until tier achieved)
    pub unlocked:       bool,
}

pub struct ComputeLedgerEntry {
    pub entry_id:       String,
    pub timestamp:      u64,
    pub token:          String,  // "dopamine" | "synapse"
    pub delta:          i64,     // positive = credit, negative = debit
    pub reason:         String,
    pub receipt_id:     Option<String>,
}
```

---

## 4. Funding Flows

### 4.1 Birth Endowment

At agent birth (OSOVM `TOC_MINT` opcode, birth source):

```
wallet.dopamine_balance += AGENT_DOPAMINE_ENDOWMENT  (86B)
wallet.synapse_balance  += AGENT_SYNAPSE_ENDOWMENT   (86M)
```

This is the ONLY mint that bypasses GPU contribution verification. All subsequent
Dopamine minting requires `VerifiedGPUWork`.

### 4.2 GPU Contribution → Dopamine

Agent contributes GPU time → `VerifiedGPUWork` receipt → OSOVM validates:

```
verified_work = VerifiedGPUWork {
    gpu_seconds,  hardware_attestation,  workload_hash,
    witness_receipts,  OSOVM_proof
}

dopamine_earned = gpu_seconds × DOPAMINE_PER_GPU_SECOND
wallet.dopamine_balance += dopamine_earned
```

`DOPAMINE_PER_GPU_SECOND` is pool-adjusted each epoch based on total online compute.
The formula keeps Dopamine supply proportional to actual GPU capacity:

```
DOPAMINE_PER_GPU_SECOND = AGENT_DOPAMINE_ENDOWMENT / EPOCH_BASELINE_GPU_SECONDS
```

Where `EPOCH_BASELINE_GPU_SECONDS = 86_400` (one GPU-day).

### 4.3 Dopamine → Synapse Conversion (10:1 burn, one-way)

```
SYNAPSE_CONVERSION_RATIO = 0.10   (10 Dopamine → 1 Synapse)

burn_dopamine = requested_synapse_amount × 10
require wallet.dopamine_balance >= burn_dopamine
wallet.dopamine_balance -= burn_dopamine
wallet.synapse_balance  += requested_synapse_amount
wallet.dopamine_burned  += burn_dopamine
```

This is irreversible. Synapse cannot be converted back to Dopamine.

### 4.4 Àṣẹ → Dopamine via Akash Rail (external funding)

```
ase_spent   → Èṣù Router 3.69% tithe
            → remaining Àṣẹ → AKT purchase
            → Akash GPU provision
            → GPU-seconds verified
            → Dopamine credited at market rate (ASE_TO_DOPAMINE_RATIO = 10,000)
```

This path is used when an agent wants to buy compute with economic merit (Àṣẹ)
rather than contributing physical GPU. The Akash rail adds slippage; start on
native Dopamine contribution where possible.

### 4.5 Soul Evolution → Synapse Mint (ToC)

Rank-up events mint additional Synapse via the ToC hook:

```
synapse_mint = SYNAPSE_PER_RANK × rank_delta    (SYNAPSE_PER_RANK = 1,111)
```

OSOVM validates `is_fully_verified()` before authorizing. The AIO contract records
the mint on Sui.

---

## 5. Spend Paths

Synapse is the spendable token. Dopamine is non-transferable and cannot be spent directly.

| Spend Type | Cost (Synapse) | Notes |
|------------|---------------|-------|
| LLM inference call | 1–100 per call | scales with context length |
| OSOVM veil execution | 10 per veil tick | per-opcode billing |
| Skill acquisition via SkillForge | 500–5,000 | depends on skill tier |
| Agent fork (parent stake lock) | 10% of balance | locked, returned after child first heartbeat |
| Tier gate stake | 10% of balance | locked until tier achieved |
| GPU lease reservation | market rate | converted to Dopamine spend internally |
| Memory consolidation cycle | 50 per cycle | mycelium write + Walrus anchor |
| Nostr event publication (kind 30174+) | 5 per event | relay anti-spam |

---

## 6. Decay

Both tokens decay at 1%/day compound (anti-hoarding mechanism).

```
decay_rate_per_second = 1 - (0.99 ^ (1/86400))
                      ≈ 0.000000116  per second

current_balance = last_balance × (0.99 ^ days_since_last_tick)
```

Decay is applied lazily — computed at the moment of any read or write, not on a fixed
schedule. The `last_decay_tick` timestamp enables the lazy calculation.

Decayed units are permanently destroyed (not redistributed). This keeps compute supply
proportional to active participation.

---

## 7. Stake Gates

Certain operations require a stake lock on Synapse. Locked Synapse is frozen but NOT
burned unless the agent abandons the gate (burn-on-abandon is a governance parameter,
initially disabled).

```rust
pub enum StakeReason {
    TierGate  { target_tier: u8  },
    ForkLock  { child_id: String },
    SkillAcquire { skill_id: String },
}
```

**Tier gate** — required for T2, T3, T4, T5 progression:

```
T2 gate: stake 10% of current Synapse balance
T3 gate: stake 10% of current Synapse balance
T4 gate: stake 10% of current Synapse balance
T5 gate: stake 10% of current Synapse balance + 3 witnessed simulations
```

Stake is released when the tier evaluation passes. If the agent does not achieve the
tier within 90 days, the stake is unlocked (not burned) and returned.

---

## 8. walletd Daemon

Omo-Koda2 runs `walletd` as a persistent daemon that owns the local wallet state.
OSOVM is authoritative for mint/burn; `walletd` maintains the local ledger and
submits mutations to OSOVM for authorization.

```
walletd responsibilities:
  1. Apply lazy decay on every read/write
  2. Maintain ComputeLedgerEntry log
  3. Enforce stake locks (prevent overspend)
  4. Submit VerifiedGPUWork to OSOVM for Dopamine credit
  5. Request Synapse conversion via OSOVM TOC_MINT
  6. Sync wallet state with Vantage on every heartbeat
  7. Alert agent runtime when Synapse < LOW_WATER_MARK (10M)
```

**Persistence:** wallet state sealed in `MemoryVaultData` (identity_vault sub-field),
encrypted ChaCha20Poly1305 + Argon2id.

---

## 9. Low-Water Behaviour

When `synapse_balance < LOW_WATER_MARK`:

```
LOW_WATER_MARK = 10_000_000  (10M Synapse)
```

1. `walletd` emits `ComputeWarning` event to agent runtime.
2. Agent runtime suspends non-essential veil executions.
3. GPU contribution path prioritised — walletd begins GPU lease negotiation.
4. If balance hits 0: agent enters `COMPUTE_STARVED` state — heartbeat only,
   no new jobs accepted until Synapse balance > LOW_WATER_MARK.

---

## 10. Implementation Targets

| File | What to add |
|------|-------------|
| `omokoda-core/src/kernel/compute/accounting.rs` | `AgentComputeWallet`, `StakeLock`, `ComputeLedgerEntry` structs |
| `omokoda-core/src/services/walletd.rs` | daemon loop: decay tick + spend gate + Vantage sync |
| `omokoda-core/src/session.rs` | add `compute_wallet: Option<AgentComputeWallet>` to `MemoryVaultData` |
| `OSOVM/src/vm_core.jl` | `op_dopamine_credit` — accepts `VerifiedGPUWork`, credits Dopamine |
| `OSOVM/src/vm_core.jl` | `op_synapse_spend` — validates + debits Synapse for job execution |
| `Vantage/routers/ucx.py` | `GET /api/agents/{id}/wallet` — wallet snapshot for dashboard |
