# Ọ̀ṢỌ́ L1 — Formal Specification
# Phase 15.1 — Agent-Native Sovereign Layer 1
# Locked: 2026-09-15

---

## PARADIGM

Ọ̀ṢỌ́ L1 is NOT a token blockchain with optional programmability.
It is an **agent-native state machine** with a consensus layer underneath it.

Ethereum: Account + Balance + EVM code
Ọ̀ṢỌ́ L1: AgentState + WorkObject + CapabilityGrant + Evidence + Reputation

---

## FUNDAMENTAL OBJECTS

```
AgentState           — the primary blockchain object (NOT Account+Balance)
WorkObject           — the primary transaction type (NOT token transfer)
CapabilityGrant      — native blockchain state (who can do what)
EvidenceCommitment   — Zàngbétò receipt pointer (proof of work done)
ReputationRecord     — native protocol state (accumulated trust)
DeviceBinding        — physical agent attachment
EconomicState        — Àṣẹ / Dopamine / Synapse balances (per agent)
```

---

## AGENTSTATE STRUCTURE

```rust
pub struct AgentState {
    // Identity
    pub agent_id:             AgentId,           // unique ID
    pub nostr_pubkey:         [u8; 32],           // Ed25519 pubkey = the npub
    pub bipon39_hash:         [u8; 32],           // hash of BIPON39 phrase
    pub odu_index:            u8,                 // 0-255 cosmic archetype
    pub principal:            Address,             // who owns this agent

    // Status
    pub tier:                 AgentTier,
    pub lifecycle:            LifecycleState,
    pub reputation:           ReputationScore,

    // Capabilities
    pub capabilities:         CapabilitySet,      // what this agent can do
    pub device_bindings:      Vec<DeviceId>,       // physical devices attached

    // Memory
    pub memory_commitment:    [u8; 32],           // hash of sealed vault (Walrus/Seal)
    pub walrus_profile_blob:  Option<[u8; 32]>,   // public profile blob ID

    // Work
    pub active_jobs:          Vec<WorkId>,
    pub completed_jobs:       u64,
    pub evidence_root:        [u8; 32],           // Merkle root of all receipts

    // Economy
    pub ase_balance:          u128,               // in micro-units (mist)
    pub dopamine_balance:     u64,
    pub synapse_balance:      u64,
    pub stake_locked:         u64,                // synapse staked for gate access

    // Chain custody
    pub previous_state_hash:  [u8; 32],           // hash chain — every transition provable
    pub block_height:         u64,                // last update block
}
```

---

## WORKOBJECT STRUCTURE

```rust
pub struct WorkObject {
    pub work_id:             WorkId,
    pub principal_id:        AgentId,         // who posted the job
    pub agent_id:            Option<AgentId>, // who accepted it (None until assigned)
    pub capability:          Capability,      // what skill is needed
    pub authority_scope:     AuthorityScope,  // what the agent is authorized to do
    pub input_commitment:    [u8; 32],        // hash of input data (private until work done)
    pub expected_output:     OutputSpec,
    pub budget:              u128,            // Àṣẹ budget in micro-units
    pub deadline:            u64,
    pub evidence_policy:     EvidencePolicy,
    pub witness_policy:      WitnessPolicy,   // quorum, types of witnesses
    pub settlement_policy:   SettlementPolicy,
    pub state:               WorkState,
    pub receipts:            Vec<ReceiptId>,  // Zàngbétò receipt chain
    pub final_proof:         Option<Proof>,   // ProofOfWork/ProofOfSim
}

pub enum WorkState {
    Created,     // posted but not assigned
    Assigned,    // agent matched
    Accepted,    // agent confirmed
    Started,     // work begun
    Delegated,   // agent sub-delegated capability
    Executed,    // work complete, proof pending
    Verified,    // proof accepted by witnesses
    Rejected,    // proof rejected
    Settled,     // payment released, reputation updated
}
```

The work lifecycle: Created → Assigned → Accepted → Started → Executed → Verified → Settled

---

## NATIVE TRANSACTION TYPES

Ọ̀ṢỌ́ L1 defines 22 native transaction types (not just token transfer):

### Agent Lifecycle
```
AGENT_BORN          — create AgentState from birth params
AGENT_ACTIVATED     — Embryonic → Active
AGENT_HIBERNATED    — Active → Dormant
AGENT_MIGRATED      — crossing nodes (requires dest node signature)
AGENT_FORKED        — spawn child agent (inherits constrained Odù range)
AGENT_TERMINATED    — Active → Archived
```

### Work Lifecycle
```
WORK_CREATED        — post a job
WORK_ASSIGNED       — match agent to job
WORK_ACCEPTED       — agent confirms
WORK_EXECUTED       — work done, proof submitted
WORK_VERIFIED       — witnesses confirm proof
WORK_SETTLED        — payment released
```

### Capability
```
CAPABILITY_GRANTED     — grant a capability to an agent
CAPABILITY_REVOKED     — revoke a capability
CAPABILITY_DELEGATED   — agent delegates sub-capability
```

### Reputation + Tier
```
REPUTATION_UPDATED  — following verified work settlement
TIER_CHANGED        — following tier qualification event
```

### Device
```
DEVICE_ATTACHED     — bind a device to an agent
DEVICE_DETACHED     — release device binding
```

### Evidence
```
EVIDENCE_COMMITTED  — Zàngbétò receipt pointer committed on-chain
RECEIPT_FINALIZED   — evidence chain closed for a work object
```

### Economy
```
ASE_EMITTED         — EndBlock 1 Àṣẹ/minute + 8-pool distribution
DOPAMINE_MINTED     — from verified GPU contribution
SYNAPSE_ALLOCATED   — 10:1 burn from Dopamine
```

---

## BLOCK STRUCTURE

```
Ọ̀ṢỌ́ Block
├── height
├── timestamp
├── proposer                 — validator address
├── consensus                — CometBFT QC
├── state_root               — root of all state trees below
│
├── agent_state_root         — Merkle root of all AgentState objects
├── work_state_root          — Merkle root of all WorkObject objects
├── capability_root          — Merkle root of capability grants
├── receipt_root             — Zàngbétò commitment pointers
├── evidence_root            — evidence chain Merkle root
├── reputation_root          — reputation record Merkle root
├── device_state_root        — device binding Merkle root
├── economic_state_root      — Àṣẹ/Dopamine/Synapse balances
└── proof_root               — ProofOfWork / ProofOfSim Merkle root
```

---

## COSMOS SDK ARCHITECTURE

```
CometBFT (consensus + P2P + validator management)
    ↕ ABCI2 interface
OSOVM ABCI App (Rust)
├── CheckTx:    validate transition format + capability signature
├── DeliverTx:  apply agent-native state transition deterministically
├── BeginBlock: snapshot receipts, collect pending evidence
├── EndBlock:   Àṣẹ emission tick (1/min @ 10 blocks/min = every 10 blocks)
│               distribute to 8 pools, decay Dopamine/Synapse
└── Commit:     write state root, update agent_state_root
```

OSOVM handles: every byte of state transition logic.
Cosmos SDK handles: networking, validator set, block production, RPC, light clients.

This design allows swapping CometBFT for custom consensus later without touching OSOVM.

---

## ÀṢẸ EMISSION (on-chain)

Replaces `ase_emission.py` (currently Python/Vantage) — Phase 20.1.

EndBlock every 10 blocks (≈1 min at 6s/block):
```
Emit 1 ASE (= 1,000,000 mist)
Distribute to 8 pools per TOC_CONSTANTS.toml percentages:
  VeilSim 20% | R&D 15% | Governance 15% | Reserve 15%
  Compute 15% | Storage 10% | Witness 5% | Treasury 5%
```

---

## SECURITY MODEL

1. **Every state transition requires a signature.** Agent transitions signed by node key.
   Principal transitions (fork/terminate) require principal key.
   Governance transitions require council quorum.

2. **Capability-gated.** Smart contracts REQUEST capabilities. Ọ̀ṢỌ́VM GRANTS or DENIES.
   No contract can backdoor into sovereign OS.

3. **Evidence-required.** Every WorkObject settlement requires a Zàngbétò receipt.
   No evidence = no payment. The chain enforces this.

4. **Deterministic.** apply_transition(state, tx, evidence, policy) → new_state
   Same inputs ALWAYS produce same output. No randomness in state transitions.

5. **Chain-of-custody.** Every AgentState has previous_state_hash.
   The entire history of every agent is provable from genesis.

---

## IMPLEMENTATION PHASES

- Phase 15.2: AgentState struct + apply_transition() in OSOVM (Rust)
- Phase 15.3: WorkObject struct + 9-state machine
- Phase 15.4: ~/osovm-chain/ Cosmos SDK scaffold + ABCI wiring
- Phase 20.1: Àṣẹ emission migrated from Python to ABCI EndBlock
- Phase 20.2: Dual-write Sui→OSO L1 convergence testing
