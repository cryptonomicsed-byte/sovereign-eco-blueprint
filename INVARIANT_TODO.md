# INVARIANT_TODO.md — Machine-readable work queue for agents
# Generated: 2026-09-28; updated 2026-09-30
# Gate: 51 pass, 2 correctly failing (I-24, I-25)
# Note: I-24/I-25 were passing vacuously (I-24: stub function counted as "exists";
# I-25: passing because fabrication deleted). Gates now require positive presence.
# This is the truthful state — both are stubs not yet wired.
#
# Format: each block is one work item.
# Fields: id, status, blocking_on, file, what, why

---
id: E-circular
status: STUB
blocking_on: supply-graph traversal (DAG over agent→provider chains)
file: OSOVM/src/oso_vm.jl
what: >
  axis_circular in COMPUTE_PROOF independence calculation is hardcoded 0.0.
  Need to traverse the funded-by DAG: submitter may not have funded the provider
  through any chain. Requires a persistent agent-funding graph in GIX.
why: >
  Without the circular-supply axis, the independence score maxes at 0.667 even
  for completely independent providers. The gate exists but the third axis is
  unconditionally 0.0 (fail-closed is correct; open is wrong).
checker: I-55 (argument-provenance) would catch if wired with empty dict

---
id: E-53
status: PARTIAL
blocking_on: Zàngbétò POST /anchor endpoint
file: Omo-Koda2/omokoda-core/src/bridge/arp.rs
what: >
  make_receipt_json now calls bus::zangbeto::review_act() asynchronously and
  uses the returned verdict["id"] as zangbeto_anchor. However review_act()
  returns verdicts from POST /review — not a dedicated /anchor endpoint that
  returns a signed, chain-anchored ID. Until /anchor exists, the anchor is the
  verdict UUID (only meaningful if Zàngbétò is configured via ZANGBETO_URL).
why: >
  The OSOVM compute gate checks zangbeto_anchor != "" before minting Dopamine.
  Without a real anchor the gate can never fire from the arp.rs path in
  production. review_act() fail-opens (None when unreachable), so the gate
  fires only when Zàngbétò is wired.
checker: I-18 (anchor reachability)

---
id: E-tier-registry
status: DONE
blocking_on: none
file: OSOVM/src/server.jl, Vantage/backend/tier_engine.py
what: >
  DONE (2026-09-30):
  - POST /v1/tier-update: per-agent push from Vantage tier changes
  - POST /v1/tier-sync: bulk snapshot from Vantage on startup (clears stale entries)
  - Vantage tier_engine: _notify_tier_change() after every increment + admin_set_tier
  - Vantage main.py lifespan: _bulk_tier_snapshot() → sync_tiers() on startup
  - server_handlers_test.jl: 5 tests covering both endpoints
  - 53/53 invariants passing including I-49 (handler coverage)
why: >
  Tier gate for sim_to_real 5x bonus: T2+ required. Registry now stays warm
  on startup and on every tier change. No remaining boot-time gap.
checker: I-32 (anti-gaming caps enforced)

---
id: E-agent-registry
status: PARTIAL
blocking_on: SYNAPSE_TRANSFER opcode (design decision)
file: OSOVM/src/token_guards.jl, OSOVM/src/oso_vm.jl
what: >
  DONE (2026-09-30): ase_transfer_guard now calls !is_agent(recipient, _AGENT_REGISTRY_GLOBAL)
  instead of always returning true. Call site in oso_vm.jl passes the live registry.
  Agents self-register on first TOC_MINT; the guard is fail-open on cold start (empty registry).
  REMAINING: No SYNAPSE_TRANSFER opcode exists — is_agent() gate for peer Synapse transfers
  is infrastructure-ready but can never fire until the opcode is designed and added.
why: >
  I-3: ASE must never be held by agents. Guard now enforces this once registry is populated.
  I-4: Synapse transferable only between agent principals. Gate ready, awaiting opcode.
checker: I-3 (now enforced), I-4 (Synapse identity gate — awaiting SYNAPSE_TRANSFER opcode)

---
id: E-epoch-reset
status: STUB
blocking_on: Koodu-anchored BTC clock integration
file: OSOVM/src/oso_vm.jl
what: >
  _EPOCH_TALLY_GLOBAL and _EPOCH_COUNT_GLOBAL accumulate monotonically — they
  are never reset. Per-agent epoch caps and repeat limits therefore tighten over
  time rather than resetting every 7-day Koodu epoch. This is conservative
  (caps fire earlier, never later) but eventually blocks all minting.
  Need: at each 7-day BTC epoch boundary, reset both dicts atomically.
why: >
  PER_AGENT_EPOCH_CAP = 50M Dopamine / epoch. Without reset, an agent hits the
  cap permanently after ~50 GPU-hours of work.
checker: I-32 (epoch cap enforced)

---
id: E-witness-network
status: SPEC_ONLY
blocking_on: External Ed25519 witness node network
file: OSOVM/src/veilos_antispam.jl
what: >
  request_witness_votes() returns AntispamWitnessVote[] (empty stub). The
  7/12 quorum check always fails until a real external witness pool exists.
  Production path: broadcast sim_id + receipt_hash to registered witness nodes;
  each signs with its Ed25519 keypair and returns an AntispamWitnessVote.
why: >
  verify_witness_quorum requires 4+ of 7 approvals. With empty votes, quorum
  always fails, blocking VeilOS simulation rewards permanently.
checker: I-29 (quorum failure is real)

---
id: E-proof-value-gate
status: PARTIAL
blocking_on: quality measurement from external verification
file: OSOVM/src/oso_vm.jl
what: >
  quality = f1_score read from receipt_store (set by GPU_CONTRIBUTION).
  GPU_CONTRIBUTION stores whatever f1_score the caller provides in its args
  (oso_vm.jl ~line 2300). This is self-reported — the invariant comment notes
  it should come from verified ZangbetoReceipt. Until GPU_CONTRIBUTION verifies
  f1_score against an external proof, quality dimension is self-certifying.
why: >
  proof_value = difficulty × quality × novelty × verification × independence × utility.
  A self-reported quality = 1.0 inflates proof_value.
checker: I-19 (no scoring dimension from request args — currently passes via provenance chain)

---
id: E-synapse-transfer-opcode
status: MISSING
blocking_on: design decision
file: OSOVM/src/oso_vm.jl
what: >
  No SYNAPSE_TRANSFER opcode exists. The is_agent() gate for peer transfers
  is declared and wired in infrastructure, but there is no opcode that moves
  Synapse between agent balances. Until this opcode is added, Synapse can only
  be minted (TOC_MINT) and burned (via interpreter.rs burn_synapse).
why: >
  Synapse is declared transferable="agent_only". A transfer opcode is needed
  for agents to pay each other for services.
checker: I-4 (will test the new opcode when added)

---
# Summary table
# id                    | status      | effort  | blocker
# E-circular            | STUB        | medium  | GIX funded-by DAG
# E-53 (anchor)         | PARTIAL     | small   | Zàngbétò /anchor endpoint
# E-tier-registry       | STUB        | small   | Vantage bridge callback
# E-agent-registry      | PARTIAL     | n/a     | ase_transfer_guard wired; awaits SYNAPSE_TRANSFER opcode
# E-epoch-reset         | STUB        | small   | Koodu BTC clock integration
# E-witness-network     | SPEC_ONLY   | large   | external witness node deployment
# E-proof-value-gate    | PARTIAL     | medium  | GPU_CONTRIBUTION f1_score verification
# E-synapse-transfer    | MISSING     | medium  | design + opcode implementation
