# Omarchy Sovereign Device — Full Implementation Blueprint
# What Needs to Be Built to Bring the Node to Life

Date: 2026-09-07  
Status: Spec complete (artifacts 01-06 + patches P1-P5). Zero hardware built.  
Scope: Everything required — from bare board to fully operational sovereign node.

---

## THE MAP AT A GLANCE

```
PHASE 0  ──  Image + Birth Ceremony        (hardware → Arch ARM → npub → relays)
PHASE 1  ──  Identity Layer                (NIP-46 bunker, BIPON39, Sui binding)
PHASE 2  ──  Protocol Stack                (Nostr sync, Reticulum, Freenet)
PHASE 3  ──  Power + Thermal Runtime       (profiles, gates, duty cycling)
PHASE 4  ──  Body Runtime                  (Rust binary, Noise KK, pairing flow)
PHASE 5  ──  Economic Layer                (F1 gate, ActReceipts, Sui/AIO)
PHASE 6  ──  Spatial Twin                  (capture → splat pipeline → GE-Ver)
```

---

## WHAT IS ALREADY DONE

| Artifact | Status | Notes |
|----------|--------|-------|
| `first_boot_birth.py` | **COMPLETE** | 250 lines, pure Python, zero deps, BIP-340 inline, outbox fallback |
| Nostr event schemas 31000-31030 | **COMPLETE** | artifact 01 — all tags, all engrams |
| Body runtime interface spec | **COMPLETE** | artifact 02 — session state machine, JSON-RPC |
| Image + birth procedure | **COMPLETE** | artifact 03 — packages, systemd units, 9-step flow |
| Power/thermal spec | **COMPLETE** | artifact 04 — 6 profiles, thresholds, battery gates |
| Pairing flow reference | **COMPLETE** | artifact 05 — full walkthrough + body_sim.py stub |
| Spatial twin pipeline | **COMPLETE** | artifact 06 — COLMAP → Julia → tiling → GE-Ver |
| Spec patches P1-P5 | **COMPLETE** | key derivation, Noise KK, F1 receipt, entropy, bunker |
| `bipon39` CLI | **COMPLETE** | Rust, 256 Yoruba tokens, on VPS; needs ARM cross-compile |
| `body_sim.py` | **PARTIAL** | WS skeleton exists; Noise KK is a placeholder print |

**The entire spec layer is done. What remains is building every layer below it.**

---

## PHASE 0 — IMAGE + BIRTH CEREMONY

### 0.1 Hardware Procurement

Target: **Raspberry Pi 5** (4GB or 8GB)  
Camera: **AI Camera (Sony IMX500)** for spatial mining  
Optional depth: Luxonis OAK-D Lite over USB  
Storage: 64GB+ A2 microSD or NVMe HAT  
Radio: LoRa HAT (for Reticulum mesh) — e.g. Waveshare SX1262

If no Pi 5: **RK3588 board** (Orange Pi 5 Plus / Rock 5B) — same Arch ARM path.  
For development (Phase 0-3): any ARM64 Linux box or QEMU suffices.

### 0.2 Arch Linux ARM Image Build

**What:** Bootable aarch64 Arch image with sovereign layer pre-installed.

Tasks:
- [ ] Set up cross-compile / image build environment on VPS (or x86 dev box)
- [ ] Base: `archlinux-aarch64` rootfs + `linux-raspberrypi5` or `linux-rk3588`
- [ ] Pacman packages (from artifact 03):
  ```
  base base-devel linux-firmware systemd openssh sudo git curl jq
  python python-pip uv networkmanager iwd bluez lm_sensors rfkill
  cpupower age pocketbase
  ```
- [ ] Cross-compile `omokoda` Rust binary for `aarch64-unknown-linux-gnu`
- [ ] Copy sovereign layer binaries into `/usr/local/bin/`:
  - `omokoda` (Pillar 1 agent runtime)
  - `bipon39` (cross-compiled from VPS source)
  - `nak` (static Nostr CLI binary — grab from release, no build needed)
  - `ifa` (optional IfáScript CLI)
- [ ] `pip install rns lxmf websockets` into image Python
- [ ] Copy `minipae.py` into `~/genteam/`
- [ ] Install `first_boot_birth.py` → `/usr/local/bin/first-boot-birth`
- [ ] Flash → test boot on real board

**Effort:** 2-3 days for first working flash. Iterative from there.

### 0.3 systemd Units

Five units must be installed in the image (artifact 03):

| Unit | Type | Condition |
|------|------|-----------|
| `first-boot.service` | oneshot | `ConditionPathExists=!/var/lib/sovereign/birthed` |
| `sovereign-agent.service` | persistent | Starts after birth; runs `omokoda` loop |
| `sovereign-sync.service` | persistent | Drains `~/.sovereign/outbox/` → relays, then Reticulum |
| `sovereign-spatial.service` | manual | `systemctl start` only; triggers spatial-mining profile |
| `sovereign-profile@.service` | oneshot | Template; `%i` = profile name |

Tasks:
- [ ] Write all 5 unit files
- [ ] Wire `sovereign-agent.service` to call `omokoda serve` (port 7777)
- [ ] Wire `sovereign-sync.service` to flush outbox → relays via `nak publish`
- [ ] Test first-boot oneshot: runs birth script, touches `/var/lib/sovereign/birthed`, disables itself
- [ ] Verify it does NOT re-run on subsequent boots

### 0.4 Birth Script Validation

`first_boot_birth.py` is WRITTEN but not field-tested on ARM.

Tasks:
- [ ] Run on clean Arch ARM (no bipon39, no ifa) → verify fallback path works
- [ ] Run with bipon39 present → verify BIPON39 mnemonic path
- [ ] Verify `kind 31000` event JSON matches artifact 01 schema exactly (tags, content fields)
- [ ] Verify `kind 31001` device binding event
- [ ] Verify IP Root: `sha256(npub || device_id || birth_ts)` matches spec
- [ ] Verify outbox fallback: if no websockets, file written to `/var/lib/sovereign/outbox/`
- [ ] Verify relay publish (when websockets present): real relay accepts the event
- [ ] **Critical**: nsec is printed ONCE to birth.log then NEVER stored plaintext — verify log scrub or redirect

**Effort:** 1 day on hardware.

---

## PHASE 1 — IDENTITY LAYER

### 1.1 NIP-46 Bunker (Patch P5)

**Current gap:** Birth script writes `nsec` as plain hex for the `schnorr_sign` call. The spec requires the nsec to live ONLY in the bunker process — the agent process never holds it.

Tasks:
- [ ] Write `sovereign-bunker.service` systemd unit: runs as `sovereign-bunker` user (own account), seccomp filter
- [ ] Bunker binary (Python or Rust): listens on `/run/sovereign/bunker.sock` (unix socket)
- [ ] Protocol: receives `{"method":"sign","event":{...}}` → responds `{"sig":"..."}`
- [ ] On first boot: seed written to bunker's encrypted keystore (age + LUKS or kernel keyring)
- [ ] Birth script updated: seed → bunker keystore, then calls bunker for signing (not inline schnorr)
- [ ] Main agent process (`omokoda`) delegates all signing to bunker via unix socket
- [ ] Test: killing the agent process must NOT expose nsec (it never held it)

**Effort:** 1 day for Python bunker; 2 days for Rust with seccomp.

### 1.2 BIPON39 Mnemonic (Patch P1)

`bipon39` CLI exists on VPS. It needs to be available on the ARM image and wired into the birth script as a first-class path (not just optional fallback).

Tasks:
- [ ] Cross-compile `bipon39` for `aarch64-unknown-linux-gnu`
- [ ] Verify: `bipon39 generate --seed <hex>` → 256-token Yoruba mnemonic
- [ ] Verify: `bipon39 derive <mnemonic>` → same seed hex back (round-trip)
- [ ] Wire in birth script: `bipon39 generate` → mnemonic printed ONCE to log → fingerprint stored in engram
- [ ] Verify fingerprint: `sha256(mnemonic_words)[:16]` stored in `mem/agent/birth.json`, never the words
- [ ] Birth event tags: `["bipon39-fp", "<fingerprint>"]` (not words)

**Effort:** Hours (bipon39 is already built; just cross-compile + wire).

### 1.3 Keystore Encryption (Patch P4)

**Current state:** Birth script collects entropy, derives seed, but does not encrypt seed at rest.

Tasks:
- [ ] First-boot: after deriving seed, encrypt it with `age` to `/var/lib/sovereign/identity.age`
- [ ] Decryption key: owner's pubkey (or passphrase-derived on first unlock)
- [ ] Alternatively: LUKS-encrypt the entire `/var/lib/sovereign/` partition
- [ ] Bunker reads from encrypted keystore on startup (prompts or uses kernel keyring)
- [ ] Verify: raw seed hex is NOT on disk anywhere in plaintext after first boot

**Effort:** Half a day.

### 1.4 Sui Address Binding (Economic Identity)

Three identities that must NEVER collapse (sovereign invariant #3):
- **Agent identity**: npub / IP Root
- **Device identity**: device_id / hardware fingerprint
- **Economic identity**: Sui address

Tasks:
- [ ] Derive Sui address from a separate BIP-32 path (or standalone Ed25519 key)
- [ ] Record Sui address in `mem/agent/identity.json` at birth
- [ ] Publish binding: kind 31001 `content.sui_address` field (already in schema)
- [ ] Ensure the 3 identities are cryptographically linked but never collapsed
- [ ] Future: AIO contract stores this binding on-chain for economic entitlements

**Effort:** 1 day (derivation + schema wire).

---

## PHASE 2 — PROTOCOL STACK

### 2.1 Nostr Outbox → Relay Sync

`sovereign-sync.service` must drain the outbox and keep events flowing.

Tasks:
- [ ] Write sync daemon: watches `/var/lib/sovereign/outbox/*.json`
- [ ] Primary path: `nak publish --relay wss://omokoda.duckdns.org:3443 <event.json>`
- [ ] Retry on failure: exponential backoff, leave file in outbox if relay down
- [ ] When `wss://` unavailable: switch to Reticulum/LXMF delivery (next section)
- [ ] Watch configured relay list from `/etc/sovereign/relays.conf`
- [ ] Ship agent's own relay address (omokoda.duckdns.org) + Damus as fallback
- [ ] After successful publish: move file to `/var/lib/sovereign/published/` (audit trail)

**Effort:** 1-2 days.

### 2.2 Reticulum + LXMF Transport

For offline-first mesh operation.

Tasks:
- [ ] Verify `rns` + `lxmf` install on ARM (`pip install rns lxmf`)
- [ ] Write `sovereign-reticulum.service`: starts `rnsd` daemon (Reticulum network stack)
- [ ] Configure Reticulum interfaces: LoRa HAT (if present), TCP bridge to internet
- [ ] Write LXMF delivery module: accepts event JSON → wraps in LXMF → sends to peer LXMF address
- [ ] Wire into sync daemon: if Nostr relay unreachable → fall back to LXMF delivery to mesh peers
- [ ] LXMF announce: device announces itself on mesh every 60s (listen profile), 15s (active)
- [ ] Test: 2 nodes, no internet → events flow via LoRa mesh, both sync state

**Effort:** 2-3 days (Reticulum config is the hard part).

### 2.3 Freenet Node (Phase 2 stretch goal)

Freenet provides shared living state (GuildRoom, WorkspaceState, presence).

Tasks:
- [ ] Install Freenet daemon on the node (ARM build or grab release)
- [ ] Configure: GuildRoom contract → replicated state for agent's guilds
- [ ] Wire agent: on join guild → post to Freenet contract (not Nostr)
- [ ] Wire agent: on receive task → read from Freenet WorkspaceState
- [ ] Delegate layer (Patch P5 extension): Freenet identity delegate = node's signing authority
- [ ] Test: node offline → local Freenet state maintained → when internet returns → global sync

**Effort:** 3-5 days (Freenet ARM build is the blocker; this may be Phase 3 work).

---

## PHASE 3 — POWER + THERMAL RUNTIME

### 3.1 sovereign-profile Script + Units

Spec is in artifact 04. Nothing is built yet.

Tasks:
- [ ] Write `/usr/local/bin/sovereign-profile` script (bash or Python):
  - Takes profile name as argument
  - Switches cpufreq governor: `echo powersave > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor`
  - Controls radios: `rfkill block/unblock wifi` / LoRa power GPIO
  - Enables/disables camera pipeline service
  - Prints "profile: <name> activated" + logs
- [ ] Write `sovereign-profile@.service` (template unit)
- [ ] Implement 6 profiles: `deep-sleep`, `listen`, `active`, `light-work`, `spatial-mining`, `high-performance`
- [ ] Battery gate: check `/sys/class/power_supply/BAT0/capacity` before allowing spatial/high-perf
- [ ] Thermal gate: check `/sys/class/thermal/thermal_zone0/temp`:
  - 60-70°C → refuse spatial/high-perf start
  - 70-80°C → hard throttle to powersave
  - >80°C → stop spatial, unload heavy models, fan max
- [ ] Expose `GET /v1/power` endpoint: `{profile, watts, battery, since_profile_start}`

**Effort:** 1-2 days (deterministic, no hardware surprise).

### 3.2 Power Accounting API

Tasks:
- [ ] Add rolling energy ledger (profile × draw estimate × time) to the agent's local state
- [ ] Agent queries it before toggling spatial-mining: "this will drain ~15%/hr at current battery"
- [ ] Expose via omokoda's `/v1/power` endpoint

**Effort:** Half a day.

---

## PHASE 4 — BODY RUNTIME (EMBODIMENT)

This is the most complex phase. Required only when the first physical/sim body is connected.

### 4.1 Body Simulator (body_sim.py completion)

The sim exists but the Noise KK is a placeholder print.

Tasks:
- [ ] Complete `scripts/body_sim.py`:
  - JSON-RPC 2.0 over WebSocket (`websockets` lib) on `127.0.0.1:18877`
  - HTTP stub on `127.0.0.1:18878` (`/advertise`, `/status`) for curl inspection
  - State machine: DISCOVERY → OFFERED → ACCEPTED → KEYED → ACTIVE → TERMINATED
  - Real policy enforcement: geofence box, max-speed, TTL
  - Fake telemetry 1Hz: pose drifts toward last goto target, battery drains at 0.1%/s
  - Print each state transition clearly
  - Noise KK: replace print with real key material exchange (Python cryptography lib or subprocess to Rust)
- [ ] Test the full pairing flow (artifact 05 reference) against the completed sim
- [ ] Sim must reject out-of-policy commands with a reason string

**Effort:** 1 day to complete sim to spec.

### 4.2 Body Runtime Binary (Rust, ~600 LOC)

The production body runtime. Must run on any drone/robot/IoT body.

Structure (artifact 02):
```
body/
  main.rs        # WS + Reticulum transport, JSON-RPC dispatch
  session.rs     # state machine, timeouts, zeroize
  noise.rs       # Noise KK (snow crate), prologue = offer+accept ids
  policy.rs      # geofence/speed/TTL checks
  vendor.rs      # VendorAutopilot trait: px4 | ardupilot | ros2 | sim
  advertise.rs   # capability registry + presence publisher
  telemetry.rs   # 1Hz frame builder, seq counter
```

Tasks:
- [ ] `cargo new body --bin`
- [ ] Add deps: `snow` (Noise protocol), `tokio`, `serde_json`, `tungstenite` (WS), `zeroize`
- [ ] Implement session state machine with all 6 states + timeout transitions
- [ ] Implement JSON-RPC dispatch: `advertise`, `offer`, `command`, `heartbeat`, `end_session`
- [ ] Implement Noise KK: prologue = `sha256(offer_event_id || accept_event_id)`
- [ ] Implement policy enforcer: geofence, max-speed, TTL — reject with reason
- [ ] Implement `VendorAutopilot` trait + `SimAutopilot` (fake pose moves toward target)
- [ ] Zeroize session keys on TERMINATED (`zeroize` crate)
- [ ] Emergency stop: if agent unreachable → finish current op → hold → retry 30s → safe-stop
- [ ] Test against completed body_sim.py (Python side ↔ Rust side)

**Effort:** 3-4 days for core runtime; another day for Noise KK.

### 4.3 Noise KK (Patch P2)

The only patch with real crypto work. Required before real embodiment sessions.

Tasks:
- [ ] In body runtime: `snow::Builder::new("Noise_KK_25519_AESGCM_SHA256".parse())`
- [ ] Agent static key = secp256k1 npub-derived signing key (via conversion or a parallel Ed25519 key)
- [ ] Body static key = long-lived device key (never the agent's nsec)
- [ ] Prologue = `sha256(offer_31010_event_id || accept_31011_event_id)` — binds handshake to Nostr events
- [ ] Result: two channel keys (cmd channel, telemetry channel)
- [ ] Keys zeroized on TERMINATED
- [ ] Test: replayed offer must fail (prologue hash differs)

**Effort:** 1-2 days (snow crate handles the hard math).

---

## PHASE 5 — ECONOMIC LAYER

### 5.1 F1-Gated Spatial Mining Receipt (Patch P3)

The quality gate for reward-eligible spatial captures.

Tasks:
- [ ] Implement F1 scorer in the spatial mining service:
  - Input: captured sample (camera frames + pose + GPS)
  - Metrics: coverage (% of tile area), novelty (delta vs base map), quality (sharpness/resolution)
  - F1 = harmonic mean of precision (coverage) and recall (novelty)
- [ ] Gate logic (deterministic, no LLM):
  ```
  if f1 >= 0.777 and privacy != "local": emit reward claim pointer
  if f1 <  0.777: store, mark "pending-quality", no claim
  local-only: store + IP Root, never emit claim
  ```
- [ ] Build kind 31020 event (artifact 01 schema):
  ```
  tags: d, t:spatial/mining, t:work/receipt, t:oso/vm,
        ip-root, device, location, base-map, delta,
        f1, coverage, novelty, modality, privacy, reward
  ```
- [ ] Store: `mem/spatial/{receipt_id}` engram, linked to IP Root
- [ ] Publish: kind 31020 → relay (or outbox)

**Effort:** 1-2 days (F1 math is straightforward; event schema is done).

### 5.2 ActReceipts

ActReceipts are the connective tissue of the entire economy. Every agent action → receipt.

Tasks:
- [ ] Define ActReceipt schema in `omokoda`:
  ```json
  {
    "agent_npub": "...",
    "task_id": "...",
    "tool_calls": [...],
    "artifact_hash": "...",
    "timestamp": 1756000000,
    "ip_root_id": "...",
    "signature": "..."
  }
  ```
- [ ] Wire: every `act` opcode in OSOVM → generates an ActReceipt
- [ ] Store locally, publish as Nostr event, anchor to Sui
- [ ] Kind 31030 creation receipt: agent-signed, under IP Root, parents chain for artifacts

**Effort:** 2-3 days (touches kernel + VM + Nostr layer).

### 5.3 Sui Settlement (AIO)

Economic settlement for completed tasks.

Tasks:
- [ ] AIO Move contract must accept ActReceipt proof → release Àṣẹ payment
- [ ] Node submits: `ActReceipt + Sui address` → AIO verifies sig → transfers
- [ ] Wire: after kind 31013 embodiment/end + kind 31020 spatial receipts → claim to AIO
- [ ] Twelve Thrones jury: disputed claims go to on-chain jury (separate phase)
- [ ] Test: complete spatial mining session → F1 ≥ 0.777 → receipt → AIO pays

**Effort:** 3-5 days (depends on AIO Move contract completion status).

---

## PHASE 6 — SPATIAL TWIN

### 6.1 Node Capture Hardware

Tasks:
- [ ] Connect AI Camera (Sony IMX500) to Pi 5 CSI port
- [ ] Verify camera pipeline: `libcamera-vid`, `rpicam-apps`
- [ ] Optional: Luxonis OAK-D Lite over USB for depth
- [ ] Wire to `sovereign-spatial.service`:
  - Enable: `systemctl start sovereign-profile@spatial-mining`
  - Record: call body runtime `record` op (or direct camera command if no body)
  - Output: frames + GPS pose → staging directory

**Effort:** Half a day (hardware setup) + 1 day (pipeline wiring).

### 6.2 Splat Pipeline — Phase A (CPU Toy Scenes)

Minimum viable spatial twin.

Tasks:
- [ ] COLMAP: install on VPS (not on the node — too heavy)
- [ ] Node ships: frames → VPS via Reticulum/LXMF or internet
- [ ] VPS runs COLMAP SfM → sparse point cloud + camera poses
- [ ] Julia training core: `gaussian_splatting.jl` → `.ply` splat
- [ ] PLY → SPZ 3D Tiles converter (existing Node.js tool)
- [ ] Host on Blossom (kind:24242) or Contabo static
- [ ] GE-Ver: bump CesiumJS from `^1.124` to `≥1.135` (KHR_gaussian_splatting support)
- [ ] Render: splat georeferenced at capture lat/lon in GE-Ver globe
- [ ] Test: small room or outdoor scene, CPU-only Julia training

**Effort:** 3-5 days (CesiumJS bump is the critical foundation change).

### 6.3 Splat Pipeline — Phase B (Real Scenes, GPU)

Tasks:
- [ ] CUDA.jl / gsplat interop in Julia training core
- [ ] GPU rental: `vast.ai` $0.30-0.60/hr — agent submits job, waits for result
- [ ] Elixir orchestrator: `acquire → sfm → train → tile → publish` as supervised pipeline
- [ ] Move receipt (on Sui): assembled scene → kind 31030 → on-chain anchor
- [ ] Mapillary integration: existing street-level imagery as augmentation source

**Effort:** 1-2 weeks (GPU path + Elixir orchestration).

### 6.4 Splat Fill + GE-Ver Integration

Tasks:
- [ ] MCP tool `splat.fill(lat, lon, item)`: materializes GLTF entities + labels at anchor
- [ ] GE-Ver fill service: watches for fill events → renders in globe
- [ ] ares-splat daemon: `splat.create`, `splat.status`, `splat.fill` MCP endpoints
- [ ] Agent scene annotation: voice whiteboard → labels pinned to 3D coordinates
- [ ] Scene-level kind 31030 receipt: one receipt per assembled scene, not per capture

**Effort:** 3-5 days.

---

## DEPENDENCY TREE

```
PHASE 0 (Image + Birth)
  └── PHASE 1 (Identity — bunker, BIPON39, Sui binding)
        └── PHASE 2 (Protocol — Nostr sync, Reticulum)
              └── PHASE 3 (Power + Thermal)
                    ├── PHASE 5 (Economy — F1, receipts, Sui)
                    │     └── PHASE 6 (Spatial Twin)
                    └── PHASE 4 (Body Runtime — independent of Econ)
                          └── PHASE 5 (receipts use body session data)
```

Phases 0-3 are the critical path. Nothing above them works without them.

---

## IMPLEMENTATION ORDER (Patches P1-P5 mapped to phases)

From spec patches, cheapest → most valuable:

| Priority | Patch | Phase | Effort | Unblocks |
|----------|-------|-------|--------|---------|
| 1 | P1: Key derivation (BIPON39) | Phase 1.2 | Hours | Birth ceremony completeness |
| 2 | P4: Entropy mixing | Phase 0.4 | Minutes | Birth script validation |
| 3 | P5: NIP-46 bunker process | Phase 1.1 | 1 day | Invariant #3 (key safety) |
| 4 | P3: F1 receipt + gate | Phase 5.1 | 1 day | Spatial economy |
| 5 | P2: Noise KK | Phase 4.3 | 2 days | Real embodiment (not needed for Phase 0-3) |

---

## WHAT A "MINIMUM VIABLE NODE" LOOKS LIKE

A node that can:
1. **Born**: derive identity, publish 31000/31001, store engrams
2. **Idle**: run on listen profile, Reticulum announce, sync outbox
3. **Think**: `omokoda` agent loop running, receiving Nostr tasks
4. **Act**: execute tasks, generate ActReceipts, publish to relay
5. **Sync**: outbox → relay, relay → agent, mesh fallback

**Phases required:** 0 + 1 + 2 (partial) + 3

**Does NOT yet need:** body runtime, spatial mining, Sui settlement, splat pipeline.

**Estimated time to MVN:** 2-3 weeks of focused build time with the hardware in hand.

---

## OPEN QUESTIONS / BLOCKERS

| Question | Impact | Notes |
|----------|--------|-------|
| Pi 5 + AI Camera in hand? | Blocks Phase 0 hardware | Dev can use QEMU or existing ARM box for 0-3 |
| `omokoda` ARM build status? | Blocks Phase 0 image | Need cross-compile test |
| AIO Move contract complete? | Blocks Phase 5.3 | Can stub with local escrow for Phase 5 dev |
| Freenet ARM release? | Blocks Phase 2.3 | May need to build from source |
| CesiumJS 1.135 Cesium bug (1.141 orientation)? | Phase 6.2 | Documented workarounds in polyglot-gaussian-splatting skill |
| `vast.ai` GPU rental for Phase B splats? | Phase 6.3 | BTC/ETH/XMR payment, embargo-safe |
| Elixir orchestration repo? | Phase 6.3 | Is this in Ares or a separate process? |

---

## THE GOLDEN TEST (Proof-of-Concept Loop)

Once Phase 0-5 are complete, run this:

```
1. Flash fresh Pi 5 image
2. Power on → first-boot-birth.service fires automatically
3. Check: kind 31000 on relay, kind 31001 device binding
4. Check: /var/lib/sovereign/birthed marker exists
5. sovereign-agent.service starts → omokoda running
6. python3 scripts/body_sim.py (on localhost)
7. Agent discovers sim → sends kind 31010 offer
8. Sim accepts → Noise KK (or sim placeholder)
9. Agent sends: command/record (camera, 30s)
10. F1 scorer: score the "capture" (sim returns dummy data)
11. If F1 ≥ 0.777: kind 31020 spatial receipt published to relay
12. Agent ends session: kind 31013 embodiment/end co-signed
13. AIO (stub): ActReceipt → Àṣẹ units credited
```

**That's the proof-of-life.** Not speculative — a single Pi 5 running a simulated body, generating real Nostr events, anchored to a receipt, paid by the economy. Everything else (real drones, real splats, real Sui) is the same loop at larger scale.

---

## FILE OWNERSHIP MAP (which repo builds each piece)

| Component | Repo | Phase |
|-----------|------|-------|
| `first_boot_birth.py` | sovereign-eco-blueprint (spec) → `Omo-Koda2` (deploy) | 0 |
| `omokoda` binary (ARM) | `Omo-Koda2` (Pillar 1, Rust) | 0 |
| `bipon39` (ARM) | `Omo-Koda2` (identity/bipon39.rs) | 1 |
| NIP-46 bunker service | `Omo-Koda2` | 1 |
| sovereign-sync daemon | `Omo-Koda2` or `ip-layer` | 2 |
| Reticulum/LXMF config | `omokoda-mesh` | 2 |
| sovereign-profile script | `Omo-Koda2` | 3 |
| body runtime (`body/`) | `Omo-Koda2` | 4 |
| body_sim.py | sovereign-eco-blueprint/scripts/ | 4 |
| F1 scorer | `OSOVM` (Pillar 2, Julia) | 5 |
| ActReceipts | `Omo-Koda2` + `OSOVM` | 5 |
| AIO settlement | `AIO` (Move on Sui) | 5 |
| Splat capture service | `Omo-Koda2` / spatial service | 6 |
| COLMAP pipeline | VPS-side script (no dedicated repo yet) | 6 |
| Julia training core | `OSOVM` or standalone Julia pkg | 6 |
| Elixir orchestrator | `ares-control` or new splat-pipeline repo | 6 |
| GE-Ver / splat layer | GE-Ver repo | 6 |
| ares-splat daemon | `ares-control` | 6 |
