# Attestation · Witness Quorum · Heterogeneous Consensus · Jev
## Assessment of the three pasted proposals against the live codebase

Date: 2026-09-27
Method: every claim checked against source in ~/OSOVM, ~/Omo-Koda2, ~/Vantage,
~/fomopulse-convergence. Where the proposal and the code disagree, the code wins.
Nothing here is relayed — each verdict carries a file:line.

Repos referenced (all public, github/cryptonomicsed-byte):
  OSOVM            main    Julia   Ọ̀ṢỌ́VM — the Heart VM, Àṣẹ mint authority (SPP-1)
  Omo-Koda2        main    Rust    Ọmọ Kọ́dà — Core Agent OS (SRP-1); remote = omokoda-agent
  Vantage          main    Python  Society — settlement (SEP-1)
  fomopulse-convergence    Python  signal engine (research, no execution)

---

# PART 0 — What was sent

Three essays plus framing, over three turns:

  ESSAY A  "Attestation as the Agent OS trust primitive"
           attestation → witnesses → quorum → anti-gaming → Sybil → receipts →
           attestation ≠ consensus → weighted attestations → heterogeneous quorum

  ESSAY B  "Agents as first-class consensus participants"
           mixed human-machine attestation → tiers → graduated consensus →
           agents as witnesses (mower, vehicles) → independence domains →
           physical/device class → blockchain as output

  ESSAY C  "Jev inside the consensus/attestation layer"
           Jev as judgment layer → decomposed multi-question decisions →
           Jev as evidence-quality evaluator (not witness) → evidence-based
           heterogeneous consensus → three layers → primitive mapping table →
           decision fabric

  SHORT    "TypeSafe emphasizes Jev's probabilities are consumed by surrounding
           software which chooses thresholds — matches our architecture almost exactly."

---

# PART 1 — Claim-by-claim

## 1.1 Attestation

CLAIM: an attestation is "I observed this state/event/action, under these
conditions, and here is evidence that lets others verify my claim."

EXISTS: `OSOVM/src/zangbeto_receipts.jl:37` `struct ZangbetoReceipt` — receipt_id,
sim_id, creator_wallet, timestamp, veil_ids, opcodes_executed, entity_count,
step_count, f1_score, energy_drift, robustness, referent_id, execution_hash,
trajectory_hash, receipt_hash, block_height, chain_target.

VERDICT — **BUILT, and closer to the proposal than the proposal realizes.**
The struct carries the claim (what ran), the evidence (execution_hash,
trajectory_hash), the conditions (veil_ids, opcodes), and the binding
(receipt_hash). `referent_id` (:56) is the withheld artifact the score was
measured against — the field that makes a score falsifiable. Its own comment
states the precondition: *"Must be set by a non-claimant; absent → empty string
(score is unfalsifiable)."* That is Essay A §1's definition, implemented, with
the correct caveat attached.

GAP: the non-claimant requirement is a **comment, not a check**. Nothing enforces it.

## 1.2 Witnesses

CLAIM: independent observers each produce an attestation; the signature proves
the witness claims it, not that it happened.

EXISTS: `WitnessVote` at `zangbeto_receipts.jl:67` — witness_id (0-11),
receipt_hash, approved, witness_hash, voted_at. Comment on the field:
*"Deterministic witness signature"*. Twelve witnesses, `QUORUM_REQUIRED = 7`
(:34).

VERDICT — **THE STRUCTURE IS THERE; THE WITNESSES ARE NOT.**
Two independent implementations, both non-functional as witnesses:

  (a) PRODUCTION PATH — `zangbeto_receipts.jl:369`
      ```julia
      function request_witness_votes(receipt_hash)::Vector{WitnessVote}
          # External witness nodes are not yet wired.
          WitnessVote[]
      end
      ```
      Returns empty. `check_quorum` (:381) therefore fails **100% of the time**.
      The docstring at :359 says "Contact the 12 independent Zàngbétò witness
      nodes" — aspirational prose over an empty function.

  (b) SIMULATION PATH — `veilos_antispam.jl:263-277`
      ```julia
      witness_ids = shuffle(1:WITNESS_TOTAL)[1:WITNESS_QUORUM]
      for witness_id in witness_ids
          vote = check_f1_threshold(f1_score)
          # Create signature (mock)
          signature = "0x$(bytes2hex(sha256("$witness_id:$sim_id:$f1_score"))[1:32])"
      ```
      Three defects in four lines:
        1. `shuffle(1:12)[1:7]` invents witness identities by shuffling integers.
           There is no pool. The "12 independent nodes" are array indices.
        2. Every vote is `check_f1_threshold(f1_score)` — a deterministic function
           of **the claimant's own reported F1**. All 7 vote identically by
           construction. Unanimity is arithmetic, not agreement.
        3. The signature is SHA-256 of public inputs, self-labelled `(mock)`.
           A hash is not a signature; anyone can compute it.

A witness set that cannot disagree with itself is not a witness set. Asked
"is the evidence sufficient?" over this, any judgment engine returns a
confident number about fabricated indices.

## 1.3 Witness quorum

CLAIM: quorum = how much independent confirmation is required before the system
accepts something. "An attestation is evidence. A quorum is collective agreement
about evidence."

EXISTS: `check_quorum(votes) = (count(v -> v.approved, votes) >= QUORUM_REQUIRED, approvals)`
— a pure vote count. `QUORUM_REQUIRED = 7` of 12.

VERDICT — **BUILT, but it is exactly the thing Essay A warns against.**
It counts signatures. It has no notion of independence, domain, evidence class,
timing, or provenance. Essay A §3 proposes a richer predicate:

  quorum = 3 independent witnesses
         + ≥2 distinct execution domains
         + no shared identity cluster
         + valid evidence hashes
         + temporal consistency

None of those five terms exists in the code. The current quorum is
`approvals >= 7`, nothing more.

NOTE: the Sui Seal bridge has a threshold concept with the same problem —
`seal_bridge.jl:38` documents `SEAL_THRESHOLD  e.g. "2" for 2-of-3 (default "1")`.
**The default is 1.** An unconfigured threshold of one is a quorum of one.

## 1.4 Anti-gaming

CLAIM: a naïve system is gamed by creating 1,000 fake witnesses; the system must
distinguish "number of signatures" from "number of independent sources of evidence."

EXISTS: nothing. `grep -riE "sybil|collusion|operator|ownership|domain_authority|lineage"
OSOVM/src` returns only unrelated hits (`:ANCESTRAL_CALL` lineage opcode 0xad,
`:EQUITY` ownership share 0xc6 — both divination/business opcodes, not
anti-Sybil machinery).

The single closest thing: `oso_vm.jl:2507`
```julia
independence = (!isempty(provider_id) && provider_id != agent_id) ? 1.0 : 0.0
```

VERDICT — **ABSENT, and the one substitute is itself an instance of the defect
this whole codebase is being hardened against.** "Independence" is a single
string inequality, binarised to 1.0/0.0. There is no ownership field, no
operator, no hardware lineage, no funding graph, no credential authority.

`independence = ... ? 1.0 : 0.0` is a plausible-looking number written under a
name that implies measurement.

## 1.5 Sybil resistance — the six independence axes

CLAIM (Essay B §"critical distinction"): judge independence across identity,
execution, evidence, temporal, resource, historical.

EXISTS: one axis (identity, crudely), as a string compare. Plus
`check_self_deal(buyer, gpu_host, birther)` in `OSOVM/src/token_guards.jl:107` —
three roles, one boolean.

VERDICT — **THE MOST VALUABLE IDEA IN ALL THREE ESSAYS, AND IT IS ABSENT.**
The stack has 3 roles and 1 axis. The proposal has 7 domains. The gap is real
and it is the actual answer to Sybil/collusion.

CRUCIAL FRAMING: this is **a registry problem, not a model problem.** It cannot
be solved by adding an intelligence layer; it requires recording who owns/operates
what. Buildable with no Jev at all.

## 1.6 Attestation beyond transactions

CLAIM: attest to actions, tool use, retrieval, observation, policy adherence,
artifact production, authorization, verification.

EXISTS — and this is where the stack is **well ahead of the proposal**:

  Aether/IfáScript operation taxonomy — `Omo-Koda2/omokoda-core/src/ifscript_gate.rs:59,67`
    "Identity operations: birth, keypair generation, profile management."
    "Economic records: ARP receipts, Zàngbétò attestation, settlement."

  Nostr-native attestation layer — `omokoda-core/src/ip_layer.rs`
    line 32: "Nostr kind 1901 — Creation Receipt, per ip-layer's schema."
    line 37: "Nostr kind 1902 — Attestation, per ip-layer's schema."
    line 115: `Publish a Creation Receipt (kind 1901) at birth.`
    line 159: `Publish an Attestation event (kind 1902) linking the IP Root to the…`
    published via `publish_attestation(...)` (called from interpreter.rs:2353)

VERDICT — **BUILT, and the essays never mention it.** There is already a signed,
relay-published, addressable attestation substrate with two event kinds: a
creation receipt at birth and an attestation linking to an IP root. Any proposal
for "attestation as the Agent OS trust primitive" must start by reading
`ip_layer.rs`, not by designing a new one.

## 1.7 Receipts

CLAIM (Essay A §7): a cryptographic action receipt with inputs_hash, outputs_hash,
tools_used, evidence[], previous_state, new_state, signature; then witness
attestations referencing `receipt_hash`.

EXISTS: `ZangbetoReceipt` (above) + `ReceiptBundle` at `zangbeto_receipts.jl:77`:
  receipt, votes, quorum_met, total_approvals,
  status ("VERIFIED" | "SLASHED" | "QUORUM_FAILED"),
  **seal** — "Layer 1: SHA-256 tamper-evidence commitment (always present, VM-native)"
  **seal_dek_fingerprint** — "Layer 2 ('dual seal'): SHA-256 fingerprint of a real
  DEK fetched from Sui Seal's decentralized key servers … Empty string when SEAL_*
  env vars aren't configured (**fail-open**, same as Omo-Koda2's seal_bridge.rs)"

VERDICT — **BUILT, and BETTER than the proposal's shape** — a two-layer seal
(SHA-256 always, plus a real decentralized-key-server DEK) plus a status enum
including SLASHED. The proposal's receipt is a flat JSON blob; this is a bundle
with a lifecycle.

**BUT: the dual seal is documented FAIL-OPEN.** Unconfigured ⇒ empty string ⇒
silently degrades to Layer 1 only. That is the favourable-default family
(I-20/I-46). The comment is honest, which is why it's survivable — but a seal
that silently weakens is not a seal.

## 1.8 Attestation ≠ consensus

CLAIM: attestation = "I observed X"; quorum = "enough observers attest X";
consensus = "network agrees X is canonical"; finality = "not reverted."
Composable, but you don't need chain consensus for every attestation.

EXISTS and CONFIRMS the proposal's instinct — the stack already separates these:
  - attestation/quorum   = Zàngbétò, `zangbeto_receipts.jl`
  - ordering/settlement  = SEP-1, `sovereign-stack/CANONICAL_PILLAR_CONTRACT.md:14`
  - Àṣẹ issuance          = the clock, `abci_endblock.jl`
  - chain anchoring      = optional; `chain_target` ∈ {"sui","arweave","ethereum"} (:64)

And `OSOVM/CANONICAL_PILLAR_CONTRACT.md:86`: *"Tithe (3.69%) is deducted by the
**settlement layer, not OSOVM**."*

VERDICT — **CORRECT AND ALREADY ARCHITECTED.** The proposal's "attestation layer
above a blockchain, where the chain provides immutable ordering" is precisely the
existing 3-pillar federation: OSOVM attests, Vantage settles, the chain anchors.
`chain_target` being a field rather than a hard dependency is the proposal's
point, already built.

## 1.9 Weighted attestations

CLAIM: weight each witness, but "even that can be gamed if weight simply comes
from token ownership." Proposed:
  attestation_weight = identity_integrity × historical_accuracy × independence
                     × evidence_quality × stake/reputation × domain_authority

EXISTS: the **identical shape**, already in production, already broken:
`oso_vm.jl:2514`
```julia
proof_value = difficulty × quality × novelty × verification × independence × utility
mint_eligible = value >= 0.3
```
Six factors, multiplied. `independence` ∈ {1.0, 0.0}. `quality` = 0.0.
`novelty` pinned 1.0.

VERDICT — **THIS IS THE MOST IMPORTANT FINDING IN THE WHOLE ASSESSMENT.**

The proposal's trust function is structurally identical to `proof_value`, and
`proof_value` **demonstrates the failure mode**:

  A product containing a 0.0 is 0.0 — an absorbing element. Because `quality`
  is uninstrumented (0.0), the entire product is 0.0, which is why
  COMPUTE_PROOF is inert today and why that inertness was declared permanent
  (Decision A).

Six heterogeneous, correlated, mostly-uninstrumented judgments multiplied is not
a trust score. It is a score-shaped number that collapses to zero the moment one
instrument is missing — and a zero looks like a strict judgment rather than a
missing measurement.

Critically: the proposal's six terms are **not independent**. "identity_integrity"
and "independence" and "domain_authority" are all functions of the same underlying
registry. Multiplying correlated probabilities overstates confidence twice.

If Jev's multiple judgments (see 1.20) are combined this way, the same death
follows. **The combination rule must be stated, and it must not be a product.**

## 1.10 The Agent OS trust primitive

CLAIM: Attestation/Witness/Quorum should be a foundational subsystem, not bolted
onto the blockchain layer. "The blockchain becomes an output of the consensus
architecture rather than the architecture itself."

EXISTS: **This is Zàngbétò.** Per the naming authority
(`references/naming-conventions.md`): *"Zàngbétò (Rust, Security Audit)"*, and in
the federation *"Zàngbétò = 4th supporting layer beneath all three."*

VERDICT — **ALREADY ARCHITECTED, WITH A NAMED LAYER.** Essay A independently
describes the layer that already exists and has a name and a place in the
federation. The proposal's closing line — *"consensus over evidence, not merely
consensus over signatures"* — is a good statement of Zàngbétò's purpose.

## 1.11 Mixed human-machine attestation / graduated consensus

CLAIM (Essay B): Tier 1 agent quorum (3 of 5), Tier 2 human quorum (2 of 3),
Tier 3 cross-domain (3/5 agents AND 2/3 humans); graduated by risk.

EXISTS: **NOTHING. There is no human/agent distinction in the receipt layer.**

This is not an oversight in the code — it is a **blocked dependency, named in the
gate**. `I-4`'s blocker string, verbatim:

  "Vantage principal registry API — is_agent() cannot return correct results
   without it"

and from the gate's own I-3 evidence:
  "(no human/agent distinction anywhere in the token layer)"

VERDICT — **UNBUILDABLE TODAY, FOR A REASON THE ESSAY DOES NOT MENTION.**
Essay B's entire tier structure rests on a human/agent classifier that does not
exist. Note also that Essay B's *own critique* — "six nominally independent
participants could actually be controlled by one entity" — applies with full
force here, because the system cannot currently tell a human from an agent, let
alone who operates either.

## 1.12 Agents as witnesses (mower, vehicles)

CLAIM: a mower attests GPS trajectory, motor telemetry, geofence events, camera
observations; another machine verifies; a human approves payment. Vehicles
exchange signed intent attestations at intersections.

EXISTS: `TeeQuote` + `verify_quote` in `OSOVM/src/nautilus_attestation.jl`, and
`code_measurement_of_engine()` = SHA-256 of `veilsim_engine.jl` itself, recomputed
at call time. Plus `attest_f1_score`.

VERDICT — **THE PATTERN EXISTS IN THE CORRECT PLACE AND IS HONESTLY SCOPE-LIMITED.**
`nautilus_attestation.jl:1-17` is the best-documented module in the codebase:

  "checks a TEE quote's code measurement against an expected value and derives a
   key from the quote's own fields. Honest about what this verifies — it checks
   that the code measurement matches (and thus binds the attestation to a specific,
   named build of the engine), but it does **NOT verify a real hardware attestation
   signature** (SGX/TDX/AWS Nitro) yet, since no real enclave is deployed anywhere
   in this ecosystem. Once one is … the seam is already correct, only the quote's
   provenance upgrades."

That is the model for how every stub in this ecosystem should be written: state
exactly what is verified, what is not, and that the seam is right.

The mower/vehicle examples are **structurally identical** to this:
`code_measurement_of_engine()` is the mower's "which build ran"; `TeeQuote` is the
device's observed state; `verify_quote` is the second machine's independent check.
The proposal's physical-agent trust network is this module with `TeeQuote`'s fields
sourced from hardware sensors instead of the current stub.

## 1.13 Independence domains

CLAIM: ENTITY → ownership · operator · hardware · software lineage · network ·
funding · credential authority. Quorum should require N independent *domains*,
not N signatures.

EXISTS: nothing (see 1.4/1.5).

VERDICT — **THE GENUINELY ADDITIVE IDEA. Adopt it.**
It is the correct answer to `check_self_deal`'s narrowness (3 roles) and
`independence`'s single axis. It is the prerequisite for 1.11's tiers and 1.17's
device class. And it is **pure infrastructure — no model required.**

## 1.14 Heterogeneous quorum / physical reality class

CLAIM: participants may be humans, agents, robots, drones, vehicles, IoT,
organizations, smart contracts, infrastructure. The engine asks "do I have
sufficient independent attestations from the required classes, supported by
verifiable evidence?" not "how many signatures?"

EXISTS: `ifscript_gate.rs` classifies operations by layer
(Identity / Economic / …), and the 7 Hermetic Principles are enforced with three
levels — **3 Hard** (Correspondence, Polarity, CauseEffect), **1 Soft**
(Vibration), **3 AuditOnly** (Mentalism, Rhythm, Gender):

  ifscript_gate.rs:426-434
  | Principle      | Enforcement | Where enforced        |
  | Mentalism      | AuditOnly   | soul vs action fn     |
  | Correspondence | Hard        | default_gate()        |
  | Vibration      | Soft        | here (odu_id=0 tier>1)|
  | Polarity       | Hard        | default_gate()        |
  | Rhythm         | AuditOnly   | default_gate()        |
  | CauseEffect    | Hard        | here (exec at tier 2+)|
  | Gender         | AuditOnly   | here (vessel balance) |

VERDICT — **THE GRADED-ENFORCEMENT MECHANISM ALREADY EXISTS, ON A DIFFERENT AXIS.**
The stack already has a first-class notion of "how strictly does this rule bind,"
(Hard/Soft/AuditOnly). The proposal's "required classes of participant" is the
same pattern applied to *who* rather than *what*. Reuse `ifscript_gate.rs`'s
enforcement-level enum rather than inventing a parallel vocabulary.

## 1.15 Blockchain as output, not architecture

CLAIM: chain provides optional immutable settlement for state the OS has already
established.

EXISTS: `chain_target::String  # "sui", "arweave", "ethereum"` — a field, not a
dependency. SEP-1 settlement is separate from OSOVM (pillar contract, verified).

VERDICT — **BUILT.** Already the architecture. Nothing to change.

## 1.16 Jev as the judgment layer

CLAIM (Essay C): insert Jev at decision points inside the quorum engine —
"Is evidence sufficient? Is witness independent? Is action consistent? Is
escalation required?" — between attestations and the policy engine.

EXISTS: Jev = `POST https://api.typesafe.ai/v1/systemone`, `Bearer <key>`,
`model: "jev-latest"`. Three closed-set primitives: `noul` (P(yes)), `choice`
(one of N + full distribution), `score` (ordered levels + distribution). Every
answer carries a distribution AND a separate confidence;
`confidence = (n·peak − 1)/(n − 1)` for choice. $0.042/MTok input, 70–500ms,
batching, early access.

VERDICT — **RIGHT BOUNDARY, WRONG LAYER FOR NOW.**

The two questions Jev must never be asked, per Essay C §4:
  "Noul: Is witness A independent of witness B?"
  "Choice: Which witness set should be consulted?"

Both are **graph properties of a registry**, not judgments about evidence content.
The stack's entire independence signal is a string inequality (`oso_vm.jl:2507`).
A stateless API cannot know who operates whom; that information is not in the
input and cannot be inferred from it. Asked anyway, Jev returns a confident number
that is *structurally incapable of being about independence* — the same defect
shape as every fabricated number above.

Where Jev legitimately lands: judging **content** consistency — does this telemetry
support the claimed action, is this trajectory plausible, is this receipt
internally contradictory. That is genuinely useful and genuinely unavailable today.

## 1.17 Multiple independent Jev judgments

CLAIM: decompose into five narrow questions (0.99, 0.96, 0.98, 0.07, 0.94), then
"code, not Jev, applies the quorum rules."

VERDICT — **CORRECT PRACTICE, MISSING THE ONE PARAGRAPH THAT MATTERS.**
The essay never states the combination rule. See 1.9: a product of heterogeneous
correlated judgments kills the signal (live proof: `proof_value` is 0.0 because
`quality` is 0.0). The rule must be gate-don't-multiply, or a log-odds sum with
policy-owned weights. Never a plain product.

Also: "Is the vehicle authorized" and "is the evidence sufficient" are correlated
by construction — the second largely presupposes the first.

## 1.18 Jev is not the witness

CLAIM: "Witness X produced claim C and evidence E. The decision layer evaluates
whether E satisfies the policy." Jev evaluates evidence quality; Jev is not the
source of truth.

VERDICT — **CORRECT AND IMPORTANT.** It matches the placement rule already
established: Jev goes where the stack *invents* a number, never where it *verifies*
one; Jev output is *cited by* settlement, never an input to it.

## 1.19 Jev confidence scoping

CLAIM (Essay C §5): "0.97 is not 97% chance the transaction happened; it's a model
judgment about the defined question." Receipt should carry decision_model,
question_hash, state_hash, policy.

VERDICT — **THE SHARPEST PART OF ALL THREE ESSAYS.** Scoping the number to a named
question is exactly what makes Jev harder to misuse than a raw score.

ONE GAP: the proposed audit record has `state_hash` but **not the judged input**.
A hash binds; it does not attest. If `state_hash` covers a state containing
fabricated witness strings, the record certifies a well-formed judgment about
fiction — precisely the I-37 lesson (the seal covers receipt_hash + approvals, so
it certifies the record didn't change, not that the claim is true).

## 1.20 Three-layer model (evidence → intelligence → protocol)

CLAIM: Layer 1 evidence (what the world provided), Layer 2 intelligence (what it
implies — Jev), Layer 3 protocol (deterministic settle/hold/reject).

EXISTS: the split is real in the codebase but the layers are **collapsed**:
  - Layer 3 is implemented (`check_quorum`, `authorize_toc_mint`)
  - Layer 2 is partly implemented (`verify_quote`, `f1_score` scoring)
  - Layer 1 is **empty** (`request_witness_votes` returns `[]`)

VERDICT — **CORRECT MODEL, AND IT IDENTIFIES THE ACTUAL GAP.** But note the
ordering consequence: the stack is missing Layer 1, not Layer 2. Adding Jev adds
intelligence on top of an empty evidence layer. Build Layer 1 first.

## 1.21 Jev primitive mapping table

CLAIM: Is receipt valid → Noul; witness independent → Noul; evidence contradicts →
Noul; which verification path → Choice; which witness set → Choice; how strong is
evidence → Score; how risky → Score; how much oversight → Score; should settle →
Choice/Noul.

VERDICT — **8 OF 9 MAP CLEANLY. Two are misplaced** ("witness independent" —
registry property, see 1.16; "which witness set should be consulted" — routing over
a registry that does not exist).

The three primitives map onto three *existing invented numbers* in the stack
(assessed separately, in the signal/trading context):
  noul   → the seven mycelium miner `confidence` fields (7 hand-picked formulas,
           2 hardcoded literals), `score_signal_quality` (`len(content)/160 +
           keyword_density`), fpconv's five manipulation filters
  score  → fpconv's `strong/watch/note/noise` ladder — structurally identical
           (ordered levels), with hand-cut constants 55/35/20
  choice → "which of these N candidate tokens is best" — where the current stack
           argmaxes a composite and **structurally cannot say "none of these"**

## 1.22 Decision fabric / Agent OS version

CLAIM: Jev belongs as "a fast probabilistic judgment engine inside the
evidence → attestation → quorum pipeline"; not the blockchain, not the agent, not
the witness.

VERDICT — **CORRECT IN SHAPE, PREMATURE IN SEQUENCE.** The pipeline's upstream
half does not exist. See PART 4.

## 1.23 "Matches our architecture almost exactly" (the TypeSafe threshold stance)

CLAIM: TypeSafe emphasizes Jev's probabilities are consumed by surrounding software
which chooses thresholds — matching our architecture.

VERDICT — **TRUE AT THE INTERFACE, FALSE AT THE AUTHORITY. The authority is the point.**

Where thresholds actually live:
  veilos_antispam.jl:249   `f1_score >= F1_THRESHOLD`         module literal (0.777)
  signals.py:107/109       `score >= 55` / `score >= 35`      module literals
  Vantage/config.py:138    `PUMPFUN_SCAN_CONVICTION = 0.72`   `# >0.7 → auto-order in ingest`

Three thresholds, three modules, **none policy-owned.** There is no constitutional
threshold table. So "the surrounding software that chooses thresholds" is whichever
module happens to contain the comparison — and one of them also fires real orders
(`trading.py:2097`: *"Conviction is a 0–1 confidence, and >0.7 auto-creates a real
order"*).

Worse, in the antispam path the input to the comparison is **chosen by the party
being judged**: `vote = check_f1_threshold(f1_score)` with claimant-reported
`f1_score`. A fixed cutoff on a self-reported quantity is functionally identical to
letting the subject pick the cutoff — the exact inversion TypeSafe's separation
exists to prevent.

SECOND, AND THE PART THE ESSAY MISSES: **a threshold is only choosable where ground
truth exists.** TypeSafe hands over the responsibility without the ability to
discharge it.
  - Trading/signal path: ground truth EXISTS (resolved outcomes, P&L, is_dust,
    later venue verdicts) → 0.72 can be *derived* by measuring precision/recall.
  - Attestation path: no witness network, no resolved outcomes, quorum fails 100%
    → no ground truth → any threshold is unfalsifiable.

So trading is the only place the stack can currently honour the contract TypeSafe
requires of integrators.

---

# PART 2 — What the essays missed that already exists

1. **Nostr-native attestation** — kinds 1901 (Creation Receipt, at birth) and 1902
   (Attestation, linking IP Root). `ip_layer.rs:32/37/115/159`. Signed, addressable,
   relay-published. The essays design a new attestation substrate that is already built.
2. **The dual seal** — SHA-256 tamper-evidence (always) + a real DEK from Sui Seal
   decentralized key servers, with a `SLASHED` status in the lifecycle.
   `zangbeto_receipts.jl:77-90`.
3. **Zàngbétò is the 4th federation layer** — the essay's "Agent OS trust primitive"
   is a named, placed layer.
4. **Graded enforcement exists** — Hard/Soft/AuditOnly over 7 Hermetic Principles,
   `ifscript_gate.rs:426-434`. Reuse rather than reinvent.
5. **`referent_id`** — the withheld-referent binding is already a field, with the
   non-claimant precondition documented (`zangbeto_receipts.jl:54-56`).
6. **`chain_target`** — chain-as-output is already a field, not a dependency.
7. **`authorize_toc_mint` requires verification in Rust** — `economics.rs:181`
   returns Err "work is not fully verified (osovm_proof / witnesses / zangbeto
   required)". **The gate the essays ask for exists in Rust and is absent in the
   exposed Julia path** — TOC_MINT (0x54) was demonstrated minting 1,000,000 with
   no gate consulted. Two implementations, one gated.

---

# PART 3 — Findings that change the answer

| # | Finding | Evidence | Consequence |
|---|---------|----------|-------------|
| 1 | Witnesses are fabricated indices whose votes derive from the claimant's own F1, mock-signed | `veilos_antispam.jl:263-277` | No evidence layer exists to judge |
| 2 | Production witness path returns empty; quorum fails 100% | `zangbeto_receipts.jl:369` | The attestation path is dead, not weak |
| 3 | `independence` is a binarised string compare | `oso_vm.jl:2507` | Independence is currently unmeasured |
| 4 | `proof_value` is a product; one 0.0 factor kills it | `oso_vm.jl:2514` + `quality=0.0` | Any multiplicative trust function dies the same way |
| 5 | Dual seal is documented fail-open | `zangbeto_receipts.jl:~88`, `seal_bridge.jl:33` | Seal silently weakens when unconfigured |
| 6 | Seal threshold defaults to 1 | `seal_bridge.jl:38` | A quorum of one by default |
| 7 | Thresholds live in 3 module literals, none policy-owned | `veilos_antispam.jl:249`, `signals.py:107`, `config.py:138` | TypeSafe's separation is not actually honoured |
| 8 | Rust gates minting on verification; Julia does not | `economics.rs:181` vs proven TOC_MINT | The control exists where it isn't exposed |
| 9 | No human/agent distinction anywhere | I-4 blocker string; I-3 evidence | Essay B's tier system is unbuildable today |
| 10 | No ownership/operator/lineage registry | grep: no such fields | Sybil resistance is infrastructure, not model |

---

# PART 4 — Dependency order

The proposals describe a correct end state. Reaching it in this order:

**0. (now) Fix the live break.** `oso_vm.jl:2519` calls
`check_sim_to_real_tier(agent_id, work_domain, Dict())` — three args — against
`check_sim_to_real_tier(agent_tier::Int)` — one arg. Proven on Julia 1.11.5:
`MethodError: no method matching check_sim_to_real_tier(::String, ::String, ::Dict{String, Int64})`.
The module loads, so the CI load-check is green while COMPUTE_PROOF (0x56) throws
instead of gating `dopamine_authorized`.

**1. Make Layer 1 exist.** Real witness keypairs; votes that can differ;
signatures that are signatures. (`I-25`, `I-27`; `veilos_antispam.jl:263-277`,
`zangbeto_receipts.jl:369`.) Nothing above this is meaningful until a witness set
can disagree with itself.

**2. Build the registry.** ownership · operator · hardware lineage · network ·
funding · credential authority. This is the anti-Sybil answer, and it is the
prerequisite for Essay B's tiers. No model needed.

**3. Compute independence from the registry.** Replace
`independence = ... ? 1.0 : 0.0`. Multi-axis, derived, auditable.

**4. Write the composition rule into the constitution.** Gate-don't-multiply.
Thresholds policy-owned in TOC_CONSTANTS, never a module literal, never the
subject's own report. Add a gate rule: a threshold literal must not appear in the
same module as the quantity it judges.

**5. Only then Jev.** Judging evidence *content* only — never independence, never
witness selection. Clamped below any auto-execution line by construction
(`PUMPFUN_SCAN_CONVICTION = 0.72`). Cached, cited by settlement, never an input
to it.

**Parallel, independent of all the above:** the signal/trading path already has
ground truth, so Jev's calibration can be falsified there *today*
(reliability diagram / Brier vs resolved outcomes). That test gates the entire
Jev programme and costs a frozen historical window.

---

# PART 5 — Honest limits

- **Jev is unmeasured by me.** Primitives, pricing, and the confidence formula are
  verified from TypeSafe's docs. **Calibration is not** — no key. Every downstream
  claim about Jev's usefulness is conditional on the reliability test.
- **The confidence formula is not calibration.** `(n·peak − 1)/(n − 1)` measures
  peakedness of the model's own output. A confidently-wrong model scores high. This
  is why the reliability test is not optional.
- **Repos are unpushed.** At time of writing OSOVM, blueprint, and Vantage were each
  1 commit ahead of origin.
- **The gate currently reports 2 failures (I-4, I-18), but 6 of the most recent 9
  flips were closures by artifact rather than by control** — renamed constants,
  an unrun test file, stubs counted as implementations. The mechanism improved this
  round (a `reachable()` caller check was added); the closures largely did not.

---

# ONE-PARAGRAPH SUMMARY

The three essays independently describe Zàngbétò — the stack's 4th federation layer —
and get the architectural boundary right: attestation is evidence, quorum is
agreement about evidence, consensus is canonical ordering, settlement is separate,
and an intelligence layer may judge evidence but must never replace it or own the
threshold. What the essays cannot know is that every prerequisite they assume is
absent in this codebase: the witnesses are shuffled integers whose votes derive from
the claimant's own number with mock signatures (`veilos_antispam.jl:263-277`), the
production path returns an empty vector so quorum fails 100%
(`zangbeto_receipts.jl:369`), independence is a binarised string compare
(`oso_vm.jl:2507`), and there is no ownership/operator registry to compute it from.
Their one genuinely new idea is the independence-domain model; their one structural
omission is the composition rule — and the stack's own `proof_value` (a six-factor
product, currently 0.0 because one factor is uninstrumented) is a live demonstration
of what happens when that rule is a multiplication.
