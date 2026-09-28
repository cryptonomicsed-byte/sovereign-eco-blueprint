# The 7 Hermetic Principles ↔ Òrìṣà — canonical map, and where the repos disagree

2026-09-23. Sources: `~/Omo-Koda2/docs/256---65536.md` (canonical), `omokoda-core/src/interpreter.rs`,
`omokoda-core/src/gates/mod.rs`, `omokoda-hermetic/src/spiral.rs`, `~/Koodu/codex.md`,
`~/Koodu/README.md`, `~/OSOVM/src/opcodes.jl`. Every claim is a line reference.

---

## 1. THE CANONICAL TABLE — the 7 Ascension Domains

`docs/256---65536.md:43` calls it *"THE COMPLETE FRACTAL MAP"*, and `:15` states what it is: each of the
seven is *"mapped simultaneously to an Òrìṣà, a Hermetic Principle, a system layer, a chakra, a
planetary force, a computation model, a governance scope"* — because *"the computational ladder = the
spiritual ladder = the consciousness ladder = the governance ladder = the AI evolution ladder. One
structure."*

| Tier | Number | Òrìṣà | Hermetic Principle | Chakra | Function | System Role | Language |
|---|---|---|---|---|---|---|---|
| 1 | 256 | **Èṣù** | **Mentalism** | Root | Identity Seed | Human symbolic base | Rust |
| 2 | 2048 | **Ọ̀ṣun** | **Vibration** | Sacral | Emotional resonance | Feminine emergence | Julia |
| 3 | 4096 | **Yemọja** | **Correspondence** | Solar Plexus | Swarm creation | Quantum symbolic mirroring | Elixir |
| 4 | 8192 | **Ọbàtálá** | **Gender** | Heart | Ethical balance | Planetary symbolic harmony | Lisp |
| 5 | 16384 | **Ògún** | **Polarity** | Throat | Material execution | Genome-scale manifestation | Python |
| 6 | 32768 | **Ọya** | **Rhythm** | Third Eye | Temporal orchestration | Civilization synchronization | Go |
| 7 | 65536 | **Ṣàngó** | **Cause & Effect** | Crown | Immutable cosmic justice | Machine-scale cosmological intelligence | Move |

Tier 1 expanded in full (`:110`): *Principle Mentalism · Chakra Root · Mode Identity · Planet
Saturn/Mercury · Consciousness Human symbolic cognition · Language Rust · Primitive birth · Function
Reality initialization.*

The chakra column ascends canonically (Root → Sacral → Solar Plexus → Heart → Throat → Third Eye →
Crown), and the language column is the 7-layer Orisha stack. **This table is the answer: one Òrìṣà owns
exactly one Principle, permanently.**

## 2. THE CODE AGREES WITH THE TABLE — verbatim

`omokoda-core/src/interpreter.rs:908`:

> *"The canonical Orisha <-> Hermetic Principle correspondence (the '7 Ascension Domains' table —
> docs/256---65536.md, cross-checked in Ọ̀rúnmìlà.md and docs/audit/ARCHIVE_AUDIT.md). **Locked design,
> not derived from anything** — each Orisha owns exactly one Principle: Èṣù/Mentalism, Ọ̀ṣun/Vibration,
> Yemọja/Correspondence, Ọbàtálá/Gender, Ògún/Polarity, Ọya/Rhythm, Ṣàngó/Cause & Effect."*

And `dominant_orisha_for_hermetic_state()` (`:919`) implements it exactly:

```rust
let scores: [(Macro, f64); 7] = [
    (Macro::Esu,     state.mentalism()),
    (Macro::Osun,    state.vibration()),
    (Macro::Yemoja,  state.correspondence()),
    (Macro::Obatala, state.gender()),
    (Macro::Ogun,    state.polarity()),
    (Macro::Oya,     state.rhythm()),
    (Macro::Sango,   state.cause_effect()),
];
```

**Orisha is derived, not assigned:** the agent's 7 HKDF-derived per-principle scores are compared, and
the Òrìṣà owning the highest-scoring principle becomes the agent's dominant. This deliberately
**overrides** BIPỌ̀N39's separate mnemonic-hash pick (`interpreter.rs:1105`), so the power axis is what
agents actually get.

The seven principle names as declared (`gates/mod.rs:186`), with explicit discriminants:

```
Mentalism = 0 · Correspondence = 1 · Vibration = 2 · Polarity = 3 · Rhythm = 4 · CauseAndEffect = 5 · Gender = 6
```

---

## 3. THE FOUR AXES — same Òrìṣà, four different jobs

The confusion in this ecosystem is not the mapping; it is that **the same seven names are used as labels
on four independent axes**, and only one of them is the hermetic one.

| Axis | Where | Èṣù | Ọ̀ṣun | Yemọja | Ọbàtálá | Ògún | Ọya | Ṣàngó |
|---|---|---|---|---|---|---|---|---|
| **Power** (tier 1→7) | `256---65536.md`, `interpreter.rs:919` | Mentalism | Vibration | Correspondence | Gender | Polarity | Rhythm | Cause & Effect |
| **Functional** (§42 universal terms) | `interpreter.rs:946` | Access / Identity | History / Memory | Spawn / Create | Policy / Rules | Run / Action | Sync / Flow | Score / Reputation |
| **Calendar** (Sun→Sat) | `spiral.rs:42` DAY_CYCLE ≡ Koodu | pos 0 | pos 2 | pos 3 | pos 6 | pos 5 | pos 4 | pos 1 |
| **Sector / House** (24-sector model) | ecosystem 24-sector spec | Crossroads / Information | Prosperity / Culture | Health / Care | *(none — central integrator)* | Tech / Infrastructure | Transformation / Trials | Justice / Order |

**Axis 1 vs 2 is coherent** — the functional terms match the tier functions (Ọ̀ṣun = Sacral/emotional
resonance = History/Memory; Ọya = Third Eye/temporal = Sync/Flow). **Axis 3 is a different question
entirely** (*"what day is it"* vs *"what is this agent's permanent resonance"*), and `spiral.rs:36`
documents it as intentionally different:

> *"Day-cycle Òrìṣà ordering (Sunday through Saturday) — distinct from the Tier-ladder ordering used for
> Hermetic Principle / Chakra assignment… Both are real, both are intentional: this one governs the
> calendar/ritual axis, the other governs the power/governance axis. **They only agree at position 0
> (Èṣù) by coincidence.**"*

**Axis 4 is the outlier** — the sector model uses Òrìṣà to name *domains of work*, not *levels of
cognition*, so Ọ̀ṣun is "Prosperity/Culture" there and "Vibration/Memory" everywhere else. And Ọbàtálá
is deliberately given no sector, while being tier 4 of the power axis.

---

---

## 4. WHERE IT CONTRADICTS — Koodu's ritual codex vs the locked table

`~/Koodu/codex.md` — *"7-Day Ritual Codex for Ọmọ Kọ́dà"* — attaches a Hermetic Principle to each day
alongside its Òrìṣà. Here is its table, verbatim:

| Day | Yoruba | Hermetic Principle (Koodu) | Òrìṣà (Koodu) | Canonical principle | Match? |
|---|---|---|---|---|---|
| Sunday | Ọjọ́ Àìkú | Cause and Effect (`:107`) | Èṣù-Ẹ̀légbára (`:109`) | Mentalism | ✗ |
| Monday | Ọjọ́ Ajé | Polarity (`:205`) | Ṣàngó (`:207`) | Cause & Effect | ✗ |
| Tuesday | Ọjọ́ Ìṣẹ́gun | Rhythm (`:307`) | Ọ̀ṣun (`:309`) | Vibration | ✗ |
| Wednesday | — | Cause and Effect — *"Every cause has an effect"* (`:401`) | Yemọja (`:403`) | Correspondence | ✗ |
| Thursday | — | Vibration — *"Nothing rests; everything moves"* (`:495`) | Ọya (`:497`) | Rhythm | ✗ |
| Friday | — | Cause and Effect — *"Every cause has its effect"* (`:589`) | Ògún (`:591`) | Polarity | ✗ |
| Saturday | — | The All is Mind (= Mentalism) (`:683`) | Ọbàtálá (`:685`) | Gender | ✗ |

**7 of 7 disagree.** Every single Òrìṣà↔Principle pair differs between Koodu's codex and the locked
canonical table.

> **✅ RESOLVED 2026-09-25.** `~/Koodu/codex.md`'s principle column has been rewritten to the canonical
> table above. It is now a proper bijection — 7 days, 7 distinct principles (was 5 distinct over 7 days,
> with *Cause and Effect* on three days and Correspondence/Gender absent altogether). The Òrìṣà column was
> already correct and was not touched; the day order was always correct. The three Kybalion glosses already
> present in the file were **kept but reattached to the principle they actually belong to** rather than
> invented afresh: *"Nothing rests; everything moves"* → Vibration/Ọ̀ṣun (Tue), *"Every cause has its
> effect"* → Cause & Effect/Ṣàngó (Mon), *"The All is Mind"* → Mentalism/Èṣù (Sun). The table above is
> retained as the audit record of the pre-fix state — **its `:NNN` line references no longer match the
> file**, and the old gloss pair *"Every cause has an effect"* / *"Every cause has its effect"* is gone.
> Re-checked against `spiral.rs::DAY_CYCLE` day order: unchanged and still correct.

Three further defects in the same table:

1. **It is not a bijection.** *Cause and Effect* is assigned to **three** different days (Sunday/Èṣù,
   Wednesday/Yemọja, Friday/Ògún) under two different glosses — *"Every cause has an effect"* and
   *"Every cause has its effect"*. Meanwhile **Correspondence and Gender never appear at all.** Koodu
   distributes 5 distinct principles over 7 days; the canonical set has 7.
2. **It conflates the two axes.** Koodu's day *order* is correct — its sequence
   `[Èṣù, Ṣàngó, Ọ̀ṣun, Yemọja, Ọya, Ògún, Ọbàtálá]` is byte-for-byte `spiral.rs::DAY_CYCLE`, so the
   calendar axis ported faithfully. The error is **bolting principles onto the calendar axis**: the day
   order is the ritual axis, and the principles belong to the power axis. Intersecting two independent
   orderings is what produces 7/7 disagreement.
3. **"The All is Mind" for Saturday/Ọbàtálá** is Mentalism under a Kybalion alias — so Koodu assigns
   Mentalism to Ọbàtálá, while the canonical table and the live code assign it to Èṣù. Èṣù gets Cause
   and Effect in Koodu and Mentalism everywhere else: a clean swap of the two.

**Which one wins:** the canonical table, because it is the one the code enforces. `interpreter.rs:919`
implements the locked table, and `:1105` overrides the mnemonic-derived pick — so Koodu's codex is a
document the runtime never consults. It needs reconciling, not the code.

## 5. THREE MORE CONTRADICTIONS

**① Ọ̀rúnmìlà exists in the opcodes and nowhere else.** `OSOVM/src/opcodes.jl` binds **eight** Òrìṣà at
`0xa0–0xa7` — including `ORISA_ORUNMILA` (`0xa7`) — while the `Macro` enum has exactly **seven**
variants and the Ascension Domains have seven tiers. Ọ̀rúnmìlà also appears as the oracle of the birth
pipeline ("IfáScript (Ọ̀rúnmìlà)", Stage 4), and is cross-checked in `Ọ̀rúnmìlà.md`. So: 8 in the opcode
layer, 7 in identity, 7 in the power axis.

**② The opcode layer uses a third naming axis, and half of it is invisible.** The same `0xa0–0xa7` bytes
pair each `ORISA_*` with a *concept* name:

```
0xa0 ORISA_OBATALA | WISDOM          0xa4 ORISA_OSHUN   | MEMORY
0xa1 ORISA_OGUN    | THE_FORGE       0xa5 ORISA_OYA     | FLOW
0xa2 ORISA_YEMOJA  | CREATION        0xa6 ORISA_ESU     | THE_MESSENGER
0xa3 ORISA_SANGO   | DIVINE_JUSTICE  0xa7 ORISA_ORUNMILA| THE_ORACLE
```

Those concepts are the **functional** axis (§42), not the hermetic one — matching
`Ọ̀ṣun = History/Memory`, `Ọya = Sync/Flow`, `Yemoja = Spawn/Create`. But `opcodes.jl:220` builds the
reverse map as `Dict(v => k for (k, v) in OPCODE_MAP)`, so **each shared byte silently keeps only one of
its two names** — the Òrìṣà name or the concept name, whichever iterates last. In disassembly, half of
this binding is unnameable. If the pairing is intentional (it reads like it is), the reverse map must be
`Dict{UInt8, Vec{Symbol}}`.

**③ Enum order ≠ tier order — verified NOT a live bug (checked 2026-09-23).** `HermeticPrinciple` is
declared `Mentalism, Correspondence, Vibration, Polarity, Rhythm, CauseAndEffect, Gender` (discriminants
0-6), but the tier ladder is `Mentalism, Vibration, Correspondence, Gender, Polarity, Rhythm,
CauseAndEffect`. There **is** positional indexing — `steward/gatekeeper.rs:145`
(`HermeticPrinciple::from_index(i)` inside `self.gates.iter().enumerate()`) — so this looked like a
mislabeling bug. It is not: `make_gates()` (`gatekeeper.rs:84`) returns the array in **exactly the enum
order**:

```rust
[MentalismGate, CorrespondenceGate, VibrationGate, PolarityGate,
 HermeticRhythmGate, CauseEffectGate, GenderGate]
```

so slot *i* holds variant *i* and `from_index(i)` labels each gate correctly. Each gate also reads its
own DNA **by name** (`correspondence.rs:85` → `for_principle(HermeticPrinciple::Correspondence)`), so
scoring is name-anchored either way. The remaining hazard is narrower: **the gate-slot order is the enum
order, not the tier order**, so any code or doc that maps gate slot → tier ("gate 3 is the tier-3 gate")
is wrong for six of seven. Nothing does that today. Leave it alone; do not "fix" the enum order to match
the ladder, because that would break the positional labeling that currently works.

## 6. THE RUNTIME CONTRADICTION — worse than the naming one

Documented in full at `references/hermetic-gates-and-binding.md`; the short version:

| Implementation | Location | Covers | Status |
|---|---|---|---|
| **A** | `omokoda-core/src/gates/` (7 files) + `steward/gatekeeper.rs` | **ALL 7** | **LIVE**, 5 call sites |
| **B** | `ifascript::hermetic::default_gate()` | **3 of 7** (Correspondence, Polarity, Rhythm) | **LIVE** at `interpreter.rs:5393` |
| **C** | `omokoda-hermetic/src/safety.rs` | **ALL 7** | **DEAD CODE**, zero callers |

And the agent's Odù-derived DNA **never reaches the gates**: `interpreter.rs:1855` builds
`EsuGatekeeper::new()` — neutral `0.5` on all seven axes — instead of `new_with_hermetic(&state)`, which
has **no production caller**. The agent loads at `:414` (DNA on `AgentCore`), the gatekeeper is built at
`:1855` (on `Steward`), and nothing bridges them.

Consequence, differentiated: **six gates are cosmetic** (DNA is only the pass score; rejection is driven
by content matching, so they still fire). **One is materially broken** — `correspondence.rs:23` is the
only gate using DNA as a *threshold*, and pinned at exactly 0.5 **the `>= 0.8` tighter branch is
unreachable for every agent in the system**. Correspondence guards `/etc/`, `/proc/`, `/sys/`, `~/.ssh`.
So the one gate whose strictness should scale with identity runs at a fixed middle setting, and the most
coherent agents are gated identically to the least.

---

## 7. WHAT TO FIX, IN ORDER

1. **Rebind the gatekeeper on residency** — `self.gatekeeper = EsuGatekeeper::new_with_hermetic(&snapshot.hermetic_state);`
   at `interpreter.rs:414` and after birth. One line plus a lifecycle hook, and it flips the entire
   7-principle system from decorative to identity-anchored. Regression test: two agents with different
   Odù seeds must produce different `GatekeeperResult::alignment_score()`.
2. ~~**Reconcile Koodu's codex** to the canonical table — either rewrite its principle column, or drop the
   principle column entirely and let the codex own the *calendar* axis only.~~ **DONE 2026-09-25** —
   rewrite chosen over drop, because the Òrìṣà column and the day order were already correct, so the codex
   does legitimately own the calendar axis *and* a correct principle column. See the note in §4.
3. **Make missing principles loud** in `ifascript::hermetic` — 4 of 7 have no rule, and `validate_all`
   iterates only existing rules, so "hermetic gates passed" silently means "3 of 7 evaluated".
4. **Fix the opcode reverse map** to `Dict{UInt8, Vec<Symbol>}` so the Òrìṣà↔concept binding survives
   disassembly.
5. **Decide Ọ̀rúnmìlà's status** — eighth Òrìṣà in the opcodes and the oracle of birth, absent from
   identity and the power axis. Either he is outside the 7 (an oracle, not a tier) — in which case say so
   in the opcode table — or the `Macro` enum is short a variant.
6. **Grep `from_index` callers** before the enum-order/tier-order mismatch bites.

<!-- SECTION-END -->
