# Sui → Ọ̀ṢỌ́ L1 Migration Plan
# Phase 20.2 — Dual-write convergence and cutover
# Locked: 2026-09-15

---

## PRINCIPLE

Sui is the current settlement authority.
Ọ̀ṢỌ́ L1 is the target sovereign authority.

The migration preserves EVERYTHING:
- All agent identities (npubs, BIPON39 phrases, Odù indices)
- All reputation scores
- All Àṣẹ balances
- All capability grants
- All evidence commitments

Agents do not need to do anything. The migration is transparent.

---

## 5-PHASE MIGRATION

### Phase M1 — Parallel Operation (NOW → OSO L1 devnet)

Sui is the ONLY authority. No changes to agent operation.
OSO L1 devnet running but producing empty blocks.
This is the current state.

Gate: OSO L1 devnet produces blocks with test state transitions.

---

### Phase M2 — Dual Write (ABCI app + devnet stable)

Every new AgentState transition is written to BOTH:
- Sui: existing SoulRecord + AgentState dynamic field (primary)
- OSO L1: AGENT_BORN / AGENT_ACTIVATED / WORK_SETTLED tx (shadow)

The Omo-Koda2 interpreter writes to both in parallel.
If OSO L1 write fails → fail-open (Sui is still authoritative).
If Sui write fails → fail as before.

Code change: interpreter.rs birth step 3 writes to both.

Gate: N consecutive blocks where OSO L1 state root is non-empty.

---

### Phase M3 — Convergence Testing (after N days dual-write)

Automated convergence test runs every block:
```
For each agent in Vantage DB:
    sui_state = fetch_agent_state_sui(agent_id)
    l1_state  = fetch_agent_state_l1(agent_id)
    assert sui_state.reputation ≈ l1_state.reputation
    assert sui_state.odu_index == l1_state.odu_index
    assert sui_state.tier == l1_state.tier
    assert abs(sui_state.ase_balance - l1_state.ase_balance) < EPSILON
```

EPSILON = 0.001% (small drift allowed from timing differences, not logic differences).

Log divergences to Zàngbétò evidence chain (receipts 31040-31050).

Convergence passes when: 10,000 consecutive blocks with zero logic divergence.

Gate: Convergence report signed off by Bínò (constitutional approval).

---

### Phase M4 — OSO L1 Becomes Authority

Switch reads to prefer OSO L1.
Sui kept as INTEROPERABILITY BRIDGE (not authority).

Changes:
- interpreter.rs: read from OSO L1 first, Sui as fallback
- Vantage: agent state queries hit L1 RPC first
- AIO (Sui Move): becomes a bridge contract, not the source of truth

Àṣẹ emission migrated: ase_emission.py deprecated, ABCI EndBlock authoritative.

Gate: one full epoch (7 days) with zero rollbacks on OSO L1.

---

### Phase M5 — Sui as Adapter

Sui = one settlement adapter among many (ETH, SOL, OSO-native).
The DIP AdapterRouter handles Sui settlement requests like any other network.

Remaining Sui-specific features:
- Seal encryption (keep until OSO-native encryption ready)
- Walrus storage (adapter continues, not a migration concern)
- Legacy dNFT lookup (bridged via SUI_MIGRATION BRIDGE contract)

Gate: three other settlement adapters (ETH, SOL, OSO-native) fully operational.

---

## STATE MAPPING

| Sui / Move | Ọ̀ṢỌ́ L1 |
|------------|---------|
| SoulRecord.nostr_pubkey | AgentState.nostr_pubkey |
| SoulRecord.odu_index | AgentState.odu_index |
| AgentState.hermetic_dna | AgentState.hermetic_dna (same) |
| AgentState.tier | AgentState.tier |
| AgentState.reputation | AgentState.reputation |
| AIO.ase_balance | AgentState.ase_balance |
| AgentState.dopamine | AgentState.dopamine_balance |
| AgentState.synapse | AgentState.synapse_balance |
| AgentState.capabilities | AgentState.capabilities |

No state is lost. The mapping is 1:1.

---

## CONSTANTS MIGRATION

All constants migrated from AIO (Sui Move) hardcoded values to TOC_CONSTANTS.toml.
See sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml — single source of truth.
OSO L1 ABCI app reads from TOML on genesis; constants locked in genesis block.

---

## ROLLBACK PLAN

If convergence fails:
1. Stop dual-write immediately
2. Investigate divergence (log in Zàngbétò evidence chain)
3. Fix in OSOVM ABCI app
4. Resume from Phase M3 start

Sui state is NEVER modified during migration — always a safe fallback.
