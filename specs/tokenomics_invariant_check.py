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

# ── I-12 Mint has exactly one door ─────────────────────────────────────────
impact = grep(r"function impact_mint", OSOVM / "src")
guard = grep(r"impact_mint\(ase_amount", OSOVM / "src")
check(
    "I-12",
    "The IMPACT mint path is gated (no caller-supplied mint amount)",
    len(impact) == 0,
    "\n".join(impact + guard),
    "impact_mint must derive the amount from verified work, not from args[:ase]",
)

# ── I-13 The quality gate is on the request path ───────────────────────────
server = (OSOVM / "src" / "server.jl").read_text() if (OSOVM / "src" / "server.jl").exists() else ""
antispam_wired = "veilos_antispam" in server or "F1_THRESHOLD" in server
fabricated = bool(re.search(r"f1_score\s*=\s*ase_minted > 0\.0 \? 0\.92", server))
check(
    "I-13",
    "The F1 >= 0.777 gate is reachable from the HTTP mint surface, and no f1 is fabricated",
    antispam_wired and not fabricated,
    f"veilos_antispam referenced in server.jl: {antispam_wired}; fabricated f1 present: {fabricated}",
    "wire veilos_antispam.check_mint into the mint path; delete the 0.92/0.88 heuristic",
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
