# PAPERCLIP → SOVEREIGN-STACK / VANTAGE — graded extraction

2026-09-23. Target: `~/sovereign-stack` (Rust workspace, `972f4bb`, Society pillar / SEP-1) and
Vantage (Python FastAPI :8001). Source: the `~/paperclip` clone. Pattern-only.

---

## 0. WHAT SOVEREIGN-STACK ALREADY IS (read before planning any import)

`REPO_PLAYBOOK.md` states the governing rule, dated 2026-09-12:

> **"sovereign-stack = protocol crates only.** It is connective tissue between 32 repos — not an
> application. If you are writing business logic, stores, economy, governance, or perception loops and
> you think 'I'll put it in sovereign-node' — **you are wrong.**"

Workspace members (Cargo.toml): `sovereign-types`, `sovereign-runtime`, `ip-layer`, `dip`, `vcp`,
`twin-protocol`, `arp-types`, `arp-broker`, `ucx-protocol|provider|broker`, `swarm-types|broker`,
`witness-types|broker`, `sovereign-pipeline`, `sovereign-a2a`, `sovereign-node`, `sovereign-cli`,
`sovereign-os`, `mycelium-finetune`.

`CANONICAL_PILLAR_CONTRACT.md` = **SEP-1**, port 8080, MCP at `POST /mcp`:

> *"Every state transition MUST produce an `ActionReceipt` from `sovereign-types::work_id`."*

With these **already-specified** fields: `receipt_id` (BLAKE3 of canonical fields), `work_id`,
`principal_id`, `agent_id`, `action`, `input_hash`, `output_hash`, `timestamp_ms`, `signature`
(ed25519) — plus **SRP-1**: *"All receipts MUST be chain-linked via `previous_receipt`. The
`receipt_store` module maintains the chain and MUST reject receipts with a broken chain link."*

And the economics, already contracted: **OSOVM is the sole mint authority** · 1 Àṣẹ/minute
(1440/day, 525,600/yr) · **8 DistributionPools** · tithe **3.69% = 369/10_000** · **1440
SovereignWallet seats**.

---

## 1. WHAT ALREADY EXISTS — so do NOT import it from paperclip

This is the most important section, because the pasted doc proposes importing several things that
are already built and tested here.

**`sovereign-types/src/work_id.rs`** — `WorkId(pub String)`, `new(namespace, id)` →
`wk:{namespace}:{ulid}`, with namespaces `sim | real | hybrid | gov | license | capture | scene`.
Its own header comment states the division of labour:

> *"Vantage creates WorkIDs, Omo-Koda2 executes against them, OSOVM verifies them, Sui settles them."*

Verified on disk, not aspirational. `WorkId::namespace()` parses and asserts.

**`sovereign-types/src/work_claim.rs`** — the generalised verification primitive, and it cites an
earlier Hermes audit by name:

> *"WorkClaim — generalized verification primitive for the sovereign L1. **Replaces the GPU-specific
> `claimed_gpu_seconds` parameter in `is_fully_verified()`.** A WorkClaim carries WHAT was done, HOW
> to verify it, and WHO must corroborate. … Hermes audit: **'The verification layer, as built,
> verifies exactly one kind of thing.'**"*

`WorkDomain` = `GpuCompute | Simulation | SimToReal | PrintJob | AerialFlight | GroundRobot | SciSim
| SpatialCapture | Custom(String)`. This is the same `is_fully_verified()` whose Blocksim copy I
audited earlier today — the generalisation exists in the protocol crate already.

**`sovereign-types/src/governance.rs`** — not an empty shell: `EMISSION_PER_MINUTE_MIST` (1 Àṣẹ,
in mist units), `SOVEREIGN_SEAT_COUNT = 1440`, `DistributionPool`, `EmissionReceipt`, `EpochKind`,
`SimEligibility`, **`COUNCIL_SEAT_COUNT = 12`**, `SECTORS_PER_SEAT = 2`, **`SECTOR_COUNT = 24`**,
`CouncilSeat`, `Sector`, `ProposalStage`, `BinoVetoCategory`, `BinoSignOff`, `SovereignWallet`,
`GovernanceStrata`.

**`sovereign-runtime/src/`** — `capability.rs`, `chain.rs`, `device.rs`, `embodiment.rs`,
`evidence.rs`, `execution.rs`, `power.rs`, `principal.rs`, `receipt.rs`, `safety.rs`. Capability
chain, safety gates, evidence, power budget — present.

**`sovereign-runtime/tests/sep1_conformance.rs`** — the receipt spine is *tested*, not claimed:
receipt carries every SEP-1 field · `work_id_is_well_formed` (namespace asserted `"real"`) ·
`receipt_id_is_blake3_over_canonical_fields` · input/output hashes equal `blake3_of_json` of the
payloads · **`receipt_id_changes_when_payload_changes`** (*"payload is not covered by receipt_id"*) ·
signing populates the signature and flips `is_sep1_conformant()` · a malformed base64 key errors ·
**`denial_is_conformant_without_a_signature`** (`ActionOutcome::Denied`).

**`sovereign-a2a`** — already "A2A v1.0 agent card, task lifecycle, dispatch router, client".

**Consequence:** the pasted doc's proposals to (a) introduce WorkID, (b) make WorkID the canonical
cross-system identifier, and (c) extract paperclip's "task" model into a Work object, are **already
satisfied — and in a stronger form than paperclip's**. Paperclip's issue IDs are per-company UUIDs
with no cross-system protocol; `WorkId` is a namespaced, cross-pillar, receipt-anchored identifier
with BLAKE3 receipt chaining. **Nothing to import there. Do not touch that layer.**

---

## 2. THE GRADED VERDICT ON THE PASTED DOC

Verified against source. Buckets: ✅ confirmed · ⚠️ needs correction · ❌ not in the repo.

| # | Claim | Verdict |
|---|---|---|
| 0 | "control plane rather than an agent runtime" | ✅ `doc/GOAL.md`: *"We are the control plane, the nervous system, the operating layer."* README: *"Open-source orchestration."* |
| 1 | Company → Goal, Agents, Org chart, Projects, Issues, Budgets, Routines, Governance | ✅ all present. Org chart = `reportsTo` in AGENTS.md frontmatter, not a table. |
| 2 | Work model: assignee, parent task, project, goal, dependencies, status, comments, **execution locks**, work products | ✅ present — but **already beaten** by `work_id.rs` + `work_claim.rs` (§1). Import nothing. |
| 2 | "atomic checkout, two agents cannot claim the same task" | ✅ `AGENTS.md` §5 invariants: *"single-assignee task model"*, *"atomic issue checkout semantics"*. |
| 3 | Wake sources: "schedule, assignment, @mention, manual invocation, approval resolution" | ⚠️ **The real enum is 4 values, different names.** `packages/shared/src/validators/agent.ts:222` → `["timer", "assignment", "on_demand", "automation"]`. `@mention` is a **timeline edge kind** (`"delegation" \| "assignment" \| "mention"`) and approval resolution arrives as *wake context* (`PAPERCLIP_APPROVAL_ID`, `PAPERCLIP_APPROVAL_STATUS`, `PAPERCLIP_WAKE_COMMENT_ID`, `PAPERCLIP_WAKE_REASON`), not as a source value. Right shape, wrong enumeration. |
| 3 | Heartbeat: identity check → review → select → checkout → execute → update status | ✅ in substance. The agent-facing skill: *"You run in **heartbeats** — short execution windows… Each heartbeat, you wake up, check your work, do something useful, and exit. **You do not run continuously.**"* Env contract: `PAPERCLIP_AGENT_ID/COMPANY_ID/API_URL/RUN_ID` always, wake-context vars when relevant, and a **short-lived run JWT** for local adapters. |
| 4 | Org chart → Hive; roles, manager, capabilities, budget | ✅ `reportsTo`, `role`, `skills` in frontmatter; `.paperclip.yaml` carries `permissions.canCreateAgents`. |
| 5 | Approval gates: hiring, strategic plans, overrides, pausing, terminating, reassignment + audit trail | ✅ structurally (`approvals`, `approval_comments`, `join_requests`, `activity_log`). Exact gate list not enumerated in the docs I read. |
| 6 | Cost accounting at company/agent/project/goal/issue/provider/model + hard stops | ✅ `budget_policies` + `budget_incidents`; §5 invariant *"budget hard-stop auto-pause behavior"*. Levels not individually verified. |
| 7 | Control plane vs execution plane separation | ✅ and it maps cleanly onto your existing crate boundaries (§4). |
| 8 | "out-of-process plugin system with capability-gated host services, scheduling, tool exposure and UI contributions" | ⚠️ **Partly unverified.** `packages/plugins/` + **13** `plugin_*` tables exist (`config, state, jobs, webhooks, entities, database, logs, managed_resources, company_settings`). "Capability-gated host services" and "UI contributions" not confirmed from source. |
| — | "Don't import reputation" | ❌ **There is no reputation system in paperclip.** No table matches `reput|score|trust|rating`. That list item is a phantom — same failure class as the `DOPAMINE_MINT` opcode earlier today. |
| — | 20-item audit checklist | ⚠️ Reasonable but **mis-prioritised for you** (see §3): it omits the four things that actually matter — the Hermes adapter, durable continuation, the task watchdog, and the telemetry gate. |

**Missing from the doc entirely:** paperclip ships **`hermes_local` + `hermes_gateway` adapters** and a
`HERMES_GATEWAY_ONBOARDING.md` join flow — the single most relevant thing in the repo for a stack that
runs four Hermes instances. Also missing: *"Paperclip does not keep an agent process alive between
turns"* (durable continuation), the **task watchdog**, the **reflection coach**, and the fact that
**telemetry is opt-out to a Paperclip endpoint by default**.

---

## 3. THE REAL GAP LIST (verified absent from sovereign-stack)

Grepped the workspace for each concept; `target/` excluded. Right-hand column = where it landed.

| Concept | Hits in sovereign-stack | Reading |
|---|---|---|
| `status_decision` / decision→effects | **zero** | No record of *a decision* separate from *what it caused*. Paperclip splits these deliberately. |
| heartbeat / wakeup run model | none of ours — only `buzz-OG/crates/buzz-acp/*` (a fork of Block's Buzz) and unrelated FFN/shard files | **No heartbeat/wakeup primitive at all.** This is the real gap. |
| scheduler / reconciler | `buzz-OG` only | No stranded-work reconciliation. |
| budget policies / incidents | incidental in `tier.rs`, `mesh_envelope.rs`, `sui_anchor.rs` | No budget-as-entity, and no record of what a cap actually stopped. |
| memberships (`agent_memberships`, `project_memberships`) | incidental in `ip-layer`, `buzz-OG` | No multi-guild membership table. |
| approvals as first-class entities | `governance.rs` has `ProposalStage`, `BinoSignOff`, `ProposalStage` — **proposal** machinery, not *request-and-approve* machinery | Governance strata exist; approval *requests with comments* do not. |
| idempotency | `sovereign-node/tests/api.rs` | Idempotency is tested at the API boundary; there is no idempotency **key** on a wake. |
| agent config revisions | none | No versioned agent definition. |
| watchdog / verification-of-stopped-work | none | — |
| reflection coach / config-diff proposal | none | — |

**The one-sentence summary:** your *evidence* layer is ahead of paperclip's, and your *control* layer
is behind it. `sovereign-types` knows exactly what a receipt is and proves it in conformance tests;
nothing in the workspace knows what a *wakeup* is, what a *decision* is, or what happened when a
budget stopped work.

---

## 4. CRATE-LEVEL PLACEMENT (honouring THE ONE RULE)

Every paperclip pattern gets a home that respects *"protocol crates only; not an application."*

| Paperclip pattern | Lands in | Why there |
|---|---|---|
| Wakeup request record (`idempotency_key`, `coalesced_count`, actor, `run_id`) | **`sovereign-a2a`** | It already owns "A2A v1.0 agent card, **task lifecycle**, dispatch router". A wake IS a task-lifecycle transition. |
| Heartbeat run (finite: start → work → terminal result → exit) | **`sovereign-runtime`** | It already owns `execution.rs`, `chain.rs`, `receipt.rs`, `safety.rs`. A run is an execution unit; a run that ends must emit a receipt through the existing chain. |
| Continuation intent + stranded reconciliation | **`sovereign-pipeline`** (stage/phase) + a reconciler in **`sovereign-node`** | Continuation is a pipeline concept. The reconciler is daemon-shaped — and `sovereign-node` is explicitly *"THIN REFERENCE DAEMON ONLY"*, so the reconciler needs a **deliberate decision**, see §6. |
| Atomic claim enforcement | **`sovereign-types/src/work_claim.rs`** (exists) + `sovereign-node/src/receipt_store.rs` | The claim primitive exists; what is missing is a **claim store** that rejects a second claimant, the way `receipt_store` already rejects a broken chain link. |
| Budget policy + incident | **`sovereign-types`** (new module next to `governance.rs`) | It is an economic primitive. `tier.rs` already carries budget-ish fields — reconcile rather than duplicate. |
| Memberships | **`sovereign-types`** | A membership is an identity relation; `identity.rs` + `governance.rs` are the neighbours. |
| Approval request as an entity | **`sovereign-types/src/governance.rs`** — extend, don't add | `ProposalStage`/`BinoSignOff`/`GovernanceStrata` are already there. Add *request → comments → resolution*, not a parallel system. |
| Status decision → effects | **`sovereign-types`** | Domain primitive. Two records, deliberately separate. |
| Task watchdog (verification-shaped) | **`sovereign-runtime/src/evidence.rs`** + a gate in the act path | It is verification, and `evidence.rs` already exists. |
| Reflection coach | **Vantage** (application) — it produces a *reviewable diff*, which is UI/workflow | Per THE ONE RULE, proposing a change to an agent's definition is application logic. |
| Guild manifest as files | **Vantage** | Guilds are the civilisation interface. Not a protocol crate. |
| Durable continuation *policy* | **Vantage** | The *mechanism* is a crate; *which* work continues is application. |

**Note what this means:** only about half the paperclip patterns belong in `sovereign-stack` at all.
The rest are Vantage's. That is the correct outcome of THE ONE RULE, and it is why the pasted doc's
instinct to put the control plane "into Omo-Koda2" would have been wrong — Omo-Koda2 is the Agent
pillar, and the wakeup/dispatch layer is Society's (A2A) plus the Runtime's (runs).

---

## 5. BUILD ORDER

**1. `WakeRequest` in `sovereign-a2a`.** Cheapest, highest leverage, and it has a home already.
Fields: `idempotency_key`, `coalesced_count`, `source` (use paperclip's four real values —
`timer | assignment | on_demand | automation` — not the doc's five invented ones), `reason`,
`requested_by_actor_type|id`, `run_id`, `requested_at | claimed_at | finished_at`, `status`.
Wire the existing daemons through it before inventing anything downstream.

**2. `ClaimStore` beside `receipt_store.rs`.** You already wrote the hard half: `receipt_store` rejects
a broken chain link. Add the same refusal for a second claimant on one `WorkId`. That single change
turns paperclip's "atomic checkout" invariant into a mechanism rather than a convention — and it is
what your 36-daemon fleet has no protection against today.

**3. `HeartbeatRun` in `sovereign-runtime`.** A run is finite and terminates in a receipt. Because
`receipt.rs` and the SEP-1 conformance tests already exist, a heartbeat run that ends without a
receipt becomes *detectable* — which is the Universal Execution Reflex ("no ActionReceipt = P0 bug")
finally given a runtime to enforce it in.

**4. The watchdog in `evidence.rs`,** opt-in per work tree, verification-shaped. Target the receipt
tree first, since every economic mechanism downstream of it (emission, pools, tithe, settlement)
depends on receipts that are currently produced by the kernel and audited by a human.

**5. `StatusDecision` / `BudgetPolicy` / `BudgetIncident` in `sovereign-types`.** Last, because they
need the run model from steps 1-3 to have anything to record.

**Vantage-side, in parallel:** the guild manifest files, and the reflection coach.

---

## 6. THE ONE DECISION THIS FORCES

`REPO_PLAYBOOK.md` forbids business logic in `sovereign-node` — but a *reconciler* that
"reaps orphans → promotes due retries → resumes queued work → reconciles stranded assignments" on
every tick is neither pure protocol nor pure application. Paperclip put its equivalent in
`server/src/services/heartbeat.ts` — the monolithic service layer you deliberately do not have.

So before step 3: **decide the home of the reconciler.** Three honest options:

- a new thin `sovereign-control` crate whose only job is scheduling + reconciliation (clean, but a
  21st workspace member);
- `sovereign-node` with a written exception in `REPO_PLAYBOOK.md` (fastest, erodes the playbook);
- Vantage, as an application service that drives crates (fits the playbook, but makes the VPS Python
  process load-bearing for kernel-side continuation).

**My read: the first.** The reconciler is the one piece whose absence breaks every other piece, it is
strictly protocol-adjacent, and adding a *named* crate is how you avoid the accidental-service-layer
drift that put paperclip at 5,629 open issues.

---

## 7. WHAT STAYS OUT — permanently

❌ Paperclip's Company model · ❌ its agent identity · ❌ its task IDs · ❌ its governance authority ·
❌ its budgets as economic truth · ❌ its execution authority · ❌ its memory model · ❌ its settlement.
(Note: ❌ **its reputation** — that does not exist in paperclip; do not plan around removing it.)

And the hard gate: **paperclip's telemetry is opt-out and sends to a Paperclip endpoint by default.**
Never adopt the server or its client telemetry path into anything sovereign. Read it, mine it, don't
run it.

**The corrected one-liner:** you don't need paperclip's work model, its IDs, or its governance — you
already built stronger versions of all three. You need its **control loop**: wakeup → finite run →
terminal result → continuation or stranded-reconciliation. That is the layer `sovereign-types` does
not contain, and it is the layer every economic mechanism downstream is quietly waiting for.

<!-- SECTION-END -->
