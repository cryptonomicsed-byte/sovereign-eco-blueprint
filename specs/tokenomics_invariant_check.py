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

import collections
import fnmatch
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Repo roots. The defaults reproduce the original single-developer $HOME layout;
# the env vars let CI -- or any other checkout shape -- point the gate at the
# real trees. Before this the gate hard-coded $HOME/<repo>, so despite the
# docstring claiming "CI can gate on it", it could only run on one machine.
HOME = Path(os.environ.get("ECO_HOME", str(Path.home())))
BP = Path(os.environ.get("ECO_BP_ROOT", HOME / "sovereign-eco-blueprint"))
OSOVM = Path(os.environ.get("ECO_OSOVM_ROOT", HOME / "OSOVM"))
KODA2 = Path(os.environ.get("ECO_KODA2_ROOT", HOME / "Omo-Koda2"))
VANTAGE = Path(os.environ.get("ECO_VANTAGE_ROOT", HOME / "Vantage"))
TOC = BP / "specs" / "TOC_CONSTANTS.toml"

FAILURES: list[str] = []

# Collects every hit string returned by grep() during a normal run so that the
# --self-test assertions can validate the corpus without re-scanning.
_GREP_LOG: list[str] = []

# Absence must never read as compliance. A root the gate could not look at, and
# a grep that timed out, are both UNMEASURED -- and an unmeasured check is a
# failed check, not a passed one (I-44). Silently `continue`-ing on either made
# the gate fail OPEN: point it at a machine missing Vantage and it reports
# FEWER failures -- a better score for a less-verified tree. That is the same
# shape as server.jl:247 (omitted f1 => 0.88 => clears the gate), one level up.
UNMEASURED: dict[str, set[str]] = {
    "missing_root": set(),
    "timeout": set(),
    "declared_absent": set(),
}

# Roots that are legitimately not reproducible off this machine (a retired-account
# mirror, a vendored tree only this box has). Naming one here does NOT make it a
# pass -- it prints [SKIP] not-measured on every run, so the gap stays visible
# instead of being laundered into compliance. Set ECO_ALLOW_ABSENT to a
# comma-separated list of path substrings.
ALLOW_ABSENT: tuple[str, ...] = tuple(
    s.strip() for s in os.environ.get("ECO_ALLOW_ABSENT", "").split(",") if s.strip()
)


def strip_jl_comments(text: str) -> str:
    """Drop Julia `#` line comments and triple-quoted docstrings before matching.

    Two passes, in this order:

    1. Strip `#`-to-EOL comments (guarded by even-quote count).
       Must come FIRST so that a comment like  # the \"\"\" marker
       cannot pair with the next real docstring in pass 2, which would
       silently delete source lines between them.

    2. Replace each triple-quoted span with an equal number of blank lines.
       Blank replacement (not a sentinel token) keeps the stripped line list
       the same length as the raw line list, so the zip in grep() stays
       aligned and citations point at the correct source line.
    """
    import re

    # Pass 1: strip # comments
    lines = []
    for line in text.splitlines():
        i = line.find("#")
        while i != -1:
            if line[:i].count('"') % 2 == 0:
                line = line[:i]
                break
            i = line.find("#", i + 1)
        lines.append(line)
    text = "\n".join(lines)

    # Pass 2: replace docstring spans with equal-length blank-line runs
    def _blank_span(m: "re.Match[str]") -> str:
        return "\n" * m.group(0).count("\n")

    return re.sub(r'""".*?"""', _blank_span, text, flags=re.DOTALL)


def grep(pattern: str, *roots: Path, glob: str = "", fixed: bool = False) -> list[str]:
    """Return 'path:lineno:text' matches, skipping build/vcs noise.

    Julia (.jl) files are comment-stripped before matching (stripping # from .rs
    would delete #[derive] annotations; no other file type has the tombstone
    problem). The original line is always returned as evidence so diffs are
    readable; only the match decision uses the stripped version.
    """
    # __pycache__ and friends hold COMPILED artifacts. The rglob() walk below
    # visits every file, so without these the gate reads .pyc bytecode and
    # returns its raw bytes as evidence -- which put NUL bytes in the report and
    # made results depend on whether a stray build cache happened to exist.
    # Measured: before this list, I-4 cited __pycache__/main.cpython-313.pyc.
    _SKIP_DIRS = {
        ".git", "target", "node_modules", "__pycache__",
        ".pytest_cache", ".mypy_cache", ".ruff_cache",
        "build", "dist", ".venv", "venv", ".tox",
    }
    # Belt and braces: never read anything that looks compiled or packed.
    _BINARY_SUFFIXES = {
        ".pyc", ".pyo", ".so", ".o", ".a", ".bin", ".class", ".jar", ".whl",
        ".zip", ".gz", ".tar", ".lock", ".png", ".jpg", ".jpeg", ".gif", ".ico",
        ".pdf", ".woff", ".woff2", ".ttf", ".wasm", ".db", ".sqlite", ".parquet",
    }
    try:
        rx = re.compile(re.escape(pattern) if fixed else pattern)
    except re.error:
        return []

    hits: list[str] = []
    for root in roots:
        if not root.exists():
            bucket = "declared_absent" if any(a in str(root) for a in ALLOW_ABSENT) else "missing_root"
            UNMEASURED[bucket].add(str(root))
            continue
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for fpath in files:
            if any(d in fpath.parts for d in _SKIP_DIRS):
                continue
            if fpath.suffix.lower() in _BINARY_SUFFIXES:
                continue
            if glob and not fnmatch.fnmatch(fpath.name, glob):
                continue
            try:
                raw = fpath.read_text(errors="ignore")
            except OSError:
                continue
            # Definitive guard: a NUL byte means this is not source. Skipping it
            # here is what keeps binary out of the evidence regardless of which
            # cache directory or extension it arrives under.
            if "\x00" in raw:
                continue
            raw_lines = raw.splitlines()
            if fpath.suffix == ".jl":
                match_lines = strip_jl_comments(raw).splitlines()
            else:
                match_lines = raw_lines
            for lineno, (mline, rline) in enumerate(zip(match_lines, raw_lines), 1):
                if rx.search(mline):
                    hits.append(f"{fpath}:{lineno}:{rline}".replace(str(HOME) + "/", ""))
    _GREP_LOG.extend(hits)
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


def _self_test(hit_log: list[str]) -> int:
    """Meta-checks verifying that grep() itself is sound.

    Three assertions:
      (a) no control bytes in any hit — a NUL or backspace means binary leaked through
      (b) each guard in grep() is independently falsifiable via a three-probe fixture:
            plain.pyc     — plain text, no NULs, root dir   — only SUFFIX guard catches it
            sneaky.jl     — NUL bytes, .jl name, root dir   — only NUL guard catches it
            __pycache__/notes.jl — plain text, .jl, skip dir — only SKIP-DIR guard catches it
            source.jl     — legitimate source, root dir     — must still be found
          Dropping any one guard fails exactly the probe that guard owns.
          The previous single-probe design (one .pyc with NULs in __pycache__) was caught
          by all three guards simultaneously, so a dropped guard hid behind its neighbours.
      (c) every cited path has a source extension, never a compiled artifact

    Run via:  python3 specs/tokenomics_invariant_check.py --self-test
    Exit code is the count of self-test failures so CI can gate on it separately
    from the invariant suite.
    """
    _COMPILED = {".pyc", ".pyo", ".so", ".o", ".a", ".bin", ".class",
                 ".jar", ".whl", ".wasm", ".db", ".sqlite", ".parquet"}
    _CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")

    fails = 0
    print()
    print("── self-test " + "─" * 59)

    # (a) No control bytes in any hit string
    bad_ctrl = [h for h in hit_log if _CTRL.search(h)]
    if bad_ctrl:
        print(f"[ST-FAIL] (a) control bytes in {len(bad_ctrl)} hit(s) "
              f"— binary leaked into evidence")
        for h in bad_ctrl[:3]:
            print(f"          {h!r}")
        fails += 1
    else:
        print(f"[ST-PASS] (a) no control bytes — {len(hit_log)} hits clean")

    # (c) No compiled/binary artifact extension in any cited path
    bad_ext = [h for h in hit_log if Path(h.split(":")[0]).suffix.lower() in _COMPILED]
    if bad_ext:
        print(f"[ST-FAIL] (c) {len(bad_ext)} hit(s) cite compiled artifacts")
        for h in bad_ext[:3]:
            print(f"          {h}")
        fails += 1
    else:
        print(f"[ST-PASS] (c) no compiled artifacts in {len(hit_log)} hit(s)")

    # (b) Each guard is independently falsifiable — three probes, one per guard
    with tempfile.TemporaryDirectory() as _td:
        _troot = Path(_td)
        # Legitimate source — must be found (guards must not be over-aggressive)
        (_troot / "source.jl").write_text("module ProbeSource\nend\n")
        # SUFFIX probe: plain text, no NULs, root dir — only suffix guard catches it
        (_troot / "plain.pyc").write_text("module ProbeSuffix\n")
        # NUL probe: NUL bytes inside, .jl extension, root dir — only NUL guard catches it
        (_troot / "sneaky.jl").write_bytes(b"\x00module ProbeNul\x00")
        # SKIP-DIR probe: plain text, .jl extension, __pycache__ — only skip-dir catches it
        (_pycache := _troot / "__pycache__").mkdir()
        (_pycache / "notes.jl").write_text("module ProbeSkipDir\n")

        _hits_b = grep(r"\bmodule\b", _troot)
        _files_b = {h.split(":")[0] for h in _hits_b}
        _b_fails: list[str] = []
        if any("plain.pyc" in f for f in _files_b):
            _b_fails.append("suffix guard bypassed — plain.pyc appeared")
        if any("sneaky.jl" in f for f in _files_b):
            _b_fails.append("NUL guard bypassed — sneaky.jl appeared")
        if any("notes.jl" in f for f in _files_b):
            _b_fails.append("skip-dir guard bypassed — __pycache__/notes.jl appeared")
        if not any("source.jl" in f for f in _files_b):
            _b_fails.append("guard over-aggressive — source.jl not found")
        if _b_fails:
            print(f"[ST-FAIL] (b) {len(_b_fails)} guard(s) failed:")
            for msg in _b_fails:
                print(f"          {msg}")
            fails += 1
        else:
            print("[ST-PASS] (b) all 3 guards verified independently, source found")

    print("─" * 72)
    if fails:
        print(f"self-test: {fails} assertion(s) FAILED")
    else:
        print("self-test: all assertions hold")
    return fails


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
# Match the legacy split only where it is USED -- a definition or an indexed
# read -- not the bare name. grep() does not strip comments, so matching the
# name alone flagged the tombstone comment the I-5 deletion left behind
# ("# DISTRIBUTION_RATIOS deleted (I-5 / 2026-09-27)"), i.e. the check failed on
# prose describing the fix. Negative invariants measure text, not behaviour
# (spec 3.4b); this narrows I-5 to text that could actually split a pool.
legacy = grep(
    r"const\s+DISTRIBUTION_RATIOS\s*=|DISTRIBUTION_RATIOS\s*\[|treasury\s*=>\s*0\.50",
    OSOVM / "src",
)
check(
    "I-5",
    "Exactly one canonical emission split in the codebase",
    not (canonical and legacy),
    f"canonical 8-pool sites: {len(canonical)} | legacy 5-wallet sites: {len(legacy)}\n"
    + "\n".join(legacy[:3]),
    "delete the legacy split; emission routes through POOL_WEIGHTS in abci_endblock.jl "
    "(50/25/15/10 belongs only to 24-sector tithe inflow, never to a mint)",
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
    "derive the cap (emission_per_minute x 60 x emission_window_hours) so 1440 means only "
    "the seat count; renaming alone leaves two literals and does not close this check",
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
# Scoped to SCORING DIMENSIONS only. Earlier this also matched :receipt_hash and
# :environment_hash, which are not dimensions: receipt_hash is the identifier the
# fix text itself prescribes ("receipts referenced by id"), and environment_hash
# is a label for the novelty lookup. Matching them made I-19 report four
# violations where two are real, which is the same conflation of id/label with
# value that this invariant exists to prevent.
hits = grep(r"get\(args, :f1_score|get\(args, :gpu_seconds|get\(args, :difficulty|"
            r"get\(args, :quality|get\(args, :verification|get\(args, :independence|"
            r"get\(args, :novelty|get\(args, :utility",
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

# ── I-38..I-42  THE HTTP SURFACE (where all of the above becomes reachable) ─

SERVER = OSOVM / "src" / "server.jl"

# I-38  mint-capable opcodes require authority over HTTP
auth = grep(r"authorization|bearer|api_key|apikey|x-api-key|authenticate|verify_request_signature",
            SERVER)
check(
    "I-38",
    "Mint-capable opcodes require authenticated authority over HTTP",
    len(auth) > 0,
    f"auth-related lines in server.jl: {len(auth)}",
    "POST /run executes IMPACT (0x11, 'Mint ASE from work') with no key, token or signature",
)

# I-39  the caller cannot choose the credited identity
hits = grep(r"vm\.current_sender\s*=\s*agent|:agent, \"genesis\"", SERVER)
check(
    "I-39",
    "The caller cannot choose the credited identity",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "identity is bound",
    "current_sender must come from an authenticated principal, not a request field",
)

# I-40  the API does not report a score it never computed
hits = grep(r"ase_minted > 0\.0 \? 0\.92|\? 0\.92 :", SERVER)
check(
    "I-40",
    "The API does not report a score it never computed",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "no fabricated score in the response",
    "delete the 0.92/0.88 heuristic; return a score only if one was computed",
)

# I-41  gated paths must be reachable -> state must outlive a request
hits = grep(r"OsoVM\.create_vm\(\)", SERVER)
check(
    "I-41",
    "No gated path is architecturally unreachable (state must outlive a request)",
    len(hits) == 0,
    ("\n".join(hits[:3]) + "\n=> fresh VM per request: GPU_CONTRIBUTION state is discarded, so "
     "toc_is_fully_verified can never pass, while stateless mints (IMPACT/ASE_MINT) still work")
    if hits else "state persists across requests",
    "persist VM state (or the contribution log) so the gated path can actually accumulate proof",
)

# I-42  mint-capable opcodes are not publicly enumerable
hits = grep(r"function handle_opcodes|CORE_OPCODES|EXPANSION_OPCODES", SERVER)
check(
    "I-42",
    "Mint-capable opcodes are not publicly enumerable by unauthenticated callers",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "opcode table is not exposed",
    "GET /opcodes publishes every mint-capable opcode name to anonymous callers",
)

# ── I-43..I-46  THE SELF-ISSUED SCORE (the loop closes) ───────────────────
# f1_score means four different things in one codebase: a real measurement, a
# pass-by-default constant, a tautology over ase_minted, and a caller argument.
# They share a name and a plausible range, so consumers cannot tell them apart.

MEASURE = r"f1_score|quality|accuracy|score"

# I-43  no response field is derived from another response field by a constant
hits = grep(r"f1_score *=.*\? *[0-9]", OSOVM / "src", glob="*.jl")
check(
    "I-43",
    "No response field is fabricated from another response field by a constant",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "no tautological response field",
    "delete server.jl:181; it restates ase_minted as a plausible-looking quality score",
)

# I-44  a measurement-named field is written only by a measurement function
import re as _re
lits = []
for h in grep(r"\bf1_score *=|f1_score *= ", OSOVM / "src", glob="*.jl"):
    rhs = h.split("=", 1)[1] if "=" in h else ""
    if _re.search(r"[0-9]\.[0-9]", rhs) or _re.search(r"\? *[0-9]", rhs):
        lits.append(h)
check(
    "I-44",
    "A measurement-named field is written only by a measurement, never by a literal or default",
    len(lits) == 0,
    "\n".join(lits[:4]) if lits else "no constant writes to f1_score",
    "f1_score must come from compute_f1/veil_f1_score, never from a constant",
)

# I-45  the API cannot both emit a value and accept it as evidence
emit = grep(r'"f1_score"\s*=>', OSOVM / "src" / "server.jl")
accept = grep(r"get\(args, :f1_score", OSOVM / "src")
check(
    "I-45",
    "The API cannot both emit a value and accept that same value as evidence",
    not (emit and accept),
    (f"emitted in {len(emit)} response(s); accepted as evidence in {len(accept)} place(s)\n"
     "=> POST /run returns f1_score 0.92 for any minting call, and COMPUTE_PROOF accepts a\n"
     "   caller-supplied f1_score as the 'quality' factor of proof_value. The system issues\n"
     "   the evidence, then accepts it back.") if (emit and accept) else "no self-issued evidence",
    "a value the API emits may never be an input the API trusts; strip f1_score from the response "
    "or strip it from the scoring path",
)

# I-46  a defaulted measurement must fail closed
hits = grep(r'"f1",\s*(get\([^,]+, :f1,\s*)?0\.88|:f1,\s*0\.88', OSOVM / "src", glob="*.jl")
check(
    "I-46",
    "A defaulted measurement fails closed (default must not pass the gate)",
    len(hits) == 0,
    ("\n".join(hits[:3]) + "\n=> default 0.88 exceeds the 0.777 gate, so an OMITTED f1 passes")
    if hits else "no pass-by-default measurement",
    "default a missing score to 0.0; note zangbeto_receipts.jl:149 already does",
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


# ── I-49 Handlers must be exercised by a test ──────────────────────────────
# 11 handlers, 1,124 tests, zero references between them. That is how
# server.jl carries both a fabricated score (line 181: f1_score = 0.92 whenever
# ase_minted > 0) and a crash path (local vm_result has no default, so a non-Dict
# return from execute_instruction raises UndefVarError at line 192) without
# either being noticed. A handler nobody calls is where a dead endpoint hides,
# so gate on the reference itself, not on anyone's reading of the body.
_srv_path = OSOVM / "src" / "server.jl"
_handlers = (
    re.findall(r"^function (handle_[a-z_]+)", _srv_path.read_text(), re.M)
    if _srv_path.exists() else []
)
_tested: set[str] = set()
if _handlers:
    _refs = grep("|".join(_handlers), OSOVM / "test")
    _tested = {h for h in _handlers if any(h in ln for ln in _refs)}
_untested = sorted(set(_handlers) - _tested)
check(
    "I-49",
    "Every HTTP handler is exercised by a test that invokes it",
    len(_untested) == 0,
    f"handlers in server.jl: {len(_handlers)} | invoked from test/: {len(_tested)}\n"
    f"untested: {', '.join(_untested) if _untested else '(none)'}\n"
    f"an uninvoked handler is where a dead endpoint hides",
    "add a test per handler that calls it and asserts on the response body",
)

# ── I-50  A function that computes a scored quantity must be reachable ──────
# Four times now the violation has lived in DEAD code: mint_ase_for_veil with
# its 50/25 revenue split (I-5), evaluate_simulation/evaluate_gaussian with
# difficulty=1.0 / quality=0.8 / independence=0.8 (I-20), and
# src/scoring/simulation_scoring.jl -- a whole module never `include`d, carrying
# an all-1.0 default constructor, a 7-factor product that diverges from the live
# 6-factor one, and a division guard that returns full credit.
#
# The gate greps source text, so it cannot distinguish dead from live code: a
# generous default inside an unreachable function reads exactly like a live bug.
# That is why each of these was found by hand. Negative invariants measure text,
# not behaviour (spec 3.4b), and reachability is behaviour.
#
# Scoped to scoring vocabulary on purpose: a naive zero-reference census flags
# 24 of 625 functions including demo helpers (doThing, stopIt) and print
# utilities, which would make the check noise and train people to ignore it.
# Scoring vocabulary narrows it to the class that has actually bitten.
#
# Comments are stripped before counting. Verified necessary: with tombstones
# naming deleted functions, an unstripped census counted the tombstone as a
# reference, so re-adding a live dead difficulty_factor reported PASS. A check
# blinded by the comment describing the very thing it guards is not a check.
_SCORING_VOCAB = re.compile(
    r"score|difficulty|quality|novelty|verification|independence|utility|emission|reward",
    re.IGNORECASE,
)
_bodies: list[str] = []
for _root in (OSOVM / "src", OSOVM / "test", KODA2, VANTAGE):
    if not _root.exists():
        continue
    for _p in _root.rglob("*.jl"):
        if _p.is_file() and "julia-1.10" not in str(_p):
            try:
                _bodies.append(strip_jl_comments(_p.read_text(errors="ignore")))
            except OSError:
                pass
_blob = "\n".join(_bodies)
_id_counts = collections.Counter(re.findall(r"[A-Za-z_][A-Za-z0-9_!]*", _blob))
_def_counts = collections.Counter(
    re.findall(r"^\s*function\s+([A-Za-z_][A-Za-z0-9_!]*)", _blob, re.M)
)
_unreachable = sorted(
    n for n, d in _def_counts.items()
    if _id_counts.get(n, 0) - d <= 0 and _SCORING_VOCAB.search(n)
)
check(
    "I-50",
    "A function computing a scored quantity is reachable from live code",
    len(_unreachable) == 0,
    f"zero-reference scoring functions: {len(_unreachable)}\n"
    + "\n".join(_unreachable[:5]),
    "delete the dead function, or wire it to the canonical factor site "
    "(compute_evaluation) with attested inputs — never leave generous defaults "
    "in code nobody can reach",
)

# ── Unmeasured input is a failure, reported last so it is not buried ────────
# A root the gate could never look at is NOT a passed check -- I-44 applied to
# the gate itself. Declared-absent roots print [SKIP] and never a pass, so a
# known gap stays visible instead of being laundered into compliance, while an
# UNDECLARED gap counts as a failure. Each unmeasured root is its own failing
# check, because "7 roots unseen" and "1 root unseen" are not the same news.
def _rel(root: str) -> str:
    return root.replace(str(HOME) + "/", "")


for _root in sorted(UNMEASURED["declared_absent"]):
    print(f"[SKIP]     not measured (declared absent): {_rel(_root)}")
    print("        anything this root would have proven is UNVERIFIED, not fine")

for _root in sorted(UNMEASURED["missing_root"]):
    check(
        "I-47",
        f"Unmeasured root is not compliance: {_rel(_root)}",
        False,
        "the gate could not look here, so it must not report compliance",
        "check the repo out beside the others, set its ECO_*_ROOT env var, or "
        "declare it via ECO_ALLOW_ABSENT if it is genuinely unreproducible",
    )

for _root in sorted(UNMEASURED["timeout"]):
    check(
        "I-48",
        f"Timed-out grep is not a clean grep: {_rel(_root)}",
        False,
        "grep exceeded 60s -- 'no hits' was never established",
        "narrow the pattern or raise the timeout; a timeout is not a clean result",
    )

print()
print(f"{'=' * 72}")
if UNMEASURED["missing_root"] or UNMEASURED["timeout"] or UNMEASURED["declared_absent"]:
    print(f"coverage: {len(UNMEASURED['missing_root'])} undeclared-absent, "
          f"{len(UNMEASURED['timeout'])} timed-out, "
          f"{len(UNMEASURED['declared_absent'])} declared-absent root(s)")
if FAILURES:
    _uniq = sorted(set(FAILURES), key=lambda c: (len(c), c))
    print(f"{len(FAILURES)} check(s) FAILING: {', '.join(_uniq)}")
else:
    print("all invariants hold")

_st_fails = _self_test(_GREP_LOG) if "--self-test" in sys.argv else 0
sys.exit(len(FAILURES) + _st_fails)
