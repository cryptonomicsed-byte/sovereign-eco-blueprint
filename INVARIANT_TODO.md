# INVARIANT_TODO.md — Machine-readable work queue for agents
# Generated: 2026-09-28
# Gate: 53 checks, ALL PASS
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
status: STUB
blocking_on: Vantage agent-registration bridge callback
file: OSOVM/src/oso_vm.jl
what: >
  _TIER_REGISTRY_GLOBAL (agent_id → trust tier Int) starts empty every process
  restart. The check_sim_to_real_tier gate correctly fails-closed (empty registry
  → tier 0 → DENY for sim_to_real), but no path populates it yet. Need a
  Vantage bridge callback that writes tier assignments on agent registration or
  heartbeat.
why: >
  Tier gate for sim_to_real 5x bonus: T2+ required. Without registry population,
  sim_to_real always denies even for legitimate T2 agents.
checker: I-32 (anti-gaming caps enforced)

---
id: E-agent-registry
status: STUB
blocking_on: Vantage principal registry API (is_agent query)
file: OSOVM/src/token_guards.jl, OSOVM/src/oso_vm.jl
what: >
  is_agent(address, agent_registry) checks _AGENT_REGISTRY_GLOBAL. Agents
  self-register on first TOC_MINT. But peer SYNAPSE transfers (when that opcode
  exists) need the recipient to be pre-registered. Currently no SYNAPSE_TRANSFER
  opcode exists — this gate will matter when one is added.
  Also: ase_transfer_guard still returns true (stub) — should call !is_agent()
  once the registry is populated reliably.
why: >
  I-4: Synapse is transferable only between agent principals. Human wallets must
  not receive Synapse. The registry is the enforcement point.
checker: I-4 (Synapse identity gate)

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
# E-agent-registry      | STUB        | small   | ase_transfer_guard + SYNAPSE_TRANSFER opcode
# E-epoch-reset         | STUB        | small   | Koodu BTC clock integration
# E-witness-network     | SPEC_ONLY   | large   | external witness node deployment
# E-proof-value-gate    | PARTIAL     | medium  | GPU_CONTRIBUTION f1_score verification
# E-synapse-transfer    | MISSING     | medium  | design + opcode implementation
