# If-Script ↔ Ọ̀ṢỌ́ Boundary Specification
**Status: LOCKED 2026-09-15**

This document defines exactly where If-Script ends and Ọ̀ṢỌ́ begins, and how the
two languages interoperate. It is the canonical reference for Phase 22.3 and the
foundation for the oso-compiler pipeline (Phase 26.2).

---

## Two Languages, One Cognitive Loop

```
If-Script  →  WHAT / WHY (policy, divination, ritual)
Ọ̀ṢỌ́       →  HOW      (state mutation, compute, economy)
```

If-Script is the **policy and divination layer** — it evaluates Odù archetypes,
hermetic gate conditions, ritual sequences, and prescriptions. Its output is a
*decision* or *intent*, not an action.

Ọ̀ṢỌ́ is the **execution layer** — it takes that decision and emits concrete VM
instructions (IrInstructions) that mutate state, transfer Àṣẹ, read/write
storage, or fire agent actions.

Neither language subsumes the other. An agent cannot execute Ọ̀ṢỌ́ without first
passing through If-Script's gate-evaluation; If-Script cannot act without
delegating to Ọ̀ṢỌ́ for state changes.

---

## Boundary Contract

### Rule 1 — If-Script owns the WHY layer

If-Script `RitualDef` and `OduDef` compile to a **decision vector**:

```rust
pub struct IfDecision {
    /// The selected Odù archetype (0..255)
    pub odu_index: u8,
    /// Gate scores from hermetic evaluation (0.0..1.0 per gate)
    pub gate_scores: Vec<f32>,
    /// Chosen ritual name (becomes the Ọ̀ṢỌ́ call target)
    pub ritual: String,
    /// Arguments to pass to the Ọ̀ṢỌ́ entry point
    pub params: serde_json::Value,
}
```

If-Script never emits `IrInstruction` directly. It emits `IfDecision`.

### Rule 2 — Ọ̀ṢỌ́ owns the HOW layer

The Ọ̀ṢỌ́ entry point mapped to `IfDecision.ritual` receives `params` and
compiles to an `IrProgram` (Vec<IrInstruction>) for OSOVM execution.

Every Ọ̀ṢỌ́ attribute (`@EMIT_ASE`, `@STORE_BLOB`, etc.) maps to a OSOVM
opcode byte. No Ọ̀ṢỌ́ attribute may query an Odù oracle — that lives in If-Script.

### Rule 3 — Gate alignment flows one way

```
If-Script gate_scores → gate_alignment float
gate_alignment → Ọ̀ṢỌ́ context (read-only)
Ọ̀ṢỌ́ must NOT write back to gate_scores
```

The multiplier formula: `m = 0.8 + (hermetic_balance × 0.25) + (gate_alignment × 0.15)`
is computed by the If-Script runtime BEFORE Ọ̀ṢỌ́ executes. Ọ̀ṢỌ́ receives `m` as a
constant; it cannot change it.

### Rule 4 — Invocation protocol

The runtime invocation sequence:

1. **If-Script**: evaluate `OduDef` + `RitualDef` → produce `IfDecision`
2. **If-Script → OSOVM bridge**: call `oso_dispatch(decision: IfDecision) → IrProgram`
3. **Ọ̀ṢỌ́ parser** (oso-parser crate): source → tokens → IrInstructions
4. **OSOVM executor**: run IrProgram, emit ActionReceipt

```
 IfaScript::compile(source)
     └─> [IfDecision]
           └─> OsoDispatch::dispatch(decision)
                 └─> oso_parser::compile(oso_source)
                       └─> [IrProgram]
                             └─> OSOVM::execute(program)
                                   └─> ActionReceipt
```

### Rule 5 — Forbidden crossings

| Forbidden | Reason |
|-----------|--------|
| Ọ̀ṢỌ́ calling `get_odu()` | Divination is If-Script's domain |
| If-Script calling `@EMIT_ASE` | Economy ops are Ọ̀ṢỌ́'s domain |
| Ọ̀ṢỌ́ modifying `gate_scores` | Gate eval is one-way before execution |
| If-Script emitting `IrInstruction` | Bypass of execution contract |

---

## Language Domains (reference)

### If-Script owns:
- Odù archetype selection (256-element grid, `get_odu(index)`)
- Hermetic gate evaluation (7 gates → balance score)
- Ritual definitions (`@ritual`, `@attribute`, `@prescription`)
- Policy conditions (`@condition`, `@unless`)
- Memory retrieval queries (Mandelbrot/REM)
- Goal Genesis inputs: Genesis₀, Odù, HermeticDNA

### Ọ̀ṢỌ́ owns:
- Agent state mutation (`@STORE`, `@LOAD`)
- Economy operations (`@EMIT_ASE`, `@BURN_ASE`, `@TRANSFER_ASE`)
- Compute dispatch (`@GPU_CONTRIB`, `@SIM_STEP`)
- Storage operations (`@STORE_BLOB`, `@SEAL_DATA`)
- Lifecycle control (`@AGENT_BIRTH`, `@AGENT_ACT`)
- Governance execution (`@PROPOSE`, `@VOTE`, `@EXECUTE`)

### Shared / negotiated:
- `@AGENT_THINK` — If-Script provides the goal context; Ọ̀ṢỌ́ executes the thinking step
- `@DNA_BIND` — birth-time only, initiated by If-Script ritual but executed by Ọ̀ṢỌ́

---

## Compiler Integration Point

In the `oso-compiler` crate (Phase 26.2), the dispatch function is:

```rust
pub fn oso_dispatch(decision: &IfDecision, ritual_registry: &RitualRegistry)
    -> OsoResult<IrProgram>
{
    let oso_source = ritual_registry.get(&decision.ritual)?;
    let context = CompileContext {
        gate_alignment: decision.gate_scores.iter().sum::<f32>() / 7.0,
        params: decision.params.clone(),
    };
    oso_parser::compile_with_context(oso_source, &context)
}
```

`RitualRegistry` maps ritual names → Ọ̀ṢỌ́ source strings.
`CompileContext` injects `gate_alignment` and `params` as compile-time constants.

---

## File Locations

| Component | Location |
|-----------|----------|
| If-Script compiler | `If-Script/src/compiler/` |
| If-Script AST | `If-Script/src/compiler/ast.rs` |
| IfDecision type | `Omo-Koda2/omokoda-core/src/decision.rs` (to be created Phase 26.2) |
| Ọ̀ṢỌ́ parser | `Omo-Koda2/oso-parser/` |
| Ọ̀ṢỌ́ compiler | `Omo-Koda2/oso-compiler/` (Phase 26.2) |
| OSOVM executor | `OSOVM/src/` (Julia; Rust ABCI planned Phase 20) |
| Opcode table | `OSOVM/src/opcodes.jl` + `Omo-Koda2/oso-parser/src/ir.rs` |
