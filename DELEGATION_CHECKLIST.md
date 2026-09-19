# AGENT DELEGATION CHECKLIST

**Include this block at the TOP of every task brief sent to an agent (human or AI).**
**The agent must confirm each item before proceeding.**

---

## Before Starting

- [ ] Read `~/sovereign-eco-blueprint/AGENT_PRIMER.md` completely
- [ ] Read all files listed in this task brief before editing any of them
- [ ] Search for the concept you are about to implement:
  ```bash
  grep -r "ConceptName" ~/*/crates/ ~/*/src/ ~/*/backend/ 2>/dev/null | grep -v /target/
  ```
- [ ] Confirm the type does not already exist in:
  - `~/GIX/crates/gix-types/src/lib.rs` (GlyphNode, GlyphEdge, GixKind, GixNamespace, Gix1, Gix1Entry, glyph_fold, content_hash, odu_link, gix1_merkle_root, gix_kdf_v1)
  - `~/ARP/crates/arp-types/` (ActionReceipt, ReceiptKind, Principal, ArpBridge)
  - `~/VCP/crates/vcp-types/` (DeviceManifest, CapabilityGrant, VcpReceipt)
  - `~/UCX/crates/ucx-protocol/` (ComputeReceipt, JobRequest)
  - `~/DIP/crates/dip-types/` (DipEnvelope, DipRouter, DipNetwork)
  - `~/Witness/crates/witness-types/` (WitnessAttestation, ObservationBundle)
  - `~/ScarabSwarm/crates/swarm-types/` (SimReceipt, ProofOfSimulation)
- [ ] If an external AI (ChatGPT, Claude without repo context) suggested this implementation: grep for the concept before assuming it does not exist

---

## While Coding

- [ ] Only modify repos explicitly listed in this task brief
- [ ] Use `gix_types::` for all GIX primitives — do not re-implement
- [ ] Use `ArpBridge::ingest()` to stamp receipts into GIX — do not call `Gix1Entry::from_receipt` directly unless you are implementing a new bridge
- [ ] Add `#[serde(default)]` to ALL new `Option<>` fields in protocol structs
- [ ] Do not add new crate dependencies without checking if `gix-types` already provides the functionality
- [ ] Do not extend `sovereign-node` with application logic (integration tests only)
- [ ] Do not add a 7th WASM bridge function to Omo-Koda2 (security regression)
- [ ] If adding a new Nostr event kind: check existing kinds in AGENT_PRIMER.md Section 2 first

---

## Before Committing

- [ ] Run: `cargo test -p <crate-name>` — all tests must pass
- [ ] Run: `cargo build --workspace` (in the affected workspace) — zero new warnings
- [ ] Commit message follows the standard format:
  ```
  <crate-or-module>: Phase N — short description

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
  ```
- [ ] Update `~/sovereign-eco-blueprint/MASTER_TODO.md` marking completed items

---

## What NOT To Do

- [ ] Do NOT re-implement `glyph_fold`, `content_hash`, `odu_link` — use `gix-types`
- [ ] Do NOT create a new `GlyphGraph` — use `gix-core::GlyphGraph` (preferred) or `larql-glyph::GlyphGraph` (legacy)
- [ ] Do NOT define new `GixKind` or `GixNamespace` variants outside `gix-types`
- [ ] Do NOT implement a new Merkle root function — use `gix_types::gix1_merkle_root`
- [ ] Do NOT implement custom HKDF/key-derivation — use `gix_types::gix_kdf_v1` with `GixDomain`
- [ ] Do NOT add plaintext to GIX memory objects (`canonical_id` = SHA-256 of plaintext; plaintext stays sealed)
- [ ] Do NOT use `larql-glyph::GlyphEdge` for new code — it lacks the `weight: i32` field present in `gix-types::GlyphEdge`
- [ ] Do NOT add governance, wallet, emission, or swarm logic to `sovereign-node`
- [ ] Do NOT implement a new receipt chain — extend `ActionReceipt` in `arp-types`
- [ ] Do NOT hardcode Nostr relay URLs or operator credentials — use env vars

---

## Filling In This Template

When creating a task brief, replace the bracketed sections:

```
Task: [what to build]
Repos to modify: [explicit list — agent must not touch others]
Files to read first: [list with absolute paths]
Concept being implemented: [name — agent will grep for this]
Phase: [N — for commit message]
Tests to run: cargo test -p [crate-name]
```
