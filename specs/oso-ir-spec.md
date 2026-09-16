# Ọ̀ṢỌ́ Intermediate Representation (OSO-IR) Specification
# Version 1.0 — Phase 21.1 / 21.3
# Locked: 2026-09-15

---

## PURPOSE

The OSO-IR is the JSON-serialisable intermediate representation that bridges:

- **Source**: Ọ̀ṢỌ́ language (what the developer writes — declarative, agent-native)
- **Target**: Move / WASM / Native contract backends (what actually executes)

The compiler pipeline is:

```
Ọ̀ṢỌ́ source
   → OSO-IR (this document) ← validation gate
      → Move codegen (Sui testnet / OSOVM L1)
      → WASM codegen (browser / edge)
      → Native codegen (Rust — kernel-local execution)
```

---

## DESIGN PRINCIPLES

| Principle | Detail |
|---|---|
| **Declarative** | IR describes *what*, not *how*. Backend chooses execution strategy. |
| **Backend-agnostic** | Same IR document compiles to Move, WASM, or Native unchanged. |
| **Security-explicit** | Capabilities are declared, not assumed. Missing capability = compile error. |
| **Evidence-native** | Proof requirements are first-class IR fields, not afterthoughts. |
| **Lifecycle-complete** | Every contract state machine is declared in the IR (no implicit transitions). |
| **Sovereign-economics** | Fee routing, ASE burn, Èṣù tithe, and pool distribution declared per contract. |

---

## TOP-LEVEL SCHEMA

```json
{
  "oso_ir_version": "1.0",
  "contract_class":  "<ContractClass>",
  "contract_name":   "<string>",
  "assets":          [ <AssetSpec>, ... ],
  "capabilities":    [ "<string>", ... ],
  "minimum_tier":    <u8>,
  "evidence":        <EvidenceSpec>,
  "witness_policy":  <WitnessPolicySpec>,
  "settlement":      <SettlementSpec>,
  "policy":          <PolicySpec>,
  "lifecycle":       [ "<StateLabel>", ... ]
}
```

### `oso_ir_version` (string, required)

Current value: `"1.0"`. Validators must reject unknown versions.

### `contract_class` (enum, required)

One of: `"financial"`, `"agent"`, `"work"`, `"device"`, `"evidence"`, `"governance"`.

Each class has class-specific validation rules (see section below).

### `contract_name` (string, required)

PascalCase identifier. Must match `[A-Z][A-Za-z0-9]{2,63}`.

### `assets` (array, required, non-empty)

Each `AssetSpec`:
```json
{
  "name":   "<string>",
  "fields": ["<field_name>", ...]
}
```
Field names must be snake_case. At least one asset is required.

### `capabilities` (array, required for `work` contracts)

Declares the capability tokens the contract consumes or grants.
Standard capabilities: `GPU_COMPUTE`, `DEVICE_INHABIT`, `AGENT_SPAWN`,
`PROPOSAL_CREATE`, `MEMORY_WRITE`, `EVIDENCE_SUBMIT`.

Work contracts MUST declare at least one capability.

### `minimum_tier` (u8, default 0)

Minimum agent tier required to interact with this contract (0–5).

### `evidence` (object, required)

```json
{
  "required":  true,
  "type":      "<EvidenceKind>",
  "fields":    ["<field>", ...]
}
```

`EvidenceKind` values: `ComputeReceipt`, `DeviceAttestation`, `ZangbetoReceipt`,
`WitnessBundle`, `AgentLifecycle`, `WorkCompletion`, `GovernanceVote`.

When `required: false`, `type` and `fields` may be omitted.

### `witness_policy` (object, optional)

```json
{
  "quorum": <u8>,
  "types":  ["peer" | "device" | "agent" | "node"]
}
```

`quorum` = minimum number of witness signatures before settlement proceeds.
Omit for contracts that do not require external witnessing.

### `settlement` (object, required)

```json
{
  "currency":       "ASE" | "SUI" | "USDC",
  "fee_routing":    "6-pool" | "direct" | "dao-pool",
  "creator_share":  <f64>,
  "burn_share":     <f64>,
  "provider_share": <f64>
}
```

All shares are fractions (0.0–1.0). Validation rule: shares must sum ≤ 1.0.
Remainder flows to the ecosystem pool unless `fee_routing: "direct"`.

The `"6-pool"` routing follows the 8-pool ASE emission distribution, specifically
the 6 pools that contract fees flow to (excludes genesis pool and validator pool).

### `policy` (object, required)

Freeform key-value map for contract-specific behavioural policies:

| Common key | Type | Meaning |
|---|---|---|
| `deadline_enforcement` | bool | Auto-slash stake if deadline missed |
| `quality_threshold` | f64 | Min output quality score (0.0–1.0) for settlement |
| `esu_tithe` | f64 | Èṣù justice tithe on all settlements (canonical: 0.0369) |
| `fork_allowed` | bool | Agent may fork this contract's asset class |
| `private_execution` | bool | Work is sealed (Seal protocol) — output not public |
| `escalation_path` | string | On dispute: "council" | "peer-vote" | "auto-slash" |

### `lifecycle` (array of strings, required)

Ordered state labels forming the contract's state machine. First label is the
initial state; last is terminal. All transitions are sequential by default
unless a `policy.fork_allowed` creates branching.

---

## CONTRACT CLASSES — SCHEMA AND VALIDATION

### 1. `financial` — AsePool, treasury, staking

Additional required fields: none beyond base schema.

Validation:
- `settlement.currency` must be `"ASE"` for native financial contracts
- `evidence.required` should be `true` (Zàngbétò receipt on every flow)
- At least one asset must contain `balance` or `pool` in its field list

Typical lifecycle: `["OPEN", "FUNDED", "ACTIVE", "SETTLING", "CLOSED"]`

### 2. `agent` — AgentRegistry, reputation, identity

Validation:
- `assets` must contain a field named `agent_id`
- `capabilities` may be empty (agents don't always consume capabilities;
  they ARE the capability origin)
- `lifecycle` must include `"REGISTERED"` and `"DEREGISTERED"`

Typical lifecycle: `["CREATED", "REGISTERED", "ACTIVE", "SUSPENDED", "DEREGISTERED"]`

### 3. `work` — JobContract, GPU marketplace, task assignment

Validation:
- `capabilities` MUST be non-empty
- `evidence.required` MUST be `true`
- `settlement.provider_share` must be > 0.5 (provider does most of the work)
- `lifecycle` must contain `"ASSIGNED"`, `"EXECUTED"`, `"VERIFIED"`, `"SETTLED"`

Typical lifecycle: `["CREATED", "ASSIGNED", "ACCEPTED", "STARTED", "EXECUTED", "VERIFIED", "SETTLED"]`

### 4. `device` — DeviceRegistry, VCP binding, sensor mesh

Validation:
- `assets` must contain a field named `device_id`
- `evidence.type` must be `"DeviceAttestation"` when `evidence.required: true`
- `lifecycle` must include `"BOUND"` and `"UNBOUND"`

Typical lifecycle: `["DISCOVERED", "MANIFESTED", "BOUND", "ACTIVE", "SUSPENDED", "UNBOUND"]`

### 5. `evidence` — ZangbetoReceipt, WitnessBundle, ARP receipts

Validation:
- `assets` must contain a field named `receipt_hash`
- `settlement.fee_routing` should be `"direct"` (evidence contracts don't charge market fees)
- `lifecycle` must include `"SUBMITTED"` and `"VERIFIED"`

Typical lifecycle: `["SUBMITTED", "PENDING_WITNESS", "VERIFIED", "ARCHIVED"]`

### 6. `governance` — CouncilDAO, proposal voting, constitutional gates

Validation:
- `assets` must contain fields `proposal_id` and `proposer`
- `witness_policy.quorum` must be ≥ 7 (Council of 12 requires supermajority)
- `lifecycle` must include `"PROPOSED"`, `"VOTING"`, `"ENACTED"`, `"REJECTED"`

Typical lifecycle: `["PROPOSED", "SECONDED", "VOTING", "TALLYING", "ENACTED", "REJECTED"]`

---

## VALIDATION RULES (COMPLETE)

The OSO-IR validator (`omokoda-core/src/oso_ir.rs`) enforces:

| Rule | Error |
|---|---|
| `oso_ir_version` must be `"1.0"` | `unknown oso_ir_version: X` |
| `contract_class` must be a known class | `unknown contract_class: X` |
| `contract_name` must match `[A-Z][A-Za-z0-9]{2,63}` | `contract_name fails PascalCase rule` |
| `assets` must be non-empty | `assets cannot be empty` |
| `work` contracts: `capabilities` must be non-empty | `work contracts must declare at least one capability` |
| `work` contracts: `evidence.required` must be `true` | `work contracts require evidence` |
| `work` contracts: `settlement.provider_share > 0.5` | `work provider_share must exceed 0.5` |
| `governance` contracts: `witness_policy.quorum >= 7` | `governance quorum must be >= 7` |
| `evidence` contracts: assets must include `receipt_hash` field | `evidence contracts require receipt_hash asset field` |
| `settlement` shares must sum ≤ 1.0 | `settlement shares exceed 1.0` |
| `lifecycle` must be non-empty | `lifecycle cannot be empty` |
| `minimum_tier` must be 0–5 | `minimum_tier out of range` |

---

## COMPILER TARGETS

### Move (Sui / OSOVM L1)

The Move codegen emits:
- One Move `struct` per `AssetSpec`
- One `public entry fun` per lifecycle transition
- `CapabilityGrant` check at function entry for each declared capability
- `EvidenceCommitment` assert before settlement calls
- `transfer::transfer` to the provider address at settlement

### WASM

The WASM codegen emits:
- One `wasm-bindgen` struct per `AssetSpec`
- Policy checks as `require!()` guards
- Evidence as JS-side `Promise<Bytes>` resolved before `settle()`

### Native (Rust)

The Native codegen emits:
- One Rust struct with `serde` derives per `AssetSpec`
- `OsoIR::validate()` call at construction
- Direct ASE transfer via OSOVM `execute_opcode()`

---

## EXAMPLE: WorkContract (GPU Compute Marketplace)

```json
{
  "oso_ir_version": "1.0",
  "contract_class": "work",
  "contract_name": "GPUComputeMarketplace",
  "assets": [
    {
      "name": "ComputeJob",
      "fields": ["job_id", "creator", "budget_mist", "gpu_requirement_gb", "deadline_unix"]
    },
    {
      "name": "ComputeResult",
      "fields": ["job_id", "provider", "output_hash", "gpu_seconds", "completed_at"]
    }
  ],
  "capabilities": ["GPU_COMPUTE"],
  "minimum_tier": 2,
  "evidence": {
    "required": true,
    "type": "ComputeReceipt",
    "fields": ["gpu_seconds", "output_hash", "device_id", "model_hash"]
  },
  "witness_policy": {
    "quorum": 2,
    "types": ["peer", "device"]
  },
  "settlement": {
    "currency": "ASE",
    "fee_routing": "6-pool",
    "creator_share": 0.10,
    "burn_share": 0.05,
    "provider_share": 0.85
  },
  "policy": {
    "deadline_enforcement": true,
    "quality_threshold": 0.777,
    "esu_tithe": 0.0369,
    "escalation_path": "peer-vote"
  },
  "lifecycle": [
    "CREATED", "ASSIGNED", "ACCEPTED", "STARTED",
    "EXECUTED", "VERIFIED", "SETTLED"
  ]
}
```

---

## CHANGELOG

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-09-15 | Initial specification (Phase 21.1 / 21.3) |
