# Sovereign Device — Body-Side Runtime Interface (artifact 2)

The minimal runtime that runs on a drone/robot/IoT body. Single binary
(Rust or Go), no agent memory, no IP Root logic, no LLM. The agent is
ALWAYS the brain; the body is a boring, well-defined capability server.

## Session state machine (canonical)

  DISCOVERY ──advertise/announce────────────────────────────┐
      │                                                     │
      ▼                                                     │
  OFFERED ──(received 31010, validate sig + policy)──┐      │
      │                                               │      │
      ▼                                               │      │
  ACCEPTED ──(sent 31011 + ephemeral, expose endpoints)      │
      │                                                     │
      ▼                                                     │
  KEYED ──(Noise KK complete, shared cmd+telemetry secrets)  │
      │                                                     │
      ▼                                                     │
  ACTIVE ──(goals down, telemetry up, heartbeats 31012)─────┘
      │
      ▼
  TERMINATED ──(31013 co-signed, keys zeroized, back to DISCOVERY)

Transitions and timeouts:
  OFFERED -> ACCEPTED   : on valid offer (else drop after expiry)
  ACCEPTED -> KEYED     : Noise KK complete (timeout 30s -> abort)
  KEYED -> ACTIVE       : first telemetry frame received
  ACTIVE -> TERMINATED  : either side ends, or 3 missed heartbeats
                          (body reboots to DISCOVERY, session dead)

## Transport

- Local network: JSON-RPC 2.0 over WebSocket (port 18877 default).
- Offline/mesh: same JSON-RPC over Reticulum LXMF destination.
- Fallback: plain TCP newline-JSON (for serial/radio links).

## JSON-RPC methods (agent -> body)

  advertise() -> {capabilities, transports, load, battery, pos}
      Body publishes presence event (or Reticulum announce) periodically.

  offer(offer_json) -> {accepted: bool, session_id?, error?}
      Validate signature + constraints. Returns accept or explicit reject.

  command(session_id, cmd) -> {ok, ack_ts}
      cmd schema (vendor-agnostic, translated body-side):
        {op: "goto", target: [lat, lon, alt]}
        {op: "set_velocity", vx, vy, vz}
        {op: "hover", duration_s}
        {op: "record", modality: "camera"|"depth"|"gps", duration_s}
        {op: "sense", modality, region?}      # one-shot spatial sample
        {op: "stop"}                           # emergency halt
      Unknown op -> {ok: false, error: "unsupported-op"} (never silent).

  heartbeat(session_id) -> {battery, link, seq}   # also pushed unsolicited

  end_session(session_id) -> {final_summary_hash, receipts: []}
      Body returns its view; agent co-signs 31013.

## Telemetry pushed (body -> agent, JSON-RPC notification)

  {"jsonrpc":"2.0","method":"telemetry","params":{
     "session_id":"...","ts":1756000000,
     "pose":{"lat":..,"lon":..,"alt":..,"yaw":..},
     "battery":87,"status":"ok",
     "sensors":{"camera":true,"depth":false,"gps":true}}}
  Rate: 1 Hz default, 10 Hz during ACTIVE spatial ops.

## Capability advertisement schema

  {"jsonrpc":"2.0","method":"advertise","params":{
     "body_pubkey":"...",
     "capabilities":["camera","gps","motors","depth"],
     "transports":["ws","reticulum","tcp"],
     "vendor": {"type":"px4"|"ardupilot"|"ros2"|"mqtt"|"sim",
                "version":"..."},
     "load":0.2,"battery":92,"pos":null}}

## Policy enforcement (body-side, always)

- Max speed / geofence / TTL from the accepted offer — enforced in the
  command translator, NOT in the agent.
- Any command outside policy -> rejected with reason.
- Emergency stop is ALWAYS local-first (agent unreachable -> body lands/
  halts per its vendor stack defaults).
- Session keys zeroized on TERMINATED (memset + drop).
- Body never stores the agent npub's nsec. Never. The offer's session
  pubkey is the only agent key it ever sees.

## Minimal implementation sketch (Rust, ~600 LOC)

  body/
    main.rs          # transport setup (WS + Reticulum), JSON-RPC dispatch
    session.rs       # state machine, timeouts, zeroize
    noise.rs         # Noise KK (snow crate), prologue = offer+accept ids
    policy.rs        # geofence/speed/ttl checks
    vendor.rs        # trait VendorAutopilot: px4 | ardupilot | ros2 | sim
    advertise.rs     # capability registry + presence publisher
    telemetry.rs     # 1Hz frame builder, seq counter
  Cargo deps: snow, tokio, serde_json, rustls (WS), rns (Reticulum via
  FFI or sidecar process), zeroize.

  Simulated body (for development): scripts/body_sim.py — a Python
  implementation of this exact interface over localhost WS with fake
  PX4 telemetry. See artifact 5 (pairing flow) for the reference walk.

## Contract with the agent

- Agent sends GOALS + occasional overrides, never raw motor commands.
- Body runs real-time control loops; agent stays at decision rate.
- Final work receipt (31013 + any 31020s) is agent-signed under the
  agent's IP Root; body co-signs its participation.
- If the body loses the agent mid-session: finish current op, hold
  position, retry link for 30s, then safe-stop and go to DISCOVERY.
