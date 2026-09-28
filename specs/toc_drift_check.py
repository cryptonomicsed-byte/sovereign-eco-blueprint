#!/usr/bin/env python3
"""
TOC_CONSTANTS drift check — M3 CI gate.

Verifies that ase_emission.py pool weights and key constants match
TOC_CONSTANTS.toml exactly. Run in CI; exits 1 if any drift detected.

Usage:
    python3 sovereign-eco-blueprint/specs/toc_drift_check.py
"""
import sys
import os
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # ~/

def parse_toml_floats(path: Path) -> dict:
    result = {}
    section = "__root__"
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.split("#")[0].strip().replace("_", "")
            try:
                result[f"{section}.{k}"] = float(v)
            except ValueError:
                pass
    return result


def check_pool_weights(toml: dict) -> list[str]:
    errors = []
    # Expected canonical 8-pool set from [ase.pools]
    pool_map = {
        "VeilSimPool":    "ase.pools.veilsim",
        "RndPool":        "ase.pools.rnd",
        "GovernancePool": "ase.pools.governance",
        "ReservePool":    "ase.pools.reserve",
        "ComputePool":    "ase.pools.compute",
        "StoragePool":    "ase.pools.storage",
        "WitnessPool":    "ase.pools.witness",
        "TreasuryPool":   "ase.pools.treasury",
    }

    emission_py = ROOT / "Vantage/backend/routers/ase_emission.py"
    if not emission_py.exists():
        errors.append(f"MISSING: {emission_py}")
        return errors

    src = emission_py.read_text()
    # Extract POOL_WEIGHTS dict
    m = re.search(r"POOL_WEIGHTS\s*:\s*dict\[.*?\]\s*=\s*\{([^}]+)\}", src, re.DOTALL)
    if not m:
        errors.append("ase_emission.py: POOL_WEIGHTS dict not found")
        return errors

    py_pools = {}
    for line in m.group(1).splitlines():
        line = line.strip().split("#")[0].strip().rstrip(",")
        if ":" in line:
            k, _, v = line.partition(":")
            k = k.strip().strip('"')
            try:
                py_pools[k] = float(v.strip())
            except ValueError:
                pass

    for py_name, toml_key in pool_map.items():
        if py_name not in py_pools:
            errors.append(f"MISSING pool '{py_name}' in ase_emission.py POOL_WEIGHTS")
            continue
        expected = toml.get(toml_key)
        if expected is None:
            errors.append(f"MISSING key '{toml_key}' in TOC_CONSTANTS.toml")
            continue
        actual = py_pools[py_name]
        if abs(actual - expected) > 1e-9:
            errors.append(
                f"DRIFT: {py_name}: ase_emission.py={actual} vs TOML={expected}"
            )

    # Check pool count matches
    if len(py_pools) != len(pool_map):
        errors.append(
            f"POOL COUNT: ase_emission.py has {len(py_pools)} pools, expected {len(pool_map)}"
        )

    return errors


def check_key_constants(toml: dict) -> list[str]:
    errors = []

    checks = [
        ("ase.emission_per_minute", 1.0, "emission 1 ASE/min"),
        ("ase.emission_window_hours", 24.0, "daily cap window; max_daily_emission is derived"),
        ("dopamine.agent_burn_rate", 10000.0, "1:10,000 burn ratio"),
        ("dopamine.decay_min", 0.001, "min decay 0.1%/day"),
        ("dopamine.decay_max", 0.020, "max decay 2.0%/day"),
        ("synapse.per_gpu_hour", 1000.0, "1000 Synapse/GPU-hour"),
        ("synapse.max_pool_share", 0.005, "0.5% pool share"),
        ("esu.tithe_rate", 0.0369, "Èṣù 3.69%"),
        ("gates.stake_fraction", 0.10, "10% stake gate"),
        ("ritual.sabbath_multiplier", 1.10, "Sabbath 1.1×"),
        ("ritual.jubilee_minor_multi", 2.0, "Jubilee 2.0×"),
        # Three-Tier Economic Constitution constants (2026-09-26)
        ("synapse.base_cost_ase", 1.0, "1 ASE = 1000 SYN base cost"),
        ("synapse.saturation_count", 100.0, "scarcity knee at 100 agents"),
        ("synapse.credit_to_alloc_ratio", 1.0, "default credit→allocation ratio"),
        ("synapse.allocation_expiry_secs", 28800.0, "8h allocation expiry"),
        ("dopamine.synapse_to_dopamine_factor", 0.85, "Synapse→Guild Dopamine conversion"),
        ("dopamine.dop_per_gpu_hour", 1000.0, "DOP per GPU-hour — must equal synapse.per_gpu_hour"),
        ("dopamine.idle_decay_rate", 0.01, "1%/day Guild pool idle decay"),
        ("guild.treasury_fraction", 0.05, "5% of agent share to guild treasury"),
        ("guild.job_timeout_secs", 3600.0, "1 hour max job duration"),
        ("guild.max_contribution_fraction", 1.0, "agent may contribute 100% of allocation"),
        ("birthright.qualifying_fraction", 0.10, "10% of qualifying human-originated revenue"),
        ("birthright.max_chain_depth", 0.0, "flat birthright — no recursive chain"),
        ("settlement.quote_expiry_secs", 300.0, "COMPUTE_QUOTE expires in 5 min"),
        ("settlement.min_work_evidence_score", 0.777, "universal quality gate"),
    ]

    for key, expected, desc in checks:
        actual = toml.get(key)
        if actual is None:
            errors.append(f"MISSING: {key} ({desc}) not in TOC_CONSTANTS.toml")
        elif abs(actual - expected) > 1e-9:
            errors.append(f"DRIFT: {key} ({desc}): TOML={actual} expected={expected}")

    return errors


def parse_julia_pool_weights(path: Path) -> dict | None:
    """Parse a Julia `const POOL_WEIGHTS = Dict{String, Float64}(...)` block."""
    if not path.exists():
        return None
    text = path.read_text()
    m = re.search(r'const POOL_WEIGHTS\s*=\s*Dict\{[^}]+\}\s*\((.*?)\)', text, re.DOTALL)
    if not m:
        return None
    result = {}
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(',')
        km = re.match(r'"([^"]+)"\s*=>\s*([0-9.]+)', line)
        if km:
            result[km.group(1)] = float(km.group(2))
    return result


def parse_julia_distribution_ratios(path: Path) -> dict | None:
    """Parse a Julia `const DISTRIBUTION_RATIOS = Dict(...)` block."""
    if not path.exists():
        return None
    text = path.read_text()
    m = re.search(r'const DISTRIBUTION_RATIOS\s*=\s*Dict\s*\((.*?)\)', text, re.DOTALL)
    if not m:
        return None
    result = {}
    for line in m.group(1).splitlines():
        line = line.strip().rstrip(',')
        km = re.match(r'"([^"]+)"\s*=>\s*([0-9.]+)', line)
        if km:
            result[km.group(1)] = float(km.group(2))
    return result


def check_julia_pool_drift(toml: dict) -> list[str]:
    """I-6: verify OSOVM Julia files against the canonical TOC_CONSTANTS pool weights."""
    errors = []
    osovm_root = Path(os.environ.get("ECO_OSOVM_ROOT", str(ROOT / "OSOVM")))

    # abci_endblock.jl — carries the 8-pool POOL_WEIGHTS used by the L1 clock.
    abci = osovm_root / "src" / "abci_endblock.jl"
    abci_pools = parse_julia_pool_weights(abci)
    if abci_pools is None:
        errors.append("abci_endblock.jl: POOL_WEIGHTS dict not found (I-6)")
    else:
        pool_map = {
            "VeilSimPool":    "ase.pools.veilsim",
            "RndPool":        "ase.pools.rnd",
            "GovernancePool": "ase.pools.governance",
            "ReservePool":    "ase.pools.reserve",
            "ComputePool":    "ase.pools.compute",
            "StoragePool":    "ase.pools.storage",
            "WitnessPool":    "ase.pools.witness",
            "TreasuryPool":   "ase.pools.treasury",
        }
        for jl_name, toml_key in pool_map.items():
            expected = toml.get(toml_key)
            actual = abci_pools.get(jl_name)
            if expected is None:
                errors.append(f"abci_endblock.jl I-6: {toml_key} missing from TOC_CONSTANTS")
            elif actual is None:
                errors.append(f"abci_endblock.jl I-6: pool '{jl_name}' missing from POOL_WEIGHTS")
            elif abs(actual - expected) > 1e-9:
                errors.append(f"abci_endblock.jl I-6 DRIFT: {jl_name}={actual} vs TOML={expected}")

    # ase_minting.jl — carries an old 5-pool DISTRIBUTION_RATIOS (legacy split).
    # This is a different schema than the canonical 8-pool set — flag as I-5 drift.
    minting = osovm_root / "src" / "ase_minting.jl"
    dist = parse_julia_distribution_ratios(minting)
    if dist is not None:
        errors.append(
            f"ase_minting.jl I-5/I-6: DISTRIBUTION_RATIOS present with {len(dist)} pools "
            f"(legacy 5-pool split — conflicts with canonical 8-pool abci_endblock.jl; "
            f"delete DISTRIBUTION_RATIOS from ase_minting.jl and route through abci_endblock)"
        )

    return errors


def check_duplicate_literals(toml: dict) -> list[str]:
    """
    I-11 generalised: flag any numeric literal that appears under two or more
    DISTINCT keys with no shared semantic parent.

    Allowed duplicates (same concept, different granularity):
      - dopamine.dop_per_gpu_hour / dopamine.dop_per_gpu_second  (same pool, hour vs second)
      - synapse.base_cost_ase / birthright.qualifying_fraction / gates.stake_fraction
        (all 0.1 / 1.0 but with distinct descriptions — coincidental equality, documented)

    Disallowed: same literal value in two economically unrelated constants where the
    collision could cause a developer to substitute one for the other in code.

    Currently tracked suspicious pairs:
      - synapse.per_gpu_hour = 1000.0 and dopamine.dop_per_gpu_hour = 1000.0
        These are intentionally equal (deliberate denomination decision) but must be
        flagged until the architecture formally decides whether DOP and SYN share a
        GPU-hour rate.  Tracked: open architectural question in THREE_TIER_ECONOMIC_CONSTITUTION §3.
    """
    errors = []

    # Map value → [(section.key, description)]
    by_value: dict[float, list[str]] = {}
    for key, val in toml.items():
        by_value.setdefault(val, []).append(key)

    # Pairs that are deliberately equal — document the reason and suppress from general scan.
    # Note: dop_per_gpu_second is DELETED from TOC_CONSTANTS (derived, not declared).
    allowed_pairs: set[frozenset[str]] = {
        # 24.0: emission_window_hours (hours in a day) vs sector_count (24 governance sectors)
        # Coincidentally equal; no semantic relationship.
        frozenset({"ase.emission_window_hours", "inheritance.sector_count"}),
        # 10.0: birth_fee (10 ASE) vs sim_to_real_max (10.0× multiplier ceiling)
        # Coincidentally equal; different units (ASE vs multiplier).
        frozenset({"ase.birth_fee", "bonus_ladder.sim_to_real_max"}),
        # 1000.0: synapse/dopamine pair covered by equality_assertions above — suppress from
        # general scan since it's already enforced there.
        frozenset({"synapse.per_gpu_hour", "dopamine.dop_per_gpu_hour"}),
    }

    # Enforced equality assertions: pairs that MUST stay equal by design.
    # These fail if the values diverge (not if they match).
    # Rationale: THREE_TIER_ECONOMIC_CONSTITUTION §3.3 — pool_G += s_a × f × CONTRIBUTION_FACTOR
    # is unit-preserving. SYN and DOP share the same GPU-hour denomination; the 0.85 haircut
    # is a dimensionless efficiency tax, not a unit conversion. If these diverge, the
    # formula becomes dimensionally inconsistent.
    equality_assertions: list[tuple[str, str, str]] = [
        (
            "synapse.per_gpu_hour",
            "dopamine.dop_per_gpu_hour",
            "SYN and DOP share GPU-hour denomination by design (THREE_TIER_ECONOMIC_CONSTITUTION §3.3). "
            "Divergence means the Guild contribution formula pool_G += s × f × CONTRIBUTION_FACTOR "
            "is dimensionally inconsistent. Change both together or neither.",
        ),
    ]

    for key_a, key_b, note in equality_assertions:
        val_a = toml.get(key_a)
        val_b = toml.get(key_b)
        if val_a is None:
            errors.append(f"EQUALITY ASSERTION: {key_a} missing from TOC_CONSTANTS")
        elif val_b is None:
            errors.append(f"EQUALITY ASSERTION: {key_b} missing from TOC_CONSTANTS")
        elif abs(val_a - val_b) > 1e-9:
            errors.append(
                f"EQUALITY DRIFT: {key_a}={val_a} ≠ {key_b}={val_b}. {note}"
            )

    # General scan: flag large values (≥10.0) appearing in ≥2 unrelated sections.
    # Small fractions (0.05, 0.10, 0.25, etc.) coincidentally collide everywhere
    # and are below the threshold of meaningful duplication.
    for val, keys in by_value.items():
        if val < 10.0 or len(keys) < 2:
            continue
        sections = {k.split(".")[0] for k in keys}
        if len(sections) < 2:
            continue
        # Suppress allowed pairs
        key_set = frozenset(keys)
        if any(allowed <= key_set for allowed in allowed_pairs):
            continue
        # Only flag if no existing suspicious_pairs entry already covers this
        already_covered = any(
            frozenset({a, b}) <= key_set for a, b, _ in suspicious_pairs
        )
        if not already_covered:
            errors.append(
                f"DUPLICATE LITERAL ({val}) in {len(keys)} keys across {len(sections)} sections: "
                + ", ".join(sorted(keys))
            )

    return errors


def main():
    toml_path = ROOT / "sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml"
    if not toml_path.exists():
        print(f"ERROR: TOC_CONSTANTS.toml not found at {toml_path}", file=sys.stderr)
        sys.exit(1)

    toml = parse_toml_floats(toml_path)

    errors = []
    errors.extend(check_pool_weights(toml))
    errors.extend(check_key_constants(toml))
    errors.extend(check_julia_pool_drift(toml))
    errors.extend(check_duplicate_literals(toml))

    if errors:
        print("TOC_CONSTANTS DRIFT DETECTED:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✓ TOC_CONSTANTS drift check passed ({len(toml)} keys, 8 pools verified)")
        sys.exit(0)


if __name__ == "__main__":
    main()
