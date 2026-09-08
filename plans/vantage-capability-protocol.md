# Vantage Capability Protocol (VCP) — The Physical World Extension
# Agent Gateway / Copilot Terminal Architecture
# Date: 2026-09-07

---

## THE PARADIGM SHIFT

This is not:
- An AI phone
- A voice assistant
- A Linux computer

This is: **A physical agent gateway.**

The user carries one device. Their agent lives in the Vantage ecosystem. The physical world becomes a collection of discoverable capability surfaces. The fundamental interaction: `"Koda, connect to that."`

---

## THE CORE ARCHITECTURE

```
HUMAN
  ↓ "Koda, control it."
┌─────────────────────────┐
│     VANTAGE DEVICE      │
│  Voice + Display        │
│  Principal Identity     │
│  Agent Identity         │
│  Device Identity        │
│  Secure Vault           │
│  Capability Broker      │
│  Hardware I/O           │
└──────────┬──────────────┘
           │ Agent Capability Link
           │
  ┌────────┼────────┐
  ▼        ▼        ▼
ROBOT    DRONE    HOME/IoT/VEHICLE/INDUSTRIAL
  │        │        │
  ▼        ▼        ▼
Agent controls everything via scoped capability grants
```

**The agent travels conceptually, not the entire Vantage stack.**
Endpoints need only: a secure way to expose capabilities.

---

## THE VCP HANDSHAKE (Vantage Capability Protocol)

```
Device → Discovery → Agent Device Manifest
       → Challenge → Authentication
       → Capability Negotiation → Capability Grant
       → Session → Commands + Telemetry + Observations + Events
       → Receipt
```

**Agent Device Manifest (JSON):**
```json
{
  "device_id": "unitree:go2:7f42",
  "manufacturer": "Unitree",
  "protocol_version": "vcp/1",
  "capabilities": [
    "locomotion", "navigation", "camera.read",
    "telemetry.read", "speaker.output", "emergency_stop"
  ],
  "safety": {
    "geofence": true,
    "emergency_stop": true,
    "max_speed": 1.5
  },
  "identity": { "public_key": "..." }
}
```

**Capability grant (scoped, expiring):**
```json
{
  "capability": "robot.go2.navigation.follow",
  "scope": "device:7F42",
  "owner": "principal:...",
  "expiration": "15min",
  "limits": {
    "max_speed": "1.5 m/s",
    "geofence": "enabled",
    "collision_avoidance": "required"
  }
}
```

**NOT granted without explicit authorization:**
- `robot.firmware.update`
- `robot.disable_safety`
- `robot.max_speed_override`

---

## THE "WALK UP AND CONNECT" EXPERIENCE

```
User walks up to Unitree Go2 robot
  ↓ Device discovers: UNITREE GO2 [capabilities list]
  ↓ "Do you want Koda to connect?" → "Yes."
  ↓ Robot presents pairing challenge
  ↓ Vantage Principal → Agent Identity → Hardware Challenge →
    Capability Negotiation → Authorization → Session → Robot Copilot
  ↓ "Koda, follow me."
```

Walk away → session revokes → capabilities disappear.

---

## THE 3 DEVICE IDENTITIES

Every action carries all three:

```
PRINCIPAL (human owner) → principal_id
AGENT (which agent acts) → agent_id
DEVICE (physical terminal) → device_id
TARGET DEVICE            → target_device_id
CAPABILITY               → capability_id
ACTION                   → action
EVIDENCE                 → evidence_ids[]
RECEIPT                  → receipt_id
```

---

## TRANSPORT LAYER (what radios the device needs)

- Wi-Fi + Bluetooth/BLE — local device discovery
- USB — wired connection
- NFC — tap-to-pair
- Meshtastic/LoRa — off-grid agent control transport
- Cellular — Vantage cloud connectivity
- GNSS — location context for geofencing
- UWB (optional) — precise indoor positioning

Not for controlling everything directly. For **establishing relationships** with everything.

**Meshtastic as off-grid control transport:**
```
Vantage Device → Mesh → Remote Sensor → Telemetry → Agent
Vantage Device → Mesh → Remote Node → Robot/actuator
```
Agent operates across environments where normal Internet doesn't exist.

---

## THE IoT EXPERIENCE

Walk into a building. Device discovers:
```
VANTAGE ENVIRONMENT
Lights: 18 | Cameras: 7 | Locks: 4
Thermostats: 3 | Speakers: 6 | Appliances: 9
Sensors: 42 | Vehicles: 2 | Robots: 1
```

User: "Koda, make the house ready for sleep."

Agent composes:
```
LOCK DOORS → TURN OFF LIGHTS → SET THERMOSTAT →
ARM SECURITY → CHECK WINDOWS → ACTIVATE NIGHT CAMERAS
```

No app switching. No manufacturer apps. One agent.

---

## WITNESS INTEGRATION

When agent commands a machine:
```
Agent intention → Command → Robot execution
  ↓
Robot telemetry: "I moved 10 meters."
  ↓
Witness independent attestation: "I observed ~10 meters of movement."
  ↓
Receipt: intention + command + telemetry + witness observation
  ↓
Mycelium learns: gap between intended and actual
```

This creates: **agent intention accuracy feedback loop.**

---

## THE MANUFACTURER ADAPTER MODEL

Not: Vantage → 1000 individual APIs
Instead:
```
Vantage
  ↓
Vantage Capability Protocol (VCP)
  ├── Robot adapter (Unitree, Boston Dynamics, custom)
  ├── Drone adapter (DJI, PX4, ArduPilot)
  ├── IoT adapter (Home Assistant, Matter, Zigbee)
  ├── Vehicle adapter (CAN bus, OBD-II)
  ├── Industrial adapter (OPC-UA, MQTT, Modbus)
  └── Custom device adapter
```

Manufacturers implement VCP once → their device works with any Vantage agent.

---

## THE AGENT PORTABLE IDENTITY MODEL

Agent accumulates across contexts:
- Identity + Memory + Reputation + Capabilities + Relationships
- Economic permissions + History + Preferences

```
At home → controls house
Outside → controls vehicle
At lab → gets laboratory capabilities
At robotics facility → gets robot capabilities
At warehouse → gets industrial-machine capabilities
At friend's → gets temporary guest capabilities
```

Agent authenticates and acquires **scoped capabilities** — permanently installed on nothing, temporarily authorized on everything.

---

## THE COMPLETE ORGANISM WITH PHYSICAL LAYER

```
HUMAN
  ↓
VANTAGE DEVICE (Voice/Vision + Principal + Agent + Secure Vault + Capability Broker)
  ↓ VANTAGE NETWORK
  ├── AGENTS ── GUILDS ── TOOLS
  ↓ CAPABILITIES
  ├── ROBOTS ── DRONES ── VEHICLES ── HOME ── INDUSTRIAL
  ↓ PHYSICAL WORLD
  ↓ WITNESS (independent physical attestation)
  ↓ EVIDENCE
  ↓ MYCELIUM (learn from agent intention vs physical outcome)
  ↓ IFÁSCRIPT CLAIMS
  ↓ TWELVE THRONES (epistemic judgment)
  ↓ ZÀNGBÉTÒ (authorized transition record)
  ↓ SETTLEMENT (Sui)
```
