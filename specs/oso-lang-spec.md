# Ọ̀ṢỌ́ Language Specification
# Version 1.0 — Phase 22 LOCKED
# Locked: 2026-09-24

---

## OVERVIEW

Ọ̀ṢỌ́ is the agent-native dApp expression language for the sovereign OS.
It is NOT another Solidity clone. It describes **what a contract is** in sovereign OS
terms: assets, capabilities, actions, evidence, and settlement — not low-level
EVM mechanics.

Ọ̀ṢỌ́ source (`.oso` files) compiles to **Ọ̀ṢỌ́-IR** (see `oso-ir-spec.md`),
which then compiles to Move / WASM / Native backends.

---

## FOUR SUB-LANGUAGES

| Sub-language | Description | Maps to IR field |
|---|---|---|
| **Declaration** | `dapp Name { }` top-level container | `name`, `contract_class` |
| **Asset language** | `asset Name { field: type }` | `assets[]` |
| **Policy language** | `require expr` conditions | `actions[].requires` (PolicyExpr) |
| **Agent interface** | `action name(args) { }` body | `actions[]` |

---

## GRAMMAR (PEG notation)

```peg
// Top level
Program     <- WS* DappDecl WS* EOF
DappDecl    <- 'dapp' WS+ Name WS* '{' WS* DappBody WS* '}'
DappBody    <- DappItem*
DappItem    <- ClassDecl / AssetDecl / CapDecl / ActionDecl
             / EvidenceDecl / SettlementDecl / WitnessDecl / MetaDecl

// Contract class
ClassDecl   <- 'class' WS+ ClassKind SEMI?
ClassKind   <- 'financial' / 'agent' / 'work' / 'device' / 'evidence' / 'governance'

// Assets
AssetDecl   <- 'asset' WS+ Name WS* '{' WS* FieldList WS* '}' SEMI?
FieldList   <- FieldDecl*
FieldDecl   <- Name WS* ':' WS* TypeExpr SEMI?
TypeExpr    <- 'string' / 'u64' / 'u32' / 'bool' / 'hash' / 'address' / Name

// Capabilities
CapDecl     <- 'capability' WS+ CapName CapOpts? SEMI?
CapOpts     <- '{' WS* CapOpt* WS* '}'
CapOpt      <- ('tier' WS* ':' WS* TierLit / 'required' WS* ':' WS* BoolLit) SEMI?
TierLit     <- 'T' [0-5]
CapName     <- [A-Z][A-Z0-9_]*

// Actions
ActionDecl  <- 'action' WS+ Name WS* '(' WS* ParamList WS* ')' WS* ActionBody? SEMI?
ParamList   <- (Name (',' WS* Name)*)?
ActionBody  <- '{' WS* ActionStmt* WS* '}'
ActionStmt  <- RequireStmt / PayStmt / EmitStmt / VesselStmt
RequireStmt <- 'require' WS+ PolicyExpr SEMI?
PayStmt     <- 'pay' WS+ Name WS+ 'from' WS+ Name SEMI?
EmitStmt    <- 'emit' WS+ Name SEMI?
VesselStmt  <- 'vessel' WS+ VesselName SEMI?
VesselName  <- 'Act' / 'Oracle' / 'Create' / 'Destroy' / 'Transfer' / 'Observe'
             / 'Communicate' / 'Compute' / 'Store' / 'Retrieve' / 'Execute'
             / 'Validate' / 'Govern' / 'Prove' / 'Attest' / 'Sign'

// Policy expressions
PolicyExpr  <- OrExpr
OrExpr      <- AndExpr ('||' WS* AndExpr)*
AndExpr     <- NotExpr ('&&' WS* NotExpr)*
NotExpr     <- '!' WS* NotExpr / Atom
Atom        <- '(' WS* PolicyExpr WS* ')'
             / 'capability' '(' WS* CapName WS* ')'
             / 'principal' '.' Role
             / 'proof' '.' ('valid' / 'accepted')
             / 'evidence' '.' ('accepted' / 'submitted')
             / FieldRef WS* CompOp WS* Value
Role        <- 'authorized' / 'provider' / 'creator' / 'owner' / Name
FieldRef    <- Name ('.' Name)*
CompOp      <- '>=' / '<=' / '>' / '<' / '==' / '!='
Value       <- Number / StringLit / BoolLit / Name

// Evidence block
EvidenceDecl <- 'evidence' WS* '{' WS* EvidenceOpt* WS* '}' SEMI?
EvidenceOpt  <- ('required' WS* ':' WS* BoolLit / 'type' WS* ':' WS* Name
              / 'minimum_count' WS* ':' WS* Number) SEMI?

// Settlement block
SettlementDecl <- 'settlement' WS* '{' WS* SettlementOpt* WS* '}' SEMI?
SettlementOpt  <- ('currency' WS* ':' WS* CurrencyName
               / 'fee_routing' WS* ':' WS* StringLit
               / 'treasury_pct' WS* ':' WS* Number) SEMI?
CurrencyName   <- 'ASE' / 'DOPAMINE' / 'SYNAPSE' / 'SUI' / 'USDC'

// Witness policy block
WitnessDecl <- 'witness' WS* '{' WS* WitnessOpt* WS* '}' SEMI?
WitnessOpt  <- ('quorum' WS* ':' WS* Number / 'upgradeable' WS* ':' WS* BoolLit
             / 'requires_council' WS* ':' WS* BoolLit) SEMI?

// Metadata
MetaDecl    <- 'meta' WS* '{' WS* MetaOpt* WS* '}' SEMI?
MetaOpt     <- Name WS* ':' WS* Value SEMI?

// Primitives
Name        <- [a-zA-Z_][a-zA-Z0-9_]*
Number      <- [0-9]+ ('.' [0-9]+)?
StringLit   <- '"' [^"]* '"'
BoolLit     <- 'true' / 'false'
WS          <- [ \t\n\r] / Comment
Comment     <- '//' (!'\n' .)* '\n'
SEMI        <- WS* ';' WS*
```

---

## EXAMPLE SYNTAX — ALL 6 CONTRACT CLASSES

### 1. `financial` — ASE Pool

```oso
dapp AsePool {
    class financial

    asset Pool {
        pool_id:   string
        balance:   u64
        owner:     address
    }

    capability SIGN_TX
    capability STORAGE_WRITE

    action deposit(amount) {
        require principal.authorized
        require amount > 0
        vessel Store
        emit PoolDeposited
    }

    action withdraw(amount) {
        require principal.owner
        require amount <= balance
        vessel Transfer
        emit PoolWithdrawn
    }

    evidence {
        required:      true
        type:          ZangbetoReceipt
        minimum_count: 1
    }

    settlement {
        currency:     ASE
        fee_routing:  "6-pool"
        treasury_pct: 3.69
    }
}
```

### 2. `agent` — Agent Registry

```oso
dapp AgentRegistry {
    class agent

    asset AgentRecord {
        agent_id:  string
        nostr_pub: string
        tier:      u32
        born_at:   u64
    }

    action register(agent_id, nostr_pub) {
        require principal.authorized
        vessel Create
        emit AgentRegistered
    }

    action deregister(agent_id) {
        require principal.owner
        vessel Destroy
        emit AgentDeregistered
    }

    action update_tier(agent_id, new_tier) {
        require principal.authorized
        require new_tier <= 5
        vessel Govern
        emit TierUpdated
    }

    settlement {
        currency:     ASE
        fee_routing:  "direct"
        treasury_pct: 3.69
    }
}
```

### 3. `work` — GPU Compute Marketplace

```oso
dapp GpuComputeMarketplace {
    class work

    asset ComputeJob {
        job_id:     string
        creator:    address
        budget:     u64
        gpu_memory: u32
        deadline:   u64
    }

    asset ComputeResult {
        job_id:      string
        provider:    address
        output_hash: hash
        gpu_seconds: u64
    }

    capability GPU_COMPUTE {
        tier: T2
        required: true
    }

    action submit_job(job) {
        require principal.authorized
        require budget > 0
        vessel Create
        emit JobSubmitted
    }

    action accept_job(job) {
        require capability(GPU_COMPUTE)
        vessel Act
        emit JobAccepted
    }

    action submit_result(job, result) {
        require capability(GPU_COMPUTE)
        require proof.valid
        vessel Compute
        emit ResultSubmitted
    }

    action settle(job) {
        require evidence.accepted
        pay provider from budget
        vessel Transfer
        emit JobSettled
    }

    evidence {
        required:      true
        type:          ComputeReceipt
        minimum_count: 1
    }

    settlement {
        currency:     ASE
        fee_routing:  "6-pool"
        treasury_pct: 3.69
    }

    witness {
        quorum: 2
    }
}
```

### 4. `device` — Device Registry

```oso
dapp DeviceRegistry {
    class device

    asset DeviceRecord {
        device_id:  string
        agent_id:   string
        manifested: u64
        capability: string
    }

    capability DEVICE_INHABIT {
        tier: T1
    }

    action bind(device_id, agent_id) {
        require capability(DEVICE_INHABIT)
        vessel Attest
        emit DeviceBound
    }

    action unbind(device_id) {
        require principal.owner
        vessel Validate
        emit DeviceUnbound
    }

    evidence {
        required:      true
        type:          DeviceAttestation
        minimum_count: 1
    }

    settlement {
        currency:     ASE
        fee_routing:  "direct"
        treasury_pct: 3.69
    }
}
```

### 5. `evidence` — Zàngbétò Receipt Contract

```oso
dapp ZangbetoReceipt {
    class evidence

    asset Receipt {
        receipt_hash: hash
        agent_id:     string
        action_name:  string
        timestamp:    u64
        payload_hash: hash
    }

    action submit_receipt(receipt) {
        require proof.valid
        vessel Attest
        emit ReceiptSubmitted
    }

    action verify_receipt(receipt) {
        require evidence.submitted
        vessel Prove
        emit ReceiptVerified
    }

    action archive_receipt(receipt) {
        require evidence.accepted
        vessel Store
        emit ReceiptArchived
    }

    evidence {
        required:      true
        type:          ZangbetoReceipt
        minimum_count: 1
    }

    settlement {
        currency:     ASE
        fee_routing:  "direct"
        treasury_pct: 3.69
    }
}
```

### 6. `governance` — Council DAO

```oso
dapp CouncilDao {
    class governance

    asset Proposal {
        proposal_id: string
        proposer:    address
        title:       string
        sector:      u32
        created_at:  u64
    }

    asset Vote {
        proposal_id: string
        voter:       address
        in_favor:    bool
        voted_at:    u64
    }

    capability PROPOSAL_CREATE {
        tier: T3
    }

    action create_proposal(proposal) {
        require capability(PROPOSAL_CREATE)
        require principal.authorized
        vessel Govern
        emit ProposalCreated
    }

    action vote(proposal, in_favor) {
        require principal.authorized
        vessel Validate
        emit VoteCast
    }

    action enact(proposal) {
        require evidence.accepted
        vessel Execute
        emit ProposalEnacted
    }

    action reject(proposal) {
        vessel Govern
        emit ProposalRejected
    }

    evidence {
        required:      true
        type:          WitnessBundle
        minimum_count: 7
    }

    settlement {
        currency:     ASE
        fee_routing:  "dao-pool"
        treasury_pct: 3.69
    }

    witness {
        quorum:           7
        requires_council: true
    }
}
```

---

## IF-SCRIPT ↔ Ọ̀ṢỌ́ BOUNDARY SPECIFICATION (Phase 22.3)

### Core separation

| Dimension | Ọ̀ṢỌ́ | If-Script |
|---|---|---|
| **Question answered** | *What is this contract?* | *When / how does the agent act?* |
| **Layer** | Contract declaration (compile-time) | Agent behavior (runtime) |
| **Author** | Developer writing the dApp | Agent's policy / DNA / context |
| **Scope** | On-chain logic, capabilities, assets | Agent's tool selection, vessel routing, gate alignment |
| **Output** | `OsoIr` document → Move/WASM/Native | `VesselAlignment` decision → tool call approval |
| **Temporal** | Fixed at compile/deploy time | Evaluated on every agent turn |

### How they interact

```
Developer writes:        agent evaluates:
  .oso source     →     OsoIr (static)
       ↓                     ↓
  oso-compiler           If-Script gate
       ↓                     ↓
  Move/WASM/Native     vessel alignment check
       ↓                     ↓
  deployed contract    runtime tool call approval
```

**Ọ̀ṢỌ́ declares** the `vessel` for each action (e.g. `vessel Compute`).
**If-Script verifies** at runtime that the agent's chosen vessel matches its DNA alignment
and capability tier before the tool call executes.

### Overlap: `require` expressions

`require` clauses in `.oso` source become `PolicyExpr` entries in `OsoIr.actions[].requires`.

At **compile time**: the Move/WASM/Native backend enforces these as on-chain preconditions.

At **runtime**: the If-Script gate reads the same `PolicyExpr` to decide whether to
present the action to the LLM's tool list at all (pre-selection hermetic gate).

This means: **policy is declared once in Ọ̀ṢỌ́, enforced twice** — once on-chain by
the contract backend, once in-process by the If-Script gate.

### Canonical boundary

```
                    ┌─── Ọ̀ṢỌ́ territory ─────────────────────┐
                    │                                           │
  .oso source → parser → OsoIr → backend compiler → deployed  │
                                                               │
                    └───────────────────────────────────────────┘
                    ┌─── If-Script territory ──────────────────┐
                    │                                           │
  agent turn → DNA context → vessel alignment →                │
  → gate check → tool list → LLM → tool call → receipt        │
                    │                                           │
                    └───────────────────────────────────────────┘
                         ↑
         shared: PolicyExpr from OsoIr.actions[].requires
```

### Non-overlap (explicit)

| Topic | NOT If-Script | NOT Ọ̀ṢỌ́ |
|---|---|---|
| Which tool the LLM picks | ✓ If-Script only | — |
| Asset field types | — | ✓ Ọ̀ṢỌ́ only |
| Backend compilation target | — | ✓ Ọ̀ṢỌ́ only |
| DNA gate_alignment score | ✓ If-Script only | — |
| Treasury percentage | — | ✓ Ọ̀ṢỌ́ only |
| Vessel name in action | both (declared in Ọ̀ṢỌ́, checked by If-Script) | — |

---

## COMPILER PIPELINE

```
.oso file
  │
  ▼
DappLexer      → Vec<DappToken>         (token.rs)
  │
  ▼
DappParser     → DappAst                (parser.rs)
  │
  ▼
AstToIr        → OsoIr                  (lower.rs)
  │
  ▼
oso_ir::validate() → ValidationResult  (oso-ir crate)
  │
  ▼
backend: oso-move / oso-wasm / oso-deployer
```

Implementation lives in `oso-compiler/src/dapp/`.

---

## CHANGELOG

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-09-24 | Phase 22 — grammar + examples + If-Script boundary LOCKED |
