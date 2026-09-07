# Sovereign Device — Reference Pairing Flow (artifact 5)

Walkthrough of one full embodiment session: agent (personal device) pairs
with a BODY (here: simulated drone) using the artifact-2 interface, over
localhost WebSocket. The sim is real code (scripts/body_sim.py) — run it,
then drive it with the JSON-RPC calls below.

## Setup

  # terminal 1 — start the simulated body (fake PX4 on localhost:18877)
  python3 scripts/body_sim.py
  # -> {"jsonrpc":"2.0","result":{"advertise":true,"body_pubkey":"b0d1..."},
  #     "id":1}  + starts advertising + telemetry loop

## 1. DISCOVERY

Body publishes presence (in sim: prints an advertise JSON + can be
fetched):
  {"jsonrpc":"2.0","method":"advertise","params":{
     "body_pubkey":"b0d1...",
     "capabilities":["camera","gps","motors"],
     "transports":["ws"],"vendor":{"type":"sim","version":"1.0"},
     "load":0.1,"battery":95,"pos":null}}

Agent sees it via relay filter (t=embodiment/presence) or Reticulum
announce. For the sim: agent queries GET /advertise on the sim's HTTP
stub (the sim exposes one: http://127.0.0.1:18878/advertise).

## 2. OFFER -> ACCEPT

Agent signs kind 31010 offer (schema in artifact 1), sends over WS:
  {"jsonrpc":"2.0","method":"offer","params":{
     "offer_event": { ...full 31010 json, signed by agent npub... }},
   "id":2}

Body validates signature + policy (geofence inside, max-speed 5, ttl
3600) -> returns:
  {"jsonrpc":"2.0","result":{"accepted":true,"session_id":"s-9f21",
     "body_session_pubkey":"bb01..."},"id":2}

## 3. KEYED (Noise KK)

In the sim, the key agreement is replaced with a recorded placeholder
(the sim prints "NOISE-KK prologue=31010id|31011id — would derive
shared secrets"). In the real body runtime (artifact 2, `snow` crate):
  - prologue = sha256(offer_event_id || accept_event_id)
  - KK handshake, one round trip, both statics authenticated.
  Result: two channel keys (cmd + telemetry). Sim prints the derived
  session id and marks state ACTIVE.

## 4. ACTIVE — command + telemetry

  {"jsonrpc":"2.0","method":"command","params":{
     "session_id":"s-9f21","cmd":{"op":"goto","target":[23.1136,-82.3666,50]}},
   "id":3}
  -> {"jsonrpc":"2.0","result":{"ok":true,"ack_ts":1756000100},"id":3}

Sim streams telemetry (1 Hz):
  {"jsonrpc":"2.0","method":"telemetry","params":{
     "session_id":"s-9f21","ts":1756000101,
     "pose":{"lat":23.1136,"lon":-82.3666,"alt":49.8,"yaw":12},
     "battery":94,"status":"ok","sensors":{"camera":true,"gps":true}}}

  {"jsonrpc":"2.0","method":"command","params":{
     "session_id":"s-9f21","cmd":{"op":"sense","modality":"camera","region":"tile-7"}},
   "id":4}
  -> {"jsonrpc":"2.0","result":{"ok":true,"sample_id":"sp-0001"},"id":4}

Agent scores the sample (F1 >= 0.777?) -> if pass, emits kind 31020
spatial receipt under its IP Root (schema in artifact 1).

## 5. TERMINATED

  {"jsonrpc":"2.0","method":"end_session","params":{"session_id":"s-9f21"},
   "id":5}
  -> {"jsonrpc":"2.0","result":{
       "final_summary_hash":"ab12...",
       "receipts":["sp-0001"]},
     "id":5}

Agent publishes kind 31013 embodiment/end (co-signed), zeroizes session
keys, body returns to DISCOVERY.

## Full message order (reference)

  1. advertise (body, periodic)
  2. offer 31010 (agent -> body, WS "offer")
  3. accept (body -> agent, WS response)
  4. NOISE-KK (one round trip, prologue bound)
  5. command/goto (agent -> body)
  6. telemetry* (body -> agent, 1 Hz)
  7. command/sense -> sample
  8. 31020 spatial receipt (agent -> relays, if F1 passes)
  9. end_session (agent -> body)
  10. 31013 embodiment/end (agent -> relays, co-signed by body key)
  11. session keys zeroized; body -> DISCOVERY

## Security invariants exercised

  - Body NEVER receives the agent nsec. Only the 31010 session pubkey.
  - Policy (geofence/speed/ttl) enforced body-side in the command
    translator — sim rejects any out-of-policy op.
  - Prologue binds handshake to the published offer/accept events, so a
    replayed offer cannot re-derive the same channel.
  - Final receipt links session -> spatial receipts -> IP Root.

## scripts/body_sim.py — what it does

  - JSON-RPC 2.0 over WS on 127.0.0.1:18877 (websockets lib).
  - HTTP stub on 127.0.0.1:18878 for /advertise + /status (curl-able).
  - Fake PX4 telemetry loop (1 Hz), battery drains, pose moves toward
    the last goto target.
  - Policy enforcer: geofence (Havana box 23.0-23.3 / -82.5..-82.2),
    max-speed 5 m/s, ttl 3600s — rejects violations with a reason.
  - State machine: DISCOVERY -> OFFERED -> ACCEPTED -> KEYED(sim) ->
    ACTIVE -> TERMINATED (prints each transition).
  - Placeholder Noise-KK print (real handshake lives in the Rust body
    runtime, artifact 2).
