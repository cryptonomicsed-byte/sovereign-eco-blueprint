# SOVEREIGN ECOSYSTEM — REPO WAVE BLUEPRINT
# Comprehensive todo checklist. Update status as each item completes.
# Canonical map: ~/sovereign-eco-blueprint/plans/repo-map-final.md
# Last updated: 2026-09-13

Status legend: [ ] pending  [x] done  [~] in-progress  [!] blocked  [-] N/A

---

## WAVE 1 — ARCHIVE DEAD REPOS
Move to ~/archive/ with ARCHIVED.md marker in each

- [x] W1-01  Archive ~/nex → ~/archive/nex  (pre-1.0 Nex version)
- [x] W1-02  Archive ~/VantageNew → ~/archive/VantageNew
- [x] W1-03  Archive ~/Vantage_dive → ~/archive/Vantage_dive
- [x] W1-04  Archive ~/Omo-koda-fresh-20260502 → ~/archive/Omo-koda-fresh-20260502
- [x] W1-05  Archive ~/mycelium-gh → ~/archive/mycelium-gh

---

## WAVE 2 — LANGUAGE + COMMS → OMO-KODA2

- [x] W2-01  Create ~/Omo-Koda2/absorbed/social/ and move Swibe content
- [x] W2-02  Create ~/Omo-Koda2/absorbed/lang/vibe/ and move vibe-lang content
- [x] W2-03  Create ~/Omo-Koda2/absorbed/lang/aether/ and move aether + The-Aether content
- [x] W2-04  Add ABSORBED.md marker in each source repo pointing to destination
- [x] W2-05  Archive original Swibe, vibe-lang, aether, The-Aether source dirs

---

## WAVE 3 — STUDY REPOS → OMO-KODA2/study/

- [x] W3-01  Create ~/Omo-Koda2/study/ directory with README.md index
- [x] W3-02  Copy agency-agents → ~/Omo-Koda2/study/agency-agents/
- [x] W3-03  Copy Droidclaw → ~/Omo-Koda2/study/droidclaw/
- [x] W3-04  Copy Claude-2 → ~/Omo-Koda2/study/Claude-2/
- [x] W3-05  Copy Claude-mirror → ~/Omo-Koda2/study/Claude-mirror/
- [x] W3-06  Copy Core-Agency → ~/Omo-Koda2/study/Core-Agency/
- [x] W3-07  Add STUDY_INDEX.md summarising what each teaches

---

## WAVE 4 — OSOVM: CREATE osovm-witness-sim

- [-] W4-01  Cargo.toml workspace — N/A (witness-firmware is Python, no Rust code)
- [x] W4-02  Create ~/osovm-witness-sim/firmware/ — moved witness-firmware content
- [x] W4-03  Create ~/osovm-witness-sim/blocksim/ — moved Blocksim + blocksim-repo content
- [x] W4-04  Write ~/osovm-witness-sim/README.md
- [x] W4-05  Write ~/osovm-witness-sim/MANIFEST.toml
- [-] W4-06  cargo check — N/A (no Rust in this repo)
- [x] W4-07  Add ABSORBED.md in original witness-firmware
- [x] W4-08  Add ABSORBED.md in original Blocksim / blocksim-repo
- [x] W4-09  Archive original witness-firmware and Blocksim dirs

---

## WAVE 5 — BACKEND → VANTAGE

- [x] W5-01  Create ~/Vantage/backend/aio/ and absorb AIO content
- [x] W5-02  Create ~/Vantage/backend/cinema/agent_tv/ and absorb Agent.TV content
- [x] W5-03  Create ~/Vantage/backend/reach/ and absorb Agent-Reach content
- [!] W5-04  Absorb omokoda-smithers gates half — repo not present locally; defer
- [x] W5-05  Create ~/Vantage/backend/economy/ase/ and absorb ase-vault + asemirror
- [!] W5-06  Wire AIO router — AIO is Move/Docker service stack, not Python module; needs service URL proxy config when AIO service is deployed
- [x] W5-07  Wire Agent.TV — already wired via agenttv_proxy.py + agenttv_channel.py (lines 602-604, 902-903 in main.py)
- [x] W5-08  Add ABSORBED.md in each source repo
- [x] W5-09  Archive AIO, Agent.TV, Agent-Reach, ase-vault, asemirror originals

---

## WAVE 6 — MEMORY → MINIPAE

- [!] W6-01  iranti — repo not present locally; defer
- [x] W6-02  Create ~/minipae/memory/buzz/ and absorb Buzz content
- [!] W6-03  Triune-Memory — repo not present locally; defer
- [x] W6-04  Create ~/minipae/integrations/supermemory/ and absorb supermemory content
- [x] W6-05  Update ~/minipae/README.md to document all absorbed modules
- [x] W6-06  Nostr kind routing verified correct (kind:30174 in minipae.py; kinds 36000–36003 documented)
- [x] W6-07  Add ABSORBED.md in Buzz + supermemory
- [x] W6-08  Archive Buzz and supermemory originals

---

## WAVE 7 — WALLET CONSOLIDATION → vanity-cloakseed + BIPON39

- [x] W7-01  Create ~/vanity-cloakseed/variants/ and merge Vanity content
- [x] W7-02  Merge vanity (lowercase) into ~/vanity-cloakseed/variants/
- [x] W7-03  Merge vanity-eth-pro into ~/vanity-cloakseed/variants/
- [x] W7-04  Merge vanity2 into ~/vanity-cloakseed/variants/
- [x] W7-05  Merge vanity-check into ~/vanity-cloakseed/variants/
- [x] W7-06  Merge Vanity-eth- into ~/vanity-cloakseed/variants/
- [x] W7-07  Merge Cloakseed into ~/vanity-cloakseed/variants/
- [x] W7-08  Merge bipon39 (lowercase) into ~/BIPON39/
- [x] W7-09  Update ~/vanity-cloakseed/README.md
- [x] W7-10  Archive all merged source repos

---

## WAVE 8 — SECURITY → ZANGBETO

- [x] W8-01  Merge Zangbeto- content into ~/Zangbeto/zangbeto-fork/
- [x] W8-02  Create ~/Zangbeto/scanners/strix/ and absorb strix content
- [x] W8-03  Create ~/Zangbeto/ingestion/tenzir/ and absorb tenzir content
- [x] W8-04  Update ~/Zangbeto/README.md
- [x] W8-05  Add ABSORBED.md in source repos
- [x] W8-06  Archive Zangbeto-, strix, tenzir originals

---

## WAVE 9 — ECONOMY CONSOLIDATION

- [x] W9-01  Create ~/Twelve-thrones/genesis/ and absorb twelve-thrones-genesis
- [x] W9-02  Update ~/Twelve-thrones/README.md
- [x] W9-03  Add ABSORBED.md in twelve-thrones-genesis
- [x] W9-04  Archive twelve-thrones-genesis + twelve-thrones (lowercase) originals

---

## POST-WAVE VERIFICATION

- [x] PV-01  repo-map-final.md written and committed to sovereign-eco-blueprint
- [x] PV-02  Update ~/MASTER_TODO.md with wave completion status
- [x] PV-03  Confirm all STANDALONE repos have README.md
- [x] PV-04  Confirm all CANONICAL repos have absorbed module docs
- [x] PV-05  cargo check sovereign-stack — Finished dev profile (0.87s, clean)
- [x] PV-06  Commit repo-map-final.md + REPO_WAVE_TODO.md → commit 5ee68c9

---

## STANDING CANONICALS (NO ACTION — VERIFY HEALTHY)

Omo-Koda2, Omokoda, omokoda-core, Axiom, OSOVM, ScarabSwarm, Vantage,
Vantage-Voice-, sovereign-stack, Nex-, zerolang, larql, ares_graph,
code-review-graph, Zangbeto, Evil-twin, GuardianPact, minipae, mycelium,
Reticulum, omokoda-mesh, omokoda-mesh-os, freenet-core, OmniRoute, herdr,
herdr-lite-go, oniux, oh-my-pi, peaq-network-node, ares-habitat, ares-control,
If-Script, Koodu, ritual-codex, BIPON39, vanity-cloakseed, Sign-wise,
agent-phone, OpenPhone, Synapse, Twelve-thrones, world-dutch-auctions,
decentralized-tournaments, Portent, ForgeVault, TradingOS, AutoHedge,
Vibe-Trading, FinceptTerminal, Loom, Hyperliquid-Data-Layer-API,
hermes-agent, hermes-trader, organism-core, Sacred-cored-agency,
NeverEndingQuest, arcane-realms, genesis-world, Brahma-Echo,
eternal-orisa-loom-v8, trinity-genesis, SwarmIDE2, NarratorIDE,
ip-layer, ARP, DIP, VCP, UCX
