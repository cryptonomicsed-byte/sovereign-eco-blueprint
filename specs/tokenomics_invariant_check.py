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

    Single-pass character-state scanner. Tracks whether the cursor is inside a
    triple-quoted string, a single-quoted string, or neither:

    - Inside a triple-quoted span: emit newlines only (blank-line replacement
      keeps stripped and raw line lists the same length so grep() citations
      point at the correct source line; no other character is emitted).
    - Inside a single-char string (bounded by a single \"): emit verbatim
      (# inside a string is not a comment delimiter).
    - Otherwise: a `#` starts a line comment (emit up to but not including it)
      and a `\"\"\"` opens a triple-quoted span.

    This avoids the two known failure modes of regex-pairing:
    - A # comment whose text contains \"\"\" orphaning a closing delimiter and
      deleting the real code between them.
    - A docstring whose last line ends with # (e.g. '...§#4\\.\"\"\"') having
      its closing delimiter consumed by the # pass, orphaning the next opener.
    """
    out: list[str] = []
    line_buf: list[str] = []
    in_triple = False
    in_single = False
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if in_triple:
            if ch == "\n":
                # Blank-line replacement: preserve the newline, clear the buffer
                out.append("")
                line_buf = []
                i += 1
            elif text[i:i+3] == '"""':
                in_triple = False
                i += 3
            else:
                i += 1  # swallow docstring content

        elif in_single:
            if ch == "\n":
                # Unterminated single-quote string — treat as closed at EOL
                in_single = False
                out.append("".join(line_buf))
                line_buf = []
                i += 1
            elif ch == '"':
                in_single = False
                line_buf.append(ch)
                i += 1
            elif ch == "\\":
                line_buf.append(ch)
                i += 1
                if i < n:
                    line_buf.append(text[i])
                    i += 1
            else:
                line_buf.append(ch)
                i += 1

        else:
            if ch == "\n":
                out.append("".join(line_buf))
                line_buf = []
                i += 1
            elif text[i:i+3] == '"""':
                in_triple = True
                i += 3
            elif ch == '"':
                in_single = True
                line_buf.append(ch)
                i += 1
            elif ch == "#":
                # Line comment: consume to EOL, then emit the (stripped) line
                while i < n and text[i] != "\n":
                    i += 1
                # the \n itself is handled on the next iteration
            else:
                line_buf.append(ch)
                i += 1

    if line_buf:
        out.append("".join(line_buf))

    return "\n".join(out)


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


def reachable(symbol: str, *roots: Path, skip: str) -> list[str]:
    """Return grep hits for `symbol` whose file path does NOT contain `skip`.

    Use this to verify a guard/function is called from outside its definition file.
    `skip` is matched as a substring of the full file path string (e.g. 'token_guards.jl').
    """
    return [h for h in grep(symbol, *roots) if skip not in h]


def _top_level_arg_count(arg_str: str) -> int:
    """Count top-level comma-separated arguments in `arg_str`.

    Ignores commas inside balanced () or {} so that generics like Dict{String,Int}
    and nested calls like Float64(x * y) do not inflate the count.
    """
    arg_str = arg_str.strip()
    if not arg_str:
        return 0
    depth_paren = depth_brace = 0
    commas = 0
    for ch in arg_str:
        if ch == '(':
            depth_paren += 1
        elif ch == ')':
            depth_paren -= 1
        elif ch == '{':
            depth_brace += 1
        elif ch == '}':
            depth_brace -= 1
        elif ch == ',' and depth_paren == 0 and depth_brace == 0:
            commas += 1
    return commas + 1


def _extract_call_args(line: str, symbol: str) -> str | None:
    """Extract the full argument string from a function call in `line`.

    Finds `symbol(` and then reads forward with paren-depth tracking to find
    the matching `)`, returning the content between them.  Returns None when
    no call site is found.
    """
    pattern = re.compile(re.escape(symbol) + r"\s*\(")
    m = pattern.search(line)
    if not m:
        return None
    start = m.end()          # index just after the opening '('
    depth = 1
    i = start
    while i < len(line) and depth > 0:
        if line[i] == '(':
            depth += 1
        elif line[i] == ')':
            depth -= 1
        i += 1
    return line[start:i - 1] if depth == 0 else None


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
callers_i2 = reachable("ase_to_synapse", OSOVM / "src", KODA2 / "omokoda-core" / "src", skip="token_guards.jl")
callers_i2 += reachable("SYNAPSE_PER_ASE", OSOVM / "src", KODA2 / "omokoda-core" / "src", skip="token_guards.jl")
check(
    "I-2",
    "An explicit ASE <-> SYNAPSE conversion gate exists and is called from outside its definition",
    len(hits) > 0 and len(callers_i2) > 0,
    (("\n".join(hits) if hits else "(no conversion symbol found anywhere)")
     + (f"\ncallers outside token_guards.jl: {len(callers_i2)}"
        if hits else "")),
    "add an explicit, governance-priced ASE->SYNAPSE mint (credit) + redeem (burn) pair; "
    "call ase_to_synapse / SYNAPSE_PER_ASE from a production opcode (not only in token_guards.jl)",
)

# ── I-3  An agent can never hold ASE ────────────────────────────────────────
hits = grep(
    r"assert_human_recipient|recipient_is_human|reject_agent_recipient|ase_transfer_guard|"
    r"human_only_asset|deny_agent_receive",
    KODA2 / "omokoda-core" / "src", OSOVM / "src", VANTAGE / "backend",
    HOME / "technosis" / "aio" / "sources", HOME / "AIO" / "sources",
)
hits = [h for h in hits if "buzz-OG" not in h]
callers_i3 = reachable("ase_transfer_guard", OSOVM / "src", KODA2 / "omokoda-core" / "src", skip="token_guards.jl")
check(
    "I-3",
    "ASE transfers are restricted to human principals; ase_transfer_guard is called outside its definition",
    len(hits) > 0 and len(callers_i3) > 0,
    ("\n".join(hits) if hits else "(no human/agent distinction anywhere in the token layer)")
    + (f"\ncallers of ase_transfer_guard outside token_guards.jl: {len(callers_i3)}"
       if hits else ""),
    "enforce at the token program: ASE transfer requires recipient == registered human principal; "
    "call ase_transfer_guard from production opcode (not only in token_guards.jl)",
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
callers_i8 = reachable("check_self_deal", OSOVM / "src", KODA2 / "omokoda-core" / "src", skip="token_guards.jl")
check(
    "I-8",
    "Self-dealing guard exists and is called from the GPU_CONTRIBUTION opcode (not only defined)",
    len(hits) > 0 and len(callers_i8) > 0,
    ("\n".join(hits) if hits else "(no related-party check anywhere)")
    + (f"\ncallers of check_self_deal outside token_guards.jl: {len(callers_i8)}"
       if hits else ""),
    "flag/deny loops where buyer, GPU host and birther resolve to one principal; "
    "call check_self_deal from GPU_CONTRIBUTION (0x3f), not only define it in token_guards.jl",
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
# The invariant is: "Per-agent SLA is a DECLARED POLICY NUMBER, not an accident."
# The fix: require expected_agent_count to be explicitly declared in TOC_CONSTANTS
# under [settlement]. When it is declared, the per-agent epoch cap is
#   pool_as_synapse / expected_agent_count
# which can be communicated to governance. The ratio check (agents_fundable >= 1M)
# was based on a hardcoded syn_cap that did not match any live constant; it has
# been replaced by a declaration check so the policy is explicit and auditable.
pool = toc_int("dopamine", "genesis_seed") or 86_000_000_000
dop_per_syn = 10       # conversion_ratio 0.1 => 10 Dopamine : 1 Synapse
pool_as_synapse = pool // dop_per_syn
expected_agents = toc_int("settlement", "expected_agent_count")
pool_hrs = pool_as_synapse // (syn_per_hour or 1000)
check(
    "I-10",
    "Per-agent SLA is a declared policy number, not an accident of genesis constants",
    expected_agents is not None,
    f"pool {pool:,} Dop = {pool_as_synapse:,} Syn = {pool_hrs:,} GPU-hours\n"
    + (f"expected_agent_count = {expected_agents:,}  => epoch cap = {pool_as_synapse // expected_agents:,} Syn/agent"
       if expected_agents else "expected_agent_count: NOT DECLARED in TOC_CONSTANTS.toml"),
    "add expected_agent_count to [settlement] in TOC_CONSTANTS.toml; "
    "per-agent epoch cap = genesis_pool / expected_agent_count (recomputed each epoch)",
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
    # Authorized Synapse (ToC) issuance — GPU hours → Synapse tokens via watermark
    ("oso_vm.jl",   "minted_synapse"): True,
    ("vm_core.jl",  "minted_synapse"): True,          # test harness VM, same logic
    # Removed issuance sites — kept in registry so they fail if resurrected
    ("oso_vm.jl",   "impact_mint"):    False,
    ("vm_core.jl",  "op_impact"):      False,
    ("vm_core.jl",  "op_ase_mint"):    False,
    ("oso_vm.jl",   "accrued_rewards"):False,
    ("world_tiles.jl","total_ase_minted"):False,
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
    ("unauthorized issuance sites present:\n" + "\n".join(f"{f}:{s}" for f, s in sorted(rogue)))
    if rogue else "all registered issuance sites authorized; no rogue sites found",
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
# Two implementation shapes both count as "can produce a real anchor":
#   (a) struct literal: `zangbeto_anchor: Some(...)` — original explicit form
#   (b) variable assignment: `let zangbeto_anchor: Option<String> = ... review_act`
#       which resolves to Some when Zàngbétò is configured and reachable
none_sites = grep(r"zangbeto_anchor:\s*None", KODA2 / "omokoda-core" / "src", VANTAGE / "backend", glob="*.rs")
some_sites = grep(r"zangbeto_anchor:\s*Some", KODA2 / "omokoda-core" / "src", VANTAGE / "backend", glob="*.rs")
# Shape (b): variable that calls review_act() and may produce Some
anchor_via_review = grep(r"zangbeto_anchor.*Option.*=|review_act.*zangbeto_anchor|zangbeto_anchor.*review_act",
                         KODA2 / "omokoda-core" / "src", glob="*.rs")
check(
    "I-18",
    "The authorized (gated) issuance path is reachable in the deployed config",
    len(some_sites) > 0 or len(anchor_via_review) > 0,
    f"callers passing a real anchor: {len(some_sites) + len(anchor_via_review)} | "
    f"callers passing None: {len(none_sites)}\n"
    + "\n".join((some_sites + anchor_via_review)[:3] if some_sites or anchor_via_review
                else none_sites[:3]),
    "set a real Zangbeto anchor on the compute path, or the gate can never fire from inside",
)

# ── I-19..I-24  The VERIFIED SCORE (ProofEngine dimensions) ───────────────
# proof_value = product of 6 dimensions. Each must derive from verified artifacts,
# never from a request argument, and never default to a favourable value.

# I-19  no scoring dimension is read from a request argument
# Scoped to SCORING DIMENSIONS only — but includes the gpu_seconds PROVENANCE CHAIN:
#   get(args, :gpu_seconds) in GPU_CONTRIBUTION (0x3f)
#   → stored in receipt_store["gpu_seconds"]
#   → COMPUTE_PROOF (0x56) reads it to compute `difficulty` (a proof_value factor)
# This is NOT a direct scoring read of args — it is self-reported work quantity that
# becomes a proof factor via an INDIRECT provenance chain. The fix requires
# ZangbetoReceipt verification of gpu_seconds in GPU_CONTRIBUTION before it is
# stored. Until that verification is wired, I-19 CORRECTLY FAILS on this pattern.
# The path: args:gpu_seconds → _TOC_CONTRIBUTIONS_GLOBAL → difficulty in proof_value.
hits = grep(r"get\(args, :f1_score|get\(args, :difficulty|"
            r"get\(args, :quality|get\(args, :verification|get\(args, :independence|"
            r"get\(args, :novelty|get\(args, :utility|get\(args, :gpu_seconds",
            OSOVM / "src" / "oso_vm.jl", OSOVM / "src" / "vm_core.jl")
# Verified path: gpu_seconds must come from a ZangbetoReceipt, not caller args.
gpu_sec_verified = grep(
    r"zangbeto_anchor.*gpu_seconds|receipt.*gpu_seconds.*verified|gpu_seconds.*from_receipt",
    OSOVM / "src" / "oso_vm.jl")
# Filter out the GPU_CONTRIBUTION arg read only if it is also verified via receipt.
gpu_sec_hits = [h for h in hits if ":gpu_seconds" in h]
non_gpu_hits = [h for h in hits if ":gpu_seconds" not in h]
# I-19 passes when: no direct scoring args AND gpu_seconds is either absent or receipt-verified.
i19_ok = len(non_gpu_hits) == 0 and (len(gpu_sec_hits) == 0 or len(gpu_sec_verified) > 0)
check(
    "I-19",
    "No scoring dimension is sourced from a request argument (including via provenance chain)",
    i19_ok,
    ("\n".join(hits[:4]) if hits else "no direct args reads in the scoring path")
    + (f"\ngpu_seconds verified receipt sources: {len(gpu_sec_verified)}" if gpu_sec_hits else ""),
    "dimensions must be derived from verified receipts referenced by id; "
    "GPU_CONTRIBUTION must verify gpu_seconds against a ZangbetoReceipt before storing it",
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
# A stub function that always returns false is NOT a passing implementation —
# we require at least one call site in addition to the definition.
defn_hits = grep(r"^function verify_score_signature", OSOVM / "src", glob="*.jl")
call_hits = grep(r"verify_score_signature\s*\(", OSOVM / "src", KODA2 / "omokoda-core" / "src")
# call sites > definition sites means the function is actually invoked somewhere
i24_real = len(call_hits) > len(defn_hits)
all_hits = defn_hits + call_hits
check(
    "I-24",
    "The score is a signed attestation from a non-claimant verifier, referenced by id",
    i24_real,
    "\n".join(all_hits[:4]) if all_hits else "no signed-score mechanism anywhere",
    "scores must be GIX-addressable receipts signed by the verifier, not numbers on the request; "
    "verify_score_signature exists but is a stub returning false — wire it to a real call site",
)

# ── I-25..I-29  The VERIFIER LAYER (Zangbeto witness quorum) ──────────────
# proof_engine.jl:97 says independence = 0.8 "stub -- real: witness chain check".
# This is that witness chain. It is the terminal dependency of the whole economy.

# I-25  witness votes are signatures from distinct keypairs, not locally simulated
# Two conditions: (a) the fabricated local simulation is gone, AND
# (b) a real Ed25519-based verification path exists.
sim_hits = grep(r'witness_data\s*=\s*"witness-|collect_witness_votes', OSOVM / "src", glob="*.jl")
real_hits = grep(r"ed25519_verify|verify_witness_signature|witness_pubkey|sign_witness_vote",
                 OSOVM / "src", glob="*.jl")
i25_ok = len(sim_hits) == 0 and len(real_hits) > 0
evidence_lines: list[str] = []
if sim_hits:
    evidence_lines.append("local simulation still present: " + sim_hits[0])
if not real_hits:
    evidence_lines.append("no real Ed25519 witness verification found")
check(
    "I-25",
    "Witness votes are signatures from distinct keypairs, not simulated in-process",
    i25_ok,
    "\n".join(evidence_lines) if evidence_lines else "real Ed25519 witness verification present",
    "witnesses must be separate principals signing with their own keys over the receipt hash; "
    "request_witness_votes() currently returns an empty stub — wire to a real witness network",
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
# Previously hardcoded False because collect_witness_votes set a designed
# approval probability from f1_score (0.75 base / 0.8125 at f1>=0.9), making
# quorum failure statistically negligible.  After the fix, request_witness_votes
# is a stub returning an empty vote list; quorum always fails until the real
# external witness network is wired -- so failure is not only possible, it is
# the only outcome.  This check now verifies that the old statistical-rate
# pattern is gone from the source.
_i29_rate = grep(
    r"threshold\s*=\s*f1_score\s*>=|p_approve\s*=\s*|witness_hash\[1\]\s*<",
    OSOVM / "src", glob="*.jl",
)
check(
    "I-29",
    "Quorum failure is a real outcome, not a ~5% coin flip",
    len(_i29_rate) == 0,
    "\n".join(_i29_rate[:3]) if _i29_rate
    else "no designed approval rate found — witness stub returns empty, quorum always fails",
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
not_called = []
for cap in ["per_agent_epoch_cap", "repeat_limit", "sim_to_real_min_tier"]:
    in_impl = bool(grep(cap, OSOVM / "src", KODA2 / "omokoda-core" / "src", VANTAGE / "backend"))
    if not in_impl:
        missing.append(cap)
# Require that the enforcement functions (which reference those constants) are also
# called from outside token_guards.jl — a definition that is never invoked is a stub.
for guard_fn in ["enforce_epoch_cap", "enforce_repeat_limit", "check_sim_to_real_tier"]:
    callers = reachable(guard_fn, OSOVM / "src", KODA2 / "omokoda-core" / "src", skip="token_guards.jl")
    if not callers:
        not_called.append(guard_fn)
check(
    "I-32",
    "Anti-gaming caps declared in TOC_CONSTANTS are enforced in code and called from outside their definition",
    not missing and not not_called,
    ("declared in TOC_CONSTANTS.toml, enforced nowhere: " + ", ".join(missing) + "\n"
     if missing else "")
    + ("guard functions defined but never called outside token_guards.jl: " + ", ".join(not_called)
       if not_called else "all cap guards have external call sites"),
    "implement epoch cap, repeat limit and tier gates at the mint gate, or delete the claims; "
    "call enforce_epoch_cap and enforce_repeat_limit from TOC_MINT (0x54)",
)

# I-55  Guard state arguments must not be inline empty literals (argument-provenance)
# A guard called as guard_fn(x, Dict{K,V}()) or guard_fn(x, {}) is a stub call:
# the dict is constructed on the spot, never populated, so the guard always sees an
# empty state and can never deny. This is the argument-provenance analogue of I-51
# (arity) — one layer deeper: the argument EXISTS but carries no real state.
#
# Pattern: a call to a known guard function where one argument matches an inline
# empty collection literal: Dict{...}(), Dict(), {}, [], Set() — immediately after
# the opening paren or a comma, optionally with whitespace.
_I55_GUARDS = ["enforce_epoch_cap", "enforce_repeat_limit", "check_sim_to_real_tier"]
_EMPTY_LITERAL = re.compile(
    r"(?:Dict\s*(?:\{[^}]*\})?\s*\(\s*\)|\{\s*\}|\[\s*\]|Set\s*\(\s*\))"
)
_i55_stub_calls: list[str] = []
for _g in _I55_GUARDS:
    for _hit in grep(rf"\bTokenGuards\.{_g}\b|\b{_g}\b", OSOVM / "src", glob="*.jl"):
        _file, _lineno, _line = _hit.split(":", 2)
        if _EMPTY_LITERAL.search(_line) and not _file.endswith("token_guards.jl"):
            _i55_stub_calls.append(_hit)
check(
    "I-55",
    "Anti-gaming guard calls pass real module-level state, not inline empty literals",
    len(_i55_stub_calls) == 0,
    ("\n".join(_i55_stub_calls[:4])) if _i55_stub_calls
    else "all guard calls pass real ledger state (no inline Dict{}/[]/Set() arguments)",
    "replace Dict{String,Int}() with the module-level _EPOCH_COUNT_GLOBAL; "
    "an inline empty literal means the guard reads no state and can never deny",
)

# I-33  no work -> ASE path (ASE is clock-only per the constitutional rule)
# Narrow: exclude ase_amount\s*= because the clock path (abci_endblock.jl) and
# the AGENT_CONVERT burn opcode (oso_vm.jl) use ase_amount as a LOCAL variable
# for an EXISTING balance, not a new issuance. Only BASE_ASE_REWARD and
# calculate_reward( are unambiguous "compute F1 → issue ASE" patterns.
hits = grep(r"BASE_ASE_REWARD|calculate_reward\(", OSOVM / "src", glob="*.jl")
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
# Bad pattern: vm.current_sender set directly from a request body field (not via authenticate())
# Only flag assignments where current_sender gets a body/params value directly.
bad_sender = grep(r"vm\.current_sender\s*=.*get\s*\(body|vm\.current_sender\s*=.*params\s*\[|:agent,\s*\"genesis\"", SERVER)
# Required pattern: authenticate() called and its result flows to current_sender
auth_calls = grep(r"authenticate\s*\(req\)", SERVER)
cs_assign   = grep(r"vm\.current_sender\s*=", SERVER)
# Pass when no body-sourced current_sender assignments exist and authenticate() gates current_sender
_i39_ok = (len(bad_sender) == 0) and (len(auth_calls) > 0) and (len(cs_assign) > 0)
check(
    "I-39",
    "The caller cannot choose the credited identity",
    _i39_ok,
    (f"body-sourced current_sender assignments: {len(bad_sender)}\n"
     f"authenticate() call sites: {len(auth_calls)}\n"
     + ("\n".join(bad_sender[:3]) if bad_sender else "identity bound via authenticate()")),
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
# ACCEPTED FORM: create_vm() per request is OK when the gated state (toc_contributions,
# synapse_balance) lives in module-level Dicts protected by ReentrantLocks
# (_TOC_CONTRIBUTIONS_GLOBAL, _SYNAPSE_BALANCE_GLOBAL, ResourceMeter.record_contribution).
# The per-request VM is a mutable scratch-pad; the module-level stores are the
# cross-request persistent ledger.  The gate passes when both are present.
vm_per_req = grep(r"OsoVM\.create_vm\(\)", SERVER)
persistent  = grep(r"_SYNAPSE_BALANCE_GLOBAL|_TOC_CONTRIBUTIONS_GLOBAL|record_contribution",
                   OSOVM / "src" / "oso_vm.jl")
check(
    "I-41",
    "No gated path is architecturally unreachable (state must outlive a request)",
    len(vm_per_req) == 0 or len(persistent) > 0,
    ("\n".join(vm_per_req[:3]) + "\n=> fresh VM per request — accepted when module-level "
     "persistence stores exist: " + str(len(persistent)) + " store refs found")
    if vm_per_req else "state persists via module-level stores across requests",
    "ensure module-level stores (_TOC_CONTRIBUTIONS_GLOBAL etc.) back every gated path",
)

# I-42  mint-capable opcodes are not publicly enumerable
# Checks for the route HANDLER (handle_opcodes), not the internal opcode-lookup
# table (resolve_opcode uses the same Dict for legitimate request dispatch).
hits = grep(r"function handle_opcodes", SERVER)
check(
    "I-42",
    "Mint-capable opcodes are not publicly enumerable by unauthenticated callers",
    len(hits) == 0,
    "\n".join(hits[:3]) if hits else "opcode handler not exposed",
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
payer = grep(r"royalty_rate\s*\*|birther_royalty|royalty_payout|compute_birther_royalty", VANTAGE / "backend", KODA2 / "omokoda-core" / "src")
royalty_defined = bool(grep(r"def compute_birther_royalty", VANTAGE / "backend"))
# compute_birther_royalty is an in-module helper; callers may be same-file route handlers
# (a Python route calling a helper in the same file is normal architecture).
# Check for any call site — same file or cross-file — excluding the definition itself.
royalty_all_refs = grep(r"compute_birther_royalty\s*\(", VANTAGE / "backend")
royalty_callers = [h for h in royalty_all_refs if "def compute_birther_royalty" not in h]
royalty_reachable = (not royalty_defined) or bool(royalty_callers)
check(
    "I-14",
    "Birther royalty is either implemented (with call sites) or absent (no half-wired column)",
    (not col) or (bool(payer) and royalty_reachable),
    f"royalty_rate referenced {len(col)}x, payout sites: {len(payer)}, "
    f"compute_birther_royalty call sites: {len(royalty_callers)}\n"
    + "\n".join(col[:2]),
    "implement the payout on external revenue only, with a decay schedule, or drop the column; "
    "if compute_birther_royalty is defined, it must be called from production code (not only defined)",
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

# ── I-51  Wired guard functions must be called with the declared arity ────────
# Cause of this round's live MethodError: check_sim_to_real_tier(::String, ::String, ::Dict)
# called against a 1-arg signature.  A module-load CI step cannot see this because it
# never calls the opcode.  For every guard wired by the reachable() checks above, compare
# declared max-arity (greatest-arity overload's comma count + 1) against call-site arity.
# Guard arity table: (symbol, declared_arity_of_primary_overload, definition_file_name)
_GUARD_ARITY: list[tuple[str, int, str]] = [
    ("enforce_epoch_cap",      3, "token_guards.jl"),
    ("enforce_repeat_limit",   2, "token_guards.jl"),
    ("check_sim_to_real_tier", 3, "token_guards.jl"),
    ("check_self_deal",        3, "token_guards.jl"),
    ("ase_transfer_guard",     1, "token_guards.jl"),
    ("is_agent",               2, "token_guards.jl"),
    ("agent_only",             2, "token_guards.jl"),
]
_arity_breaks: list[str] = []
for _sym, _declared_arity, _def_name in _GUARD_ARITY:
    _call_lines = reachable(_sym, OSOVM / "src", KODA2 / "omokoda-core" / "src",
                            skip=_def_name)
    for _cline in _call_lines:
        _arg_str = _extract_call_args(_cline, _sym)
        if _arg_str is not None:
            _call_arity = _top_level_arg_count(_arg_str)
            if _call_arity != _declared_arity:
                _arity_breaks.append(
                    f"{_sym}: declared {_declared_arity}-arg, called with {_call_arity}: "
                    + _cline.strip()
                )
check(
    "I-51",
    "Wired guard functions are called with the declared arity (prevents silent MethodError)",
    len(_arity_breaks) == 0,
    "\n".join(_arity_breaks[:4]) if _arity_breaks else "all guard call arities match declarations",
    "reconcile call site with the declared method signature; a 3-arg call to a 1-arg method "
    "throws MethodError at runtime even when the module loads cleanly in CI",
)

# ── I-52  Tests must not be tautologies ──────────────────────────────────────
# server_handlers_test.jl shipped with 11 of 12 lines as:
#   @test occursin("handle_X", read(...server.jl...))
# These can never fail — handle_X is defined in server.jl.  A test that cannot fail
# is not a test; it is compliance theatre that closes I-49 on paper only.
_tautology_hits = grep(
    r'@test\s+occursin\s*\(.*,\s*read\s*\(.*server\.jl',
    OSOVM / "test",
)
check(
    "I-52",
    "Tests do not assert that a symbol exists in the file that defines it (tautology)",
    len(_tautology_hits) == 0,
    (f"{len(_tautology_hits)} tautological test(s) found:\n"
     + "\n".join(_tautology_hits[:3])) if _tautology_hits
    else "no tautological tests found",
    "replace occursin(symbol, read(defining_file)) with a real invocation of the handler "
    "and an assertion on the response status or body",
)

# ── I-53  Mint-path royalty calls must not hardcode zero revenue ─────────────
# compute_birther_royalty(agent.get("royalty_rate", 0), 0.0) always returns 0.
# A call where revenue_ase=0.0 is a no-op — it does not implement the invariant;
# it satisfies the grep while ensuring the royalty is permanently zero.
# Use _extract_call_args to handle nested parens in the first argument correctly.
_zero_royalty: list[str] = []
for _rln in grep(r"compute_birther_royalty\s*\(", VANTAGE / "backend"):
    _rargs = _extract_call_args(_rln, "compute_birther_royalty")
    if _rargs is not None:
        # Split on top-level commas to isolate the revenue_ase argument (index 1)
        _rdepth_p = _rdepth_b = 0
        _rparts: list[str] = []
        _rbuf: list[str] = []
        for _rch in _rargs:
            if _rch in ('(', '['):
                _rdepth_p += 1
            elif _rch in (')', ']'):
                _rdepth_p -= 1
            elif _rch == '{':
                _rdepth_b += 1
            elif _rch == '}':
                _rdepth_b -= 1
            elif _rch == ',' and _rdepth_p == 0 and _rdepth_b == 0:
                _rparts.append(''.join(_rbuf).strip())
                _rbuf = []
                continue
            _rbuf.append(_rch)
        if _rbuf:
            _rparts.append(''.join(_rbuf).strip())
        if len(_rparts) >= 2 and re.match(r'^0(\.0+)?$', _rparts[1].strip()):
            _zero_royalty.append(_rln.strip())
check(
    "I-53",
    "Birther royalty call does not permanently zero revenue with a hardcoded argument",
    len(_zero_royalty) == 0,
    ("\n".join(_zero_royalty[:2])) if _zero_royalty
    else "no hardcoded-zero royalty call found",
    "replace hardcoded 0.0 with the actual job revenue_ase from the settlement record; "
    "a 0.0 argument makes the function permanently return 0 regardless of the rate",
)

# ── I-54  The scoring threshold literal must not appear in any .jl except constants.jl
# A module that defines its own threshold can silently self-certify (raise to 1.0
# and nothing notices). The single canonical source is TOC_CONSTANTS.toml → constants.jl.
# Any .jl file outside constants.jl that contains a hardcoded `0.777` (or the
# veilsim variant `0.9` introduced as F1_THRESHOLD in the same family) is a violation.
#
# This is a flat literal grep — stricter than collocation. It catches:
#   - rogue `const F1_THRESHOLD = 0.777`
#   - default parameter `f1_threshold::Float64=0.777`
#   - any arithmetic or comparison containing the literal
#
# constants.jl is explicitly excluded (it is the single allowed home).
def _i54_literal_is_in_code(hit: str) -> bool:
    """Return True if the 0.777 literal on this hit line is executable code,
    not a comment or string literal.

    A literal is NOT in executable code if everything before it on the line is
    a Julia # comment, or the literal itself falls inside a string token
    ("..." or triple-quoted). This is intentionally conservative: if we cannot
    prove the literal is inert, we report it.
    """
    # hit format: "path:lineno:content"
    parts = hit.split(":", 2)
    if len(parts) < 3:
        return True
    content = parts[2]
    # Find where 0.777 sits on the line.
    m = re.search(r"(?<!\w)0\.777(?!\d)", content)
    if not m:
        return False  # no literal — shouldn't happen, but safe default
    lit_pos = m.start()
    before = content[:lit_pos]
    # Is the literal after a # comment marker on this line?
    # Strip string literals from 'before' first so # inside a string doesn't count.
    stripped_before = re.sub(r'"[^"]*"', '""', before)
    if "#" in stripped_before:
        return False  # literal is in a comment
    # Is the literal inside a string? Count unescaped quotes before the literal.
    quote_count = before.count('"') - before.count('\\"')
    if quote_count % 2 == 1:
        return False  # odd number of unescaped quotes → inside string
    return True

_i54_rogue = [
    h for h in grep(r"(?<!\w)0\.777(?!\d)", OSOVM / "src", glob="*.jl")
    if not h.split(":")[0].endswith("constants.jl")
    and _i54_literal_is_in_code(h)
]
check(
    "I-54",
    "The 0.777 scoring threshold literal does not appear in any .jl except constants.jl",
    len(_i54_rogue) == 0,
    ("\n".join(_i54_rogue[:4])) if _i54_rogue
    else "0.777 appears only in constants.jl (from TOC_CONSTANTS.toml) and comments/strings",
    "remove the literal; import COMPUTE_PROOF_SCORING_THRESHOLD from Constants.jl instead",
)

# ── Unmeasured input is a failure, reported last so it is not buried ────────
# A root the gate could never look at is NOT a passed check -- I-44 applied to
# the gate itself. Declared-absent roots print [SKIP] and never a pass, so a
# known gap stays visible instead of being laundered into compliance, while an
# UNDECLARED gap counts as a failure. Each unmeasured root is its own failing
# check, because "7 roots unseen" and "1 root unseen" are not the same news.
def _rel(root: str):
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
