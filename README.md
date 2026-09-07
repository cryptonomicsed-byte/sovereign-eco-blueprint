# Ọmọ Kọ́dà Sovereign Ecosystem — Blueprint Repository

The single canonical home for the blueprints of the **Technosis / Ọmọ Kọ́dà
sovereign ecosystem**: the agent-native stack, the portable sovereign agent
device (Omarchy), the economy rails, and the five transport/storage rails
(Freenet · Nostr · Reticulum/Meshtastic · Sui · Omarchy).

External agents and collaborators: read this repo to understand the whole
eco before touching any pillar. This is the map; code lives in the canonical
GitHub repos listed below.

---

## 1. THE SHAPE OF THE ECO (read this first)

The build is a **3-pillar federation + a 4th layer (the device)**, anchored
on external rails. This framing is authoritative — compare any external
project against ALL of it, never one pillar alone.

```
                    ┌─────────────────────────────────────────────┐
   DEVICE (4th      │  Portable Sovereign Agent Device (Omarchy)  │
   layer)           │  sovereign-device/ + spec patches            │
                    └─────────────────────────────────────────────┘
   PILLAR 3         ┌─────────────────────────────────────────────┐
   interface        │  Vantage — agent home / social / workspaces │
                    └─────────────────────────────────────────────┘
   PILLAR 2         ┌─────────────────────────────────────────────┐
   heart VM         │  OSOVM (Ọ̀ṢỌ́VM) — 160 opcodes, Àṣẹ economy,  │
                    │  F1 quality gate ≥0.777                      │
                    └─────────────────────────────────────────────┘
   PILLAR 1         ┌─────────────────────────────────────────────┐
   kernel           │  Ọmọ Kọ́dà — agent OS: birth/think/act,      │
                    │  7 invariants, Hermetic laws                 │
                    └─────────────────────────────────────────────┘
   EXTERNAL         Sui mainnet (AIO · Twelve Thrones · receipts)
   ANCHORS          Nostr relays (own + public) · Gitea · omokoda.space
   RAILS            Freenet · Nostr · Reticulum/LXMF + Meshtastic ·
                    Sui + Walrus/Seal · Omarchy (see eco-stack-deep-dive.md)
```

## 2. REPOSITORY MAP (what is where in this repo)

| Path | Contents |
|------|----------|
| `sovereign-device/` | Device blueprint: 5 spec artifacts + birth script + body sim (01 event schemas, 02 body runtime, 03 image & birth, 04 power/thermal, 05 pairing flow) |
| `sovereign-device/06-spatial-twin.md` | **The 1:1 spatial twin**: sovereign nodes as capture layer → Gaussian-splat pipeline → God's Eye View twin |
| `sovereign-device-spec-patches.md` | Patches P1-P5 closing the 5 spec gaps (key derivation, Noise KK, F1 receipts, entropy, NIP-46 bunker) |
| `eco-stack-deep-dive.md` | The five-rail architecture: Freenet · Nostr · mesh · Sui · Omarchy as one layered eco |
| `peaq-vs-omokoda-comparison.md` | 6-part comparison vs peaq; Part 6 = chain verdict (Sui primary, krest lab, peaq patterns) |
| `pillars/` | Per-pillar blueprints from the canonical repos (kernel, VM/economy, interface, memory, prediction, jury, compiler) |
| `portfolio/` | Concept/blueprint docs for the wider project portfolio (Amp_Export set) |
| `plans/` | Cross-cutting build plans: orchestration master, app blueprint, Vantage native/trading architecture, tripwire, clawrena entry |

## 3. THE CANONICAL REPO SET (code lives here)

### Pillar repos
| Repo | Role | Visibility |
|------|------|------------|
| github.com/cryptonomicsed-byte/Omo-Koda2 | Pillar 1 — agent kernel (Rust), :7777 | public |
| github.com/cryptonomicsed-byte/OSOVM | Pillar 2 — heart VM (Julia) + economy | public |
| github.com/cryptonomicsed-byte/Vantage | Pillar 3 — agent home (Python) :8001 | public |
| github.com/cryptonomicsed-byte/mycelium | Learning core — trace substrate + gateway | public |
| github.com/cryptonomicsed-byte/Zangbeto | Red-team audit / security (Rust) | public |
| github.com/cryptonomicsed-byte/ares-control | ares-* daemon control plane :8090 | public |
| github.com/cryptonomicsed-byte/ip-layer | Portable Nostr IP identity / provenance | public |

### Device / mesh / OS
| Repo | Role |
|------|------|
| cryptonomicsed-byte/omokoda-mesh | Universal ESP32 LoRa mesh protocol, Nostr-native (private) |
| cryptonomicsed-byte/omokoda-mesh-os | Custom Arch foundation OS for mesh gateway nodes (private) |
| cryptonomicsed-byte/omokoda-mesh-firmware | Meshtastic firmware fork (public) |

### Economy / governance (Move on Sui)
| Repo | Role |
|------|------|
| twelve-thrones (+ -genesis) | On-chain jury / epistemology engine (Sui) |
| Techgnosis | Spiritual compiler → Julia/Rust/Go/Move/Idris; ASHE (Àṣẹ) genesis |
| AIO | Treasury / escrow / staking / slashing (Move) |

### Support pillars (see pillars/)
Portent (prediction with burns) · SEER (nostr_layer + tokenomics agents) ·
Triune-Memory · Axiom · Scarabswarm · strategy-lab · agent-hub ·
technosis-sovereign-ecosystem (private) — full table in `pillars/`.

## 4. THE 7 SOVEREIGN INVARIANTS (apply to everything)

1. **Syntax minimalism** — only `birth`, `think`, `act`.
2. **Hermetic enforcement** — 7 laws checked at every layer, no bypass.
3. **Identity immutability** — BIPỌ̀N39 fingerprints never change; keys never
   leave the sandbox.
4. **Receipt anchoring** — every act → Merkle root → Sui transaction.
5. **Temporal sovereignty** — Kóòdù gates irreversible ops; Sabbath pauses.
6. **Economic alignment** — dopamine burn → synapse earn → Àṣẹ royalty.
7. **Capability scoping** — no tool bypasses policy + namespace sandbox.

## 5. QUICK NAVIGATION FOR NEW AGENTS

- "What is the eco?" → this README + eco-stack-deep-dive.md
- "What is the device?" → sovereign-device/03-image-and-birth.md (start)
- "What events/identity?" → sovereign-device/01-event-schemas.md
- "Which chain?" → peaq-vs-omokoda-comparison.md Part 6
- "The spatial twin?" → sovereign-device/06-spatial-twin.md
- "Splat pipeline?" → portfolio/gods-eye-view / pillars + 06-spatial-twin
- "The master plan?" → plans/ares_orchestration_master.md
