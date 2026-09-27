#!/usr/bin/env python3
"""
tokenomics_invariant_check.py — executable invariant gate for the 3-tier token economy.

The three tiers (spec: THREE_TIER_TOKENOMICS.md):
    ASE      = human-facing only. Never held by an agent. Burned on conversion.
    SYNAPSE  = agent-facing compute credit. 1,000 Synapse = 1 verified GPU-hour.
    DOPAMINE = hive-facing capacity, non-transferable, shared between agents.

Each check below encodes an invariant that MUST hold for the economy to be
sound. A check that fails is a hole, not a style nit. Exit code is the number
of failing checks, so CI can gate on it.

Run:  python3 specs/tokenomics_invariant_check.py
"""

import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
BP = HOME / "sovereign-eco-blueprint"
OSOVM = HOME / "OSOVM"
KODA2 = HOME / "Omo-Koda2"
VANTAGE = HOME / "Vantage"
TOC = BP / "specs" / "TOC_CONSTANTS.toml"

FAILURES: list[str] = []


def grep(pattern: str, *roots: Path, glob: str = "", fixed: bool = False) -> list[str]:
    """Return 'path:line: text' matches, skipping build/vcs noise."""
    hits: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        cmd = ["grep", "-rn"]
        if fixed:
            cmd.append("-F")
        cmd += ["-E", pattern, str(root)]
        if glob:
            cmd += ["--include", glob]
        cmd += ["--exclude-dir=.git", "--exclude-dir=target", "--exclude-dir=node_modules"]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
        except subprocess.TimeoutExpired:
            continue
        for ln in out.splitlines():
            if ln.strip():
                hits.append(ln.replace(str(HOME) + "/", ""))
    return hits


def check(cid: str, title: str, ok: bool, evidence: str, fix: str) -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {cid}  {title}")
    if evidence:
        for line in evidence.splitlines()[:4]:
            print(f"        {line}")
    if not ok:
        print(f"        FIX: {fix}")
        FAILURES.append(cid)


def toc_int(section: str, key: str) -> int | None:
    """Read an integer constant out of TOC_CONSTANTS.toml."""
    if not TOC.exists():
        return None
    text = TOC.read_text()
    in_section = False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            in_section = s[1:-1] == section
            continue
        if in_section and s.startswith(key):
            m = re.search(r"=\s*([0-9_]+)", s)
            if m:
                return int(m.group(1).replace("_", ""))
    return None


# ── I-1  One-way valves: no human-facing → hive-facing bypass ────────────────
hits = grep(r"ase_to_dopamine|ASE_TO_DOPAMINE|ase-signal", OSOVM / "src", KODA2 / "omokoda-core" / "src")
check(
    "I-1",
    "No direct ASE -> DOPAMINE path (humans must not buy hive capacity directly)",
    len(hits) == 0,
    "\n".join(hits),
    "delete the ase_to_dopamine burn, or route it through a Synapse credit mint+redeem",
)

# ── I-2  A direct ASE <-> SYNAPSE conversion gate exists (the only on-ramp) ──
hits = grep(r"ase_to_synapse|ase_for_synapse|synapse_from_ase|SYNAPSE_PER_ASE", OSOVM / "src", KODA2 / "omokoda-core" / "src")
check(
    "I-2",
    "An explicit ASE <-> SYNAPSE conversion gate exists and is the declared on-ramp",
    len(hits) > 0,
    "\n".join(hits) if hits else "(no conversion symbol found anywhere)",
    "add an explicit, governance-priced ASE->SYNAPSE mint (credit) + redeem (burn) pair",
)

# ── I-3  An agent can never hold ASE ────────────────────────────────────────
hits = grep(
    r"assert_human_recipient|recipient_is_human|reject_agent_recipient|ase_transfer_guard|"
    r"human_only_asset|deny_agent_receive",
    KODA2 / "omokoda-core" / "src", OSOVM / "src", VANTAGE / "backend",
    HOME / "technosis" / "aio" / "sources", HOME / "AIO" / "sources",
)
hits = [h for h in hits if "buzz-OG" not in h]
check(
    "I-3",
    "ASE transfers are restricted to human principals (agent cannot receive ASE)",
    len(hits) > 0,
    "\n".join(hits) if hits else "(no human/agent distinction anywhere in the token layer)",
    "enforce at the token program: ASE transfer requires recipient == registered human principal",
)

# ── I-4  Synapse is agent-scoped, not openly transferable ───────────────────
todo = (BP / "specs" / "TOC_CONSTANTS.toml").read_text() if TOC.exists() else ""
transferable = re.search(r"^\s*transferable\s*=\s*true", todo, re.M)
syn_hits = grep(r"is_agent\(|agent_scope|agent_only", KODA2 / "omokoda-core" / "src", VANTAGE / "backend")
check(
    "I-4",
    "SYNAPSE transfers are identity-gated to registered agents",
    len(syn_hits) > 0 and transferable is None,
    f"transferable=true in TOC_CONSTANTS: {bool(transferable)}\n" + "\n".join(syn_hits),
    "keep transferable between agents, but enforce recipient.is_agent() at the token program",
)

# ── I-5  Exactly one canonical pool split exists ────────────────────────────
canonical = grep(r"VeilSimPool|POOL_WEIGHTS", OSOVM / "src")
legacy = grep(r"DISTRIBUTION_RATIOS|treasury\s*=>\s*0\.50", OSOVM / "src")
check(
    "I-5",
    "Exactly one canonical emission split in the codebase",
    not (canonical and legacy),
    f"canonical 8-pool sites: {len(canonical)} | legacy 5-wallet sites: {len(legacy)}\n"
    + "\n".join(legacy[:3]),
    "delete one of the two splits; port the 8 pools into ase_minting.jl or delete it",
)

# ── I-6  The drift check actually covers every implementation ───────────────
drift = (BP / "specs" / "toc_drift_check.py").read_text() if (BP / "specs" / "toc_drift_check.py").exists() else ""
check(
    "I-6",
    "toc_drift_check.py covers ALL constant implementations, not just Vantage's",
    "ase_minting.jl" in drift and "abci_endblock.jl" in drift,
    "drift check targets: " + ", ".join(re.findall(r"[\w/]+\.(?:py|jl|rs)", drift)[:6]),
    "add OSOVM/src/ase_minting.jl and abci_endblock.jl to the drift check's file list",
)

# ── I-7  Synapse is redeemable, i.e. the burn actually exists ───────────────
hits = grep(r"burn_synapse|redeem|consume_credit|burn_credit", OSOVM / "src", KODA2 / "omokoda-core" / "src")
check(
    "I-7",
    "A Synapse credit has a real burn path (redeem), and it is atomic",
    len(hits) > 0,
    "\n".join(hits) if hits else "(no redeem/burn primitive for the credit found)",
    "credit must be a unique bearer object consumed in the same tx as the allocation",
)

# ── I-8  Sybil/self-dealing guard for the compute loop ─────────────────────
PAT = r"self_deal|self-dealing|related_party|related-party|circular_supply"
hits = grep(PAT, OSOVM / "src", KODA2 / "omokoda-core" / "src", VANTAGE / "backend")
hits = [h for h in hits if "/tests/" not in h and "/test_" not in h and not h.split(":")[-1].strip().startswith("//")]
check(
    "I-8",
    "Self-dealing guard: one principal cannot be buyer + host + birther in one loop",
    len(hits) > 0,
    "\n".join(hits) if hits else "(no related-party check anywhere)",
    "flag/deny loops where buyer, GPU host and birther resolve to one principal",
)

# ── I-9  GPU-hours are the unit, and the rate is a single constant ─────────
syn_per_hour = toc_int("synapse", "per_gpu_hour")
check(
    "I-9",
    "Compute is denominated in GPU-hours with one declared rate",
    syn_per_hour is not None,
    f"[synapse].per_gpu_hour = {syn_per_hour}",
    "declare SYNAPSE_PER_GPU_HOUR in TOC_CONSTANTS and derive all capacity from it",
)

# ── I-10 Per-agent capacity must be small relative to the hive pool ────────
syn_cap = 86_000_000   # SYNAPSE_MAX_PER_AGENT (economics.rs / wallet.rs)
pool = toc_int("dopamine", "genesis_seed") or 86_000_000_000
conv = toc_int("dopamine", "ase_to_dopamine") or 10_000
dop_per_syn = 10       # conversion_ratio 0.1 => 10 Dopamine : 1 Synapse
pool_as_synapse = pool // dop_per_syn
agents_fundable = pool_as_synapse // syn_cap
hrs_per_agent = syn_cap // (syn_per_hour or 1000)
pool_hrs = pool_as_synapse // (syn_per_hour or 1000)
check(
    "I-10",
    "Per-agent SLA is a declared policy number, not an accident of genesis constants",
    agents_fundable >= 1_000_000,
    f"pool {pool:,} Dopamine = {pool_as_synapse:,} Synapse = {pool_hrs:,} GPU-hours\n"
    f"per-agent cap {syn_cap:,} Synapse = {hrs_per_agent:,} GPU-hours\n"
    f"=> only {agents_fundable:,} agents can be endowed at cap (target: millions)",
    "make per-agent capacity = pool / expected_agent_count, recomputed each epoch",
)

# ── I-11 The 1440 collision ────────────────────────────────────────────────
t = TOC.read_text() if TOC.exists() else ""
values_1440 = [
    ln for ln in t.splitlines()
    if not ln.strip().startswith("#") and re.search(r"=\s*1_?440\b", ln)
]
check(
    "I-11",
    "The value 1440 is not overloaded across unrelated meanings",
    len(values_1440) <= 1,
    f"lines where 1440 is an assigned value: {len(values_1440)}\n" + "\n".join(values_1440),
    "rename: daily emission total vs inheritance seat count must not share a literal",
)

# ── I-12  No opcode may accept a caller-supplied issuance amount ───────────
CALLER_AMOUNT = r"function impact_mint|op_ase_mint|synapse_estimate"
hits = grep(CALLER_AMOUNT, OSOVM / "src")
check(
    "I-12",
    "No opcode accepts a caller-supplied issuance AMOUNT (protocol computes the reward)",
    len(hits) == 0,
    "\n".join(hits[:5]),
    "impact_mint / ASE_MINT must not exist; drop synapse_estimate from op_toc_mint",
)

# ── I-13  ASE has exactly ONE issuance path, and it is the clock ───────────
# Registry from THREE_TIER_TOKENOMICS.md 3.1: site -> authorized?
ISSUANCE_SITES = {
    ("ase_emission.py", "ase_emission"): True,        # the one clock
    ("abci_endblock.jl", "POOL_WEIGHTS"): True,       # clock (L1, currently dead)
    ("oso_vm.jl", "impact_mint"): False,
    ("vm_core.jl", "op_impact"): False,
    ("vm_core.jl", "op_ase_mint"): False,
    ("oso_vm.jl", "accrued_rewards"): False,
    ("world_tiles.jl", "total_ase_minted"): False,
}
found = {}
for sym in [s for (_, s) in ISSUANCE_SITES]:
    for h in grep(sym, OSOVM / "src", VANTAGE / "backend"):
        base = h.split("/")[-1].split(":")[0]
        if (base, sym) in ISSUANCE_SITES:
            found[(base, sym)] = True
unknown = [k for k in found if k not in ISSUANCE_SITES]
rogue = [k for k, _ in found.items() if not ISSUANCE_SITES.get(k, True)] if not unknown else list(found)
check(
    "I-13",
    "ASE has exactly one authorized issuance path (the clock); no alternate route",
    not rogue and not unknown,
    "unauthorized issuance sites present:\n" + "\n".join(f"{f}:{s}" for f, s in sorted(rogue)),
    "route all issuance through the clock; remove IMPACT/ASE_MINT/staking-reward mints",
)

# ── I-16  Every mint site is in the registry (new ones fail CI) ────────────
MINTISH = r"impact_mint\(|op_ase_mint\(|minted_synapse\s*=|ase_minted\s*=>\s*[0-9]"
hits = grep(MINTISH, OSOVM / "src", glob="*.jl")
undeclared = [h for h in hits if not any(s in h for _, s in ISSUANCE_SITES)]
check(
    "I-16",
    "Every mint site appears in the 3.1 registry (undeclared site => CI fail)",
    len(undeclared) == 0,
    "\n".join(undeclared[:5]) if undeclared else f"all {len(hits)} mint sites declared",
    "add the new site to ISSUANCE_SITES in this file AND to the spec registry, with justification",
)

# ── I-17  The verified-work gate validates AUTHENTICITY, not non-emptiness ─
auth = grep(r"verify_zangbeto_receipt|verify_anchor_signature|anchor_signature_valid|anchor_verified",
            OSOVM / "src", KODA2 / "omokoda-core" / "src")
soft = grep(r'as \"\"|!= \"\"', OSOVM / "src", glob="*.jl")
check(
    "I-17",
    "Verified-work gate checks anchor authenticity, not merely non-emptiness",
    len(auth) > 0,
    f"authenticity checks: {len(auth)} | non-emptiness checks: {len(soft)}\n"
    + "\n".join(soft[:3]),
    "zangbeto_anchor must be a signed receipt whose signature is verified, not a non-empty string",
)

# ── I-18  The gated path is reachable in the deployed configuration ────────
none_sites = grep(r"zangbeto_anchor:\s*None", KODA2 / "omokoda-core" / "src", VANTAGE / "backend", glob="*.rs")
some_sites = grep(r"zangbeto_anchor:\s*Some", KODA2 / "omokoda-core" / "src", VANTAGE / "backend", glob="*.rs")
check(
    "I-18",
    "The authorized (gated) issuance path is reachable in the deployed config",
    len(some_sites) > 0,
    f"callers passing a real anchor: {len(some_sites)} | callers passing None: {len(none_sites)}\n"
    + "\n".join(none_sites[:3]),
    "set a real Zangbeto anchor on the compute path, or the gate can never fire from inside",
)

# ── I-19..I-24  The VERIFIED SCORE (ProofEngine dimensions) ───────────────
# proof_value = product of 6 dimensions. Each must derive from verified artifacts,
# never from a request argument, and never default to a favourable value.

# I-19  no scoring dimension is read from a request argument
hits = grep(r"get\(args, :f1_score|get\(args, :gpu_seconds|get\(args, :difficulty|"
            r"get\(args, :receipt_hash|get\(args, :environment_hash",
            OSOVM / "src" / "oso_vm.jl", OSOVM / "src" / "vm_core.jl")
check(
    "I-19",
    "No scoring dimension is sourced from a request argument",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no direct args reads in the scoring path",
    "dimensions must be derived from verified receipts referenced by id, not passed as args",
)

# I-20  no dimension defaults to a favourable value when absent
fav = grep(r'"difficulty", 1\.0|controller_stability", 0\.8|f1_score > 0\.0 \? clamp\(f1_score, 0\.0, 1\.0\) : 0\.5',
           OSOVM / "src")
check(
    "I-20",
    "No scoring dimension defaults to a favourable value when absent",
    len(fav) == 0,
    "\n".join(fav[:4]) if fav else "no favourable defaults",
    "difficulty must default to 0 (not 1.0); quality to 0 (not 0.5)",
)

# I-21  verification is a HARD GATE (0 when unverified), not a discount
hits = grep(r"verification\s*=\s*cumulative >= gpu_seconds \? 1\.0 : 0\.5", OSOVM / "src")
check(
    "I-21",
    "Unverified work scores 0 on verification (a 0.5 floor is a subsidy)",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "no 0.5 verification floor",
    "unverified => verification = 0.0, which makes proof_value 0 and mint_eligible false",
)

# I-22  independence is computed by a witness chain, not a constant
hits = grep(r"independence\s*=\s*(1\.0|0\.8)\s*(#|$)", OSOVM / "src", glob="*.jl")
check(
    "I-22",
    "Independence is computed (witness chain), not a hardcoded constant",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no constant independence",
    "wire the witness-chain check; a constant makes one sixth of proof_value free",
)

# I-23  presence of a string is not verification
hits = grep(r"!isempty\((trajectory|checkpoint|sensor|sig|signature)\)", OSOVM / "src", glob="*.jl")
check(
    "I-23",
    "Presence of a value is not accepted as verification (non-empty != valid)",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no presence-based verification",
    "verify the signature/hash, do not score on isempty()",
)

# I-24  the score is a signed receipt from a non-claimant, referenced by id
hits = grep(r"verify_score_signature|score_attestation|signed_score|verifier_pubkey",
            OSOVM / "src", KODA2 / "omokoda-core" / "src")
check(
    "I-24",
    "The score is a signed attestation from a non-claimant verifier, referenced by id",
    len(hits) > 0,
    "\n".join(hits[:4]) if hits else "no signed-score mechanism anywhere",
    "scores must be GIX-addressable receipts signed by the verifier, not numbers on the request",
)

# ── I-25..I-29  The VERIFIER LAYER (Zangbeto witness quorum) ──────────────
# proof_engine.jl:97 says independence = 0.8 "stub -- real: witness chain check".
# This is that witness chain. It is the terminal dependency of the whole economy.

# I-25  witness votes are signatures from distinct keypairs, not locally simulated
hits = grep(r'witness_data\s*=\s*"witness-|collect_witness_votes', OSOVM / "src", glob="*.jl")
check(
    "I-25",
    "Witness votes are signatures from distinct keypairs, not simulated in-process",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no local witness simulation",
    "witnesses must be separate principals signing with their own keys over the receipt hash",
)

# I-26  the quorum outcome must not depend on a claimant-reported metric
hits = grep(r"threshold\s*=\s*f1_score|approved\s*=\s*witness_hash\[1\]\s*<", OSOVM / "src", glob="*.jl")
check(
    "I-26",
    "Quorum outcome cannot be tuned by a claimant-reported metric",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no claimant-tuned approval threshold",
    "approval must come from a verified vote; f1_score must not set the approval probability",
)

# I-27  exactly one WitnessVote type and one quorum rule
types = grep(r"^struct WitnessVote", OSOVM / "src", glob="*.jl")
fields = grep(r"count\(v -> v\.(vote|approved)", OSOVM / "src", glob="*.jl")
check(
    "I-27",
    "Exactly one WitnessVote type and one quorum rule (no duplicate struct / field drift)",
    len(types) <= 1 and len({f.split("v ->")[-1].strip()[:12] for f in fields}) <= 1,
    f"WitnessVote definitions: {len(types)}\n" + "\n".join(fields[:3]),
    "declare WitnessVote once; both quorum functions must read the same field",
)

# I-28  TEE quotes are signature-verified, not merely measurement-compared
hits = grep(r"verify_quote", OSOVM / "src", glob="*.jl")
sig = grep(r"verify_attestation_signature|verify_quote_signature|sgx_dcap|tdx_verify|root_ca", OSOVM / "src")
check(
    "I-28",
    "TEE attestation verifies the quote SIGNATURE, not just the measurement field",
    len(sig) > 0,
    f"verify_quote present, signature verification sites: {len(sig)}",
    "compare enclave_id/measurement AND verify the quote signature against the vendor root",
)

# I-29  quorum failure must be a real possibility, not statistical noise
check(
    "I-29",
    "Quorum failure is a real outcome, not a ~5% coin flip",
    False,
    "collect_witness_votes: p(approve) = 0.75 base, 0.8125 when f1_score >= 0.9\n"
    "binomial(n=12): P(>=7 approvals) = 0.946 base, 0.995 at f1>=0.9\n"
    "=> the claimant reduces failures 10x by reporting a high F1; failure is noise",
    "approval must be evidence-driven; a designed approval rate is not a threshold",
)

# ── I-30..I-34  The REWARD LAYER (score -> emitted units) ─────────────────

# I-30  one reward formula per unit (two disagreeing formulas = no formula)
a = grep(r"dopamine_authorized\s*=|gpu_hours \* eval\.proof_value", OSOVM / "src" / "oso_vm.jl")
b = grep(r"function compute_score|domain_multipliers\s*=", OSOVM / "src" / "oso_vm.jl")
check(
    "I-30",
    "Exactly one reward formula emits a given unit",
    not (a and b),
    f"COMPUTE_PROOF formula (no ladder): {len(a)}\ncompute_score formula (with ladder): {len(b)}\n"
    + "\n".join(b[:2]),
    "collapse to one path; the documented ladder path is not the one COMPUTE_PROOF uses",
)

# I-31  reward multiplier and quantity never come from the request
ov = grep(r"bonus_multiplier_override|claimed_quantity", OSOVM / "src", glob="*.jl")
check(
    "I-31",
    "No reward multiplier or quantity is read from the request",
    len(ov) == 0,
    "\n".join(ov[:4]) if ov else "no request-supplied reward inputs",
    "drop bonus_multiplier_override; multiplier comes from the protocol, quantity from verified work",
)

# I-32  declared anti-gaming caps are actually enforced
missing = []
for cap in ["per_agent_epoch_cap", "repeat_limit", "sim_to_real_min_tier"]:
    in_impl = bool(grep(cap, OSOVM / "src", KODA2 / "omokoda-core" / "src", VANTAGE / "backend"))
    if not in_impl:
        missing.append(cap)
check(
    "I-32",
    "Anti-gaming caps declared in TOC_CONSTANTS are enforced in code",
    not missing,
    "declared in TOC_CONSTANTS.toml, enforced nowhere: " + ", ".join(missing),
    "implement epoch cap, repeat limit and tier gates at the mint gate, or delete the claims",
)

# I-33  no work -> ASE path (ASE is clock-only per the constitutional rule)
hits = grep(r"BASE_ASE_REWARD|calculate_reward\(|ase_amount\s*=", OSOVM / "src", glob="*.jl")
check(
    "I-33",
    "No work -> ASE issuance path exists",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no work->ASE reward path",
    "veilsim_scorer mints 5.0-7.0 ASE per sim from caller-supplied tp/fp/fn; route to Synapse instead",
)

# I-34  verification gates receive real state, not a fresh empty one
hits = grep(r"is_fully_verified\(VMState\(\)", OSOVM / "src", glob="*.jl")
check(
    "I-34",
    "Verification gates are not called with a fresh/empty state",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "no empty-state gate calls",
    "pass the real VM state; an empty one makes the check vacuous",
)

# ── I-35..I-37  EVIDENCE, NOT AUTHORITY ───────────────────────────────────
# F1 is currently a PARAMETER (from the request), wearing an INTEGRITY stamp
# (seal / merkle / receipt hash), consumed as AUTHORITY (quorum bias, quality
# dimension, ASE reward). The missing role is EVIDENCE: an observation about the
# world made by a party who could have falsified it and didn't.

# I-35  the score is an OUTPUT of verification, never an INPUT to a decision
hits = grep(r"function \w+\([^)]*\bf1\b|threshold\s*=\s*f1_score|calculate_reward\(f1",
            OSOVM / "src", glob="*.jl")
check(
    "I-35",
    "The score is an output of verification, never an input to a decision function",
    len(hits) == 0,
    "\n".join(hits[:4]) if hits else "no decision function takes a score parameter",
    "verification computes the score; the decision reads the verified record, never the number",
)

# I-36  a score must name the referent it was checked against
hits = grep(r"held_out_root|test_set_root|validation_root|novel_view_root|"
            r"\breferent_id\b|\breferent_root\b|\bwithheld_root\b",
            OSOVM / "src", glob="*.jl")
check(
    "I-36",
    "Every score names the referent it was checked against (withheld by a non-claimant)",
    len(hits) > 0,
    "\n".join(hits[:3]) if hits else "no referent field anywhere: a score is unfalsifiable by construction",
    "receipts must carry the id of the withheld artifact (test-split root / committed prediction)",
)

# I-37  integrity is not truth: a seal must not be the evidence a gate consumes
hits = grep(r'seal_data\s*=\s*"zangbeto-seal|seal_data\s*=\s*"job-seal', OSOVM / "src", glob="*.jl")
check(
    "I-37",
    "A tamper-evidence seal is not consumed as evidence of the claim's truth",
    len(hits) == 0,
    ("\n".join(hits[:3]) + "\n=> seal covers receipt_hash + approvals only; receipt_hash covers a "
     "caller-supplied f1_score, so the seal certifies the record did not change, not that it is true")
    if hits else "seals bind a referent",
    "bind the seal to the referent (withheld artefact root), or stop treating the seal as verification",
)

# ── I-14 Birther royalty: implemented, or the column must not exist ────────
col = grep(r"royalty_rate", VANTAGE / "backend")
payer = grep(r"royalty_rate\s*\*|birther_royalty|royalty_payout", VANTAGE / "backend", KODA2 / "omokoda-core" / "src")
check(
    "I-14",
    "Birther royalty is either implemented or absent (no half-wired column)",
    (not col) or bool(payer),
    f"royalty_rate referenced {len(col)}x, payout sites: {len(payer)}\n" + "\n".join(col[:2]),
    "implement the payout on external revenue only, with a decay schedule, or drop the column",
)

# ── I-15 Escrow exists for job funding ─────────────────────────────────────
esc = grep(r"escrow", HOME / "technosis" / "aio" / "sources", HOME / "AIO" / "sources")
check(
    "I-15",
    "Job funding is escrowed, so a failed job refunds and the birther cut is contingent",
    len(esc) > 0,
    f"escrow sites: {len(esc)}",
    "fund -> escrow -> convert; release Synapse and the birther cut only on delivery",
)


print()
print(f"{'=' * 72}")
if FAILURES:
    print(f"{len(FAILURES)} invariant(s) FAILING: {', '.join(FAILURES)}")
else:
    print("all invariants hold")
sys.exit(len(FAILURES))
