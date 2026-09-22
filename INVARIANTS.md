# Ecosystem invariants — data integrity and epistemic integrity

Applies to Mycelium, Vantage, Ọmọ Kọ́dà, and Ọ̀ṢỌ́VM-facing persistent state.
Binding wherever interpreted data is stored.

Written after four defects were found in one session, in code that passed its
tests. They were not exotic. Three of them were invisible to the test suite by
construction, and the fourth was a field paid for twice in opposite directions
by two components that never spoke to each other.

---

## 0. The question that decides everything

Before writing storage of any kind:

> **Can this value be reconstructed?**

```
              Can it be reconstructed?
                        │
            ┌───────────┴───────────┐
           YES                      NO
            │                        │
        DERIVED                   RECORD
            │                        │
        rebuild freely             migrate, never drop
        delete + re-sync          back up; the only copy
```

Both answers are correct. The failure mode is having no answer.

| | DERIVED | RECORD |
|---|---|---|
| test | an upstream source of truth can reconstitute it | nothing can |
| examples | a chain tape, an API cache, a public-state scan, a projection | agent history, timestamps, decisions, cursors, resolved outcomes, `state` columns |
| cost of deletion | time | information |
| policy on schema change | delete and re-sync | ALTER, and keep the old rows |

**Worked example from this ecosystem.** fomopulse deletes and re-syncs from the
chain, and is right to: its tape is derived. Vantage migrates, and is right to:
`signal_pool`'s `_SIGNAL_POOL_MINT_MIGRATION` exists for exactly this. Mycelium
is entirely RECORD — traces, findings, resolved outcomes, cursors — and had
**no policy at all**. It is the store that broke.

A store that is mostly derived can still hold RECORD columns. `fills.supply` is
the feed's reading at the moment a fill landed; nothing upstream recovers it
after a burn. Those columns need in-place ALTERs *inside* a rebuildable store,
and the regenerate path must know they are exempt.

---

## 1. Data integrity invariants

### 1.1 Never insert positionally

```sql
NEVER:   INSERT INTO table VALUES (?, ?, ?, ?)
ALWAYS:  INSERT INTO table (a, b, c, d) VALUES (?, ?, ?, ?)
```

`ALTER TABLE … ADD COLUMN` appends **physically last**. The DDL declares the
column **wherever the author put it**. A positional INSERT assigns **by physical
position**, so the same code is correct on a fresh database and writes every
value one column early on a migrated one.

```
live  (after ALTER): id, created_ts, miner, confidence, title, …, payload, direction
fresh (from DDL):    id, created_ts, miner, confidence, direction, title, …, payload
```

**A fresh-database test can never catch this.** It is the single highest-value
habit in this document, and it is one line.

### 1.2 `CREATE TABLE IF NOT EXISTS` is not a migration

It is a no-op against a table that already exists — that is, against the only
database that needs the change. A column added to the DDL without a matching
ALTER exists only on databases created since.

Every store needs a registry of column additions, applied at open, and a
`verify_schema()` that compares the live database to the code and reports drift
as **a failing writer**, not a missing feature.

### 1.3 A populated table is not a working writer

A table keeps its old rows while every new write fails. "Does the substrate have
findings" answers yes throughout an outage. Assert on a **write**, and read back
**every field** — a positional INSERT damages all of them, so checking only the
column you added passes on a corrupted row.

### 1.4 Status documents are not status sources

A README that says "there are no migrations, we just rebuild" while the
connection module carries four in-place ALTERs is a live hazard: read literally
it instructs the next reader to delete a database holding values its own
comments call irrecoverable. When a doc and the code disagree about storage,
**the code is the spec and the doc is the bug.**

---

## 2. Version and provenance invariants

Any value whose meaning can change over time carries the rules that produced it.

```
value
  + rule_version       which reconstruction/miner rules produced it
  + scoring_version    which formulas and weights interpreted it
  + policy_version     which gates and constraints were in force
  + provenance[]       where the evidence came from
  + evidence_refs[]    the specific items relied on
```

**Versions that are hand-bumped will be forgotten on the change that mattered.**
Where the version describes configuration, derive it — a digest of the actual
thresholds cannot disagree with the thresholds. Reserve integer constants for
code (formulas), digests for config (thresholds).

Two distinctions this buys, both of which are otherwise unavailable:

- **History vs. interpretation of history.** `RULE_VERSION` separates what
  happened from how we currently read it. Without it, re-deriving a stored
  verdict silently rewrites the past, and "would we have decided differently"
  becomes unanswerable because the original decision no longer exists.
- **A score with a unit.** A stored 72 under old weights and a 72 under new
  ones are different numbers. Neither is interpretable without its version.

**A DEFAULT is a guess at old rows, not a measurement.** Say so at the migration
rather than letting a later reader assume the value is real.

---

## 3. Epistemic integrity invariants

### 3.1 Multiplicity is not independence

> **How many things said it ≠ how many independent things know it.**

This is the most dangerous failure in the ecosystem, because it needs no bug. It
is correct code operating on incorrectly characterized evidence.

```
         ONE SOURCE
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
  Agent A   Agent B   Agent C
    │         │         │
    └─────────┼─────────┘
              ▼
          same evidence
```

An agent must never reason "everybody agrees" when what happened is "one source
propagated the same belief through ten agents."

### 3.2 The three collapses

Independence is computed by removing causes, in order, each independent:

| collapse | mechanism | catches |
|---|---|---|
| **rings** | entity-graph clusters — N addresses, one ring | coordinated bundlers |
| **funders** | the address that paid for a wallet — N addresses, one actor | a fresh spray the graph has not seen |
| **content** | identical payload or identical amount across reporters | one fact reported many times |

`effective = claimed_count × independence`. Report **both** quantities. A count
alone is what multiplication looks like.

### 3.3 Absent evidence is not shared evidence

A blank payload establishes nothing. Two agents that traced a bare failure made
no claim about a common cause, and collapsing them into one source merges
genuinely separate failures. **"No opinion" and "one source" are different
answers**, and a component with no data must be absent from the aggregate rather
than scored as zero.

### 3.4 Do not pay for the same fact twice, in opposite directions

Found in this ecosystem: `s_finding` paid a flat bonus for a cluster of wallets
hitting a token, while `S_independence` discounted exactly that width. Two
components, never introduced, contradicting each other about one event.

Any component that rewards a quantity must consult any component that discounts
it. When a reward is suppressed, **name it** — a suppressed bonus is a fact
about the decision.

---

## 4. Where the two classes meet

They are not the same class of defect, and conflating them hides the dangerous
one:

```
DATA INTEGRITY                       EPISTEMIC INTEGRITY
  missing migration                    correlated evidence counted repeatedly
  positional INSERT corruption         identity/independence collapse
  historical version corruption        duplicated evidence as consensus
        │                                        │
        └────────────────┬───────────────────────┘
                         ▼
              correct code operating on
           incorrectly characterized evidence
```

Data-integrity defects corrupt the record. Epistemic defects produce a
*well-formed, well-versioned, perfectly preserved* record of a belief that was
never justified. The second cannot be caught by any amount of schema discipline,
which is precisely why it needs its own invariants.

`RULE_VERSION` is where the two classes meet rather than a member of either: it
is a data-integrity mechanism whose entire purpose is to make epistemic
comparison possible.

---

## 5. Conformance checklist

Before any store or interpreter ships:

**Storage**
- [ ] Every table classified DERIVED or RECORD, in writing, in the repo.
- [ ] RECORD stores have a column-migration registry applied at open.
- [ ] `verify_schema()` exists and is run on deploy; drift exits non-zero.
- [ ] Every INSERT names its columns.
- [ ] Every migration test builds a database from the **old** DDL, then migrates it.
- [ ] A write is asserted, and read back field by field.
- [ ] Column additions have a matching `SCHEMA_VERSION` bump, and the version is *read*, not only written.

**Interpretation**
- [ ] Every value whose meaning can change carries its rule/scoring/policy version.
- [ ] Config-derived versions are digests, not hand-bumped constants.
- [ ] Decisions store an evidence snapshot: what was observed, how independent, under which rules, with what result.
- [ ] The snapshot is written in the same transaction as the decision.

**Evidence**
- [ ] Counts are reported alongside effective counts.
- [ ] Ring, funder, and content collapses applied before any count is used.
- [ ] Components that reward a quantity consult components that discount it.
- [ ] Suppressed rewards are named in the output, not silently dropped.
- [ ] Absent data is absent, never scored as zero.

---

## 6. Implementation status

Honest as of this writing — this is doctrine, and doctrine outruns code.

| invariant | where | status |
|---|---|---|
| DERIVED/RECORD classification | Mycelium | written (`SCHEMA_POLICY.md`), tables classified |
| migration registry + `verify_schema` | Mycelium | implemented, tested, CLI-exposed |
| named INSERTs | Mycelium | implemented (was positional — caused silent corruption) |
| named INSERTs | Vantage, fomopulse | already correct |
| `RULE_VERSION` | fomopulse | implemented (`fills.rule_version`) |
| `rule_version` on miner output | Mycelium | **absent** — findings do not yet carry one |
| wallet independence | signal_fusion | implemented (`S_independence`) |
| agent independence | Mycelium | implemented (`cross_agent`) |
| decision snapshot | signal_fusion | implemented (`decision_snapshots`), incl. version + provenance |
| snapshot → Mycelium memory | Mycelium | **absent** — snapshots live in the picks store; Mycelium cannot yet read them |
| provenance/evidence_refs on traces | Mycelium | **absent** — `traces` has no evidence reference |

The three absences share one shape: evidence is recorded at the point of
decision but does not flow into the memory substrate. That is the next piece of
work, and it is what turns "what did we believe" into "why did we believe it."
