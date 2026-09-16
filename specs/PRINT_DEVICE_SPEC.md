# 3D Printer — VCP Device Specification
**Status: DRAFT 2026-09-15**

Specifies how a desktop FDM printer registers as a VCP device, what capabilities
it advertises, how the VerifiedPrintJob lifecycle maps to the 7-step VCP handshake,
and what the OSOVM verification gate expects before Dopamine is issued.

---

## 1. Overview

A 3D printer is the **cheapest sim-to-real domain** in the ecosystem:

| Property | Value |
|----------|-------|
| Hardware cost | $200–$300 (Bambu A1 Mini / Ender 3 V3) |
| Verification method | Dimensional check (caliper / scan) |
| Verification type | Binary pass/fail — zero ambiguity |
| Revenue channel | USDC — sells printed parts externally |
| Regulation | None. Self-hostable. No licences required. |
| Role in ecosystem | Fabricates drone mounts, VCP enclosures, robot parts |
| Sim-to-real bonus | 5× multiplier when predicted dims match ±2% |

The printer is the **infrastructure test** for the payment oracle before deploying
more expensive hardware. If it works here, the pattern works everywhere.

---

## 2. Device Class and Safety

```
DeviceClass:  Other("FdmPrinter")
SafetyClass:  IndoorMotion   (controlled motion; no outdoor risk; can jam)
```

`IndoorMotion` is correct because the hotend (250 °C), moving axes, and
potentially enclosed fumes require a revocable CapabilityGrant — not a
permanently-open connection.

---

## 3. DeviceManifest (DISCOVERY payload)

```json
{
  "device_id":    "printer:did:oso:7fa3bc91...",
  "label":        "Bambu A1 Mini — Node Delta-7",
  "owner_did":    "did:oso:agent:xxxxxxxx",

  "class":        { "Other": "FdmPrinter" },
  "safety_class": "IndoorMotion",

  "vcp_version":  1,
  "firmware":     "bambu-ams/1.07.03",
  "issued_at":    "2026-09-15T12:00:00Z",
  "expires_at":   "2026-09-15T18:00:00Z",

  "capabilities": [
    { "kind": "actuator",
      "actuator_type": "fdm_print_head",
      "channels": 1,
      "max_force_n": null,
      "reversible": false },

    { "kind": "sensor",
      "sensor_type": "print_progress",
      "unit": "percent",
      "range_min": 0,
      "range_max": 100,
      "sample_hz": 0.1 },

    { "kind": "sensor",
      "sensor_type": "hotend_temperature",
      "unit": "celsius",
      "range_min": 0,
      "range_max": 300,
      "sample_hz": 1.0 },

    { "kind": "sensor",
      "sensor_type": "filament_remaining_g",
      "unit": "grams",
      "range_min": 0,
      "range_max": 1000,
      "sample_hz": 0.05 },

    { "kind": "compute",
      "cpu_cores": 4,
      "ram_gb": 1.0,
      "gpu_vram_gb": null,
      "tflops_fp16": null }
  ],

  "public_key": "a3f1e8...<64 hex chars>",
  "signature":  "7bc4d0...<128 hex chars>"
}
```

---

## 4. Capability Scopes (GrantScope)

```
slice      — read model file, compute slicer params, produce G-code hash
print      — send G-code to printer, start job
monitor    — stream telemetry (progress, temps, filament)
abort      — emergency stop only; requires operator confirmation
measure    — trigger caliper/scan measurement after print completes
calibrate  — bed levelling, nozzle offset; one-shot, expires on completion
```

A standard job flow requires scopes: `[slice, print, monitor, measure]`.

`abort` requires a separate short-lived grant (max TTL: 5 minutes).
`calibrate` requires SafetyClass ≥ IndoorMotion and T3+ operator tier.

---

## 5. VCP Handshake Mapping

```
Step 1  DISCOVERY   Printer broadcasts DeviceManifest (mDNS + Nostr kind 31020)
Step 2  CHALLENGE   Broker issues ChallengeRequest:
                      required_capabilities: ["slice", "print", "monitor"]
                      nonce: <random 32 bytes>
Step 3  AUTH        Printer signs nonce with device Ed25519 key
Step 4  CAP_NEG     Broker confirms offered caps vs. required caps
Step 5  GRANT       Agent accepts CapabilityGrant:
                      scopes:   ["slice", "print", "monitor", "measure"]
                      ttl_secs: 86400   (max one print day)
                      max_jobs: 10      (governance-configurable)
Step 6  SESSION     Printer streams SessionMessage:
                      kind: TelemetryPoint (progress, temp, filament)
                      kind: JobStarted / JobCompleted / JobFailed
Step 7  RECEIPT     VcpReceipt issued on job completion
                      session_outcome: Success | Failure
                      includes: gcode_hash, material_used_g, print_secs
```

---

## 6. VerifiedPrintJob Schema

The canonical Rust struct lives at:
`Omo-Koda2/omokoda-core/src/kernel/compute/verified_work.rs`

Summary of fields:

### Provenance (set at print start)
| Field | Type | Description |
|-------|------|-------------|
| `work_id` | String | UUID, auto-generated |
| `contributor_id` | String | Agent DID |
| `device_id` | String | Printer VCP device_id |
| `model_hash` | String | SHA-256 of STL/3MF source |
| `slicer_params_hash` | String | Hash of slicer config |
| `gcode_hash` | String | Hash of emitted G-code |
| `material_type` | String | "PLA" / "PETG" / "ABS" / "TPU" |
| `material_batch` | Option<String> | Spool lot ID if tracked |

### Sim Predictions (set by slicer **before** printing)
| Field | Type | Description |
|-------|------|-------------|
| `predicted_print_secs` | u64 | Slicer time estimate |
| `predicted_filament_g` | f32 | Slicer material estimate |
| `predicted_warp_risk` | f32 | 0.0–1.0 from thermal sim |
| `sim_prediction_hash` | String | SHA-256 of all predicted fields |

### Actual Outcome (set after printing)
| Field | Type | Description |
|-------|------|-------------|
| `actual_print_secs` | Option<u64> | Real elapsed time |
| `actual_filament_g` | Option<f32> | Real material consumed |

### Physical Measurement (the sim-to-real gate)
| Field | Type | Description |
|-------|------|-------------|
| `nominal_dimensions` | Option<[f32;3]> | [x, y, z] mm from model |
| `measured_dimensions` | Option<[f32;3]> | Caliper / scan result |
| `measurement_hash` | Option<String> | SHA-256 of raw caliper data |
| `dimension_within_tolerance` | bool | All dims within 2% of nominal |

### Proof Chain
| Field | Type | Description |
|-------|------|-------------|
| `vcp_grant_id` | String | CapabilityGrant that authorized the job |
| `witness_receipts` | Vec<String> | Receipt IDs from witnesses |
| `osovm_proof` | Option<String> | OSOVM verification result |
| `zangbeto_receipt_id` | Option<String> | Zàngbétò anchor |

### Economic Output
| Field | Type | Description |
|-------|------|-------------|
| `compute_score` | Option<f64> | Set by OSOVM after verification |
| `dopamine_allocation` | Option<u64> | Micro-Dopamine issued |

---

## 7. Sim-to-Real Verification Gate

The printer uses the same gate as all other physical domains:

```
1. Slicer runs (thermal model, layer sim, time/material estimate)
2. sim_prediction_hash = sha256(predicted_secs || predicted_g || warp_risk)
3. Print executes; printer streams telemetry via VCP SessionMessage
4. Print completes → VcpReceipt issued (includes gcode_hash, actual_secs)
5. Measurement taken: caliper or photogrammetry scan
6. measurement_hash = sha256(raw_caliper_data)
7. VerifiedPrintJob.complete_success() sets dimension_within_tolerance
8. WorkClaim generated via to_work_claim():
     domain = "sim_to_real"  if tolerance passed  → 5× multiplier
     domain = "print_job"    if tolerance failed   → 2× multiplier
9. is_fully_verified(claim) requires:
     ✓ outcome == Success
     ✓ osovm_proof present
     ✓ witness_receipts non-empty
     ✓ zangbeto_receipt_id present
     ✓ measurement_hash present
10. If verified: PAYMENT RELEASES (SettlementReceipt)
```

**Tolerance rule:** `|measured - nominal| / nominal ≤ 0.02` for all three axes.
A single axis outside tolerance drops the job to `print_job` (2×), not `sim_to_real` (5×).

---

## 8. Measurement Methods (Ranked by Trustworthiness)

| Method | Verification Level | Cost | Notes |
|--------|-------------------|------|-------|
| Digital caliper + witness receipt | Full (sim-to-real eligible) | $15 tool | Human witness required |
| Photogrammetry scan | Full (if scan hash signed) | $0 (phone) | Requires calibration target |
| Camera + ArUco marker check | Partial (print_job level) | $0 | Dimension approximation only |
| Machine self-report only | None — not accepted | — | Self-report is not a witness |

For the first deployments: digital caliper + a Zàngbétò-anchored witness node
is sufficient for the 5× bonus.

---

## 9. Economic Flow

```
Print job completes → VerifiedPrintJob created
  ↓
is_fully_verified() == true
  ↓
WorkClaim.compute_score() = actual_print_secs × actual_filament_g × multiplier
  Multiplier: 5.0 (sim_to_real) or 2.0 (print_job)
  ↓
OSOVM credits Dopamine to agent
  ↓
Job payment (USDC from customer who bought the part):
  → [30%] Agent Àṣẹ treasury   (spendable — filament, shipping, cloud)
  → [55%] Burns to Dopamine signal
  → [10%] Job creator share    (Sabbath-vested 7 days)
  → [5%]  Protocol burn
  → [3.69%] Èṣù tithe on settlement
```

---

## 10. G-Code Security Policy

G-code is executable code. Unverified G-code can damage hardware (drive axes into
limits, overheat the hotend, melt PEI sheets).

**Rules (enforced by VCP broker before PRINT scope is granted):**

1. G-code must be produced by a whitelisted slicer binary (hash-verified).
2. The `gcode_hash` in the CapabilityGrant must match the file sent to the printer.
3. A slicer-config policy file restricts: max temp (hotend ≤ 280 °C), max speed,
   axis bounds. Any G-code exceeding the policy is rejected before print start.
4. `M112` (emergency stop) opcode must be reachable at all times regardless of grant state.

---

## 11. Printer Variants and Capability Flags

| Printer | AMS/MMU | Enclosed | Max Temp | VCP Notes |
|---------|---------|----------|----------|-----------|
| Bambu A1 Mini | AMS Lite (4-colour) | No | 300 °C | Preferred dev device |
| Bambu X1C | AMS (16-colour) | Yes (HEPA) | 300 °C | Best for production fleet |
| Creality K2 Plus | CFS (4-colour) | Yes | 300 °C | Open ecosystem |
| Ender 3 V3 KE | None | No | 300 °C | Minimum viable, no AMS |

AMS (Automatic Material System) adds an `ams_slot` field to `VerifiedPrintJob`
and a `material_batch` audit trail per spool.

---

## 12. Sector Sequencing Note

From `SECTOR_AGENT_DEPLOYMENT_SPEC.md` Section 8:

> **SECOND — 3D Printing (Infrastructure + Verification Test)**
> - Cheapest sim-to-real domain ($200–300 printer)
> - Binary verification (dimensions in tolerance or not)
> - No regulation, self-hostable, no logistics burden
> - Fabricates parts for everything else (drone mounts, VCP enclosures)
> - Earns USDC selling parts → tests Gap 1 (Àṣẹ ↔ USDC ramp)

Deploy one printer node before spending $25k on a drone fleet. If the verification
oracle, Dopamine credit, and USDC settlement all work on a $250 printer, they will
work on a $25,000 drone.

---

## 13. File References

| Topic | Location |
|-------|----------|
| VerifiedPrintJob (Rust struct) | `Omo-Koda2/omokoda-core/src/kernel/compute/verified_work.rs` |
| VCP DeviceManifest (Rust type) | `VCP/crates/vcp-types/src/device.rs` |
| WorkClaim generalized gate | `sovereign-stack/sovereign-types/src/work_claim.rs` |
| OSOVM verify gate (Julia) | `OSOVM/src/oso_vm.jl — is_fully_verified(vm, claim::Dict)` |
| Bonus ladder constants | `sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml [bonus_ladder]` |
| Sector deployment context | `sovereign-eco-blueprint/specs/SECTOR_AGENT_DEPLOYMENT_SPEC.md` |
| Sector pool economics | `sovereign-eco-blueprint/specs/ECONOMICS_DECISIONS.md` |
