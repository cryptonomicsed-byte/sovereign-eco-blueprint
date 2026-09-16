# Witness Node Specification
**Status: DRAFT 2026-09-15**

Physical witness nodes are the hardware instantiation of the `witness` pool
(0.05 × daily Àṣẹ emission). A witness node is a low-cost, staked M5Stack
device that independently observes physical agent work and broadcasts signed
commitment hashes over LoRa mesh — without needing the internet.

---

## 1. Why Witness Nodes Exist

The payment oracle (sim → verify → execute → measure → payment) has a gap:
**who verifies that the measurement is honest?**

A robot self-reporting "I sprayed 30 ha" is an interested party.
Its own sensor log is not evidence — it could be fabricated, replayed, or wrong.

Independent witnesses close this gap:

```
Agent executes work
  → broadcasts WorkCommitment over LoRa (32-byte hash, not payload)
  → multiple nearby witness nodes independently observe and sign
  → N of M corroboration produces a WitnessBundle
  → WitnessBundle is the evidence that satisfies is_fully_verified()
  → payment releases
```

Without corroboration, verification is the agent's word.
With corroboration, verification is the aggregate of independent observers
that have no stake in the outcome.

**Fleet cost:** 50 witness nodes at ~$50 each = **$2,500**.
That is one-tenth of a single DJI T50 kit.
You can blanket a neighbourhood for the cost of one drone.

---

## 2. LoRa Is the Right Radio — For a Structural Reason

LoRa (SX1262 / SX1276) carries ~1–10 kbps effective in Meshtastic.
It cannot carry video. That is not a compromise — it is the correct architecture.

```
What the verification layer actually needs to transmit:

  WorkCommitment  =  sha256(work_id || agent_id || task_hash || timestamp)
                  =  32 bytes

  CorroborationAck = attest_id || witness_id || sig
                  =  ~100 bytes

Total per work event: < 200 bytes over LoRa.
```

The heavy data (video, sim state, point cloud, G-code) never goes on the mesh.
Only its hash does. LoRa is a **commitment radio**, and that is exactly what
the verification layer needs.

Additional advantages in target markets:
- No SIM, no carrier, no cell tower, no ISP, no permission
- Range: 2–15 km line-of-sight, 400m–2km urban
- Power: weeks on a 2000 mAh battery
- Already in `omokoda-mesh-firmware` (M5Stack env targets at release level)

---

## 3. Bill of Materials (per node)

### Tier 1 — Minimum Viable Witness Node (~$30)

| Component | Part | Price [H] | Notes |
|-----------|------|-----------|-------|
| MCU | M5Stamp LoRa Module (SX1262) | $5.50 | ESP32-S3, 8MB flash, SX1262 onboard |
| Power | LiPo 2000 mAh + USB-C | ~$6 | Weeks of runtime |
| Enclosure | 3D-printed | ~$2 | Print locally; VCP device spec covers this |
| Total | | **~$14** | Commitment-only node |

Capability: broadcasts/receives LoRa commitments, signs with device key.
No camera. Not eligible for spatial twin capture.

### Tier 2 — Standard Witness Node (~$60)

| Component | Part | Price [H/E] | Notes |
|-----------|------|------------|-------|
| MCU | M5Stack CoreS3 | ~$45 [E] | ESP32-S3, 16MB flash, display, accelerometer |
| LoRa | LoRa Module 13.2 (SX1262) | $24.90 [H] | Stackable |
| Camera | OV2640 Unit (2MP) | ~$8 [E] | Perimeter capture, not video |
| Power | 2500 mAh internal + solar top-up | ~$10 [E] | |
| Enclosure | IP65 outdoor box | ~$5 [E] | |
| Total | | **~$93** | Full evidence node |

Capability: LoRa mesh, camera snapshot on trigger, GPS optional, display shows
local work queue. Eligible for spatial capture bonus (2× compute score).

### Tier 3 — LLM Edge Node (~$200)

| Component | Part | Price [H] | Notes |
|-----------|------|-----------|-------|
| Compute | M5Stack LLM630 Compute Kit (AX630C) | $99.90 | 1 TOPS NPU, runs quantized models |
| LoRa | LoRa Module 13.2 | $24.90 | |
| Camera | Camera Module 8MP for LLM630 | $32.90 | |
| Storage | microSD 32GB | ~$8 | Offline model + evidence log |
| Power | 12V PoE or solar | ~$20 [E] | |
| Total | | **~$186** | Offline inference + witness |

Capability: on-device classification (anomaly detection, object recognition),
commitment verification at the edge without internet (see §9).

**Start with Tier 2.** Tier 1 for dense mesh fill. Tier 3 for permanent
installations (entry points, high-value infrastructure).

---

## 4. WorkCommitment Format (LoRa broadcast)

Transmitted by the agent's companion computer over LoRa when work begins and
when work completes. **Not** a full payload — a commitment only.

```
WorkCommitment {
    version:       u8 = 0x01
    kind:          u8  // 0x01=start, 0x02=complete, 0x03=abort
    work_id:       [u8; 16]   // UUID128 (truncated for LoRa efficiency)
    agent_id:      [u8; 8]    // first 8 bytes of agent DID
    task_hash:     [u8; 16]   // sha256(task_params)[..16]
    ts_unix:       u32        // epoch seconds
    signature:     [u8; 16]   // first 16 bytes of Ed25519 sig (truncation OK for LoRa)
}
Total: 1 + 1 + 16 + 8 + 16 + 4 + 16 = 62 bytes
```

On complete events, the agent appends:

```
WorkResult {
    ...WorkCommitment header (62 bytes)...
    outcome_hash:  [u8; 16]   // sha256(measurement_data)[..16]
    score_fixed:   u16        // compute_score × 100, fixed-point
}
Total: 80 bytes
```

Both fit in a single LoRa frame at SF7/125kHz.
The full SHA-256 hashes are published to Nostr/Freenet; LoRa carries only the
truncated commitments for timing and corroboration.

---

## 5. Corroboration Rule

A `WitnessBundle` is valid when:

```
N_corroborated ≥ min_witnesses  AND  N_corroborated / N_heard ≥ agreement_ratio
```

Default parameters (governance-configurable in `TOC_CONSTANTS.toml`):

| Parameter | Default | Notes |
|-----------|---------|-------|
| `min_witnesses` | 2 | Absolute floor |
| `agreement_ratio` | 0.66 | ≥ 2/3 of observers must agree |
| `max_window_secs` | 300 | Observations must be within 5 min of each other |
| `min_stake_per_witness` | 10 Àṣẹ | Witness operator stake floor |

A witness node that signs a commitment it could not have physically observed
(outside range, wrong GPS cell) is slashable. GPS + LoRa RSSI together bound
the plausible observation radius.

### Corroboration Types

| Level | Witnesses | Evidence Required | Multiplier eligible |
|-------|-----------|-------------------|-------------------|
| Single | 1 | Signed hash only | `print_job` (2×) |
| Corroborated | ≥ 2 | Signed hashes, agreement ≥ 66% | `sim_to_real` (5×) |
| Full | ≥ 3 + Zàngbétò | Hashes + sensor data + anchor | `sim_to_real` (5×) + potential bonus |

The `is_fully_verified()` check in `sovereign-types/src/work_claim.rs` requires
`witness_receipts.len() ≥ witness_policy.min_witnesses` — witness nodes are how
that requirement gets satisfied in the physical world.

---

## 6. WitnessAttestation Wire Format

When a witness node corroborates a WorkCommitment, it constructs a
`WitnessAttestation` (existing type in `Witness/crates/witness-types/src/attestation.rs`):

```rust
WitnessAttestation {
    attest_id:        uuid_v4(),
    kind:             AttestationKind::PolicyExecution,
    vcp_session_id:   <from agent's active VCP session>,
    device_id:        <witness node's VCP device_id>,
    agent_id:         <from WorkCommitment.agent_id>,
    sim_receipt_id:   <if sim was run beforehand>,
    observation_hash: sha256(WorkCommitment bytes || sensor_readings),
    outcome:          "corroborated" | "anomaly" | "not_observed",
    status:           AttestationStatus::Signed,
    latitude:         <witness GPS if available>,
    longitude:        <witness GPS if available>,
    altitude_m:       None,  // ground-level
    nostr_event_id:   <published to Nostr kind 31020>,
    zangbeto_anchor:  <if anchored>,
    arp_receipt_id:   <ARP receipt from broker>,
    timestamp:        Utc::now(),
    signature:        <Ed25519 over canonical_hash()>,
}
```

This is published to Nostr (kind 31020) and anchored to the Zàngbétò receipt
chain. The broker at `witness-broker` collects attestations and assembles the
`WitnessBundle` when min_witnesses is reached.

---

## 7. Stake Requirement

Every witness node operator must stake before their attestations count.

```
Minimum stake:   10 Àṣẹ (governance-configurable)
Stake lock:      Duration of deployment season (governance-configurable)
Slash condition: Signing a commitment that is physically impossible
                 (wrong location, wrong time window, fabricated sensor data)
Slash amount:    Up to 100% of stake for provable fraud
```

The stake is posted via `@stake` (0x20) opcode, referencing the witness node's
`device_id`. Unstaking is only allowed when no unresolved WitnessAttestation
is pending.

The stake requirement has two effects:
1. Filters Sybil witness nodes (mass-manufacturing fake witnesses costs real Àṣẹ)
2. Aligns witness operator incentive with accuracy (they earn from the pool when honest)

---

## 8. How the 0.05 Witness Pool Pays Operators

From `TOC_CONSTANTS.toml`:
```toml
[ase.pools]
witness = 0.05   # 5% of 1440 ASE/day = 72 ASE/day to the witness pool
```

**72 Àṣẹ/day** flows to the witness pool.

Distribution rules (governance-configurable):

```
Witness pool daily emission (72 ASE/day)
  → 50% proportional to verified attestations per node (earned by work)
  → 30% proportional to uptime (staked + online per epoch)
  → 20% staking yield (proportional to stake amount)
```

Example: a 50-node deployment, each staked 10 Àṣẹ, all active:
- Uptime share per node: (72 × 0.30) / 50 ≈ 0.43 Àṣẹ/day ≈ 157 Àṣẹ/year
- At current emission value, a staked node earns back its stake in roughly 3 months

This is intentionally modest. Witness nodes earn from the WORK they enable, not
from the network's growth. The incentive is operational, not speculative.

**ANTI-FARMING RULE:** A witness node that never corroborates a real
WorkCommitment earns zero from the attestation share (50%). Uptime share
still pays, but only at 30% weight. A ghost node earns ~40% of a working node.
Not zero (to prevent perverse incentives to fabricate work), but substantially less.

---

## 9. Edge Verification Spike (OSO-IR Minimal VM)

Hermes identified this as worth spiking before believing. The question:

> Can a minimal OSO-IR opcode subset fit in 512KB SRAM (ESP32-S3's available
> heap) and verify a WorkCommitment locally without internet?

The minimal subset needed for commitment verification:

```
REQUIRE   (0x29)  — pre-condition check
BALANCE   (0x23)  — query stake
RECEIPT   (0x1F)  — produce immutable proof
EMIT      (0x2A)  — broadcast result
STAKE     (0x20)  — verify stake posted
SHA256    (new)   — hash primitive (could reuse COMPUTE_PROOF opcode)
```

6 opcodes. The IrInstruction struct is ~80 bytes. A verification program
would be ~20–40 instructions = ~3.2 KB for the program.

The runtime stack, however, needs:
- Instruction dispatch table: 256 entries × 8 bytes = 2 KB
- Execution stack: 32 frames × 64 bytes = 2 KB
- String heap for receipts: ~8 KB minimum

**Estimate: ~15–20 KB for a minimal verifying runtime.**
ESP32-S3 has 512 KB SRAM but only ~300 KB free after FreeRTOS + WiFi stack.
This fits. A LoRa-only build (no WiFi) frees another ~100 KB.

**Verdict: plausible. Run the spike on a CoreS3 before committing.**

The spike target:
```
1. Implement 6-opcode subset in C (not Julia) targeting ESP32-S3
2. Load a WorkCommitment verification program from flash
3. Execute on a received LoRa frame
4. Emit RECEIPT opcode output over serial
5. Measure: peak SRAM usage, execution time per frame
```

If it passes, every Tier 2+ witness node becomes a verifying node — no internet
required. That property — **physical-world verification with no connectivity** —
is the one capability no existing DePIN has.

---

## 10. M5Stack Role Map by Sector

From Hermes: "M5Stack's Unit ecosystem has hundreds of sensors.
MAP THE UNITS TO YOUR SECTORS."

| Sector | Primary Sensor | M5Stack Unit | Node Tier |
|--------|---------------|-------------|-----------|
| Agriculture | Soil moisture, NPK, humidity | ENV III Unit | T2 |
| Water | pH, turbidity, dissolved O₂ | Water Quality Unit | T2 |
| Air | CO₂, VOC, PM2.5 | TVOC/eCO₂ Unit | T2 |
| Health | Temperature, heart rate | Heart Unit | T2 |
| Infrastructure | Vibration, crack sensor | IMU + accelerometer | T1 |
| Security | PIR, ultrasonic | PIR Unit | T1 |
| Waste | Weight, fill level | ToF Unit | T1 |
| Energy | Power consumption, solar input | Voltmeter Unit | T2 |
| Logistics | GPS track, barcode | GPS Unit + RFID | T2 |
| Spatial twin | Camera + GPS | Camera + GPS Unit | T2 |

Each node profile matches naturally to one or more of the 24 sectors.
A water-quality node staked to the "health" or "environment" sector earns from
both the witness pool and sector-specific multipliers when its readings are
used to verify agent work.

---

## 11. Citizen Terminal

From Hermes: "for 'all citizens get quarterly income' in underbanked markets,
most people have no smartphone."

M5Paper (e-ink) or Cardputer (~$20–80 [E]) as a citizen terminal:

```
Display:
  - Àṣẹ balance (UBI received this epoch)
  - Tier level
  - 3 nearest agent locations
  - Latest sector news (one-line, Nostr relay)
  - Incoming message from agent

Input:
  - Cardputer: physical keyboard for basic commands
  - M5Paper: touch buttons for confirm/deny

Connectivity:
  - Primary: LoRa mesh (no internet required)
  - Fallback: BLE to phone if available

Battery: e-ink survives weeks between charges; readable in direct sun
```

A citizen terminal is **not** a compute node. It is a display and a relay.
It earns nothing on its own — it is an access primitive for people who will
never install an app.

---

## 12. What Witness Nodes Are NOT

| Cannot do | Why |
|-----------|-----|
| Agent brain | ESP32-S3 at 240MHz / 512KB SRAM — agent runtime doesn't fit |
| Flight controller | 40kg spray drone needs STM32/Pixhawk; ESP32 is companion only |
| Dopamine compute | AX630C/AX8850 are inference NPUs; Dopamine pool is GPU training |
| Video transport | LoRa can't. Use WiFi/LTE for bulk; LoRa carries commitments only |
| Replace VCP broker | VCP broker runs on a gateway (Pi/RISC-V); witness nodes are leaf nodes |

---

## 13. Build Instructions (First Two Nodes)

Prerequisites (run on VPS or x86 box — PlatformIO on Termux ARM64 is slow):

```bash
cd ~/omokoda-mesh-firmware
pio run -e m5stack-cores3          # CoreS3 (T2 standard node)
pio run -e m5stack-stamp-c3        # Stamp C3 (T1 minimal node)
```

Flash:
```bash
pio run -e m5stack-cores3 --target upload --upload-port /dev/ttyACM0
```

Config (after flash, via Meshtastic app or serial):
```
Region:      choose correct LoRa frequency for deployment country
Node ID:     set to witness node's VCP device_id (hex)
Channel key: deployment-specific (from sector pool config)
Role:        ROUTER_CLIENT
```

**Note:** PlatformIO compile belongs on the VPS (2.25.70.156) or x86 box,
not the phone. The build outputs a `.bin` file that can be flashed anywhere.

---

## 14. File References

| Topic | Location |
|-------|----------|
| WitnessAttestation type | `Witness/crates/witness-types/src/attestation.rs` |
| ObservationBundle type | `Witness/crates/witness-types/src/observation.rs` |
| WorkClaim witness_policy | `sovereign-stack/sovereign-types/src/work_claim.rs` |
| Witness pool constant | `sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml [ase.pools]` |
| Meshtastic firmware | `omokoda-mesh-firmware/` (env:m5stack-cores3 et al.) |
| VCP device spec | `VCP/crates/vcp-types/src/device.rs` |
| Sector pool deployment | `sovereign-eco-blueprint/specs/SECTOR_AGENT_DEPLOYMENT_SPEC.md` |
| Print device (sim-to-real) | `sovereign-eco-blueprint/specs/PRINT_DEVICE_SPEC.md` |
