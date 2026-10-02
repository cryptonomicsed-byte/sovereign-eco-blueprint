# LOCAL BEARER — v0.1

The co-located, no-infrastructure bearer for DIP/VCP discovery and session
establishment. Lets an agent and a body (or two agents) find each other and open
a verified session on the same local network with **no relay, no internet, no
DHCP, no DNS, no server**.

Status: SPEC. Adds one bearer to the existing transport set; reuses the existing
handshake unchanged.

---

## 1. The gap this closes

The body runtime (sovereign-device artefacts 02/05) discovers a peer only via:

- **relay filter** (`t=embodiment/presence`), or
- a **Reticulum announce**.

There is **no bearer for the most common case**: agent and body on the same WiFi,
no internet, no relay. That is precisely the off-grid case the whole thesis turns
on, and it is currently unserved. `advertise()` lists
`transports:["ws","reticulum","tcp"]` — this adds `"lan"`.

---

## 2. Mechanism (four steps)

### Step 1 — ADVERTISE
The body/agent emits a manifest (as a QR, a static beacon, or a served endpoint):

```json
{
  "pubkey": "…",
  "capabilities": ["camera","gps","motors"],
  "transports": ["lan","ws","reticulum","tcp"],
  "addr_hints": {
    "mac": "11:22:33:44:55:66",
    "prefixes": ["fe80::/64", "fd00:…/64"],
    "explicit": ["192.168.1.42:18877"]      // fallback, always include one
  }
}
```

### Step 2 — DERIVE
The peer computes a candidate address from the remote MAC and its OWN interface:

```
own_addr  = the local interface's IPv6 link-local (fe80::/10) or ULA (fc00::/7),
            which embeds the interface's own MAC in EUI-64 form
candidate = own_addr with the MAC substituted for the remote's MAC from addr_hints
```

### Step 3 — PROBE
Probe `candidate`, then each `addr_hints.explicit` in order. First one that
answers wins.

> **Always carry an explicit address.** Android's IPv6 privacy extensions
> (RFC 4941) generate addresses that do NOT embed the MAC, which breaks the
> derivation. The derived address is a *hint*; the explicit address is the
> *fallback*. Meshenger hits this same limitation and documents it.

### Step 4 — HANDSHAKE (unchanged)
Open WS/TCP to the address, then run the EXISTING VCP flow verbatim:

```
OFFER   kind 31010, signed by the agent npub
   ↓    (body validates signature + policy: geofence, max-speed, ttl)
ACCEPT  {accepted:true, session_id, body_session_pubkey}
   ↓
KEYED   Noise KK — prologue = sha256(offer_event_id ‖ accept_event_id)
        one round trip, both statics authenticated
   ↓
ACTIVE  command + telemetry (JSON-RPC 2.0)
   ↓
RECEIPT session receipt; samples scored F1 ≥ 0.777 → kind 31020
```

Nothing in step 4 changes. This spec adds addressing and a bearer, not a protocol.

---

## 3. Why QR-first, not mDNS

Led with the QR (or a static beacon) rather than multicast discovery, because
**broadcast/multicast is commonly blocked** on community/mesh networks. Meshenger
made exactly this choice and avoided mDNS for the same reason. On a hostile or
rebuilt LAN, mDNS will silently find nothing.

---

## 4. Scope and constraints (state them plainly)

| property | value |
|---|---|
| Reach | **co-located / edge nodes only** — same LAN segment |
| NAT traversal | **off, by design** — cannot cross a NAT or firewall border |
| Internet | not required |
| DHCP / DNS | not required |
| Server | not required |
| Cloud agents | **NOT reachable** — a VPS agent is outside this bearer's reach |

⇒ The honest framing is an **edge** capability: an agent on the device, the phone,
a nearby SBC. That is a strength of the sovereign-device thesis, not a limitation
to hide. Cloud reach remains Nostr / relay.

---

## 5. What is taken from Meshenger, and what is not

| | |
|---|---|
| **Taken** | QR contact exchange; MAC → IPv6 link-local derivation for serverless local reachability; the "no infrastructure" posture; the mDNS-avoidance lesson |
| **Not taken** | the app · the Android-only constraint · ed25519 identity (eco is secp256k1) · libsodium signaling crypto (**keep Noise KK**) · WebRTC media (unless a later voice feature needs it) · the 1:1-only model |

Meshenger is a **reference implementation of an addressing pattern**, never a
dependency of the kernel. (Its GPL-3.0 licence would make it awkward as a
dependency anyway; studying a pattern carries no such obligation.)

---

## 6. Where this lands

The physical build order already puts the **RuView ESP32 adapter first** ($9,
immediate value). The `lan` bearer is the transport that makes RuView — and every
other VCP device with no internet — reachable for pairing. It is the missing
half of "walk up, connect, use, walk away":

```
walk up → scan card (AGENT_CONTACT_CARD.md) → derive address (this spec)
       → OFFER → ACCEPT → Noise KK → capability grant (15 min TTL)
       → use → walk away → session revokes
```

---

## 7. Invariant

```
Transport ≠ authority
```
This bearer delivers bytes. It executes nothing. An inbound communication becomes
a `MutationPlan` (omokoda-core/src/mutation/) which is inspected, applied,
rollback-able and receipted. The bearer is incapable of being an execution
authority — which is what makes it safe to open a socket to a stranger you met on
a local network.
