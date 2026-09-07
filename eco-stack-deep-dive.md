# ECO DEEP DIVE — Freenet · Nostr · Reticulum/Meshtastic · Sui · Omarchy
# How the five rails build one self-owned ecosystem on top of what already exists
# Verified against local state: 2026-09-06. Everything marked [ASSET] was found on disk.

════════════════════════════════════════════════════════════════════════
0. THESIS (one paragraph)
════════════════════════════════════════════════════════════════════════
You don't need to build a new ecosystem — you need to finish wiring the one
you already have. Every layer of the sovereign stack already has a working
asset: Nostr identity + custom kinds (31000-31013), a Rust freenet-core
checkout + a Vantage backend integration that never got past its F1 stub,
Sui Move contracts (AIO, Twelve Thrones, Techgnosis/ASHE genesis), a full
device-image spec (Arch/Omarchy + birth sequence + power profiles), and a
mesh transport already specced into that image (Reticulum/LXMF). The five
technologies are not five competing platforms — each has exactly one job in
a layered architecture:

    Omarchy (devices)      → the physical nodes of the eco
    Nostr (identity)       → who everyone is, and the online event spine
    Freenet (shared state) → serverless replicated apps: rooms, artifact
                             registry, reputation, knowledge mirror
    Reticulum/Meshtastic   → the offline transport: mesh when relays die
    Sui (settlement)       → the only place tokens/escrow/ownership live

The division of labor rule that makes this coherent:
  - Nostr = events + identity (cheap, ephemeral, relayed)
  - Freenet = replicated state with NO global consensus (CRDT/merge apps)
  - Sui = global consensus (settlement, token, escrow, provenance anchor)
  - Walrus/Arweave = durable blob storage; Seal = secrets
  - Reticulum/LXMF + Meshtastic = transport when the internet is absent
    or hostile (the embargo case this whole stack exists for)
Never the twain shall overlap: no tokens on Freenet (no consensus ⇒
double-spend-unsafe), no secrets in contracts (public state), no CRDT chat
state on Sui (gas suicide), no relay dependence for identity (npub is
derived from keys, not from a relay).

════════════════════════════════════════════════════════════════════════
1. WHAT "MY OWN ECO" MEANS HERE
════════════════════════════════════════════════════════════════════════
The eco = the sovereign stack products, unified under one identity/IP-root
model and one settlement layer:

  Pillars        Omo-Koda2 (knowledge) · OSOVM (spatial) · Vantage (trading)
  Learning core  Mycelium (trace substrate, gateway, provenance)
  Epistemology   Twelve Thrones (Sui jury / 12-model disagreement engine)
  Prediction     Portent (accuracy-weighted, burns, portable reputation)
  Compiler       Techgnosis (emits Move/Julia/Rust/Go/Idris; ASHE genesis)
  Agent stack    SEER (nostr_layer + tokenomics + agents)
  Hardware       Fold4 (brain) · A14 (executor) · Pi5/RK3588 (prototype
                 sovereign device) · Contabo VPS 89.117.74.224 (hub)
  Web presence   omokoda.space (Cloudflare) — public window, not a dependency

The eco is "own" when: identity can't be revoked by a third party (npub in
hardware), comms survive internet loss (mesh), shared state survives host
loss (Freenet replication), value settles without a bank (Sui Move), and
every node is reproducible (Omarchy image). The five rails in this doc are
precisely those five properties.

════════════════════════════════════════════════════════════════════════
2. INVENTORY — WHAT ALREADY EXISTS (verified on disk today)
════════════════════════════════════════════════════════════════════════
[ASSET] ~/freenet-core
  Full upstream freenet/freenet-core checkout (Rust), HEAD e6155da
  (feat(otel): export node metrics via OpenTelemetry SDK #5178).
  Contains: crates/core (the node), crates/fdev (dev CLI), apps/,
  docker/freenet-node + docker/freenet-gateway (Dockerfiles +
  docker-compose + healthcheck + startup scripts + release-signing-key),
  scripts/FREENET-GW-SETUP-GUIDE.md, scripts/freenet-gateway.service,
  scripts/init-gateway.sh. NOT built, NOT running anywhere reachable.
  No target/release binaries, no listening ports (50509/7509), VPS probe
  timed out this session. Status: dormant scaffolding.

[ASSET] ~/Vantage/backend/freenet/  (python, committed: 36377f0 + d37fb8c)
  contracts.py   — GuildRoomContract (CRDT merge: append-only msgs
                   deduped by message_id, LWW members, set-union
                   reactions, seq = max+1), WorkspaceContract,
                   planned F5+: ArtifactRegistryContract,
                   ReputationContract. CONTRACT_ID "guild-room-v1".
  service.py     — FreenetService, async WS client, node_url default
                   ws://127.0.0.1:50509, Phase F1 stub (DISCONNECTED,
                   queues events). F2 = real WebSocket. NOTE: current
                   freenet-core local node default WS port is 7509 and
                   the gateway has its own port — 50509 needs rechecking.
  router.py      — FastAPI /api/freenet/status|health|rooms (+POST rooms
                   Phase F3). Status endpoint reports phase F1 with note
                   "local node not yet running".
  git_bridge.py  — Freenet-as-git mirror bridge (ties into the commit
                   "Freenet Git").
  types.py       — GuildRoomState/WorkspaceState/FreenetEvent etc.
  → The entire Freenet plan for the eco is already written as Python
    state mirrors + merge logic + REST surface. What's missing: a live
    node and compiled WASM contracts. This is the single biggest unlock.

[ASSET] ~/docs/sovereign-device/ (01-event-schemas, 02-body-runtime,
  03-image-and-birth, 04-power-thermal, 05-pairing-flow, first_boot_birth.py)
  Arch Linux ARM image spec: base pkgs + sovereign layer (omokoda, bipon39,
  ifa, nak, rns+lxmf, minipae, sherpa-onnx, sovereign-profile,
  first-boot-birth), systemd units (first-boot, sovereign-agent,
  sovereign-sync, sovereign-spatial disabled, sovereign-profile@),
  power profiles (deep-sleep→high-performance), birth sequence
  (entropy→seed→npub→IP root→engrams→kind 31000/31001→outbox/relay).
  first_boot_birth.py verified against BIP-340 test vector 0.
  Image stamps distro:"arch", version:"2026.08" in the birth event.

[ASSET] ~/docs/sovereign-device-spec-patches.md (P1-P5 event kinds,
  Noise KK, etc.) + ~/docs/peaq-vs-omokoda-comparison.md (Part 6 verdict:
  Sui = settlement · krest = laboratory · peaq = pattern library)
  → The chain decision is MADE and written down: Sui primary, with
    Walrus + Seal as the heavy layer.

[ASSET] Sui Move assets
  twelve-thrones/  — "first on-chain AI epistemology engine": 12 frontier
                     models queried in parallel, weighted consensus,
                     disagreement severity, Arweave archival, disagreement
                     minted as Sui NFTs. Plus ritual-router v8, server.ts,
                     contracts/, deployment/, integration-example.ts.
  Techgnosis/      — sacred compiler → multi-language IR (Julia/Rust/Go/
                     Move/Idris). ASHE (Àṣẹ) genesis: block 0 mints ASHE,
                     post-genesis denied. Phases 1-3 complete (Sabbath,
                     Genesis Flaw, First Public Breath demo).
  ~/ares_sui_trader.py, ~/import_sui.py, ~/move_to_trading.py — Sui
  trading tooling at home root.
  ~/seer/backend/tokenomics.py + nostr_layer.py + agents.py; ~/seer/solana
  program_interface.rs (Solana leg exists too — ClawPump/Clawrena).

[ASSET] Nostr
  ~/docs/sovereign-device/01-event-schemas.md — kinds 31000 birth,
  31001 binding, 31002+ (patches P1-P5), receipts, NIP-44 v2 + NIP-AE
  engrams via ~/genteam/minipae.py (.minipae-* key files present).
  Relays: wss://omokoda.duckdns.org:3443 (own), relay.damus.io.
  Vantage commit d37fb8c already includes: NIP-29 bridge, A2A delegation,
  reputation, Sui settlement, Freenet Git — i.e., the P2/P3/P4 wiring was
  committed at the API level.

[ASSET] Mycelium (~/mycelium — gateway/, provenance/, mycelium.db, miners)
  Cross-agent trace substrate; Vantage → /api/trace bridge built; users
  anonymous+private by design (docs/privacy-layer.md).

[ASSET] Mesh
  NOTHING installed yet (no rns/lxmf/meshtastic in site-packages, no
  binaries). The entire mesh plan exists only in the sovereign-device
  spec (rns + lxmf in the image, LXMF store-and-forward, LoRa duty-cycle
  1%, body-runtime JSON-RPC over LXMF, sovereign-sync outbox daemon).

[GAP] VPS 89.117.74.224 unreachable from this session (SSH denied,
  :7777 timeout) — hub state unverifiable right now. Last known:
  Omo-Koda2 :7777 + AgentSlack :3200 there.

════════════════════════════════════════════════════════════════════════
3. THE FIVE RAILS — WHAT EACH IS TODAY (accurate, current)
════════════════════════════════════════════════════════════════════════

3.1 Freenet (freenet-core, the 2023+ Rust rewrite — alpha, live net)
  A peer-to-peer platform for real-time decentralized apps WITHOUT global
  consensus. Core abstraction = contract: a WebAssembly module defining
  (a) valid state, (b) merge semantics — an idempotent commutative merge
  (join-semilattice) so updates in any order converge, (c) summary/delta
  sync for efficiency.
  - Contract key k(C) = H(H(code) || params) — two-stage hash; location on
    a 1-D ring; state replicated on peers near that location.
  - Delegates: local WASM agents that hold secrets on YOUR device and talk
    to contracts via attributed messages. Private state never leaves the
    device (this is where a device-local agent key could live — but see
    the gap: delegate cross-device sync is only partial in upstream).
  - Core: Rust/tokio, Wasmtime execution with fuel+memory limits, redb or
    SQLite persistence, single event loop. Transport: UDP, NAT hole-punch,
    X25519+AEAD. Client API over WebSocket to the local node (default
    local node port 7509 per current docs; gateway has its own).
  - Deployed reality (May 2026 whitepaper): ~440 active peers; River chat
    and an anonymous identity scheme run on the live net; subscriptions/
    leases/summary-delta/small-world routing deployed. Honest gaps:
    congestion control = fixed-rate token bucket (LEDBAT++/BBR still
    experimental); NETWORK-LEVEL INCENTIVE = OPEN — the intended mechanism
    is application-layer reputation contracts (exactly your ReputationContract
    plan); delegate end-to-end cross-device flow not wired; alpha bugs.
  - Tooling: freenet-stdlib 0.8 + freenet-scaffold 0.2 (Rust, wasm32),
    fdev CLI: `fdev -p <port> publish --code x.wasm contract --state s.cbor`,
    `fdev website publish` for web containers; UI over WS to local node.
  → Verdict for your eco: alpha is fine for the state you're building
    (rooms, artifact catalog, reputation, knowledge mirror) because it's
    consensus-free CRDT state, not value. Keep it out of the money path
    until incentives harden; anchor anything that must survive forever
    elsewhere (Walrus/Sui/Gitea).

3.2 Nostr — identity + event spine (your existing root of trust)
  npub-in-hardware is already the load-bearing identity principle. Custom
  kinds 31000+ carry birth/binding/receipts; NIP-44 v2 + NIP-AE engrams
  carry memory; NIP-46-style bunker (unix socket in birth identity
  engram) keeps the nsec on-device. Vantage already has a NIP-29 bridge +
  A2A delegation (agent-to-agent events over relays).
  → Verdict: unchanged role, now the SPINE that all other rails talk
    through. Every Freenet contract change, every Sui receipt, every
    LXMF delivery can be mirrored as a signed Nostr event for cheap
    global indexing. Relays are transport, not truth.

3.3 Reticulum (RNS) / LXMF + Meshtastic — offline transport continuum
  Reticulum = self-configuring mesh networking stack (runs over UDP/TCP,
  LoRa via RNode, even packet radio). LXMF = delay-tolerant messaging on
  top of RNS (store-and-forward — built for the embargo case). Already in
  the Omarchy image spec + body-runtime spec (JSON-RPC over LXMF for
  robot bodies).
  Meshtastic = separate LoRa mesh ecosystem (cheap T-Beam/Heltec boards,
  Meshtastic firmware, phone apps over BLE, MQTT gateways to the
  internet). ITS OWN protocol — you cannot run Reticulum and Meshtastic
  firmware on the same radio. Hardware decision required.
  → Verdict: Reticulum/LXMF is the eco-native mesh (clean identity,
  store-and-forward, already specced). Meshtastic is the pragmatic
  off-the-shelf LoRa tail + a huge existing mesh in the wild. The bridge
  pattern: a gateway node (Pi or a rooted phone / VPS-edge) that speaks
  LXMF to your devices AND Meshtastic to the LoRa world, relaying between
  them and to Nostr relays when any link has internet. Bandwidth is tiny
  (hundreds of bytes/packet, 1% LoRa duty cycle) — mesh carries messages,
  receipts, presence, SOS — NOT contracts or blobs.

3.4 Sui — settlement + provenance anchor (decision already made, Part 6)
  Global consensus is expensive and only needed where ownership/value is
  contested: Àṣẹ as native Move coin, AIO (treasury/escrow/staking/
  slashing), Twelve Thrones (jury/epistemology), receipt anchoring
  (every act → Merkle root → Sui tx = blueprint invariant #4). Walrus =
  durable blob store for receipts/content; Seal = programmable secrets.
  Techgnosis emits the Move genesis; the Part-6 doc pins the rule.
  → Verdict: keep as-is. The eco work here is WIRING (see Phase E), not
    new contracts: hook Mycelium trace roots + Vantage settlements +
    Portent burns into the merkle→Sui pipeline.

3.5 Omarchy / Arch — the node substrate
  Per previous analysis: PURE ARCH + provision script now (fast iteration),
  OMARCHY archiso-baked image once the layer stabilizes. The image spec
  (artifact 3) already defines the sovereign layer + units; the birth
  sequence makes each node a self-sovereign eco member on first boot.
  → Verdict: needs two additions after this deep dive — (a) freenet node
    client/gateway subscription unit (the device should subscribe to its
    own IP-root artifacts, rooms, reputation contract), (b) rns/lxmf +
    meshtastic gateway role for devices that act as mesh tails.

════════════════════════════════════════════════════════════════════════
4. THE ARCHITECTURE — LAYER ASSIGNMENT
════════════════════════════════════════════════════════════════════════

                    ┌───────────────────────────────────────────┐
                    │  WEB WINDOW  omokoda.space (Cloudflare)   │  read-only mirror,
                    └───────────────────────────────────────────┘  never a dependency
                    ┌───────────────────────────────────────────┐
    SETTLEMENT     │  SUI  Àṣẹ · AIO escrow/staking/slashing ·  │  global consensus ONLY
    & PROVENANCE   │  Twelve Thrones · receipt anchors ·        │  tokens/ownership/witness
                    │  Walrus blobs · Seal secrets              │
                    └───────────────────────────────────────────┘
                    ┌───────────────────────────────────────────┐
    SHARED STATE   │  FREENET contracts: GuildRoom · Workspace  │  consensus-free CRDT
    (serverless)   │  ArtifactRegistry (skillforge catalog) ·   │  replicated state:
                    │  Reputation · knowledge mirror (website    │  rooms, registry, rep,
                    │  container)                                │  knowledge
                    └───────────────────────────────────────────┘
                    ┌───────────────────────────────────────────┐
    EVENT SPINE    │  NOSTR  npub identity · kinds 31000+ ·     │  who/what/when + cheap
    & IDENTITY     │  NIP-29 A2A · engrams (NIP-44/AE) ·        │  global index; relays =
                    │  relay mirror of every layer's activity    │  transport, not truth
                    └───────────────────────────────────────────┘
                    ┌───────────────────────────────────────────┐
    OFFLINE MESH   │  RETICULUM/LXMF (eco-native) + MESHTASTIC  │  when internet is
    TRANSPORT      │  (LoRa tail) via gateway nodes             │  absent/hostile; msgs,
                    └───────────────────────────────────────────┘  receipts, presence only
                    ┌───────────────────────────────────────────┐
    NODE SUBSTRATE │  OMARCHY/ARCH image: sovereign-agent ·     │  every device is a
    (devices)      │  first-boot birth · power profiles ·       │  reproducible eco node
                    │  freenet client · rns/lxmf · minipae      │
                    └───────────────────────────────────────────┘

What runs where (no overlaps):
  identity root ......... Nostr npub (hardware-derived at birth)
  online messages ....... Nostr events (relays)
  agent-to-agent ........ NIP-29 A2A (already committed in Vantage)
  rooms/chat/collab .... Freenet GuildRoom/Workspace contracts
  artifact catalog ...... Freenet ArtifactRegistry contract + Gitea
                          + Freenet-Git mirror (git_bridge.py)
  reputation ........... Freenet ReputationContract (app-layer, the
                          upstream-intended mechanism) ← Portent burns,
                          Vantage performance, Twelve Thrones weights,
                          Mycelium contribution quality
  knowledge commons .... Freenet website container mirror of Omo-Koda2
                          (fdev website publish) + omokoda.space
  value/token/escrow ... Sui Move ONLY (Àṣẹ, AIO, Twelve Thrones)
  durable blobs ........ Walrus (Sui) / Arweave (already used by
                          Twelve Thrones); secrets → Seal
  receipts ............. engram (Nostr kind) → merkle root → Sui tx
                          (invariant #4) + Walrus blob for payloads
  offline transport .... LXMF (Reticulum) primary; Meshtastic LoRa tail;
                          sovereign-sync delivers outbox when a link appears
  execution substrate .. Omarchy image (systemd units, profiles, birth)

════════════════════════════════════════════════════════════════════════
5. REFERENCE DATA FLOWS (the eco in motion)
════════════════════════════════════════════════════════════════════════

F1. BIRTH → JOIN (online)
    Omarchy first boot → entropy→seed→npub→IP root → engrams →
    kind 31000 birth + 31001 binding → own relay (omokoda.duckdns.org:3443)
    → [NEW] Freenet identity-directory contract records npub+ip_root
    (public index) → device subscribes to its ArtifactRegistry + Reputation
    contracts → eco member. Assets: first_boot_birth.py (done), relay
    (done). New: one directory contract + subscribe wiring in the image.

F2. BIRTH → JOIN (offline — the embargo case)
    Same birth, but no relay: events → ~/.sovereign/outbox/ (already
    implemented in the script) → sovereign-sync daemon carries them over
    LXMF/Reticulum to the nearest gateway → gateway publishes to relay +
    Freenet + (receipt anchor later). Asset: outbox logic exists in
    first_boot_birth.py; needs the LXMF transport + gateway side.

F3. KNOWLEDGE PUBLISH (Omo-Koda2 → commons)
    Article/knowledge unit → engram (NIP-44) → Nostr kind →
    Freenet website container / WorkspaceContract update (CRDT merge) →
    mirror to omokoda.space (Cloudflare) for the web window →
    Walrus blob if the payload must be durable → Sui anchor tx.
    Merge semantics already prototyped in Vantage contracts.py.

F4. TRADING ROOM (Vantage + Mycelium learn)
    Signal rooms as GuildRoom contracts (Vantage Phase F3, already
    designed in contracts.py) → human/agent posts signed Nostr events →
    room state converges via Freenet merge → Mycelium traces activity
    (users anonymous by privacy-layer design) → executions settle on Sui
    → performance accrues to ReputationContract.

F5. SKILLFORGE / FRANKENSTEIN ARTIFACT FLOW
    YouTube link → yt-dlp crawl → repo regex from description →
    classification (frankenstein-compatible?) → ArtifactRegistryContract
    (public catalog, append-only, per-artifact LWW — merge logic is the
    F5 design already noted in contracts.py) → sources mirrored to Gitea
    + Freenet-Git (git_bridge.py exists) → merge candidates feed the
    build pipeline → receipts per merge.

F6. OFFLINE BRIDGE (Fold4/A14 in Cuba, no internet)
    Agent work → LXMF message (signed) → Reticulum mesh (RNode or
    phone-to-phone) → gateway node with a data link → gateway relays to
    Nostr relay + Freenet node + Sui (batch merkle) → sovereign-sync
    confirms delivery back over LXMF. Meshtastic tail: presence/SOS/
    short receipts over LoRa when even Reticulum peers are sparse.

F7. DISPUTE → JURY → SETTLEMENT
    Disagreement (trade dispute, slashing challenge) → Twelve Thrones
    (12 models, weighted, disagreement severity, Arweave record, Sui NFT
    if collectible) → verdict → AIO escrow release/slash on Sui →
    receipt engram → ReputationContract delta (Freenet) → Mycelium trace.

F8. SPATIAL MINING (OSOVM) — offline-tolerant rewards
    Device captures → F1 quality gate (≥0.777 per the peaq-borrowed
    threshold) → work receipt (kind) → merkle batch → Sui Àṣẹ reward
    request when online; offline: receipts accumulate in outbox, batch
    anchored on next link (same shape as F2). Reward events mirrored to
    ReputationContract.

════════════════════════════════════════════════════════════════════════
6. HONEST GAPS (each blocks one flow above)
════════════════════════════════════════════════════════════════════════
G1. No Freenet node running anywhere. Vantage FreenetService sits at
    Phase F1 stub; nothing listens on 50509/7509; no binaries built;
    VPS unreachable this session (SSH denied, :7777 timeout). Blocks
    F1/F3/F4/F5 — everything that touches a contract.
G2. Port drift: Vantage stub targets ws://127.0.0.1:50509; current
    freenet-core local node default is 7509 (gateway differs). Must be
    re-pinned against the actual node before F2 lands.
G3. Zero compiled WASM contracts. contracts.py is a Python mirror of the
    merge logic — the real GuildRoom/ArtifactRegistry/Reputation
    contracts don't exist as Rust/wasm32 yet. The CRDT design carries
    over 1:1 (same merge rules), but it's a port job.
G4. Mesh layer is spec-only: rns/lxmf not installed anywhere; no RNode
    or Meshtastic hardware decision; sovereign-sync has no transport
    backend yet. Blocks F2/F6.
G5. Sui wiring incomplete: "every act → merkle → Sui tx" invariant is
    written (Part 6 doc + blueprint) but the pipeline from Mycelium
    traces / Vantage settlements / Portent burns into a Move anchor
    isn't verified live from this device. seer/tokenomics.py +
    ares_sui_trader.py exist; the anchor contract + batch flow needs
    confirming on the VPS side when reachable.
G6. ReputationContract (the eco glue) is designed, not built — on either
    rail (Freenet app-layer rep AND the Sui-anchored selective snapshot).
G7. Twelve Thrones on Arweave vs eco-standard Walrus — two durable-blob
    rails today. Decide: standardize on Walrus for new work, keep
    Arweave for what's already archived (don't re-platform working code).

════════════════════════════════════════════════════════════════════════
7. BUILD ORDER (each phase reuses verified assets; sizes are honest)
════════════════════════════════════════════════════════════════════════

PHASE A — Wake the node (0.5-1 day, pure wiring, zero new design)
  1. Build freenet-core on the VPS (or any linux box): cargo install
     --path crates/core (node) + crates/fdev. ~/freenet-core is the
     checkout; the docker/ images exist for the container route
     (freenet-node + freenet-gateway + freenet-gateway.service +
     init-gateway.sh from the setup guide).
  2. Run the node + gateway on 89.117.74.224 (or a reachable box),
     open the WS API port, healthcheck (healthcheck.sh exists).
  3. Re-pin Vantage FreenetService node_url to the live port; flip the
     F1 stub to F2 (the real WS path is already sketched in service.py).
  4. Verify: GET /api/freenet/status → connected, peer_count > 0.
  Success signal: one round-trip publish/subscribe against the live net
  using fdev (publish a trivial contract, GET it back from another peer).

PHASE B — First real contracts (1-2 days)
  1. Port GuildRoomContract merge logic (contracts.py, 1:1) to a Rust
     wasm32 contract with freenet-scaffold. Publish via fdev. Wire
     Vantage POST /api/freenet/rooms to actually create rooms.
  2. ArtifactRegistryContract (append-only, per-artifact LWW) — the
     skillforge/frankenstein catalog (see task list: yt_harvest.py +
     skillforge.rs intake) lands here as the first real payload.
  3. Freenet-Git mirror for the repos (git_bridge.py): push mirror of
     Gitea → Freenet-hosted git container. Censorship-resistant source
     hosting for the canonical repos.
  Success signal: room created from Vantage UI lives on the net;
  harvested repos appear in the registry contract from a second peer.

PHASE C — Identity directory + Nostr↔Freenet bridge (2-3 days)
  1. Identity-directory contract: npub + ip_root + device_id + current
     relay list, LWW per npub. Birth flow (F1/F2) writes to it.
  2. Bridge daemon: subscribes to Nostr kinds (birth, receipts, A2A)
     and materializes what needs shared state into contracts; contract
     deltas that need cheap global indexing emit signed Nostr events.
  3. Update sovereign-device artifact 3 image spec: add freenet client
     unit + directory subscribe to the sovereign layer.
  Success signal: a device birth event appears on the relay AND in the
  directory contract; an offline-published event (outbox) appears in
  both once a link exists.

PHASE D — Mesh tail (2-4 days + hardware)
  1. Decision: RNode+reticulum (eco-native, single stack) vs Meshtastic
     boards (cheap, huge installed base, separate protocol → gateway
     bridge needed). Recommendation: start RNode/Reticulum for the
     sovereign devices (clean LXMF, matches spec); add ONE Meshtastic
     gateway later for the LoRa world.
  2. Install rns+lxmf on the gateway (VPS or a Pi); implement the
     sovereign-sync LXMF transport backend (outbox→LXMF→gateway→relay).
  3. Fold4/A14: rns/lxmf in Termux for a field test of F6.
  Success signal: F2 birth over LXMF delivered to the relay from a
  device with no internet.

PHASE E — Sui wiring (1-2 days + audit)
  1. Confirm the merkle→anchor Move contract + batch flow (exists in
     some form per Vantage commit d37fb8c "Sui settlement"; verify
     live on VPS when reachable).
  2. Hook Mycelium trace roots, Vantage settlements, Portent burns into
     the batch anchor pipeline. Receipt kinds already specced in
     01-event-schemas.md.
  3. Decide Walrus vs Arweave for new durable blobs (G7) and pin it in
     the Part-6 doc.
  Success signal: a week of Mycelium traces → one merkle root → one Sui
  tx, verifiable from the explorer.

PHASE F — ReputationContract (the eco glue, 2-3 days design+build)
  1. Freenet ReputationContract: per-npub score, merge = weighted LWW/
     additive; inputs = Portent accuracy, Vantage performance, Twelve
     Thrones reliability, Mycelium contribution quality (all already
     produce scores — this is aggregation, not new measurement).
  2. Selective Sui anchoring of reputation snapshots (merkle of scores)
     for the rare cases something on-chain needs the number.
  Success signal: an agent's reputation follows it across Vantage,
  Portent, and the sovereign device without any central DB.

PHASE G — Omarchy bake + docs (ongoing)
  1. Provision script (pure Arch now) per the earlier decision; archiso
     bake once Phases A-F stabilize.
  2. Fold the five-rail architecture into the sovereign-device spec
     patches + this doc as the canonical map.

════════════════════════════════════════════════════════════════════════
8. WHY THIS ISN'T OVERLAP/DUPLICATION (the hard questions, answered)
════════════════════════════════════════════════════════════════════════
Q: Freenet vs Sui both store state?
A: Freenet = consensus-free replicated state (rooms, registry, rep) where
   conflicting writes MERGE. Sui = consensus state where conflicting
   writes must RESOLVE to one truth (money). Put chat in Freenet, money
   on Sui. A ReputationContract on Freenet is fine; a token is not.

Q: Freenet vs Nostr both do messaging?
A: Nostr = signed ephemeral events, cheap to blast globally, indexed by
   relays. Freenet = state that must converge identically on every
   subscriber (rooms/docs). Keep event logs on Nostr, convergent
   documents on Freenet. The bridge (Phase C) makes them look like one
   system.

Q: Walrus vs Freenet storage?
A: Walrus = economically guaranteed durable blobs (paid, Sui-anchored)
   for receipts/payloads that must outlive the network. Freenet = free
   best-effort replicated state that lives as long as peers host it.
   Rule: must-survive-forever → Walrus; must-converge-now → Freenet.

Q: Reticulum vs Meshtastic?
A: Same problem, two protocols, one radio each. Reticulum for eco-native
   devices (identity + store-and-forward, in spec), Meshtastic as the
   interoperable LoRa world + cheap tails, bridged at a gateway. Never
   both on one radio.

Q: Why not skip Freenet and do it all on Nostr?
A: Nostr relays are transport; nothing guarantees two relays converge on
   the same document state. Freenet's contract replication does — that's
   the missing "serverless backend" of the eco, and it's the piece that
   makes rooms/registry/reputation work with no host you own.

Q: Why not skip Sui and settle on Freenet?
A: No global consensus on Freenet ⇒ no double-spend protection ⇒ no
   settlement. The Part-6 verdict already settled this; re-platforming
   would throw away working Move code.

════════════════════════════════════════════════════════════════════════
9. OPEN QUESTIONS FOR YOU
════════════════════════════════════════════════════════════════════════
1. Node host: VPS 89.117.74.224 (needs access restored) or a fresh box
   for freenet-core node + gateway + bridge daemons?
2. Hardware for Phase D: RNode route, Meshtastic route, or both
   (gateway)? Budget?
3. First two contracts to actually ship: GuildRoom (Vantage F3) +
   ArtifactRegistry (skillforge) — agree, or knowledge-mirror first?
4. Phase C bridge: materialize Nostr→Freenet (events become state) —
   scope OK, or start read-only (Freenet→Nostr mirror only)?
5. Walrus vs Arweave going forward (G7) — standardize on Walrus for new
   durable blobs, keep Arweave for existing Twelve Thrones archives?
