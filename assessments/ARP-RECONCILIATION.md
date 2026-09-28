# ARP — what it is, and the receipt-layer collision

2026-09-23. Sources: `~/ARP` (`79f68ab`, today), `~/sovereign-stack/{arp-types,arp-broker}`,
`~/sovereign-stack/sovereign-types/src/{work_id,receipt}.rs`, deployed `/usr/local/bin/arp-broker`.

---

## 1. WHAT ARP IS

`~/ARP` — Action Receipt Protocol. Rust workspace, members `crates/arp-types` + `crates/arp-broker`,
last commit **today** (`79f68ab fix: receipt persistence store wiring (E-18)`).

**Five primitives, in chain order:** `Principal → Capability → Action → Evidence → Receipt`.
**Twelve receipt kinds:** `compute · vcp_session · emission · twin_capture · twin_scene · simulation ·
governance · economic · agent_lifecycle · witness · mesh_event · custom` — with a documented
kind→verifier routing table in `arp-types/src/lib.rs` (e.g. `twin_capture → Nostr kind 31020`,
`twin_scene → 31030`, `witness → physical observation by Witness firmware`).

**What ARP gets right that nothing else in the stack does** — the envelope carries its own adjudication:

- `ThroneEvaluation { throne_id, model, verdict, confidence, rationale, evaluated_at, signature }` —
  a jury verdict *inside the receipt*, with which model judged and at what confidence
- `ConsensusReceipt { quorum, threshold, consensus, combined_hash, settled_at }` — "N of 12 thrones"
- `WitnessAttestation` and `PhysicalAttestation { device_id, … }` — hardware/observation attestation
- `zangbeto_anchor` + `nostr_event_id` — links to the evidence fabric and the Nostr publication
- `execution_id` — links a receipt to a batch/job
- **`bridge.rs`** — `ArpBridge` wraps every `ActionReceipt` as a content-addressed `Gix1Entry`
  (`GixKind::Receipt`) in a `Gix1Index`, giving `merkle_root()` and `audit()`. *"Every ActionReceipt
  that passes through the bridge gets a content-addressed GlyphNode (kind=Receipt) … making all
  sovereign receipts queryable via the GIX graph."*
- **`zangbeto.rs`** — `anchor_receipt()`, fail-open: *"receipt operations are never blocked by Zàngbétò
  being unreachable."*

That envelope is richer than anything SEP-1 defines. **It is also not the type SEP-1 mandates.**

---

## 2. THE COLLISION — three receipt types, two of them in one crate

| | `sovereign-types::work_id::ActionReceipt` | `sovereign-types::receipt::CanonicalReceipt` | `arp-types::ActionReceipt` |
|---|---|---|---|
| Mandate | SEP-1: "Every state transition MUST produce an `ActionReceipt`" | — | "**ALL** consequential system operations MUST produce an ActionReceipt" |
| `receipt_id` | **BLAKE3 of canonical fields** | `String` | **`Uuid` (random)** |
| work attribution | **`work_id` (`wk:{ns}:{ulid}`)** | ✗ none | ✗ **none** |
| identity | `principal_id`, `agent_id` | `identity: IdentityChain` | `principal: Principal` + `CapabilityRef` |
| action | `action: String` | `action: ActionRecord` | `action: ActionSpec{kind,target,outcome,params}` |
| jury | ✗ | `throne_evaluations: Vec<Value>` **(untyped)** | `Vec<ThroneEvaluation>` **(typed)** |
| attestation | ✗ | `witness_attestations`, `physical_attestation: Option<Value>` | typed + `zangbeto_anchor`, `nostr_event_id` |
| merkle | ✗ | `merkle_root: Hash` | via `ArpBridge` |
| chain | `previous_receipt` (**BLAKE3**) | `previous_hash: Hash` | `previous_hash` (**sha256** — declared in MANIFEST.toml) |
| time | `timestamp_ms` | `Timestamp` | `timestamp` (**Unix seconds**) |
| signature | ed25519 | `Signature` | `String` |
| enforced by | `sovereign-node/src/receipt_store.rs` ("MUST reject a broken chain link") | — | `arp-broker` (:"verifies SHA-256 hash chains") |
| tested by | `sovereign-runtime/tests/sep1_conformance.rs` | — | — |

**`CanonicalReceipt` is the tell.** It is an ARP-shaped envelope (witness_attestations,
throne_evaluations, consensus_receipt, physical_attestation, previous_hash, a `ReceiptKind`) living
*inside `sovereign-types`*, but with the jury/attestation fields typed as opaque `Value` and an added
`merkle_root`. **Someone already started merging ARP into SEP-1 and stopped halfway** — leaving three
types where the design wants one envelope plus one chain core.

### The four name collisions

1. **`ActionReceipt`** — defined in `sovereign-types::work_id` *and* `arp-types`. Identical name, two
   crates, different fields. Any crate importing both needs an alias, and a silent wrong-import is the
   default outcome.
2. **`ReceiptKind`** — two enums, overlapping concepts under different names:
   `sovereign-types` has 8 (`DipRoute, VcpSession, Capture //TSP 31020, Scene //TSP 31030, Simulation,
   Observation, LicenseGrant, Validation`); `arp-types` has 12. **`VcpSession` and `Simulation` collide
   outright; `Capture`/`Scene` vs `TwinCapture`/`TwinScene` are the same concepts renamed.** Four
   concepts duplicated, eight kinds present in only one of the two.
3. **`WitnessAttestation`** — `sovereign-types::receipt` (`witness_id, merkle_commitment, timestamp,
   signature`) vs `arp-types::receipt` (`witness_id, attested_at, observation, outcome_hash,
   signature`). Same name, different fields.
4. **`ActionReceipt` in the README's own diagram** — `~/ARP/README.md` documents
   `crates/arp-core/ # signing, verification, chain linkage`, and **that crate does not exist** —
   `crates/` contains only `arp-types` and `arp-broker`. The architecture block documents a crate
   nobody built.

### The integrity divergence — the part that actually matters

SEP-1's `receipt_id` is *derived from the payload*; the conformance suite proves it with
`receipt_id_changes_when_payload_changes` (*"payload is not covered by receipt_id"*).
ARP's `receipt_id` is a **random `Uuid`**, so the id commits to nothing: two identical receipts get
different ids, and **a modified ARP receipt keeps its id**. Same word, different security property.
And ARP's envelope — the one that claims to be canonical — **has no `work_id`**, so it cannot be
attributed to the cross-pillar identifier it is supposed to be canonical for.

**Plus a version fork.** `principal.rs` and `error.rs` are byte-identical between `~/ARP/crates/arp-types`
and `sovereign-stack/arp-types`, but `lib.rs` and `receipt.rs` have **DIVERGED**, and `bridge.rs` +
`zangbeto.rs` exist **only in `~/ARP`**. Provenance check on the deployed binary:

```
/usr/local/bin/arp-broker   4374752 bytes   Sep 14 17:07
strings → crates/arp-types/src/bridge.rs
           crates/arp-types/src/receipt.rs
```

**The live ARP broker on :7795 was built from the standalone `~/ARP` tree — not from
sovereign-stack's vendored copy.** Yet `sovereign-stack/Cargo.toml` declares `arp-types` and
`arp-broker` as workspace members. So building sovereign-stack today produces a *different* ARP broker
than the one running in production, and the richer one (with `bridge.rs` + `zangbeto.rs`) is the one
outside the declared workspace.

---

## 3. NUMBER DRIFT (same pattern, one more time)

`~/ARP/README.md` opens: *"Unifies **6** incompatible receipt formats … into one canonical envelope."*
`MANIFEST.toml` and `arp-types` both declare **12** kinds. So the count is 6 in the prose, 12 in the
manifest and the code — and neither matches the third enum's 8. Three counts for one taxonomy.

---

## 4. RECONCILIATION — the target design

One envelope, one kind enum, one chain primitive, one content-addressed id.

**Keep as the chain core:** `sovereign-types::work_id::ActionReceipt` — it is the only one with a
content-addressed id, a `work_id`, an ed25519 signature, an enforcing store, and conformance tests.

**Fold into it:** ARP's typed envelope fields — `throne_evaluations: Vec<ThroneEvaluation>`,
`consensus_receipt: ConsensusReceipt`, `physical_attestation: PhysicalAttestation`,
`zangbeto_anchor`, `nostr_event_id`, `execution_id`. That is exactly what `CanonicalReceipt` tried to
do with `Value`s; do it with the real types from `arp-types`.

**Then delete `CanonicalReceipt`.** It is the half-merge, and it is the third type.

**One `ReceiptKind`:** take ARP's 12 as the base (it is the superset and it has a documented
kind→verifier routing table), add the four `sovereign-types`-only concepts (`DipRoute`, `Observation`,
`LicenseGrant`, `Validation`) → **16 kinds**, with `Capture→TwinCapture` and `Scene→TwinScene` marked
as deprecated aliases so the rename is visible in one place instead of two.

**One chain primitive — and this is a real decision, not a cleanup.** BLAKE3 (SEP-1, `previous_receipt`,
what `receipt_store` enforces and what the conformance tests pin) vs SHA-256 (ARP's MANIFEST,
what the *deployed* broker verifies). Your own drift ledger already records this as the unresolved
"SHA-256-vs-BLAKE3 primitive conflict". **The receipt layer cannot have two chain primitives** — a
chain that mixes them is not verifiable end to end. My read: **BLAKE3**, because it is the SEP-1
declared primitive, it is what the store enforces, and it is what the tests pin; ARP's SHA-256 becomes
a migration, not a parallel format.

**Where the merged type lives:** `sovereign-types`, not `arp-types`. ARP becomes the *broker/transport*
(the HTTP service, the chain verification, the GIX bridge, the Zàngbétò anchor) and stops defining a
second receipt type. That also resolves the fork: `bridge.rs` and `zangbeto.rs` move to the broker
crate, which is what they are.

**Migration order:**
1. Publish the merged `ReceiptKind` (16) in `sovereign-types` with aliases for the renamed variants.
2. Extend `work_id::ActionReceipt` with the typed ARP fields; make `receipt_id` content-addressed and
   `work_id` required.
3. Delete `CanonicalReceipt`; port its callers.
4. Drop `arp-types::ActionReceipt` and `arp-types::ReceiptKind`; keep `arp-types` for `Principal`,
   `CapabilityRef`, and the broker wire format.
5. Fix the fork: point `sovereign-stack/Cargo.toml` at the real `arp-types`, or vendor `~/ARP` whole —
   but **the declared workspace must be the deployed workspace**, or the next build silently
   regresses production.
6. Correct the README (6→16, delete the `arp-core` crate from the diagram) and add `arp-broker`
   to the verification story, since it currently chains on a primitive `receipt_store` does not accept.

---

## 5. WHY THIS IS THE RIGHT NEXT THING

Every economic mechanism in the federation — emission, the 8 pools, the 3.69% tithe, settlement,
tier proof — is downstream of a receipt. Right now:

- **two chain primitives** (BLAKE3 vs SHA-256) are both live,
- **two receipt types** claim to be canonical, and **three exist**,
- the **deployed** broker is built from a tree **outside the declared workspace**,
- and ARP's envelope — the one that carries the jury verdict, the witness attestation and the hardware
  proof — **cannot reference a WorkID**.

This is the same disease as the odù-as-`digest[0]` bug, the three split schemes, and two things named
"OS": a concept implemented twice with the same name and different rules. It is the one collision
where the cost is not confusion but **unverifiable economics**.

And it is the natural first consumer of the control loop from
`~/docs/PAPERCLIP-TO-SOVEREIGN-STACK.md`: a `HeartbeatRun` that terminates in a receipt is only
detectable if there is exactly one receipt to terminate in.

<!-- SECTION-END -->
