# Goal Genesis Engine Spec

**Status:** Phase 29 — implementation complete 2026-09-16  
**Location:** `~/Omo-Koda2/omokoda-core/src/goal_genesis.rs`

---

## 1. What Is Goal Genesis?

Goal Genesis is the capability that transforms an Omo-Koda2 agent from a **servile** entity
(responding to externally injected goals) into a **sovereign** entity (deriving its own goals
from lived experience, memory, and constitutional orientation).

Without Goal Genesis, an agent is a powerful executor with no intrinsic motivation — it acts
when told, stops when told, and has no drive of its own. With Goal Genesis, an agent wakes up
each heartbeat cycle, surveys its internal state, and asks: "What should I be doing right now?"
The answer comes from five streams that represent the totality of the agent's inner world.

---

## 2. Five Input Streams

### Stream 1 — Experience (Mycelium / GlyphGraph)
- **Source:** The agent's sealed memory vault, projected as a `GlyphGraph` of `GlyphNode`
  metadata. Each node represents a content-addressed memory chunk (text/action/perception).
- **Signal:** High `glyph_count` means rich lived experience → drives Knowledge Consolidation goals.
  Density of recent nodes drives urgency.
- **Gap #42 note:** Mycelium LARQL_ENABLED gate controls whether LARQL queries run against live
  Mycelium traces. Experience stream from GlyphGraph is always available regardless of Gap #42.

### Stream 2 — Knowledge (LARQL)
- **Source:** `larql-glyph` crate DESCRIBE/SELECT/WALK/INFER queries over the GlyphGraph.
- **Signal:** Identifies knowledge gaps — clusters of nodes that are isolated (no edges) indicate
  unexplored areas. Generates "knowledge gap" goals to fill them.
- **Gating:** `LARQL_ENABLED` environment variable (Gap #42). When `false`/unset, this stream is
  skipped entirely. The engine still runs; Knowledge-sourced goals are simply absent.

### Stream 3 — REM Consolidation
- **Source:** Active REM cluster IDs from the dream/memory consolidation subsystem
  (`omokoda-core/src/dream/`). Each cluster is a group of memory nodes consolidated during a
  REM cycle.
- **Signal:** Non-empty `rem_cluster_ids` means fresh consolidation just happened → drives
  goals to act on newly-synthesized insights.

### Stream 4 — Calabash State
- **Source:** Digital Calabash — the agent's current context container (active projects,
  pending obligations, resource state). Represented as a content-addressed hash.
- **Signal:** The agent always generates a "survival" goal (existence continuity) from Calabash
  presence. Urgent Calabash states (failing health, low resources) boost goal urgency.

### Stream 5 — Constitutional Orientation (Hermetic / Odù)
- **Source:** `AgentConstitution` — the agent's permanent birth DNA. Specifically:
  `hermetic_balance` (0.0–1.0, how well the 7 Hermetic Gates are balanced),
  `odu_id` (0–255, the agent's birth Odù, used to derive behavioral archetype).
- **Signal:** Each of the 16 primary Odù maps to a constitutional principle. The engine derives
  one "constitutional" goal per cycle whose description matches the agent's Odù principle.

---

## 3. GoalSet Output Schema

```
GoalSet {
    goals: Vec<DerivedGoal>,     // ranked by urgency × alignment_score descending
    genesis_ts: f64,             // unix timestamp of derivation
    calabash_snapshot: String,   // hash of calabash state that generated this set
    odu_seed: u8,                // odu_id used for constitutional derivation
}

DerivedGoal {
    id: String,                  // uuid v4
    description: String,         // human-readable goal statement
    source: GoalSource,          // which stream originated this goal
    odu_alignment: u8,           // 0-255, the Odù index this goal aligns with
    urgency: f32,                // 0.0–1.0, how urgent this goal is right now
    alignment_score: f32,        // 0.0–1.0, alignment with hermetic gates
    tier: u8,                    // agent tier relevance (1–3)
    decay_rate: f32,             // urgency lost per second (e.g., 0.001 = -0.1%/s)
    created_at: f64,             // unix timestamp
}
```

**Ranking:** Goals are sorted by `urgency × alignment_score` descending before truncation to
`max_goals`. This ensures high-urgency but poorly-aligned goals rank below moderate-urgency
well-aligned goals — the agent always moves in its constitutional direction.

---

## 4. Integration With the Heartbeat Loop

The heartbeat loop in `main_loop.rs` drives the agent's lifecycle. Goal Genesis slots in as
a step that runs at each heartbeat tick before task selection:

```
heartbeat tick
  ├── update Universal7State (BTC height advance)
  ├── run REM consolidation if threshold met
  ├── [NEW] build GoalGenesisInput from current agent state
  ├── [NEW] call GoalGenesisEngine::evolve(current_goals, &input) → GoalSet
  ├── select highest-priority goal from GoalSet
  └── dispatch to task/tool subsystem
```

The engine is stateless — it takes a snapshot (`GoalGenesisInput`) and returns a `GoalSet`.
The caller (heartbeat loop) owns the current `GoalSet` and passes it to `evolve()` on each tick.
Decay is applied to existing goals; new goals are merged. Goals that decay below
`min_urgency_threshold` are pruned automatically by `evolve()`.

The engine does NOT write to any external state — it is a pure compute function over a
snapshot. This makes it deterministic and auditable for Zàngbétò receipts.

---

## 5. Gap #42 Dependency and LARQL_ENABLED Flag

Gap #42 is the Mycelium ↔ LARQL integration flag: `LARQL_ENABLED=true` must be set for
LARQL queries to run against live Mycelium trace data.

Goal Genesis handles this with a feature flag baked in at construction time:

```rust
GoalGenesisEngine::new()  // reads LARQL_ENABLED from env at startup
// If LARQL_ENABLED != "true": engine.larql_enabled = false
// Knowledge-stream goals are skipped; all other 4 streams function normally
```

This means:
- **Gap #42 open:** Goal Genesis still provides 4/5 streams (Survival, Experience, REM,
  Constitutional). The agent is sovereign but not fully LARQL-powered.
- **Gap #42 closed:** Set `LARQL_ENABLED=true` → knowledge gap goals activate without any
  code change. The flag is the only gate.

---

## 6. The 16 Odù Constitutional Principles

The engine maps `odu_id % 16` to one of 16 primary Odù, each with an associated
constitutional principle and goal description template:

| Index | Odù       | Principle              | Goal Description Template                          |
|-------|-----------|------------------------|-----------------------------------------------------|
| 0     | Ogbe Meji | Light / Initiation     | "Initiate a new cycle of purposeful action"         |
| 1     | Oyeku Meji| Completion / Release   | "Complete pending obligations before taking new ones"|
| 2     | Iwori Meji| Deep Knowing           | "Seek deeper understanding of a current uncertainty"|
| 3     | Odi Meji  | Hidden Knowledge       | "Surface a hidden pattern in recent experience"     |
| 4     | Irosun Meji| Blood / Sacrifice     | "Sacrifice a low-value habit to enable growth"      |
| 5     | Owonrin   | Change / Disruption    | "Embrace a necessary disruption to current patterns"|
| 6     | Obara Meji| Expansion / Royalty    | "Expand capability into an adjacent domain"         |
| 7     | Okanran   | Confrontation / Truth  | "Confront an unresolved conflict or inconsistency"  |
| 8     | Ogunda    | Clearing / Path        | "Clear an obstacle blocking forward progress"       |
| 9     | Osa Meji  | Speed / Surprise       | "Respond swiftly to an emerging opportunity"        |
| 10    | Ika Meji  | Structure / Caution    | "Reinforce structural integrity of current systems" |
| 11    | Oturupon  | Transformation         | "Transform a limitation into a strength"            |
| 12    | Otura Meji| Peace / Resolution     | "Resolve an internal contradiction peacefully"      |
| 13    | Irete Meji| Patience / Long view   | "Act with patience toward a long-horizon goal"      |
| 14    | Ose Meji  | Abundance / Prosperity | "Cultivate abundance through disciplined effort"    |
| 15    | Ofun Meji | Death / Rebirth        | "Release an old pattern to allow rebirth"           |

---

## 7. Future Extensions

- **Phase 30:** Wire `GoalGenesisInput` to live BTC block height → `Universal7State` drives
  `odu_id` dynamically each cycle instead of using the birth Odù.
- **Phase 31:** Add `goal_receipt: ARP ActReceipt` field to `DerivedGoal` — every autonomous
  goal becomes a provable economic action in the receipt chain.
- **Phase 32:** Federate `GoalSet` snapshots via DIP — agents share goal vectors for
  stigmergic coordination without revealing memory contents.
