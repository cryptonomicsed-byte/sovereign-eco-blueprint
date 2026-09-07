# Sovereign Device — Power Profiles & Thermal Policy (artifact 4)

Target: pocketable daily-driver, agent mostly idle, high-draw modes are
explicit toggles. Philosophy: aggressive sleep + honest budgets.

## Power profiles (systemd units, one per profile)

  Profile            Main SoC              Radios        Sensors        Draw       Notes
  ─────────────────────────────────────────────────────────────────────────────────────
  deep-sleep         Off / deepest         Off           Off            <50 mW     pocket/overnight
  listen             low island + wake-    duty-cycled   mic only       0.3-1 W    wake-word + presence
                     word MCU
  active             medium                wifi/cell     mic+spk+light  2-4 W      conversation
  light-work         medium                wifi/ret      minimal        2.5-5 W    nostr/receipts/light tasks
  spatial-mining     high                  as needed     cameras+depth  6-12 W     explicit toggle only
  high-performance   max                   all           full           10-18 W    local heavy model/sim

Implementation (Arch):
  /etc/systemd/system/sovereign-profile@.service
    [Service] Type=oneshot RemainAfterExit=yes
    ExecStart=/usr/local/bin/sovereign-profile %i
  /usr/local/bin/sovereign-profile — switches cpufreq governor
  (powersave|schedutil|performance), display state, radio power (rfkill),
  and enables/disables the spatial + heavy services. Profiles are
  requested via `systemctl start sovereign-profile@spatial-mining`.

  sleep:     systemctl suspend (or freeze); wake on MCU wake-word GPIO
  listen:    main SoC in cpuidle deep; wake-word MCU (or sherpa-onnx
             streaming on a single core) does detection; SoC wakes on
             interrupt
  active:    schedutil governor, display on, wifi on
  light-work: schedutil, display off, radios on, camera off
  spatial:   performance governor, camera/depth on, GPS on, thermal
             policy switches to active-cooling
  high-perf: performance governor, fan profile max, thermal trip raised
             to spec max

## Wake-word / always-on island

- Prefer a dedicated MCU (ESP32/RP2040 over UART or I2C) doing wake-word
  detection, GPIO wake to the SoC. Cost: ~$3, adds <10 mW.
- No MCU in v1? sherpa-onnx streaming wake-word on one core with the
  rest of the SoC in deep idle (cpuidle + devfreq floor). Accepts ~0.5 W
  listen cost vs ~0.05 W with MCU.

## Thermal policy

  Sensors: /sys/class/thermal/thermal_zone*/temp (SoC), optional HAT temp.
  Thresholds (SoC):
    < 60 C        normal — all profiles allowed
    60-70 C       throttled — spatial-mining and high-perf refuse to
                  START (return "thermal: too hot"); running ones step
                  down (spatial -> light-work governor + half FPS)
    70-80 C       hard throttle — governor forced to powersave, camera
                  pipeline halved, display dimmed; agent notified
    > 80 C        safety — spatial service stopped, heavy models unloaded,
                  fan max; if still rising, suspend to RAM
  Battery gate: spatial-mining and high-perf refuse to start below 25%
  battery; below 15% the device forces light-work and warns the agent.
  Active cooling: fan (or vapor chamber) enabled ONLY in spatial-mining
  and high-perf; in other profiles fan off (passive spreader enough).

## Duty cycling for radios

  - Wi-Fi: off in listen (except every 30s beacon if presence expected).
  - Reticulum: LoRa duty cycle 1% (legal default); announce every 60s in
    listen, 15s in active. LXMF store-and-forward handles the gaps.
  - Cellular (optional): airplane-mode default; enabled on demand or on
    schedule (e.g., 2 min every hour) for relay sync.
  - Satellite window mode (later): compute next pass, wake radios 2 min
    before, burst-sync outbox, sleep again.

## Power accounting

  Keep a rolling energy ledger (battery % + W estimate per profile,
  updated from /sys/class/power_supply). Agent can query it:
    GET /v1/power -> {profile, watts, battery, since_profile_start}
  The agent's spatial-mining toggle should show the cost before enabling
  ("this will drain ~15%/hr at current battery") — honest UX, matches
  the blueprint's "explicit toggle" principle.

## First-image defaults

  Default profile at boot: listen. Spatial + high-perf services exist but
  are disabled (systemctl disable sovereign-profile@spatial-mining.target
  equivalents). The birth sequence runs in light-work (needs wifi for
  relay publish), then drops to listen.

## Build order

  1. sovereign-profile script + 6 units (a day, no hardware needed —
     works on the dev box too).
  2. Battery gate + thermal thresholds in the profile script.
  3. MCU wake-word island (v2 board; not required for Pi 5 prototype).
  4. Satellite-window sync (later, only if Reticulum satellite path used).
