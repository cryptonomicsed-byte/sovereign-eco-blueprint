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
        ("ase.max_daily_emission", 1440.0, "1440 ASE/day"),
        ("dopamine.ase_to_dopamine", 10000.0, "1:10,000 burn ratio"),
        ("dopamine.decay_min", 0.001, "min decay 0.1%/day"),
        ("dopamine.decay_max", 0.020, "max decay 2.0%/day"),
        ("synapse.per_gpu_hour", 1000.0, "1000 Synapse/GPU-hour"),
        ("synapse.max_pool_share", 0.005, "0.5% pool share"),
        ("esu.tithe_rate", 0.0369, "Èṣù 3.69%"),
        ("gates.stake_fraction", 0.10, "10% stake gate"),
        ("ritual.sabbath_multiplier", 1.10, "Sabbath 1.1×"),
        ("ritual.jubilee_minor_multi", 2.0, "Jubilee 2.0×"),
    ]

    for key, expected, desc in checks:
        actual = toml.get(key)
        if actual is None:
            errors.append(f"MISSING: {key} ({desc}) not in TOC_CONSTANTS.toml")
        elif abs(actual - expected) > 1e-9:
            errors.append(f"DRIFT: {key} ({desc}): TOML={actual} expected={expected}")

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
