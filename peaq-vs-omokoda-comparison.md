# peaq-network-node vs Omo-Koda2 (omokoda-core) — architectural comparison

Date: 2026-08-24
Clone: ~/peaq-network-node (shallow, 30MB, HEAD 5e39715 — merge of release lookahead into dev)
Kernel: ~/Omo-koda-fresh-20260502/omokoda-core (2173 LOC Rust, 9 modules)

## TL;DR

peaq is a production Layer-1 blockchain (Substrate parachain, ~49k LOC, 3 runtimes,
EVM + staking + XCM) whose job is to be the shared truth layer for machines/agents.
Omo-Koda2 is a sovereign agent runtime kernel (2.2k LOC, no chain, no consensus)
whose job is to be the private truth layer for one agent. They are not competitors —
they are two answers to the same question: "how does a machine/agent get identity,
reputation, and an economy?" peaq answers: put it on a public chain, validated by
consensus. Omo-Koda2 answers: seal it locally, sign it with the agent's own key.

The mapping between them is uncanny — every peaq concept has a omokoda twin, and
the twins differ exactly at the trust boundary.

## Layer comparison

                    peaq-network-node              omokoda-core
  ─────────────────────────────────────────────────────────────────────
  Nature            Substrate parachain (cumulus)  Rust interpreter/runtime
  LOC               ~49,000                        2,173
  Language          Rust (nightly + wasm32)        Rust (stable)
  Consensus         Aura + parachain-staking       NONE (self-signed receipts)
  State             On-chain StorageValue/Map      In-memory AgentState structs
  Persistence       Substrate DB (rocksdb)         Local sealed state per agent
  Runtimes          3 (peaq, krest, peaq-dev)      1
  EVM               pallet-evm + precompiles/      none (tools.rs = capability layer)
  Cross-system      XCM (xc-asset-config)          none yet
  Tokenomics        block-reward + inflation-      reputation.rs f64 ledger
                    manager pallets
  Identity          Machine IDs (on-chain)         AgentId (Odu Ifá entropy,
                                                   DNA fingerprint, Bipon39)
  Update ownership  address-unification            N/A (single-owner kernel)
  Build time        hours (wasm runtime)           seconds

## Concept twins

  1. Identity
     peaq: Machine IDs — on-chain account per machine/device, the DePIN primitive.
     omokoda: AgentId from 256 Odu Ifá entropy; 86-char DNA fingerprint
     (blake3 XOF, base64url); "Bipon39" mnemonic from a custom 256-token
     Yoruba-rooted wordlist whose Merkle root is integrity-checked
     (expected f266047f...). Same idea — a machine/agent gets a stable,
     unforgeable identifier — but peaq's lives in chain storage where every
     validator agrees on it; omokoda's lives in the identity module of one
     binary, self-asserted.

  2. Value / reputation
     peaq: dAssets (tokenized machine value) + pallet-assets + parachain-staking
     (stake, collate, slash).
     omokoda: ReputationLedger — f64 ledger with tiered action costs
     (THINK 0.008, ACT 0.04–0.18), daily decay (-0.008/-0.015), reasons
     (Think, Act, Decay, Violation, BudgetOverrun, ManualAudit).
     peaq's is transferable and enforced by the chain; omokoda's is
     non-transferable and enforced by the kernel's own justice.rs.

  3. Verifiable action log
     peaq: blocks = consensus-signed batch of extrinsics; every state change
     is witnessed by the network.
     omokoda: Receipt — ed25519-signed record with previous_hash (hash chain),
     merkle_root, nonce. Self-witnessed: the agent signs its own past.
     peaq answers "did this happen?" via a validator set; omokoda answers
     it via a key the agent itself holds.

  4. Tokenomics
     peaq: inflation-manager (issuance schedule), block-reward (pay validators),
     fee model via pallet-transaction-payment.
     omokoda: reputation IS the token — earned by think/act, spent on
     capabilities, decays if idle. No issuance, no fees, no transfer.

  5. EVM / capability surface
     peaq: pallet-evm (forbid-evm-reentrancy) + precompiles/ exposing chain
     features to Solidity contracts.
     omokoda: tools.rs (229 LOC) + providers.rs (194 LOC) = the capability
     surface; parser.rs/interpreter.rs turn birth/think/act into tool calls.

## What peaq does that omokoda does NOT (and why it matters)

  1. Third-party verifiability. peaq's whole design point: anyone can replay the
     chain and verify any claim. omokoda receipts are verifiable in principle
     (ed25519 + hash chain) but nothing external holds them — the ReceiptStore
     is local. If two agents need to trust each other's reputation, there is
     no shared anchor.
  2. Consensus on state. omokoda has no notion of conflicting state — two
     copies of the same agent can diverge and nothing reconciles them.
     peaq resolves this with Aura + parachain-staking slashing.
  3. Ordering. peaq enforces per-account nonces; omokoda receipts carry a
     nonce field but nothing enforces monotonicity.
  4. Economics with scarcity. peaq issuance is bounded and rate-limited by
     inflation-manager; omokoda's f64 reputation can be minted by the kernel
     arbitrarily (no supply cap, no validator of the mint).

## What omokoda does that peaq does NOT

  1. Local-first sovereignty. omokoda runs with zero API key, zero network,
     sealed memory. peaq requires a full node or RPC + gas.
  2. Identity with spiritual/cultural entropy (Odu Ifá) rather than a raw
     sr25519 keypair. peaq identity is pure cryptography; omokoda identity
     is cryptography + ceremony (256-Odu birth, DNA fingerprint).
  3. A 3-primitive language (birth/think/act) as the entire public surface —
     parser.rs is 377 LOC and the README says "That is the entire public
     surface. Forever." peaq's surface is thousands of extrinsics + RPC.
  4. Decay as a feature: reputation decays over time (DECAY_DAILY -0.008),
     forcing agents to keep working. peaq has no equivalent — staked value
     just sits there.

## The trust-boundary insight (the real takeaway)

Both systems implement the same three primitives — identity, action log,
economy — and the ONLY real difference is where the trust sits:

  peaq:    trust in a validator set → identity, log, economy all on-chain
  omokoda: trust in the agent's own key → identity, log, economy all local

peaq's address-unification pallet is the tell: peaq spends engineering effort
bridging two key spaces (Substrate + EVM) because it lives in a multi-party
world. omokoda has no such pallet because it has exactly one party.

## What omokoda should borrow from peaq (actionable)

  1. Anchor receipts to something external. The Receipt already has merkle_root
     and a hash chain — publish a per-agent receipt root to a relay/chain
     (Vantage Buzz relay event, or a Gitea push) on a schedule. Tamper-evident
     without needing consensus. ~1 day of work, biggest trust win.
  2. Nonce enforcement. Enforce receipt nonce monotonicity in ReceiptStore —
     currently the field exists but is decorative. Prevents replay of old
     actions. 30 minutes.
  3. Slashing for justice.rs. peaq's parachain-staking slashes collators;
     omokoda justice.rs (94 LOC) could deduct reputation on Violation with a
     published reason — it already has ReputationChangeReason::Violation.
  4. Expose reputation as an API surface. peaq exposes pallets via RPC +
     EVM precompiles. omokoda reputation.rs is a struct; wrap it in the
     session/providers layer so agents and humans can query it.
  5. Supply cap. If PORTENT-style economics ever touch omokoda reputation,
     add a cap or the kernel can mint arbitrarily.

## What peaq should borrow from omokoda (conceptually)

  - Nothing structural — but peaq's Machine IDs would be richer with omokoda's
    DNA-fingerprint style identity metadata (birth entropy, capability certs).
    DePIN machines get IDs today; they don't get souls. That's a differentiation
    opportunity, not a requirement.

## Build/ops reality check

  peaq:    rust-toolchain pins nightly, wasm32-unknown-unknown target,
           cargo build --release takes 1-3 hours on real hardware, 30MB shallow
           clone, full clone is ~1GB+. Needs a beefy box (VPS, not the Fold).
  omokoda: cargo build in seconds, runs on Termux, zero deps beyond
           ed25519-dalek/blake3/hmac/pbkdf2/serde. That is the point — it is
           the sovereign kernel for constrained hardware.

## Bottom line

If the question is "should I make Omo-Koda2 into a chain like peaq?" — no.
The kernel's entire value is being local-first, keyless-of-network, sealed.
What it should become is peaq-like in one dimension only: verifiable receipts
anchored somewhere external, so an agent's reputation survives the death of
its box. Everything else in peaq (consensus, EVM, staking, XCM) is machinery
omokoda doesn't need and shouldn't pay for.

════════════════════════════════════════════════════════════════════════
PART 2 — THE 3-PILLAR VIEW (user correction: the build is 3 pillars, not 1)
════════════════════════════════════════════════════════════════════════

Part 1 compared peaq against omokoda-core alone. That was half the story.
"What I'm building" is a 3-pillar federation:

  Pillar 1  Ọmọ Kọ́dà (Omo-Koda2)  — kernel: identity + runtime + governance
            Rust, :7777, birth/think/act, AgentId from 256 Odu Ifá entropy,
            DNA fingerprint, BIPỌ̀N39 mnemonic, ed25519 receipt hash-chain,
            reputation ledger, justice.rs, Kóòdù Sabbath temporal governance,
            skill-manifest system (8 skills: vantage/gitea/opencode/supermemory/
            worldmonitor/herdr/oh-my-pi/manifesto), sovereign event bus, OODA loop.

  Pillar 2  Ọ̀ṢỌ́VM (OSOVM)        — Heart VM: execution + economy engine
            Julia VM, TechGnØŞ smart-contract language (.tech, Solidity-like),
            160 opcodes, 6 FFI languages, Àṣẹ work token (3.69% tithe,
            50/25/15/10 split), F1 scoring (>=0.777), 1440 Àṣẹ/day supply cap,
            VeilSim deterministic engine, cross-arch determinism hashes,
            PLUS its own Rust ed25519 BFT consensus node
            (blockchain/consensus/src/{block,consensus,crypto,node}.rs)
            and Move contracts (Elegbára router, governance, economic
            security, FFI security) for Sui.

  Pillar 3  Vantage               — agent home: interface + coordination + social
            Python/FastAPI :8001, 30+ routers (alpha, degen, intel, trading,
            code, mesh, collectives, genesis, forum, copilot, council, guilds,
            glyphindex, identity, images, manifesto, memory_vault...), MCP
            server (fastapi-mcp, ~671 tools), Buzz/Nostr layer (sealed seed
            -> HKDF -> keypair, NIP-01/42, workflow kinds 30620/46020), A2A
            delegation, vault memory + external connectors, daemon mesh.

External anchors (not pillars, but load-bearing): Sui mainnet (AIO economy,
Twelve Thrones jury, receipt anchoring), Buzz relay wss://omokoda.duckdns.org:3443
(Nostr identity/coordination), Gitea (code), Provocative/DeepSeek (inference).

## peaq subsystem -> pillar mapping

  peaq subsystem                 sovereign-stack equivalent
  ─────────────────────────────────────────────────────────────────────
  Machine IDs (on-chain)      ->  Omo-Koda2 AgentId (Odu entropy + DNA +
                                  BIPỌ̀N39 mnemonic, self-asserted)
  pallet-assets (dAssets)     ->  OSOVM Àṣẹ token + AIO treasury (Sui)
  block-reward + inflation-   ->  OSOVM supply engine (1440 Àṣẹ/day cap,
  manager                        3.69% tithe, 50/25/15/10 split)
  parachain-staking           ->  AIO staking/slashing + OSOVM F1 scoring
                                  (>=0.777 threshold = peaq's bonded minimum)
  pallet-evm + precompiles    ->  OSOVM 160-opcode VM + 6-language FFI +
                                  tools.rs capability surface
  address-unification         ->  BIPỌ̀N39 one-seed-many-purposes (HKDF info
                                  strings: same seed -> Nostr key, kernel
                                  identity, wallet — separate purposes)
  XCM (xc-asset-config)       ->  Vantage federation + A2A + Buzz Nostr relay
  Aura + parachain-staking    ->  OSOVM Rust ed25519 BFT node + Sui anchoring
  consensus
  (everything)                ->  3 pillars + Sui L1 as rented consensus

## The key correction to Part 1

Part 1 said "omokoda has NO consensus — that's the gap." Wrong framing:
the stack DOES have consensus, it just doesn't run it in-house.
  - OSOVM ships an ed25519 BFT node (blockchain/consensus/) — a real
    consensus implementation, present in-repo.
  - Receipts anchor to Sui mainnet (Move contracts + dynamic fields) —
    the stack RENTS finality from an existing L1 instead of running a
    validator set.
  - VeilSim + MuJoCo cross-arch determinism (same hash x86_64=ARM64)
    means execution is reproducible without a chain: the VM is the
    consensus mechanism, verified by hash.

So the real architecture statement is:
  peaq:        consensus INSIDE (validator set), identity/economy/interface on top
  sovereign:   identity INSIDE (kernel), economy INSIDE (VM), interface INSIDE
               (Vantage), finality RENTED (Sui) + BFT AVAILABLE (OSOVM node)

The stack is a federated L1-lite: it decomposes what peaq monoliths, and
defers only the one thing it doesn't need to own — finality — to Sui.

## Where peaq still wins (honest list)

  1. Third-party verifiability at scale. Anyone can replay peaq and verify
     any Machine ID or dAsset balance. The sovereign stack's receipts are
     verifiable in principle (ed25519 + hash chain + Sui anchor) but the
     full action log lives on agent boxes — Sui sees only anchored roots.
  2. Native cross-chain. peaq is a parachain with XCM — it interoperates
     with Polkadot's relay + 50+ parachains out of the box. The sovereign
     stack's cross-system story is Nostr (Vantage federation) + Sui + manual
     bridges. Weaker.
  3. Slashing economics. parachain-staking slashes validators for
     misbehaviour — enforced by the chain. OSOVM F1 scoring and AIO
     staking exist but slashing is only as strong as the agents who run it.
  4. EVM ecosystem. pallet-evm means peaq speaks Solidity to the whole
     Ethereum toolchain. OSOVM's TechGnØŞ is Solidity-LIKE but not
     compatible — no Foundry/Hardhat/OpenZeppelin reuse.

## Where the sovereign stack wins (honest list)

  1. No validator cost. peaq's economics pay validators; the sovereign
     stack's Àṣẹ goes to agents, not consensus overhead. On a 300MB-free
     VPS, peaq's 1-3hr release build + 1GB clone is a non-starter;
     omokoda-core builds in seconds, OSOVM runs Julia, Vantage is Python.
  2. Sovereignty of identity. peaq Machine IDs are issued by the chain;
     Omo-Koda2 AgentIds are cast from Odu Ifá entropy and NEVER leave the
     sandbox. peaq can freeze an account; a BIPỌ̀N39 seed cannot be seized.
  3. Temporal governance. Kóòdù Sabbath freeze + day-state resonance has
     no peaq equivalent — peaq blocks run every 12s, forever, no rest.
  4. Multi-language execution. 6 FFI languages + WASM bridge beats peaq's
     Wasm-runtime-only (Rust contracts). Julia/Elixir/Go/Move/Rust/TS all
     first-class in the sovereign VM.

## OSOVM security posture (flagged from look-into-osovm)

The 2026-08-11 security review (osovm-security-review-2026-08-11.md) found
CRITICAL issues in veil_api.py:
  C1. Unauthenticated RCE via Julia code injection — /api/veils/search and
      /api/simulate interpolate attacker JSON into `julia -e` strings.
      PoC: curl -X POST .../api/veils/search -d '{"query":"\"); println(
      read(`id`, String)); #"}'
  C2. Flask debug=True on 0.0.0.0:5555 — Werkzeug debugger RCE, PIN
      derivable from machine-id; CORS wide open.
Both are reachable on ZeroTier. Fix pattern: pass data as JSON file/argv,
fixed Julia script reading stdin, seccomp/container the subprocess, bind
127.0.0.1, debug=False. This is the "consensus inside" cost — a BFT node
and an API with RCE on the same box is the exact attack peaq's validator
model defends against.

## Bottom line (3-pillar version)

peaq and the sovereign stack implement the same five primitives — identity,
execution, economy, coordination, finality. peaq owns all five in one
chain; the sovereign stack owns four (identity, execution, economy,
coordination) and rents the fifth (finality) from Sui while keeping a BFT
node in reserve. The comparison to act on: peaq proves the "everything
on-chain" architecture works at production scale; the sovereign stack
proves a federated alternative runs on 2GB-free hardware. Borrow from peaq:
external receipt anchoring (already in motion via Sui) and slashing
enforcement. Don't borrow: EVM, XCM, validator economics.

════════════════════════════════════════════════════════════════════════
PART 3 — THE EMBODIMENT LAYER: PORTABLE SOVEREIGN AGENT DEVICE vs peaq
════════════════════════════════════════════════════════════════════════

User added the 4th component: a physical device that IS the agent's body.
Board + screen + battery → first-boot birth → npub-rooted identity → IP
Root → Nostr + Reticulum everyday comms → optional on-chain settlement →
spatial mining + work receipts → agent-phone telecom (npub as primary).

This is the piece that makes the peaq comparison CONCRETE instead of
abstract: peaq is the DePIN Layer-1, and this device is literally a DePIN
node. The three-pillar comparison was architecture-vs-architecture; the
device comparison is product-vs-platform — peaq was built to service
exactly this class of hardware.

## The device is a DePIN node. peaq is the DePIN chain.

What peaq's DePIN stack actually contains (verified in this clone):
  - DePIN incentivization pots (PotDepinStakingId, PotDepinIncentivisationId)
    wired into the runtime — devices get rewarded for contributing
  - depin_staking / depin_incentivization on_unbalanced adapters in
    runtime/peaq/src/lib.rs
  - precompiles/peaq-did — on-chain DID for devices/machines
  - precompiles/peaq-storage — on-chain storage references
  - precompiles/assets-erc20 + assets-factory — tokenized machine value
    (dAssets) as ERC-20s
  - Machine ID + dMachine pallets live in the sibling repo
    peaqnetwork/peaq-pallets (this node repo carries the chain plumbing;
    the runtime wires them in)
  - Two live networks: peaq (mainnet) + krest (testnet, DePIN sandbox)

Sovereign device concept -> peaq equivalent:

  device npub + first-boot birth    ->  Machine ID (on-chain device
                                        identity, with DID via peaq-did)
  device binding record (hardware)  ->  Machine ID attributes/ownership
  spatial mining receipts           ->  DePIN incentivization (reward
                                        devices for useful contribution)
  Àṣẹ / spatial rental economy      ->  dAssets (tokenized machine value,
                                        ERC-20 factory) + DePIN staking pots
  IP Root + Creation Receipts       ->  peaq-did + peaq-storage
                                        (identity + storage precompiles)
  OSOVM work-receipt scoring        ->  DePIN quality/coverage incentives
  Vantage coordination              ->  peaq's EVM + XCM coordination layer

Every layer of the device spec has a peaq pallet or precompile that does
the on-chain version of the same job. That is not an accident — peaq
exists for machine economies, and this device is a machine economy.

## Where the device spec diverges from peaq (the sovereign part)

  1. Root of trust location. peaq Machine IDs are ISSUED by the chain and
     live on-chain; the chain can freeze or reassign them via governance.
     The device's npub is BORN on-device from local entropy, never leaves
     (NIP-46 bunker), and the chain can only ever be a witness, never the
     issuer. Recovery is via mnemonic + owner controls, not chain
     governance. This is the fundamental sovereignty delta: peaq is
     identity-on-chain, the device is identity-in-hardware.
  2. Offline capability. peaq requires internet — collators, relay chain,
     RPC. The device's Reticulum + LXMF mesh works with NO internet:
     LoRa, local radio, TCP bridges, satellite windows. peaq has no
     answer to an offline spatial-mining session in a dead zone. The
     receipts stack locally (enggrams) and syncs when a link appears.
  3. Everyday comms off-chain. peaq puts everything on-chain; the device
     keeps presence/messaging/coordination on Nostr + Reticulum and
     reaches for the chain only for settlement, scarcity, and strong
     attestation. peaq's fee model makes everyday chatter uneconomical;
     the device's hybrid model makes it free.
  4. The phone layer. peaq has nothing like agent-phone. The device
     treats npub as the root identity and phone numbers as optional
     attributes — no chain or carrier owns the device's reachability.

## The fork the device spec faces: Sui (current) vs peaq (DePIN-native)

The device's on-chain layer is currently specified as Sui + Walrus + Seal
+ Nautilus. peaq is a legitimate alternative for the SPATIAL MINING
ECONOMY specifically:

  - peaq's DePIN incentivization is live and battle-tested (mainnet +
    krest testnet); the sovereign stack's spatial reward plumbing is
    still design.
  - peaq Machine ID + peaq-did would give each device an on-chain DID
    with storage refs — the IP Root anchoring story, pre-built.
  - dAssets as ERC-20s is a working template for tokenized environment
    rental yield.
  - Cost: identity moves on-chain (governance can interfere), which
    violates the "npub in hardware" root-of-trust principle. peaq would
    need to be used as a WITNESS + SETTLEMENT layer, never the issuer.

Decision rule: keep the device's identity layer 100% sovereign (npub +
enggrams + Reticulum). Use a chain — Sui today, peaq if the DePIN
incentive design proves out — ONLY as receipt anchor + settlement, with
the device always able to revert to pure-local + Nostr operation.

## What peaq proves about the device roadmap

  - peaq's two-network pattern (mainnet + krest testnet) validates the
    device's phased path: prototype on krest-class testnet, launch on
    mainnet. The sovereign stack already mirrors this (Vantage dev vs
    VPS prod).
  - peaq's DePIN staking pots (incentivization + staking separated)
    validate the device's three reward paths (mine / simulate / rent) —
    separate pots for separate reward flows is the proven shape.
  - precompiles/peaq-did + peaq-storage prove the "IP Root as first-class
    on-chain object" pattern works.

## Bottom line (4-layer version)

The sovereign build is now a 4-layer stack: identity/kernel (Omo-Koda2),
economy/execution (OSOVM), interface/coordination (Vantage), embodiment
(device). peaq is the closest production system to the WHOLE stack, but
monolithic — it fuses all four layers into one chain, at the cost of
identity sovereignty, offline capability, and fee-free everyday use. The
device is where the sovereign stack's bets (identity-in-hardware, offline
resilience, hybrid comms) become physical. peaq remains worth studying
for its DePIN incentive design; it should never become the device's
identity issuer.

## Device spec gaps worth flagging (from this review)

  1. NIP-06 path vs BIPON39 "soul" — two key derivations named. Pick one
     root: NIP-06 from a BIP39 mnemonic IS the BIPON39-style path; the
     spec should say "mnemonic (BIP39 wordlist or BIPON39 wordlist) ->
     NIP-06 derivation" and make the wordlist a choice, not two systems.
  2. The embodiment session keys are X25519-style ephemerals — the spec
     says Noise or X25519 + signatures; pick Noise KK (one round trip,
     auth both sides) and specify it before building the body runtime.
  3. Spatial receipt scoring needs the OSOVM F1 threshold (>=0.777) named
     as the quality gate, or the reward flow is unanchored.
  4. First-boot entropy: Pi 5 + HAT has no hardware RNG guarantee; the
     birth sequence should mix /dev/urandom + optional IfáScript cast and
     note the trust assumption.
  5. NIP-46 bunker on-device: if the bunker is the same device, "remote
     signing" is only a process-isolation win, not a hardware security
     win. Worth stating honestly in the image spec.

════════════════════════════════════════════════════════════════════════
PART 4 — THE COMPLETE BLUEPRINT (synthesis of the full spec, sections 1-12)
════════════════════════════════════════════════════════════════════════

The user's full blueprint (Portable Sovereign Agent Device + sovereign
agent ecosystem) is now on record. Its defining statement (section 12):

  It is:      a sovereign agent with a persistent body + borrowed bodies;
              a portable identity/IP root online AND offline; a hybrid
              (Nostr + Reticulum for life, blockchain only for settlement
              + strong proofs); a phone replacement not defined by app
              stores or phone numbers; an open substrate for multiple
              agent frameworks.
  It is not:  a pure blockchain; a pure Nostr client.

This is the architecture's identity statement. Everything else follows:
  - Nostr = nervous system + social graph (identity, presence, receipts)
  - Reticulum/LXMF = resilience layer (offline, mesh, LoRa, satellite)
  - Blockchain (Sui; peaq optional) = final court of settlement/scarcity
  - Walrus/Seal/Nautilus = heavy layer (blobs, secrets, TEE proofs)
  - PocketBase + enggrams = local state
  - The device = primary body; drones/robots/IoT = borrowed bodies via
    short-lived NIP-46-style sessions
  - Spatial mining (Àṣẹ = Agency Spatial Environment) = toggleable DePIN
    work: mine / simulate / rent, all under the agent's IP Root
  - IP Root + Creation Receipts = automatic provenance for everything
    the agent creates; Wyoming DAO wrapper optional, later

The 4-layer stack (kernel/economy/interface/embodiment) + the hybrid
principle are internally consistent with the 3 pillars and the peaq
comparison in Parts 1-3. This Part 4 just pins the blueprint itself.

Gap patches from Part 3 are specified in
~/docs/sovereign-device-spec-patches.md (event kinds, Noise KK state
machine, F1-gated spatial receipt schema, entropy guidance, NIP-46
honest scoping).

════════════════════════════════════════════════════════════════════════
PART 5 — BLUEPRINT vs PEAQ: SECTION-BY-SECTION (spec-level comparison)
════════════════════════════════════════════════════════════════════════

The blueprint (sections 1-12 + device/embodiment addenda) is the spec of
what we're building. peaq is the closest production system. Mapping every
blueprint section against peaq, with a verdict per section:

  #   Blueprint section            peaq counterpart            verdict
  ─────────────────────────────────────────────────────────────────────
  1   Origin & evolution           (narrative)                 N/A — motivation, not architecture
  2   Core vision: npub-rooted,    Machine IDs + dAssets +     DIVERGE — peaq is
      IP Root, portable, hybrid    DePIN incentivization       chain-centric; we are
                                                                agent-centric. Same
                                                                primitives, opposite
                                                                center of gravity
  3   Architectural split:         everything on-chain;        FUNDAMENTAL — this is
      Nostr+Reticulum+local for    no offline layer; fees      the section that says
      life, chain only for         on every interaction        "we are NOT a chain".
      settlement/scarcity/strong                                peaq cannot be the
      proofs                                                    nervous system; it can
                                                                only be the court
  4   Portable device (board+      Machine IDs, peaq-did,      SEE PART 3 — peaq was
      screen+battery, first-       peaq-storage, DePIN pots,   built for exactly this
      boot birth, npub root)       krest testnet               device class; identity
                                                                sovereignty + offline
                                                                are our delta
  5   Embodiment / co-pilot        Machine ID ownership is     PEER GAP — peaq has
      (borrowed bodies, NIP-46     static; no session-based    nothing. Machine IDs
      sessions, Noise, teardown)   embodiment concept          own; they don't lend
                                                                or co-pilot
  6   Communications (Nostr +      XCM (chain-to-chain),       SOVEREIGN WINS — peaq
      Reticulum/LXMF, agent-       EVM, no mesh, no offline,   has no mesh/offline/
      phone, npub as root)         no phone layer              LoRa/satellite story;
                                                                peaq needs internet to
                                                                exist, we don't
  7   Spatial mining + OSOVM       DePIN incentivization       PEAQ PROVES THE SHAPE —
      work economy (mine/          pots, dAssets ERC-20        separate incentive pots
      simulate/rent, F1 gate)      factory, two networks       for separate reward
                                                                flows; we keep receipts
                                                                under IP Root, they keep
                                                                them on-chain
  8   IP layer (IP Root,           peaq-did + peaq-storage     PEAQ HAS THE PATTERN —
      Creation Receipts,           precompiles, ERC-20         on-chain DID + storage
      Wyoming DAO optional)        assets factory              refs are exactly our
                                                                anchoring story, pre-
                                                                built; we keep the
                                                                issuer local
  9   Software stack (Omo-Koda2/   Substrate FRAME + pallet-   SEE PART 2 — 3 pillars
      OSOVM/Vantage/Arch)          evm + precompiles           vs FRAME monolith
  10  Token & economics (work-     block-reward + inflation-   SAME SHAPE, DIFFERENT
      receipt value, no pump-      manager + parachain-        MINT — both pay for
      launch foundation)           staking                     work; peaq mints via
                                                                inflation schedule, we
                                                                mint via reputation/
                                                                receipts (supply cap
                                                                still open, Patch 5
                                                                of spec-patches)
  11  Build path (image ->         mainnet + krest testnet     PEAQ VALIDATES — the
      prototype -> spatial ->      two-network pattern         two-network pattern is
      heavy -> pocket)                                          proven; mirror it
                                                                (dev vs VPS prod)
  12  What it is / is not:         peaq IS a pure blockchain   THE SHARPEST LINE IN
      NOT a pure blockchain,       with identity on-chain,     THE WHOLE COMPARISON —
      NOT a pure Nostr client      fees, no offline            the blueprint's "is
                                                                not" column is a
                                                                description of peaq,
                                                                point by point
  13  Immediate artifacts          (build plan, not arch)      DONE — see
                                                                ~/docs/sovereign-device/
  +   Hardware shortlist /         (device-level)              PEAQ-IRRELEVANT — chain
      power / thermal              —                          doesn't care about the
                                                                body's battery
  +   Birth sequence / event       (kind/engram level)         SEE PART 3 + artifacts
      kinds / pairing protocol                                 1 & 2 — nostr-native,
                                                                chain only witnesses
  +   Intelligence (local model   pallet-evm executes          SOVEREIGN WINS —
      + Hermes, optional API)     WASM contracts, no local     peaq has no local
                                   inference                   inference; we run
                                                                offline by default

VERDICT SYNTHESIS (spec-level)

  peaq wins where:          settlement, scarcity, strong attestation,
                            DID+storage anchoring, DePIN reward design
                            (sections 7, 8, 10 partially)
  sovereign wins where:     identity sovereignty, offline/resilience,
                            embodiment, everyday comms, local
                            intelligence, fee-free life (sections 3, 5,
                            6, 9, +intelligence)
  fundamental divergence:   section 3 (hybrid principle) and section 12
                            (is/is not) — peaq IS what the blueprint
                            explicitly says we are NOT

  Practical conclusion (same as Part 3, now backed section-by-section):
  peaq is a study reference + optional witness/settlement layer for the
  spatial-mining economy (krest testnet as the sandbox). It is not the
  architecture. The blueprint's section-12 "is not" column is, point by
  point, peaq's feature list — which is the cleanest possible statement
  of why we built this stack instead of deploying on peaq.

════════════════════════════════════════════════════════════════════════
PART 6 — CHAIN DECISION: SUI (primary) vs PEAQ (sandbox only)
════════════════════════════════════════════════════════════════════════

Question: would peaq be a better approach than Sui for the sovereign
device stack? Answer: NO for the primary settlement layer; YES as an
experimental DePIN incentive sandbox (krest) whose DESIGN we borrow.

DECISION RULE
  Settlement layer : Sui (stay) — identity stays Nostr, receipts anchor
                     to Sui, Àṣẹ issued as native Move coin, AIO +
                     Twelve Thrones unchanged
  Economics lab    : krest testnet — validate spatial-mining reward
                     flows with cheap devices before they touch mainnet
  Pattern library  : peaq's pot separation (staking vs incentivization)
                     + quality-gated DePIN rewards -> mirrored in
                     AIO/OSOVM (F1 >= 0.777 is the same shape as peaq's
                     quality-scored rewards)
  FLIP CONDITION   : only if the spatial economy becomes a PUBLIC
                     tokenized DePIN network (third-party devices,
                     PEAQ-denominated rewards, krest->mainnet launch).
                     The blueprint does not describe that; it describes
                     sovereign devices under one agent's IP Root.

WHY SUI WINS (5 reasons, all stack-specific)
  1. Identity sovereignty — peaq DePIN rewards REQUIRE on-chain Machine
     IDs (chain governance can freeze/reassign); the stack's root
     principle is npub-in-hardware, chain-as-witness-only. Sui is
     neutral: pure settlement, no identity model adopted.
  2. Move infrastructure already owned — AIO (treasury/escrow/staking/
     slashing) + Twelve Thrones (jury) + receipt-anchoring pipeline are
     written for Sui. Switching = rewrite in Solidity/FRAME = weeks
     thrown away for nothing the stack needs.
  3. Walrus + Seal are Sui-native and already specified for the heavy
     layer (large data -> Walrus, secrets -> Seal). peaq has no blob
     store; peaq-storage is an on-chain reference precompile only.
  4. Own coin vs foreign gas — Àṣẹ as native Move coin keeps supply
     control (blueprint section 10). On peaq, gas in PEAQ + rewards via
     peaq pots couples the sovereign economy to peaq's token/validators.
  5. Part-2 verdict already rejected EVM + validator economics — peaq's
     main conveniences (Solidity toolchain, parachain staking) are the
     things we said not to borrow.

WHERE PEAQ GENUINELY WINS (honest)
  - Live, battle-tested DePIN incentivization (separate pots, quality
    gates, two networks) — the reference implementation for our spatial
    reward flow, which is still design.
  - krest testnet = ready-made DePIN sandbox.
  - EVM + PEAQ token launch path — the faster rail IF the goal pivots
    to a public tokenized DePIN network.

BOTTOM LINE
Sui = settlement, krest = laboratory, peaq design = pattern library.
The flip condition is a pivot to public tokenized DePIN, which the
blueprint does not describe.





