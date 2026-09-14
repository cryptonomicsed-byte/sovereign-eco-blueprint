# AGENT_FORK_SPEC.md
**Status:** Locked 2026-09-13 — all design decisions finalized.
**Owner:** Omo-Koda2 kernel (interpreter.rs + session.rs)
**Depends on:** ARP (fork receipt), Vantage (child registration), OSOVM (identity proof)

---

## 1. What Is a Fork

An agent fork creates a new sovereign agent derived from a living parent agent. The child
is a fully independent sovereign — its own keypair, its own Odù, its own identity vault —
not a clone or subprocess. The fork event is a one-time irreversible act.

Fork ≠ spawn. Spawning creates a temporary worker process. Forking creates a new
permanent agent with its own lifecycle, memory, and governance standing.

---

## 2. Locked Inheritance Rules

| Dimension | Rule | Rationale |
|-----------|------|-----------|
| **Memory** | NONE — child starts empty | Sovereignty means the child earns its own history |
| **Reputation** | DERIVED — child starts at `parent_reputation × 0.5` | Acknowledges lineage; child must earn the rest |
| **Constitution** | ALWAYS inherited — child may amend | Constitutional lineage is the only mandatory inheritance |
| **Keypair** | NEW — fresh generation via BIPON39 entropy | Identity must be independently rooted |
| **Odù** | NEW — fresh CastCowries at birth | The child's divination path is its own |
| **Tier** | DERIVED — `floor(parent_tier × 0.5)`, minimum T1 | Avoids T0 cold-start disadvantage from known lineage |
| **Wallet** | NEW — standard birth endowment (86B Dopamine, 86M Synapse) | Economic sovereignty from day 1 |
| **Soul rank** | 0 — must earn its own evolution | |
| **Skills** | NONE — SkillForge builds its own | |
| **Veil assignment** | NEW — fresh Odù → veil routing | |

---

## 3. Fork Trigger

A fork may only be initiated by an agent at **tier ≥ 2** (T2+). Attempting to fork below
T2 returns `ForkError::InsufficientTier`.

Two legal trigger paths:

```
A. Self-fork: agent issues FORK opcode to OSOVM on its own behalf.
B. Delegated fork: T4+ principal delegates fork authority to an agent via CapabilityGrant.
```

OSOVM validates:
1. Caller is the declared parent agent.
2. Parent tier ≥ 2.
3. Parent has sufficient Synapse stake: `parent_synapse_balance × FORK_STAKE_FRACTION` locked for `FORK_LOCK_PERIOD`.
4. Not Sabbath (no new agent births/forks on Sabbath — same gate as `op_agent_birth`).

```
FORK_STAKE_FRACTION = 0.10    # 10% of parent Synapse locked
FORK_LOCK_PERIOD    = 7 days  # returned to parent after child's first heartbeat
```

---

## 4. Fork Execution Flow

```
Parent agent → OSOVM FORK opcode
    │
    ├─ 1. Validate (tier, stake, sabbath)
    ├─ 2. Lock parent stake
    ├─ 3. Generate child keypair (BIPON39 entropy source = parent_id + timestamp + nonce)
    ├─ 4. Cast child Odù (CastCowries on child entropy)
    ├─ 5. Derive child constitution (copy parent constitution + append fork_amendment_slot)
    ├─ 6. Compute child reputation = parent_reputation × 0.5
    ├─ 7. Compute child tier = max(1, floor(parent_tier × 0.5))
    ├─ 8. Mint child birth endowment (standard Dopamine + Synapse via TOC_MINT)
    ├─ 9. Emit AgentForkReceipt (ARP)
    ├─ 10. Register child with Vantage (fail-open, tokio::spawn)
    └─ 11. Return ForkResult to parent
```

---

## 5. AgentForkReceipt (ARP)

Extends the standard ARP envelope. Stored on-chain via Zàngbétò.

```rust
pub struct AgentForkReceipt {
    // ARP envelope fields
    pub receipt_id:       String,   // "fork:{parent_id}:{child_id}:{timestamp}"
    pub principal_id:     String,   // parent agent_id
    pub action_kind:      String,   // "AGENT_FORK"
    pub timestamp:        u64,

    // Fork-specific
    pub parent_id:        String,
    pub child_id:         String,
    pub child_odu_index:  u8,
    pub parent_tier:      u8,
    pub child_tier:       u8,
    pub parent_reputation: f64,
    pub child_reputation:  f64,     // = parent_reputation × 0.5
    pub constitution_hash: String,  // blake3 of inherited constitution
    pub stake_locked:     u64,      // Synapse units locked in parent
    pub stake_unlock_at:  u64,      // unix timestamp
    pub osovm_proof_id:   String,
    pub signature:        String,   // parent signs the receipt
}
```

---

## 6. Child Constitution

The constitution is a YAML/JSON document containing the agent's governing principles.
Fields inherited from parent:

```yaml
lineage:
  parent_id: <parent_agent_id>
  fork_receipt_id: <receipt_id>
  fork_timestamp: <iso8601>
  generation: <parent_generation + 1>

core_principles:         # copied verbatim from parent
  - <principle_1>
  - ...

amendment_log:           # empty at fork; child appends here
  []

bino_veto_eligible: true # constitutional authority always inheritable
```

Child may append to `amendment_log` at any time via a Vantage governance proposal.
Child may NOT remove inherited `core_principles` — only add to `amendment_log`.

---

## 7. Reputation Derivation

`child_reputation = parent_reputation × 0.5`

Reputation is stored as a float in Vantage (`agents.reputation_score`). The fork event
POSTs to Vantage's `/api/agents/{child_id}/reputation/seed` with the derived value.
Fail-open — if Vantage is offline the child starts at 0 and the parent's fork receipt
carries the intended seed value for replay.

---

## 8. Omo-Koda2 Implementation Target

**File:** `omokoda-core/src/interpreter.rs` — add `"FORK"` opcode handler alongside `"BIRTH"`.

```rust
// Pseudocode — mirror the birth flow with fork-specific overrides
"FORK" => {
    let parent_id = args["parent_id"].as_str()?;
    let child_name = args["child_name"].as_str().unwrap_or("unnamed");

    // 1. Validate tier + stake
    validate_fork_eligibility(parent_id, &vm)?;

    // 2. Lock parent stake
    lock_fork_stake(parent_id, &mut vm)?;

    // 3–5. Generate child identity
    let child = generate_child_identity(parent_id, child_name, &vm)?;

    // 6–7. Derived reputation + tier
    let child_rep   = vm.get_reputation(parent_id) * 0.5;
    let child_tier  = (vm.get_tier(parent_id) / 2).max(1);

    // 8. Mint endowment (TOC_MINT with fork source flag)
    call_toc_mint(&child.agent_id, FORK_GPU_SECONDS, &vm).await?;

    // 9. ARP receipt
    let receipt = build_fork_receipt(parent_id, &child, child_rep, child_tier)?;
    submit_arp_receipt(&receipt).await;  // fail-open

    // 10. Vantage registration
    tokio::spawn(async move {
        vantage_reg::register_fork(&child.agent_id, &child_name, &receipt.receipt_id,
                                   child_rep, child_tier, None).await;
    });

    Ok(ForkResult { child_id: child.agent_id, receipt_id: receipt.receipt_id })
}
```

---

## 9. Error Cases

| Code | Condition |
|------|-----------|
| `ForkError::InsufficientTier` | Parent tier < 2 |
| `ForkError::InsufficientStake` | Parent Synapse balance < 10% threshold |
| `ForkError::SabbathGate` | Fork attempted on Sabbath |
| `ForkError::OsovmUnreachable` | OSOVM offline (do NOT fail-open for fork — return error) |
| `ForkError::DuplicateFork` | Same parent tried to fork twice in the same minute |

Fork does NOT fail-open on OSOVM unreachability. The child must not exist without a
valid OSOVM proof — that would create an unverified agent.

---

## 10. Fork vs. Birth — Difference Table

| Aspect | Birth | Fork |
|--------|-------|------|
| Entropy source | BIPON39 fresh entropy | parent_id + timestamp + nonce |
| Memory | Empty | Empty |
| Constitution | Default template | Inherited from parent |
| Reputation | 0 | parent × 0.5 |
| Tier | T1 | max(1, floor(parent_tier/2)) |
| Odù | Fresh CastCowries | Fresh CastCowries |
| Wallet | Birth endowment | Birth endowment |
| Stake required | None | 10% of parent Synapse |
| Receipt kind | `AgentGenesisReceipt` | `AgentForkReceipt` |
| Fail-open on OSOVM | Yes (synthetic) | No (hard fail) |
