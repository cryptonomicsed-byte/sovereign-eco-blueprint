# Sovereign Device Spec Patches — closing the 5 gaps from Part 3

Date: 2026-08-24
Scope: the 5 gaps flagged in the peaq comparison (Part 3) against the
Portable Sovereign Agent Device blueprint. Each patch is concrete enough
to implement directly.

## Patch 1 — Key derivation: one root, wordlist as a choice

Problem: spec names "Nostr keypair via NIP-06 path" AND "optional BIPON39-
style mnemonic soul" as if two systems. They are one system with two
wordlists.

Resolution:
- Root = mnemonic. Wordlist = CHOICE: standard BIP39 (2048 words, the
  Nostr default) or BIPỌ̀N39 (256 Yoruba-rooted tokens, ecosystem-native).
  Same derivation pipeline either way.
- Derivation: mnemonic -> PBKDF2-HMAC-SHA512 (2048 iters, salt "mnemonic")
  -> 64-byte seed -> BIP-32 path m/44'/1237'/0'/0/0 (NIP-06) -> secp256k1
  keypair -> x-only pubkey = npub. This is the canonical Nostr derivation;
  the 256-token wordlist is a drop-in entropy encoding, nothing else.
- The "soul" (IfáScript cast) does NOT create the keypair. It creates
  METADATA (primary_odu, orisha_alignment, temperament) stored in the
  birth enggram. Keys come only from entropy + mnemonic.
- BIPỌ̀N39 fingerprints (never the words) go in the birth event tags.

Implementation note: omokoda-core identity/bipon39.rs already implements
the 256-token wordlist + entropy_to_mnemonic. Wire it as a wordlist
provider behind the same NIP-06 derivation used for the standard path.
VPS has `bipon39` CLI (generate/derive/info) — reuse it on the image.

## Patch 2 — Embodiment session: Noise KK, exact state machine

Problem: spec says "Noise or simple X25519 + signatures" — underspecified.

Resolution: Noise KK (static-static, one round trip, mutual auth).
- Agent static key = its npub-derived signing key; body static key = its
  long-lived device key (never the agent's nsec).
- Handshake: KK(agent_static, body_static) -> one round trip, both sides
  authenticated, transcript bound to both identities. No extra signature
  round needed — Noise KK provides mutual auth natively.
- Prologue = session offer/accept event IDs (binds the handshake to the
  published Nostr contract; replay of an old handshake fails because the
  prologue hash differs).

Session state machine (body-side runtime):
  DISCOVERY  -> (presence event / Reticulum announce)
  OFFERED    -> (received signed session-offer; validate signature +
                 policy: geofence, speed, time limit, data policy)
  ACCEPTED   -> (sent session-accept + own ephemeral; store endpoints)
  KEYED      -> (Noise KK complete; shared secrets for cmd + telemetry)
  ACTIVE     -> (high-level goals down, telemetry up, heartbeat)
  TERMINATED -> (either side; final receipt co-signed; keys zeroized)

Events (all Nostr, signed by agent npub or body key as noted):
- 31010 embodiment/offer (agent -> body, gift-wrapped when private)
- 31011 embodiment/accept (body -> agent)
- 31012 embodiment/heartbeat (either; contains session_id + seq)
- 31013 embodiment/end + final receipt (agent co-signs)
Fields: session_id, agent_npub, body_pubkey, capabilities_req/accepted,
constraints, session_pubkeys, start/end ts, work_summary_hash.
Engram: mem/embodiment/{session_id} — contract, key-material references
(NEVER raw secrets), links to spatial/work receipts.

Body-side runtime: single Rust or Go binary. Identity (device keypair +
owner pubkey allowlist), transport (Reticulum + TCP/WS fallback), session
manager (accept/reject/expire), capability advertisement, command
translator to PX4/ArduPilot/ROS2/MQTT/vendor SDK, telemetry publisher.
No agent memory, no IP Root logic, no LLM.

## Patch 3 — F1-gated spatial mining receipt (exact schema)

Problem: receipt scoring unanchored. Resolution: OSOVM F1 threshold is
the quality gate. F1 >= 0.777 -> reward-eligible; below -> stored,
not paid.

Event kind 31020, spatial/mining receipt, d = receipt_id (NIP-33
parameterized-replaceable, consistent with ecosystem's 30620 workflows):
  tags:
    ["d", "<receipt_id>"]
    ["t", "spatial/mining"]
    ["t", "work/receipt"]
    ["t", "oso/vm"]
    ["ip-root", "<ip_root_id>"]
    ["device", "<device_id>"]           # hardware binding hash
    ["location", "<tile/area id>"]
    ["base-map", "<map ref>"]
    ["delta", "<content hash>"]
    ["f1", "<score 0..1>"]              # OSOVM quality gate
    ["coverage", "<pct>"]
    ["novelty", "<0..1>"]
    ["modality", "camera", "depth", ...]
    ["privacy", "local"|"selective"|"public"]
    ["attest", "<nautilus ref>"]        # optional TEE attestation
    ["reward", "<claim pointer>"]       # only when f1 >= 0.777
  content: JSON {location, delta_desc, scores, sensor_meta, session_id}
Engram: mem/spatial/{receipt_id}, linked to IP Root.

Reward gate logic (device-side, deterministic — no LLM):
  if f1 >= 0.777 and privacy != local: emit reward claim pointer
  if f1 <  0.777: store, mark "pending-quality", no claim
  local-only mode: store + IP Root, never emit claim
Same three paths as blueprint: mine (delta + quality), simulate (verified
sim run -> proof), rent (other agent pays to use environment -> yield).

## Patch 4 — First-boot entropy: explicit mixing + trust assumption

Problem: Pi 5 + AI HAT has no guaranteed hardware RNG. Resolution:
- Collect: /dev/urandom (kernel CSPRNG) as base.
- If present: HAT/hardware RNG or TPM/secure element output.
- Optional: IfáScript / cowrie-style structured cast (adds ceremonial
  entropy, NOT security-critical).
- Mix: SHA-512 over (urandom || hw_rng || cast) -> 256-bit seed -> NIP-06
  derivation. One hash, no entropy pool management needed on first boot.
- Trust assumption, stated in image docs: on boards without a hardware
  RNG, key strength = kernel CSPRNG quality (same as every Linux box
  without hw-rng; acceptable for v1, note for form-factor v2 which
  should include a secure element).

## Patch 5 — NIP-46 on-device: honest scoping

Problem: "remote signing so the phone process never holds the long-term
key" — on a single device, that's process isolation, not hardware
security. Resolution:
- Frame it correctly: the bunker (NIP-46 signer) runs as a SEPARATE
  process with its own user account + seccomp; the exposed agent/phone
  process holds only session keys. Win: compromise of the agent process
  does NOT leak the nsec. This is a real isolation win — just not a
  hardware win.
- Hardware upgrade path (form-factor v2): secure element (NXP SE050 /
  ATECC608) or TPM 2.0 (present on N100/N150 mini-PCs) holds the seed;
  NIP-46 signer becomes a thin wrapper over the SE. On RK3588/Pi, an
  SE050 over I2C is the realistic option.
- Image requirement: the nsec NEVER touches the main agent process's
  memory. Bunker communicates over a local unix socket or NIP-46
  nostr+local scheme. If the board has no SE, state that seed-at-rest
  protection = encrypted keystore (LUKS/dm-crypt or PocketBase-adjacent
  encrypted file), key in kernel keyring.

## Implementation order (cheapest -> most valuable)

1. Patch 1 (key derivation) — unblocks the whole birth sequence. Reuses
   existing bipon39.rs + VPS bipon39 CLI. Hours.
2. Patch 4 (entropy) — one function in the birth script. Minutes on top.
3. Patch 5 (bunker process) — systemd unit split + unix socket. A day.
4. Patch 3 (F1 receipt) — event kind + gate logic, deterministic, no LLM.
   A day.
5. Patch 2 (Noise KK) — the only one with real crypto work; needed only
   when the first body (simulated drone) appears. Later.
