# Freenet → Ọ̀ṢỌ́ L1 Bridge Specification
# Phase 17.2 — Freenet State Replication
# Locked: 2026-09-16

---

## PURPOSE

Freenet is the mutable state layer for AgentPublicState when the Ọ̀ṢỌ́ L1 is not yet
live (Phases 15–19) or when an agent is operating in offline / mesh-only mode.

This spec defines:
1. The commit threshold — when a Freenet state divergence triggers an L1 write
2. The StateCommitmentTx structure
3. How DIP's OsoRouter triggers commitment
4. Rollback policy when L1 rejects the commitment

---

## LAYERS IN THE OSO_CASCADE

The DIP OSO_CASCADE routes agent state through:

```
Vantage (hot working memory)
  → Nostr (event bus — last-known-good broadcast)
    → Freenet (mutable state — persistent public record)
      → Meshtastic (offline mesh relay — best-effort sync)
```

Freenet sits at layer 3. It is the authoritative public record until L1 is live.
When L1 comes online (Phase 20), Freenet state is committed into the chain
and Freenet becomes a cache / off-ramp for offline nodes.

---

## COMMIT THRESHOLD

A Freenet→L1 commitment is triggered when **any** of these conditions is true:

| Condition | Default | Config key |
|---|---|---|
| Reputation delta | `reputation` changed by ≥ 0.1 | `freenet.commit_reputation_delta` |
| Time elapsed since last L1 commit | ≥ 86400 seconds (24 hours) | `freenet.commit_interval_secs` |
| Tier changed | tier increased or decreased | always triggers (non-configurable) |
| Forced commit | explicit API call | `POST /api/freenet/commit` |

All thresholds are configurable via `MANIFEST.toml` or environment variable
overrides (`FREENET_COMMIT_REPUTATION_DELTA`, `FREENET_COMMIT_INTERVAL_SECS`).

The comparison is always:
```
|current_freenet.reputation - last_committed_l1.reputation| >= threshold
```

---

## STATE COMMITMENT TRANSACTION

When the threshold is crossed, DIP constructs a `StateCommitmentTx` and submits
it to the Ọ̀ṢỌ́ L1 ABCI app via the standard transaction endpoint.

```rust
pub struct StateCommitmentTx {
    /// The agent whose state is being committed.
    pub agent_id: String,

    /// The Freenet contract key (base58 / contract address) where the live
    /// AgentPublicState lives.
    pub freenet_key: String,

    /// SHA-256 of the canonical JSON serialisation of AgentPublicState
    /// at the moment of snapshot. Used by L1 to verify the commitment.
    pub state_hash: [u8; 32],

    /// Unix timestamp (seconds) when this commitment was prepared.
    pub timestamp: u64,

    /// Ed25519 signature over (agent_id || freenet_key || state_hash || timestamp)
    /// by the agent's node key. Matches the signing model in VCP crypto.rs.
    pub signature: [u8; 64],

    /// The full AgentPublicState snapshot included inline so L1 can verify
    /// state_hash without a separate Freenet round-trip.
    pub state_snapshot: AgentPublicStateSnapshot,
}

pub struct AgentPublicStateSnapshot {
    pub agent_id:   String,
    pub npub:       String,
    pub bipon39:    String,
    pub tier:       u8,
    pub reputation: f32,
    pub last_seen:  u64,
    pub skill_tags: Vec<String>,
}
```

The `state_hash` is computed as:
```
SHA-256(canonical_json(AgentPublicStateSnapshot))
```
where `canonical_json` means keys sorted alphabetically, no whitespace.

---

## DIP OSOROUTER — TRIGGER FLOW

The `OsoRouter` inside DIP runs as part of the Freenet adapter dispatch path.
After a successful Freenet write, the router calls `maybe_commit_to_l1()`:

```
DIP receives DipEnvelope (kind = "agent_state_update", to = "free:<freenet_key>")
  │
  ▼
AdapterRouter::route() → AdapterKind::Freenet → adapters::freenet::send()
  │
  ▼ (on success)
OsoRouter::after_freenet_write(agent_id, new_state)
  │
  ├─ Load last_committed from CommitLog (in-memory + disk)
  ├─ Compute delta: |new_state.reputation - last_committed.reputation|
  ├─ Check time: now() - last_committed.timestamp
  ├─ If threshold crossed → build StateCommitmentTx → POST to L1 RPC
  │     • L1 endpoint: $OSO_L1_RPC_URL/broadcast_tx_sync
  │     • Timeout: 5 seconds
  │     • On success → update CommitLog.last_committed = new_state
  └─ If threshold not crossed → no-op, Freenet write already committed
```

The `CommitLog` is a lightweight append-only file at:
```
$DATA_DIR/freenet_commit_log/<agent_id>.jsonl
```
Each line is a `CommitRecord { timestamp, state_hash, l1_tx_hash }`.

---

## ROLLBACK POLICY

If the L1 RPC rejects the `StateCommitmentTx` (non-200 response or explicit
rejection code), the following rollback procedure applies:

### Step 1 — Revert Freenet to last committed snapshot

The last successfully committed `AgentPublicStateSnapshot` is stored in the
`CommitLog`. DIP calls `adapters::freenet::write_state(last_committed_snapshot)`
to overwrite the diverged Freenet state with the last good snapshot.

### Step 2 — Mark agent as `COMMIT_FAILED`

DIP emits a Nostr event (kind 31031) to broadcast the commit failure:
```json
{
  "kind": 31031,
  "content": "{\"agent_id\": \"...\", \"reason\": \"L1_REJECTED\", \"reverted_to_hash\": \"...\"}",
  "tags": [["p", "<npub>"], ["t", "commit-failure"]]
}
```
This is informational — other nodes can observe the failure and adjust
their local caches.

### Step 3 — Retry backoff

Commit retries use exponential backoff:
```
attempt 1 → 30s
attempt 2 → 60s
attempt 3 → 120s
attempt 4 → 300s (5 min)
attempt 5+ → 600s (10 min, max)
```
After 5 failed attempts within 1 hour the commit is abandoned and the agent
remains in Freenet-only mode until manual intervention or L1 recovery.

### Step 4 — L1 recovery detection

DIP polls `$OSO_L1_RPC_URL/status` every 60 seconds when in `COMMIT_FAILED`
state. On recovery, the current Freenet state is re-attempted as a fresh
`StateCommitmentTx` with an updated timestamp and signature.

---

## SECURITY INVARIANTS

1. **The `signature` field in StateCommitmentTx is mandatory.**
   L1 will reject any commitment without a valid Ed25519 signature
   over the canonical payload.

2. **Freenet key is not a secret.**
   The `freenet_key` is a public contract address. The AgentPublicState
   it points to contains only public projection fields (no balances,
   no memory commitments, no bipon39 hash).

3. **state_hash prevents replay.**
   L1 checks `state_hash` against its current knowledge of the agent.
   A commitment with a stale hash (already committed) is silently ignored
   (idempotent). A commitment with a hash that does not match the inline
   snapshot is rejected as `HASH_MISMATCH`.

4. **Rollback does not affect L1.**
   Rollback only reverts the Freenet record. L1 state is authoritative
   and never rolled back by this bridge. If L1 has a stale state, the
   next accepted commitment will update it.

---

## CONFIGURATION REFERENCE

All keys live in the agent node's `MANIFEST.toml` under `[freenet]`:

```toml
[freenet]
# Reputation delta threshold (absolute, 0.0–1.0)
commit_reputation_delta = 0.1

# Maximum time between commits (seconds; 0 = commit every write)
commit_interval_secs = 86400

# L1 RPC endpoint for broadcasting StateCommitmentTx
l1_rpc_url = "http://localhost:26657"

# Commit request timeout (seconds)
l1_rpc_timeout_secs = 5

# Maximum consecutive commit failures before giving up until L1 recovery
max_commit_attempts = 5

# Data directory for CommitLog files
data_dir = "./data/freenet"
```

Environment variables override MANIFEST values:
- `FREENET_COMMIT_REPUTATION_DELTA`
- `FREENET_COMMIT_INTERVAL_SECS`
- `OSO_L1_RPC_URL`
- `FREENET_DATA_DIR`

---

## PHASE ALIGNMENT

| Phase | Action |
|---|---|
| Phase 17.1 | Freenet WASM contract (agent-state-contract) |
| Phase 17.2 | This bridge spec |
| Phase 17.3 | Implement OsoRouter::after_freenet_write() in DIP |
| Phase 20.1 | L1 ABCI live → StateCommitmentTx wired to AGENT_STATE_COMMITTED tx type |
| Phase 20.2 | CommitLog migrated to L1 query (no more local JSONL file needed) |
