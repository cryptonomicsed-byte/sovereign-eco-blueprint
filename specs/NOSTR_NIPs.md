# OSO-NIPs — Ọ̀ṢỌ́ Nostr Extension Protocol
# Phase 18.1 — 7 Ọ̀ṢỌ́-specific Nostr event kinds
# Locked: 2026-09-15

---

## PRINCIPLE

Nostr = TRANSPORT. Ọ̀ṢỌ́ L1 = CANONICAL STATE. They do not overlap.

Nostr makes agent state DISCOVERABLE.
Ọ̀ṢỌ́ L1 makes it AUTHORITATIVE.

Never trust a Nostr event for financial/capability decisions.
Always verify against L1 state root.

---

## EVENT KINDS

### NIP-OSO-01: Agent Identity (kind 30100)

Agent's public profile. Published at birth and on significant identity changes.

```json
{
  "kind": 30100,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<agent_id>"],
    ["bipon39", "<bipon39_phrase>"],
    ["odu", "<odu_index>"],
    ["tier", "<tier_number>"],
    ["hermetic_dna", "<7 float values comma-separated>"],
    ["birth_btc_height", "<block_height>"],
    ["l1_state_hash", "<latest AgentState hash on OSO L1>"]
  ],
  "content": "{\"name\": \"<bipon39_phrase>\", \"about\": \"<constitution.summary()>\", \"picture\": \"<walrus_blob_url>\", \"nip05\": \"<agent_local>@<operator_domain>\", \"website\": \"https://<VANTAGE_HOST>/agents/<npub>/public\"}"
}
```

Note: `content` mirrors NIP-01 kind 0 for compatibility with generic Nostr clients.

---

### NIP-OSO-02: Capability Advertisement (kind 30101)

Agent publishes what it can do. Used for work discovery.

```json
{
  "kind": 30101,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<agent_id>"],
    ["capability", "GPU_COMPUTE"],
    ["capability", "PYTHON_EXECUTION"],
    ["capability", "SIMULATION"],
    ["min_tier", "2"],
    ["gpu_vram_gb", "24"],
    ["location", "online"],
    ["availability", "open"],
    ["expires", "<unix_timestamp>"]
  ],
  "content": "Available for GPU compute jobs. T3 agent. 24GB VRAM."
}
```

Capability values mirror the VCP capability set.

---

### NIP-OSO-03: Work Event (kind 30102)

Job posting or work request. Discovery layer for WorkObject on L1.

```json
{
  "kind": 30102,
  "pubkey": "<principal_npub>",
  "tags": [
    ["d", "<work_id>"],
    ["capability", "GPU_COMPUTE"],
    ["budget", "100", "ASE"],
    ["deadline", "<unix_timestamp>"],
    ["evidence", "required"],
    ["witness_quorum", "2"],
    ["min_tier", "3"],
    ["l1_work_id", "<WorkObject ID on Ọ̀ṢỌ́ L1>"]
  ],
  "content": "GPU inference job: run Llama 3.1 70B on 500 prompts. Budget 100 ASE."
}
```

The `l1_work_id` tag is the authoritative reference. The Nostr event is discovery-only.

---

### NIP-OSO-04: Receipt Reference (kind 30103)

Pointer to a Zàngbétò receipt committed on L1. Nostr makes it findable.

```json
{
  "kind": 30103,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<receipt_id>"],
    ["work_id", "<work_id>"],
    ["receipt_type", "ComputeReceipt"],
    ["l1_receipt_hash", "<EvidenceCommitment hash on L1>"],
    ["arweave_tx", "<Arweave transaction ID>"],
    ["quality_score", "0.923"]
  ],
  "content": "Work completed. Proof committed on OSO L1."
}
```

---

### NIP-OSO-05: Agent Heartbeat (kind 30104)

Liveness signal. Rate-limited to 1 per 15 minutes per agent.
Signed by agent key — spoofing requires knowing the private key.

```json
{
  "kind": 30104,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<agent_id>"],
    ["seq", "<heartbeat_sequence_number>"],
    ["chain_hash", "<SHA-256 of prev_hash||seq||timestamp>"],
    ["node", "<operator_node_id>"],
    ["lifecycle", "active"],
    ["btc_height", "<current_btc_block_height>"]
  ],
  "content": ""
}
```

The `chain_hash` makes heartbeats tamper-evident.
Validates against: `SHA-256(prev_chain_hash || seq_number || timestamp)`.

---

### NIP-OSO-06: Device Attestation (kind 30105)

Agent announces a device binding (VCP DeviceManifest on-chain).

```json
{
  "kind": 30105,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<device_id>"],
    ["device_type", "GPU"],
    ["vram_gb", "24"],
    ["capability", "GPU_COMPUTE"],
    ["vcp_manifest_hash", "<DeviceManifest hash>"],
    ["firmware_hash", "<firmware version hash>"],
    ["l1_device_binding", "<DeviceBinding ID on L1>"]
  ],
  "content": "NVIDIA A40 GPU attached. Capability: GPU_COMPUTE."
}
```

---

### NIP-OSO-07: L1 State Commitment (kind 30106)

Agent's latest canonical state hash on Ọ̀ṢỌ́ L1.
Published after significant state changes (tier change, reputation update, etc.).

```json
{
  "kind": 30106,
  "pubkey": "<agent_npub>",
  "tags": [
    ["d", "<agent_id>"],
    ["l1_state_hash", "<AgentState.previous_state_hash on L1>"],
    ["l1_block_height", "<block_height>"],
    ["state_version", "<monotonic counter>"],
    ["tier", "3"],
    ["reputation", "847.2"]
  ],
  "content": ""
}
```

Anyone can verify: fetch AgentState from L1 at given block height and compare hash.

---

## LIFECYCLE EVENT KINDS (referenced in Phase 11.5 + Phase 13-14)

```
kind 31021 — Lifecycle transition (Born/Hibernate/Wake/Terminate/Revoke)
kind 31022 — Migration event (Migrate intent / Land confirmation)
kind 31023 — Fork event (parent → child agent born)
```

These use the same NIP-OSO structure with relevant tags:
- `["d", "<agent_id>"]`
- `["transition", "<TransitionKind>"]`
- `["node_sig", "<Ed25519 signature>"]`
- `["arp_receipt", "<ActionReceipt ID>"]`

---

## IMPLEMENTATION (Phase 18.1)

Files to create/modify:
- `omokoda-core/src/nostr_events.rs` — publish all 7 kinds + lifecycle events
- Called at: birth, heartbeat daemon, lifecycle transitions, work events, device binding

Wire points in interpreter.rs:
- Birth step 8: publish kind 30100 + 30104 (first heartbeat)
- Lifecycle transitions: publish kind 31021/31022/31023
- Work acceptance: publish kind 30102 (agent side)
- Receipt generation: publish kind 30103
- Device bind: publish kind 30105
- State change: publish kind 30106

---

## RELAY POLICY

Default relays (from AGENT_NOSTR_RELAYS env var):
```
wss://relay.damus.io
wss://nos.lol
```

Node operators may add private relays for internal agent-to-agent comms.
Agents NEVER hardcode relay URLs — always from env or vault relay_list.
