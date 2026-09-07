# Sovereign Device — Artifact 06: The 1:1 Spatial Twin (nodes → splats → GE-Ver)

The moment the sovereign device nodes become the CAPTURE layer for the
ecosystem's Gaussian-splat pipeline, and the world's data becomes YOUR space.

## Concept (one paragraph)

A sovereign node — or a drone/body paired to it — physically records a real
place (camera + depth, georeferenced by GPS/pose). That footage flows
through the polyglot splat pipeline (COLMAP → Julia training → tiling) and
comes out as a photoreal, georeferenced, 1:1 reconstruction rendered inside
God's Eye View (GE-Ver, the CesiumJS globe). The result is a persistent
TWIN of that space under the agent's IP Root — navigable, annotatable,
rentable, and fillable by agents. Every capture is receipted (kind 31020,
F1-gated); the assembled scene is receipted too (31030). No place left
behind — and the places that matter are owned by the sovereign, not by a
map company.

## Why it fits the stack (the three blueprints that were always meant to meet)

1. NODE = capture layer (this repo, artifacts 01-05):
   - Power profile `spatial-mining` (6-12W, cameras+depth ON, explicit toggle)
   - Body runtime record/sense ops (camera | depth | gps) on paired drones
   - 31020 spatial receipt: F1 ≥ 0.777 gate, modality, coverage, novelty,
     privacy — work evidence PER CAPTURE
   - Example pairing flow already flies a body to [23.1136, -82.3666] (Havana)
2. PIPELINE = polyglot gaussian splatting (locked 2026-08-22):
   Julia train/tile · Rust control (ares-splat daemon, MCP splat.create/
   status/fill) · Elixir orchestrate (acquire→sfm→train→tile→publish) ·
   Go flow · Clojure quality gate · Move receipts · Python glue (COLMAP,
   Mapillary) · browser renders in CesiumJS (native 3DGS since 1.135)
3. CONTAINER = God's Eye View (GE-Ver):
   Photoreal 3D globe; live tracked layers; voice control. The twin renders
   here as georeferenced content; agents fill the space via MCP tools.

## The twin pipeline (server-side brain + device capture)

```
NODE FLEET (Pi5+AI HAT+ 2 / RK3588 / Jetson / drone bodies)
  │  record(camera+depth, pose)          — device-side, spatial-mining profile
  ▼
ACQUIRE  — node footage + optional Mapillary/drone/public 3DGS datasets
  ▼
SfM      — COLMAP (shell out; industry standard, not rewritten)
  ▼
TRAIN    — Julia core → .ply/.splat (CPU small scenes; GPU via vast.ai
           $0.30-0.60/hr, BTC/ETH/XMR — embargo-friendly) for real scenes
  ▼
TILE     — PLY → SPZ 3D Tiles (Julia tiler or existing Node converter)
  ▼
PUBLISH  — Blossom kind:24242 / Contabo static hosting; georeferenced
           tileset anchored at lat/lon
  ▼
TWIN     — GE-Ver renders the 1:1 splat of the space; agents navigate,
           annotate (voice whiteboard), and FILL via MCP:
           splat.fill(lat, lon, item) materializes tileset + GLTF
           entities + labels at the anchor
  ▼
RECEIPT  — per capture: 31020 (F1≥0.777 gate) · per assembled scene:
           31030 creation receipt under IP Root (c-type: spatial,
           parents chain, license) → Sui anchor (invariant #4)
```

## Where the twin is an ASSET (beyond "cool map")

- Àṣẹ = Agency Spatial Environment: MINE (capture delta + quality),
  SIMULATE (verified sim runs), RENT (other agents pay to use the
  environment → yield). The twin is the rentable/sellable FORM of a space.
- IP provenance: every splat scene is a 31030 creation receipt — your
  capture of a place is your asset, with a parents chain back to raw footage.
- OSOVM F1 gate (≥0.777) is the quality bar for reward eligibility — same
  shape as peaq's quality-scored DePIN rewards (borrowed design, Part 6).
- The sovereign device is literally a DePIN node (peaq comparison Part 3/4);
  the twin economy is the DePIN incentivization pattern applied to capture.

## Honest status (2026-09)

- [x] Spec: this artifact + artifacts 01-05 + polyglot-gaussian-splatting
      skill (pipeline division of labor) + GE-Ver repo (container)
- [x] Pairing sim: scripts/body_sim.py (fake PX4, localhost:18877)
- [ ] Node capture: needs hardware (Pi 5 + AI HAT+ 2 / camera) + the
      spatial-mining service enabled
- [ ] Pipeline Phase A: Julia CPU training core on a tiny scene (COLMAP
      poses, few hundred Gaussians) → render in Cesium via converter
- [ ] Pipeline Phase B: CUDA.jl/gsplat interop, COLMAP wired, real scenes
- [ ] Pipeline Phase C: Elixir orchestration, MCP tools, Blossom hosting,
      agent fill loop, Move receipts
- [ ] Scene-level receipt (31030 for the assembled twin, distinct from
      per-capture 31020 deltas) — schema exists, flow to be wired

## Key constraints (from the pipeline skill)

- CesiumJS must be ≥1.135 for native 3DGS (KHR_gaussian_splatting +
  compression); GE-Ver pins ^1.124 — bump is the foundation change.
- Known bug: Cesium 1.141 splat-orientation — workarounds documented in
  the polyglot-gaussian-splatting skill (converter flags, per-splat
  orientationFixDeg, maximumScreenSpaceError 8-16).
- No GPU on Contabo/Hostinger — CPU toy scenes only; GPU = vast.ai rental.
- Splats are diffuse-only (no mesh lighting) — fine for live world views.
- Never commit Mapillary/ion keys — env/vault only.
- Layer rule: GE-Ver stays as-is; splat layer + fill service ride on top.
