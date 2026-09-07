# Sovereign Device — Event & Engram Schemas (artifact 1)

All events are ordinary NIP-01 Nostr events signed by the agent npub (or
the body key where noted). Kinds are NIP-33 parameterized-replaceable
(30000-39999) so each has a `d` tag and only the latest version is kept —
consistent with the ecosystem's existing 30620 (workflow) and 30174
(NIP-AE engram) usage. Ranges chosen to avoid collisions:

  used:  9 (channel), 9021 (join), 22242 (auth), 24134 (pairing),
         30620 (workflow), 46020 (workflow trigger), 5 (delete),
         9901-9912 (SEER), 30174 (NIP-AE engrams)
  new:   31000-31001 (birth/binding), 31010-31013 (embodiment),
         31020 (spatial), 31030 (creation receipt)

## 31000 — Agent birth (d = ip_root_id)

The genesis event. Published once at first boot; NIP-33 replaceable so a
re-birth on new hardware supersedes (but the original id stays on relays).

tags:
  ["d", "<ip_root_id>"]
  ["t", "agent/birth"]
  ["t", "ip/root"]
  ["device", "<device_id>"]                # sha256 of hardware fingerprint
  ["image", "<image build hash>"]          # Arch image version that birthed it
  ["bipon39-fp", "<mnemonic fingerprint>"] # NEVER the words — hash only
  ["odu", "<primary_odu>"]                 # IfáScript cast result (if cast)
  ["orisha", "<orisha_alignment>"]         # optional
  ["entropy", "urandom", "hw-rng?", "cast?"]  # sources actually mixed
  ["owner", "<owner npub>"]                # optional owner binding
  ["created", "<unix ts>"]

content (JSON):
  {
    "npub": "<agent npub>",
    "ip_root_id": "<ip_root_id>",
    "device_id": "<device_id>",
    "birth_receipt_id": "<event id of THIS event>",
    "created_at": 1756000000,
    "owner_binding": null,
    "soul": {"primary_odu": "...", "temperament": "...", "destiny_threads": [...]},
    "image": {"distro": "arch", "version": "2026.08", "hash": "..."}
  }

## 31001 — Device binding (d = device_id)

Binds the agent to this specific hardware. Re-published on migration to
new hardware (new device_id, same npub).

tags:
  ["d", "<device_id>"]
  ["t", "device/binding"]
  ["agent", "<npub>"]
  ["hw", "<board class: pi5|rk3588|n100>"]
  ["fp", "<hardware fingerprint hash>"]    # cpu serial / dtb / mac mix
  ["created", "<unix ts>"]

content: {device_id, board, fingerprint, binding_type: "primary"|"borrowed"}

## 31010 — Embodiment offer (agent -> body)

Signed by agent npub. Gift-wrapped (NIP-17/44) when privacy matters.

tags:
  ["d", "<session_id>"]
  ["t", "embodiment/offer"]
  ["agent", "<agent npub>"]
  ["body", "<body pubkey>"]
  ["expiry", "<unix ts>"]                  # session offer expiry
  ["caps", "camera", "gps", "motors"]      # requested capabilities
  ["constraint", "geofence:<lat,lon,r>"]
  ["constraint", "max-speed:5"]
  ["constraint", "ttl:3600"]
  ["data-policy", "local"|"selective"|"public"]

content: {
  session_id, agent_npub, body_pubkey,
  session_pubkey (agent ephemeral for Noise KK),
  capabilities_requested: [...], constraints: {...},
  prologue: "<offer event id>",            # bound into Noise handshake
  payment_pointer: null                    # optional deposit
}

## 31011 — Embodiment accept (body -> agent)

Signed by the BODY's key (not the agent). Contains body's Noise ephemeral.

tags:
  ["d", "<session_id>"]
  ["t", "embodiment/accept"]
  ["agent", "<agent npub>"]
  ["body", "<body pubkey>"]

content: {
  session_id, body_pubkey, body_session_pubkey,
  capabilities_accepted: [...], endpoints: {cmd: "...", telemetry: "..."},
  prologue: "<accept event id>"
}

## 31012 — Embodiment heartbeat (either side)

tags: ["d", "<session_id>"], ["t", "embodiment/heartbeat"], ["seq", "<n>"]
content: {session_id, seq, battery, link: "nostr"|"reticulum"|"local"}

## 31013 — Embodiment end + final receipt (agent co-signs)

tags: ["d", "<session_id>"], ["t", "embodiment/end"], ["work", "<summary hash>"]
content: {
  session_id, start_ts, end_ts,
  work_summary_hash,                   # of full telemetry/outcome bundle
  receipts: ["<31020 ids produced>"],  # spatial/work receipts from session
  co_signers: ["<body pubkey>"]        # body co-signed if it participated
}

## 31020 — Spatial mining receipt (d = receipt_id)

Full schema in sovereign-device-spec-patches.md Patch 3. Summary:
  ["d", "<receipt_id>"], ["t", "spatial/mining"], ["t", "work/receipt"],
  ["ip-root", "<ip_root_id>"], ["device", "<device_id>"],
  ["location", "<tile>"], ["base-map", "<ref>"], ["delta", "<hash>"],
  ["f1", "<0..1>"], ["coverage", "<pct>"], ["novelty", "<0..1>"],
  ["modality", ...], ["privacy", ...], ["attest", ...], ["reward", ...]
Reward gate: f1 >= 0.777 AND privacy != local -> claim pointer emitted.

## 31030 — Creation receipt (d = ip_root_id + ":" + creation_hash)

Automatic IP provenance for ANY significant creation (music, video, code,
spatial asset, simulation result).

tags:
  ["d", "<ip_root_id>:<creation_hash>"]
  ["t", "creation/receipt"]
  ["t", "ip/root"]
  ["ip-root", "<ip_root_id>"]
  ["c-type", "music"|"video"|"code"|"spatial"|"sim"|"text"]
  ["c-hash", "<sha256 of artifact>"]
  ["license", "<SPDX or custom>"]        # default: "all-rights-reserved-sovereign"
  ["parents", "<creation hashes derived from>"]   # provenance chain
  ["attest", "<nautilus ref>"]           # optional

content: {ip_root_id, artifact_hash, artifact_type, license,
          derived_from: [...], created_at, session_id?}

## Engram schemas (minipae / NIP-AE, kind 30174 style)

mem/agent/birth        {npub, device_id, ip_root_id, birth_receipt_id,
                        created_at, owner_binding, soul_meta}
mem/agent/identity     {npub, mnemonic_fingerprint, key_derivation:
                        "nip06", wordlist: "bip39"|"bipon39", bunker: "unix-socket"}
mem/embodiment/{sid}   {contract (offer+accept ids), session_pubkeys refs,
                        start/end, work_summary_hash, receipt_ids: []}
mem/spatial/{rid}      {receipt_id, ip_root_id, location, delta_hash,
                        f1, coverage, novelty, privacy, reward_state}
mem/ip/{ip_root_id}    {root, creation_count, latest_creation_hash,
                        anchors: [{chain: "sui"|"peaq", tx: "..."}]}

## Relay/binding notes

- Birth + binding publish to configured relays (wss://omokoda.duckdns.org:3443
  first; public relays when online).
- Offline first boot: events + engrams go to local outbox
  (~/.sovereign/outbox/), a sync daemon publishes when a link appears
  (Nostr over Reticulum/LXMF when no internet).
- Gift-wrapping: embodiment offer/accept use NIP-44 v2 (pure-python impl
  in ~/genteam/minipae.py, verified against official vectors).
