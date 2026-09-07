# Sovereign Device — Pi 5 / RK3588 Image: Packages + First-Boot Birth (artifact 3)

Target: Arch Linux ARM (aarch64) on Raspberry Pi 5 (or RK3588 board).
Image ships WITHOUT a large LLM. Everything critical is deterministic
code + small binaries.

## Base packages (pacman)

  base base-devel linux-raspberrypi (or linux-rk3588) linux-firmware
  systemd openssh sudo git curl jq python python-pip uv
  networkmanager iwd bluez
  lm_sensors (thermal) rfkill cpupower
  pocketbase (AUR or single binary download to /usr/local/bin)
  age (keystore encryption) cage (kiosk compositor, later)

## Sovereign layer (installed into the image, not pacman)

  omokoda        — agent runtime binary (build on VPS, scp in)
  bipon39        — identity CLI (from VPS /usr/local/bin)
  ifa            — IfáScript CLI (from VPS, optional; skip if absent)
  nak            — Nostr CLI (single static binary; key gen + publish)
  rns + lxmf     — pip install rns lxmf (Reticulum + LXMF)
  minipae        — ~/genteam/minipae.py (NIP-44 v2 + NIP-AE engrams)
  sherpa-onnx    — streaming wake-word + STT (AUR; v2, not in first image)
  sovereign-profile — power profile switcher (artifact 4)
  first-boot-birth — the birth script below (systemd oneshot)

## systemd units in the image

  first-boot.service     — oneshot, runs birth script, only if
                           /var/lib/sovereign/birthed does not exist;
                           on success touches it and disables itself
  sovereign-agent.service — the agent loop (omokoda or single binary)
  sovereign-sync.service  — outbox -> relay sync daemon (Nostr, then
                            Reticulum/LXMF when no internet)
  sovereign-spatial.service — spatial mining, DISABLED by default
  sovereign-profile@.service — power profiles (artifact 4)

## First-boot birth script

Path: /usr/local/bin/first-boot-birth (installed into image).
systemd: [Unit] ConditionPathExists=!/var/lib/sovereign/birthed
         [Service] Type=oneshot ExecStart=/usr/local/bin/first-boot-birth
See the script file in this directory: first_boot_birth.py

What it does, in order:
  1. Collect entropy: /dev/urandom + /dev/hwrng (if present) + optional
     IfáScript cast -> SHA-512 mix -> 32-byte seed.
  2. Derive keypair: secp256k1 (pure python, inline) -> x-only pubkey
     (npub hex). Seed hex printed ONCE (owner records it); stored
     encrypted (age) at /var/lib/sovereign/identity.age.
  3. Mnemonic: if `bipon39` binary present, generate 256-token mnemonic
     and store fingerprint only (never words on disk).
  4. IfáScript: if `ifa` present, cast -> odu metadata (non-fatal).
  5. IP Root genesis: ip_root_id = sha256(npub || device_id || birth_ts).
  6. Engrams: write mem/agent/birth.json + mem/agent/identity.json +
     mem/ip/{ip_root_id}.json into ~/.sovereign/state/ (PocketBase sync
     later).
  7. Publish: build kind 31000 birth + kind 31001 binding events; if
     `websockets` python lib present -> publish to configured relays;
     else write to ~/.sovereign/outbox/ for sovereign-sync to deliver.
  8. Touch /var/lib/sovereign/birthed; disable first-boot.service.
  9. Drop to `listen` power profile; start sovereign-agent.service.

Output: /var/lib/sovereign/birth.log — npub, ip_root_id, device_id,
relay status. The status TUI/web page reads this + /v1/status.

## Why pure-python crypto in the script

The image is Arch (glibc), so `pip install coincurve` WOULD work — but
the birth script must run with zero network and zero build step. The
inline secp256k1 + schnorr implementation is the same one verified
against the official BIP-340 test vector in the SEER stack
(~150 lines, zero deps). `nak` can be used instead if present — the
script prefers nak, falls back to inline. Deterministic either way.
