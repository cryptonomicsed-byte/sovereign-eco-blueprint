# Ọ̀ṢỌ́ Intermediate Representation (OSO-IR) Specification
# Version 1.0 — Phase 21 LOCKED
# Locked: 2026-09-24

---

## PURPOSE

The OSO-IR is the JSON-serialisable intermediate representation that bridges:

- **Source**: Ọ̀ṢỌ́ language (declarative, agent-native)
- **Target**: Move / WASM / Native contract backends

The compiler pipeline is:

```
Ọ̀ṢỌ́ source (.oso)
   → Ọ̀ṢỌ́-IR (this spec) ← validator gate (oso-ir crate)
      → Move codegen   (Sui / OSOVM L1)
      → WASM codegen   (CosmWasm model)
      → Native codegen (Rust ABCI handler)
```

Distinct from the OSOVM opcode IR in `oso-parser` (which is VM-execution level).
This IR operates at *contract semantics* level: what the contract IS, not how
opcodes execute step by step.

---

## RUST CRATE

`oso-ir` — part of the Omo-Koda2 workspace.

Public API surface:
```rust
pub use types::{
    OsoIr, ContractClass, AssetDef, CapabilityRef, ActionDef,
    EvidencePolicy, SettlementPolicy, WitnessPolicy, PolicyExpr,
    BackendTarget, IrError,
};
pub use validator::{validate, ValidationResult, ValidationError};
```

---

## DESIGN PRINCIPLES

| Principle | Detail |
|---|---|
| **Declarative** | IR describes *what*, not *how*. Backend chooses execution strategy. |
| **Backend-agnostic** | Same IR document compiles to Move, WASM, or Native unchanged. |
| **Security-explicit** | Capabilities are declared with tier requirements. |
| **Evidence-native** | Proof requirements are first-class IR fields. |
| **Sovereign-economics** | Fee routing and treasury tithe declared per contract. |
| **Content-addressed** | Every IR document has a BLAKE3 content hash. |

---

## TOP-LEVEL SCHEMA (`OsoIr`)

```json
{
  "ir_version":      "1.0",
  "contract_class":  "<ContractClass>",
  "name":            "<string>",
  "version":         "0.1.0",
  "assets":          [ <AssetDef>, ... ],
  "capabilities":    [ <CapabilityRef>, ... ],
  "actions":         [ <ActionDef>, ... ],
  "evidence":        <EvidencePolicy | null>,
  "settlement":      <SettlementPolicy | null>,
  "policy":          <WitnessPolicy | null>,
  "backend_targets": [ "<BackendTarget>", ... ],
  "metadata":        { "<key>": <value>, ... }
}
```

### `ir_version` (string, default `"1.0"`)
Current value: `"1.0"`.

### `contract_class` (enum, required)
One of: `"financial"` | `"agent"` | `"work"` | `"device"` | `"evidence"` | `"governance"`.

### `name` (string, required)
Human-readable contract name. Must not be empty or whitespace-only.

### `version` (string, default `""`)
SemVer contract version string.

### `assets` (array of `AssetDef`, default `[]`)
```json
{
  "name":        "<PascalCase>",
  "fields":      [ { "name": "<snake_case>", "field_type": "<string>", "required": true } ],
  "transferable": true,
  "divisible":   false
}
```
Asset names must be unique within a contract.

### `capabilities` (array of `CapabilityRef`, default `[]`)
```json
{
  "name":          "GPU_COMPUTE",
  "minimum_tier":  2,
  "required":      true
}
```
`minimum_tier` range: 0–5. Values > 5 are validation errors.

Standard capability names: `GPU_COMPUTE`, `DEVICE_INHABIT`, `AGENT_SPAWN`,
`PROPOSAL_CREATE`, `MEMORY_WRITE`, `EVIDENCE_SUBMIT`, `SIGN_TX`,
`STORAGE_WRITE`, `STORAGE_READ`.

### `actions` (array of `ActionDef`, default `[]`)
```json
{
  "name":          "submit_job",
  "requires":      [ <PolicyExpr>, ... ],
  "emits":         [ "JobSubmitted" ],
  "mutates_state": true,
  "vessel":        "Act"
}
```
- `requires`: preconditions — array of `PolicyExpr` (see below)
- `emits`: event/receipt type names emitted on success
- `vessel`: If-Script vessel this action maps to (optional; non-canonical values produce a warning)

Canonical If-Script vessels:
`Act`, `Oracle`, `Create`, `Destroy`, `Transfer`, `Observe`,
`Communicate`, `Compute`, `Store`, `Retrieve`, `Execute`, `Validate`,
`Govern`, `Prove`, `Attest`, `Sign`.

### `evidence` (`EvidencePolicy | null`, default `null`)
```json
{
  "required":       true,
  "evidence_type":  "ComputeReceipt",
  "minimum_count":  1
}
```
When `required: true`, `evidence_type` must be non-empty (validation error otherwise).
`minimum_count` must be ≥ 1.

### `settlement` (`SettlementPolicy | null`, default `null`)
```json
{
  "currency":     "ASE",
  "fee_routing":  "6-pool",
  "treasury_pct": 3.69
}
```
Known currencies: `ASE`, `DOPAMINE`, `SYNAPSE`, `SUI`, `USDC`.
Unknown currencies produce a warning (not an error — extensible).
`treasury_pct` must be in `[0, 100]`.

### `policy` (`WitnessPolicy | null`, default `null`)
```json
{
  "witness_quorum":    2,
  "quality_threshold": 90,
  "upgradeable":       false,
  "requires_council":  false
}
```

### `backend_targets` (array of `BackendTarget`, default `[]`)
Values: `"move"` | `"wasm"` | `"native"`.

### `metadata` (object, default `{}`)
Arbitrary JSON values. Common keys: `author`, `license`, `description`.

---

## `PolicyExpr` — precondition grammar

Tagged union (`"kind"` discriminator):

```json
{ "kind": "capability", "name": "GPU_COMPUTE" }
{ "kind": "principal",  "role": "provider" }
{ "kind": "numeric",    "field": "budget", "op": ">=", "value": 100 }
{ "kind": "proof",      "proof_type": "ComputeReceipt" }
{ "kind": "and",        "exprs": [ <PolicyExpr>, ... ] }
{ "kind": "or",         "exprs": [ <PolicyExpr>, ... ] }
{ "kind": "not",        "expr": <PolicyExpr> }
```

---

## CONTRACT CLASS VALIDATION RULES

| Rule | Classes | Severity |
|---|---|---|
| `name` must not be empty | all | error |
| Asset names must be unique | all | error |
| `capabilities[].minimum_tier` must be 0–5 | all | error |
| Action names must be unique | all | error |
| `evidence.evidence_type` required when `evidence.required=true` | all | error |
| `evidence.minimum_count` must be ≥ 1 | all | error |
| `settlement.treasury_pct` must be in [0,100] | all | error |
| `work` contracts: at least one action required | `work` | error |
| `governance` + `move`-only target: suggest `native` | `governance` | warning |
| `action.vessel` not in 16 canonical vessels | all | warning |
| `settlement.currency` not in known set | all | warning |

---

## CONTENT HASH

Every `OsoIr` document exposes:
```rust
pub fn content_hash(&self) -> String  // BLAKE3 hex of canonical JSON
```

---

## EXAMPLE IR DOCUMENTS

Six canonical examples live in `oso-ir/src/examples/mod.rs`:

1. `financial_ase_pool()` — `ContractClass::Financial`, ASE pool, 6-pool routing, 3.69% tithe
2. `agent_registry()` — `ContractClass::Agent`, agent registration with Nostr identity
3. `work_gpu_compute_job()` — `ContractClass::Work`, GPU compute with ComputeReceipt evidence
4. `device_registry()` — `ContractClass::Device`, VCP device binding, tier-2
5. `evidence_zangbeto_receipt()` — `ContractClass::Evidence`, Zàngbétò receipt contract
6. `governance_council_dao()` — `ContractClass::Governance`, 24-sector Council DAO

---

## COMPILER TARGETS

### Move (Sui / OSOVM L1)
- One Move `struct` per `AssetDef`
- One `public entry fun` per action
- `CapabilityGrant` check at function entry
- `EvidenceCommitment` assert before settlement
- `transfer::transfer` to provider at settlement

### WASM (CosmWasm model)
- One `wasm-bindgen` struct per `AssetDef`
- Policy checks as `require!()` guards
- Evidence resolved as `Promise<Bytes>` before `settle()`
- Ọ̀ṢỌ́ host interfaces for storage, identity, receipts

### Native (Rust ABCI)
- One Rust struct with `serde` derives per `AssetDef`
- `validate()` call at construction
- Direct ASE transfer via OSOVM `execute_opcode()`
- ABCI `DeliverTx` handler per action

---

## CHANGELOG

| Version | Date | Notes |
|---|---|---|
| 1.0-draft | 2026-09-15 | Initial draft (Phase 21.1/21.3) |
| 1.0-locked | 2026-09-24 | Phase 21.4 lock — matches oso-ir crate types exactly |
