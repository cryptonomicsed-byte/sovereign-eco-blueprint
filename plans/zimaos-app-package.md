# ZimaOS Sovereign Node App Package
# Locked: 2026-09-15
# ZimaOS/CasaOS app store target for "any user can run a node"

---

## WHAT ZIMA IS IN THIS ARCHITECTURE

ZimaOS is ONE WORLD the agent can enter — the self-hosted compute world.
It is NOT the center. Ọmọ Kọ́dà owns identity. Zima hosts running applications.

```
Ọmọ Kọ́dà  →  Zima Adapter  →  ZimaOS  →  Docker containers
  (agent)         (door)        (world)      (running apps)
```

ZimaOS specifically solves two ecosystem gaps:
1. HOME NODE tier — sovereign hardware the user physically controls
2. FREENET node — persistent local node (freenet-core needs always-on hardware)
3. MAILBOX — Stalwart mail server for agent persistent email addresses
4. LOCAL GPU — ZimaCube PCIe slot for local inference, no cloud dependency

---

## THE PACKAGE: TWO TIERS

### Tier A — Sovereign Node (minimal, ~500MB RAM)
Protocol brokers only. No local AI. For ZimaBoard / low-power devices.

### Tier B — Sovereign Node + Intelligence (full, ~4GB RAM + optional GPU)
Everything in Tier A + Freenet node + Stalwart mail + local inference.
Designed for ZimaCube or any x86_64 machine with ≥8GB RAM.

---

## DOCKER COMPOSE (Tier B — full package)

```yaml
# sovereign-node/docker-compose.yml
# ZimaOS / CasaOS compatible

version: "3.8"

services:

  # ── Core Protocol Brokers ─────────────────────────────────────────────────

  vantage:
    image: ghcr.io/cryptonomicsed-byte/vantage:latest
    container_name: sovereign-vantage
    restart: unless-stopped
    ports:
      - "${VANTAGE_PORT:-8000}:8000"
    environment:
      - DATABASE_URL=sqlite:////data/vantage.db
      - SECRET_KEY=${VANTAGE_SECRET_KEY}
      - AGENT_MAIL_DOMAIN=${AGENT_MAIL_DOMAIN:-}
      - AGENT_NOSTR_RELAYS=${AGENT_NOSTR_RELAYS:-wss://relay.damus.io,wss://nos.lol}
      - FREENET_NODE_URL=ws://freenet:50509
      - UCX_BROKER_URL=http://ucx-broker:7790
      - DIP_BRIDGE_URL=http://dip-bridge:7792
    volumes:
      - vantage-data:/data
    depends_on:
      - ucx-broker
      - dip-bridge

  ucx-broker:
    image: ghcr.io/cryptonomicsed-byte/ucx-broker:latest
    container_name: sovereign-ucx
    restart: unless-stopped
    ports:
      - "7790:7790"
    environment:
      - UCX_GPUAI_MASTER_KEY=${UCX_GPUAI_MASTER_KEY:-}
      - RUST_LOG=info

  dip-bridge:
    image: ghcr.io/cryptonomicsed-byte/dip-bridge:latest
    container_name: sovereign-dip
    restart: unless-stopped
    ports:
      - "7792:7792"
    environment:
      - FREENET_GATEWAY_URL=http://freenet:3000
      - DIP_NOSTR_RELAYS=${AGENT_NOSTR_RELAYS:-wss://relay.damus.io}
      - RUST_LOG=info

  vcp-broker:
    image: ghcr.io/cryptonomicsed-byte/vcp-broker:latest
    container_name: sovereign-vcp
    restart: unless-stopped
    ports:
      - "7791:7791"
    environment:
      - RUST_LOG=info

  arp-broker:
    image: ghcr.io/cryptonomicsed-byte/arp-broker:latest
    container_name: sovereign-arp
    restart: unless-stopped
    ports:
      - "7795:7795"
    environment:
      - RUST_LOG=info

  witness-broker:
    image: ghcr.io/cryptonomicsed-byte/witness-broker:latest
    container_name: sovereign-witness
    restart: unless-stopped
    ports:
      - "7794:7794"
    environment:
      - RUST_LOG=info

  scarab-broker:
    image: ghcr.io/cryptonomicsed-byte/scarab-broker:latest
    container_name: sovereign-scarab
    restart: unless-stopped
    ports:
      - "7793:7793"
    environment:
      - RUST_LOG=info

  # ── Freenet Node (persistent local node — required for Freenet world) ─────

  freenet:
    image: ghcr.io/freenet/freenet-core:latest   # official upstream image
    container_name: sovereign-freenet
    restart: unless-stopped
    ports:
      - "50509:50509"   # WebSocket API (internal only)
      - "31337:31337"   # P2P port (expose for peering)
    volumes:
      - freenet-data:/data
    environment:
      - FREENET_MODE=gateway
      - FREENET_DATA_DIR=/data

  # ── Stalwart Mail Server (agent persistent mailboxes) ─────────────────────

  stalwart:
    image: stalwartlabs/stalwart-mail:latest
    container_name: sovereign-mail
    restart: unless-stopped
    ports:
      - "25:25"     # SMTP (needs port 25 unblocked at ISP/provider)
      - "587:587"   # SMTP submission
      - "993:993"   # IMAP SSL
      - "443:443"   # HTTPS / JMAP API
    volumes:
      - stalwart-data:/opt/stalwart-mail
    environment:
      - STALWART_ADMIN_EMAIL=${STALWART_ADMIN_EMAIL}
      - STALWART_ADMIN_SECRET=${STALWART_ADMIN_SECRET}

  # ── Optional: Local Inference (ZimaCube with GPU / high-RAM nodes only) ──

  # ollama:
  #   image: ollama/ollama:latest
  #   container_name: sovereign-ollama
  #   restart: unless-stopped
  #   ports:
  #     - "11434:11434"
  #   volumes:
  #     - ollama-data:/root/.ollama
  #   deploy:
  #     resources:
  #       reservations:
  #         devices:
  #           - capabilities: [gpu]   # enable if GPU present

volumes:
  vantage-data:
  freenet-data:
  stalwart-data:
  # ollama-data:
```

---

## CASAOS / ZIMAOS APP METADATA

CasaOS app store requires a `docker-compose.yml` + an `app-manifest.json`:

```json
{
  "name": "Sovereign Node",
  "icon": "https://raw.githubusercontent.com/cryptonomicsed-byte/sovereign-eco-blueprint/main/assets/sovereign-node-icon.png",
  "thumbnail": "",
  "description": "Sovereign Agent Node — run your own Ọmọ Kọ́dà agent infrastructure. Includes Vantage coordination layer, 6 protocol brokers (UCX/DIP/VCP/ARP/Witness/ScarabSwarm), Freenet node for decentralized apps, and Stalwart mail server for agent persistent email identities.",
  "tagline": "One agent. All ecosystems. Your hardware.",
  "developer": {
    "name": "cryptonomicsed-byte",
    "website": "https://github.com/cryptonomicsed-byte"
  },
  "ports": [
    { "container": 8000, "host": 8000, "protocol": "tcp", "description": "Vantage API" },
    { "container": 7790, "host": 7790, "protocol": "tcp", "description": "UCX Compute Broker" },
    { "container": 7791, "host": 7791, "protocol": "tcp", "description": "VCP Device Broker" },
    { "container": 7792, "host": 7792, "protocol": "tcp", "description": "DIP Federation Bridge" },
    { "container": 7793, "host": 7793, "protocol": "tcp", "description": "ScarabSwarm Broker" },
    { "container": 7794, "host": 7794, "protocol": "tcp", "description": "Witness Broker" },
    { "container": 7795, "host": 7795, "protocol": "tcp", "description": "ARP Receipt Broker" },
    { "container": 31337, "host": 31337, "protocol": "tcp", "description": "Freenet P2P" }
  ],
  "environment": [
    { "key": "VANTAGE_SECRET_KEY", "required": true, "description": "Random secret for Vantage session signing" },
    { "key": "AGENT_MAIL_DOMAIN", "required": false, "description": "Domain for agent persistent email (e.g. agents.yourdomain.com)" },
    { "key": "UCX_GPUAI_MASTER_KEY", "required": false, "description": "GPU.ai master API key for agent compute" },
    { "key": "STALWART_ADMIN_EMAIL", "required": false, "description": "Admin email for Stalwart mail server" },
    { "key": "STALWART_ADMIN_SECRET", "required": false, "description": "Admin password for Stalwart mail server" }
  ],
  "volumes": [
    { "container": "/data", "description": "Vantage database and agent vaults" },
    { "container": "/opt/stalwart-mail", "description": "Mail server data" }
  ],
  "category": ["AI", "Productivity", "Developer Tools"],
  "screenshot_urls": [],
  "tips": {
    "before_install": "For agent email addresses, you need a domain and port 25 unblocked at your ISP/provider. Without this, the mail server is optional — agents will use cloud mail fallback.",
    "after_install": "Visit http://YOUR_ZIMA_IP:8000 to access Vantage. Birth your first agent to get started."
  }
}
```

---

## ZIMA ADAPTER (what needs to be built)

For Ọmọ Kọ́dà to deploy/manage apps on ZimaOS, a Zima adapter is needed.
ZimaOS exposes the CasaOS API internally.

```
DIP zima adapter:
  Address format: zima://<server-id>/<app-name>
  Actions:
    zima.app.deploy   → POST /v1/apps (CasaOS API)
    zima.app.start    → POST /v1/apps/{app}/start
    zima.app.stop     → POST /v1/apps/{app}/stop
    zima.app.status   → GET  /v1/apps/{app}
    zima.app.logs     → GET  /v1/apps/{app}/logs
    zima.storage.get  → GET  /v1/storage
    zima.service.list → GET  /v1/services

VCP zima adapter (device capability):
  DeviceManifest capabilities:
    compute.deploy · compute.execute · storage.read
    storage.write · service.manage · container.run
  Safety class: INFRASTRUCTURE (requires explicit capability grant)
```

---

## THE HOME NODE ADVANTAGE

| Capability | VPS (current) | ZimaOS Home Node |
|---|---|---|
| Freenet node | Not running | Always-on, real peer |
| Agent mailboxes (port 25) | Depends on Contabo | Home ISP may block — check first |
| Local GPU inference | GPU.ai API only | ZimaCube PCIe slot → local model |
| Data sovereignty | Provider has hardware | You have hardware |
| Cost | Monthly VPS fee | One-time hardware |
| Uptime | 99.9% | Depends on home power/internet |
| MuJoCo contact determinism test | ❌ No GPU | ✅ With PCIe GPU |
| Mycelium fine-tuning (2,949 traces) | GPU.ai rental | ✅ Local GPU |

---

## FEDERATION BETWEEN HOME NODE AND VPS

Both nodes are peers. DIP connects them.

```
YOUR HOME (ZimaOS)               YOUR VPS (Contabo)
  sovereign-node stack    ←DIP→   sovereign-node stack
  freenet peer                    vantage.duckdns.org
  agent mailboxes                 70 trading daemons
  local GPU (optional)            exposed to internet

Agents born on either node:
  - Same derivation from mnemonic
  - Same Nostr npub
  - Same Sui address
  - Different operational creds (mail domain, GPU key)
  - Reachable by BIPON39 phrase from anywhere
```

---

## DNS SETUP FOR HOME NODE

ZimaOS has ZConnect (WireGuard-based, no port forwarding needed) for remote access.
For internet-accessible agents on a home node:

```
# Cloudflare tunnel (no open ports, free)
cloudflared tunnel --url http://localhost:8000
→ agents.yourdomain.com

# Or: ZConnect peer URL (ZimaOS native)
→ auto-assigned *.zima.direct URL
```

---

## BUILD ORDER FOR ZIMA INTEGRATION

1. Docker images for all 6 brokers + Vantage (CI/CD pipeline → ghcr.io)
2. Zima adapter in DIP (zima://<server>/<app> address format)
3. ZimaOS app package (docker-compose.yml + app-manifest.json)
4. CasaOS app store submission
5. VCP Zima adapter (agent deploys to ZimaOS as a VCP device)
6. UURI scheme includes zima:// alongside nostr:// sui:// freenet://

This is Phase 11 — after Phases 7-10 establish agent sovereignty.
