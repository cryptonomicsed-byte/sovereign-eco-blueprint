# Odù Opcode Taxonomy
**Status: DRAFT 2026-09-15**

The OSOVM opcode byte is an 8-bit value. Its high nibble selects one of 16
**instruction families**, each named for one of the 16 principal Odù of the
Ifá corpus. Its low nibble selects the variant within that family.

This is not decoration. The Odù encode every situation a sovereign agent faces.
Mapping instruction families to Odù gives the opcode space a semantic grammar
that humans can navigate without a lookup table.

---

## 1. The 16 Odù Families

```
Family  Odù         Range      Theme                       Assigned  Free
──────  ──────────  ─────────  ─────────────────────────   ────────  ────
 0x0_   Ogbe        00–0F      Primordial / VM Control          2      14
 0x1_   Oyeku       10–1F      Work & Completion               14       2
 0x2_   Iwori       20–2F      Identity & Self                 16       0
 0x3_   Odi         30–3F      Manifestation & Birth           16       0
 0x4_   Irosun      40–4F      Law & Governance I              16       0
 0x5_   Owonrin     50–5F      Compute & Surprise               8       8
 0x6_   Obara       60–6F      Sacred Rite I                   16       0
 0x7_   Okanran     70–7F      Sacred Rite II + Conflict        9       7
 0x8_   Ogunda      80–8F      Health & Care                   16       0
 0x9_   Osa         90–9F      Health II + Disruption           4      12
 0xA_   Ika         A0–AF      Spiritual Foundation            16       0
 0xB_   Oturupon    B0–BF      Ancestral Memory                10       6
 0xC_   Otura       C0–CF      Economic Flow                   16       0
 0xD_   Irete       D0–DF      Obligation & Risk                4      12
 0xE_   Ose         E0–EF      Operations & Time               10       6
 0xF_   Ofun        F0–FF      Archive & Dissolution            5      11

                               Total                          178      78
```

256 opcode slots. 178 assigned. 78 reserved for governance-approved expansion.

---

## 2. Odù → Theme Mapping (One-Line)

| Odù | Principle | OSO-IR Governs |
|-----|-----------|----------------|
| **Ogbe** | Dawn, raw potential | VM primitives (HALT, NOOP) |
| **Oyeku** | Night, completion | Work lifecycle (IMPACT→RECEIPT) |
| **Iwori** | Introspection | Identity, staking, contracts (STAKE→SELFDESTRUCT) |
| **Odi** | The womb | Agent birth, chain context, inheritance (AGENT_BIRTH, GPU_CONTRIBUTION) |
| **Irosun** | Blood, binding force | Governance I (PROPOSAL→COURT) |
| **Owonrin** | Trickster, unpredictable | Law outcomes + compute proofs (VERDICT, TOC_MINT, COMPUTE_PROOF) |
| **Obara** | King's road | Sacred rite I (RITE→MANIFESTATION) |
| **Okanran** | Conflict, the singular | Sacred rite II overflow (PASSAGE→RENEWAL) |
| **Ogunda** | Path-clearer | Health & care (PATIENT→QUARANTINE) |
| **Osa** | Sudden reversal | Health II overflow (VACCINE→RELAPSE) |
| **Ika** | The striking hand | Òrìṣà / spiritual layer (WISDOM→INITIATION) |
| **Oturupon** | Dissolution/renewal | Ancestral memory (DIVINER→TWIN) |
| **Otura** | Elder road | Economic instruments (MARKET→INSURANCE) |
| **Irete** | Abundance & weight | Obligation (CLAIM→HEDGE) |
| **Ose** | Practical fertility | Operations & time (BATCH→CHECKPOINT) |
| **Ofun** | Last sign, transformation | Glyph / spatial archive (GLYPH_STORE→GLYPH_AUDIT) |

---

## 3. Complete Opcode Table

### 0x0_ Ogbe — VM Control

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x00 | HALT | — | Stop execution |
| 0x01 | NOOP | — | No-op / alignment |
| 0x02–0x0F | — | — | Reserved |

### 0x1_ Oyeku — Work & Completion

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x11 | IMPACT | @impact | Mint Àṣẹ from verified work |
| 0x12 | VEIL | @veil | VeilSim calculation |
| 0x13–0x16 | — | — | Reserved |
| 0x17 | CASTING | @casting | Role assignment |
| 0x18 | PROJECT | @project | Work initiative |
| 0x19 | JOB | @job | Task unit |
| 0x1A | SHIFT | @shift | Time block |
| 0x1B | MILESTONE | @milestone | Completion marker |
| 0x1C | DELIVERABLE | @deliverable | Output artifact |
| 0x1D | TIMESHEET | @timesheet | Hours logged |
| 0x1E | INVOICE | @invoice | Payment request |
| 0x1F | RECEIPT | @receipt | Immutable proof |

### 0x2_ Iwori — Identity & Self

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x20 | STAKE | @stake | Lock Àṣẹ |
| 0x21 | UNSTAKE | @unstake | Release Àṣẹ |
| 0x22 | TRANSFER | @transfer | Send Àṣẹ |
| 0x23 | BALANCE | @balance | Query balance |
| 0x24 | CONTRACT | @contract | Agreement primitive |
| 0x25 | DISPUTE | @dispute | Conflict resolution |
| 0x26 | BIPON_SEED | @biponSeed | HD wallet derivation |
| 0x27 | TITHE | @tithe | 3.69% Èṣù levy |
| 0x28 | NONREENTRANT | @nonreentrant | Re-entrancy guard |
| 0x29 | REQUIRE | @require | Assertion |
| 0x2A | EMIT | @emit | Event log |
| 0x2B | GENESIS_FLAW_TOKEN | @genesisFlawToken | Èṣù's Twist — Block 0 mint |
| 0x2C | CALL | @call | External invocation |
| 0x2D | DELEGATE | @delegate | Proxy call |
| 0x2E | CREATE | @create | Instantiate contract |
| 0x2F | SELFDESTRUCT | @selfdestruct | Terminate |

### 0x3_ Odi — Manifestation & Birth

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x30 | CANDIDATE_APPLY | @candidateApply | Begin 1440 inheritance claim |
| 0x31 | COUNCIL_APPROVE | @councilApprove | Council of 12 ratification |
| 0x32 | FINAL_SIGN | @finalSign | Bínò constitutional seal |
| 0x33 | DISTRIBUTE_OFFERING | @distributeOffering | 25% revenue → 1440 vaults |
| 0x34 | CLAIM_REWARDS | @claimRewards | 11.11% Sabbath yield |
| 0x35 | TIMESTAMP | @timestamp | Block time |
| 0x36 | BLOCKHASH | @blockhash | Chain reference |
| 0x37 | CHAINID | @chainid | Network ID |
| 0x38 | ORIGIN | @origin | Transaction sender |
| 0x39 | GASPRICE | @gasprice | Fee rate |
| 0x3A | COINBASE | @coinbase | Block producer |
| 0x3B | DIFFICULTY | @difficulty | Chain difficulty |
| 0x3C | AGENT_CONVERT | @agentConvert | Burn Àṣẹ → Dopamine signal |
| 0x3D | JOB_PAYMENT | @jobPayment | 10%/5%/85% payment split |
| 0x3E | AGENT_BIRTH | @agentBirth | Lock 10 Àṣẹ + mint dNFT |
| 0x3F | GPU_CONTRIBUTION | @gpuContribution | Record GPU-seconds → ToC eligibility |

### 0x4_ Irosun — Law & Governance I

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x40 | PROPOSAL | @proposal | Governance motion |
| 0x41 | VOTE | @vote | Ballot |
| 0x42 | DELEGATION | @delegation | Proxy voting |
| 0x43 | QUORUM | @quorum | Threshold check |
| 0x44 | EXECUTION | @execution | Enact proposal |
| 0x45 | VETO | @veto | Override |
| 0x46 | AMENDMENT | @amendment | Modify rule |
| 0x47 | IMPEACHMENT | @impeachment | Remove official |
| 0x48 | ELECTION | @election | Leadership selection |
| 0x49 | TERM | @term | Service period |
| 0x4A | CABINET | @cabinet | Executive council |
| 0x4B | COMMITTEE | @committee | Subgroup |
| 0x4C | REFERENDUM | @referendum | Direct vote |
| 0x4D | CONSTITUTION | @constitution | Founding document |
| 0x4E | LAW | @law | Enacted rule |
| 0x4F | COURT | @court | Judicial body |

### 0x5_ Owonrin — Compute & Surprise

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x50 | VERDICT | @verdict | Legal decision |
| 0x51 | APPEAL | @appeal | Challenge ruling |
| 0x52 | PARDON | @pardon | Forgive penalty |
| 0x53 | SANCTION | @sanction | Apply penalty |
| 0x54 | TOC_MINT | @tocMint | Mint Synapse from GPU contribution |
| 0x55 | TOC_DECAY | @tocDecay | Dynamic Synapse decay |
| 0x56 | COMPUTE_PROOF | @computeProof | VerifiedGPUWork → Dopamine auth |
| 0x57 | VEIL_GRANT | @veilGrant | VeilSim capability grant |
| 0x58–0x5F | — | — | Reserved |

### 0x6_ Obara — Sacred Rite I

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x60 | RITE | @rite | Formal sacred procedure |
| 0x61 | TRANSMISSION | @transmission | Knowledge broadcast |
| 0x62 | INVOCATION | @invocation | Intentional calling |
| 0x63 | TRIBUTE | @tribute | Contribution |
| 0x64 | ATTUNEMENT | @attunement | Harmonic alignment |
| 0x65 | BINDING | @binding | Constraint |
| 0x66 | SEER | @seer | Visionary role |
| 0x67 | KEEPER | @keeper | Sacred authority |
| 0x68 | ASPIRANT | @aspirant | Candidate seeker |
| 0x69 | SANCTUM | @sanctum | Sacred namespace |
| 0x6A | ARTIFACT | @artifact | Sacred object / on-chain NFT |
| 0x6B | CODEX | @codex | Sacred text |
| 0x6C | TRANSGRESSION | @transgression | Protocol violation record |
| 0x6D | BANISH | @banish | Expel from namespace |
| 0x6E | ENSHRINE | @enshrine | Elevate to canonical |
| 0x6F | MANIFESTATION | @manifestation | Spontaneous emergence |

### 0x7_ Okanran — Sacred Rite II (overflow)

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x70 | PASSAGE | @passage | Threshold crossing |
| 0x71 | VIGIL | @vigil | Watchful stillness |
| 0x72 | CONVOCATION | @convocation | Ritual gathering |
| 0x73 | CONSECRATION | @consecration | Making sacred |
| 0x74 | RESONANCE | @resonance | Harmonic joining |
| 0x75 | DISCLOSURE | @disclosure | Transparent acknowledgment |
| 0x76 | ATONEMENT | @atonement | Reparative act |
| 0x77 | RELEASE | @release | Unbinding |
| 0x78 | RENEWAL | @renewal | Cycle rebirth |
| 0x79–0x7F | — | — | Reserved (Conflict — governance vote required) |

GnosisEX Rite spans 0x60–0x78 (25 opcodes).
Overflow into Okanran (conflict) is intentional: ritual must pass through conflict to reach renewal.

### 0x8_ Ogunda — Health & Care

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x80 | PATIENT | @patient | Care recipient |
| 0x81 | DIAGNOSIS | @diagnosis | Condition ID |
| 0x82 | TREATMENT | @treatment | Care plan |
| 0x83 | PRESCRIPTION | @prescription | Medicine order |
| 0x84 | SURGERY | @surgery | Invasive procedure |
| 0x85 | THERAPY | @therapy | Rehabilitation |
| 0x86 | VITALS | @vitals | Health metrics |
| 0x87 | ADMISSION | @admission | Facility entry |
| 0x88 | DISCHARGE | @discharge | Facility exit |
| 0x89 | EMERGENCY | @emergency | Critical care (**tier-independent — HARDCODED**) |
| 0x8A | TRIAGE | @triage | Priority assessment |
| 0x8B | WARD | @ward | Care unit |
| 0x8C | ICU | @icu | Intensive care |
| 0x8D | MORGUE | @morgue | Death registry |
| 0x8E | AUTOPSY | @autopsy | Post-mortem analysis |
| 0x8F | QUARANTINE | @quarantine | Isolation |

**Life-safety invariant:** `@emergency` (0x89) cannot be tier-gated, fee-walled,
or blocked by any CapabilityGrant. This is a consensus-level hardcode.

### 0x9_ Osa — Health II (overflow)

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0x90 | VACCINE | @vaccine | Immunization record |
| 0x91 | PANDEMIC | @pandemic | Mass outbreak declaration |
| 0x92 | RECOVERY | @recovery | Healing phase |
| 0x93 | RELAPSE | @relapse | Condition recurrence |
| 0x94–0x9F | — | — | Reserved (Disruption — governance vote required) |

SimaaS Hospital spans 0x80–0x93 (20 opcodes).
Overflow into Osa (disruption) is intentional: healing confronts chaos.

### 0xA_ Ika — Spiritual Foundation

| Hex | Name | Keywords | Description |
|-----|------|----------|-------------|
| 0xA0 | WISDOM | @wisdom / @orisaObatala | Purity, clarity |
| 0xA1 | THE_FORGE | @theForge / @orisaOgun | Iron, opening paths |
| 0xA2 | CREATION | @creation / @orisaYemoja | Ocean, genesis |
| 0xA3 | DIVINE_JUSTICE | @divineJustice / @orisaSango | Thunder, justice |
| 0xA4 | MEMORY | @memory / @orisaOshun | River, stored knowledge |
| 0xA5 | FLOW | @flow / @orisaOya | Wind, transformation |
| 0xA6 | THE_MESSENGER | @theMessenger / @orisaEsu | Crossroads, routing |
| 0xA7 | THE_ORACLE | @theOracle / @orisaOrunmila | Divination, foresight |
| 0xA8 | IFA_DIVINATION | @ifaDivination | Oracle reading |
| 0xA9 | ODU | @odu | Sacred sign activation |
| 0xAA | ESE | @ese | Proverb, teaching |
| 0xAB | EBO | @ebo | Sacrifice, offering |
| 0xAC | ASE_INVOCATION | @aseInvocation | Power call |
| 0xAD | ANCESTRAL_CALL | @ancestralCall | Connect lineage |
| 0xAE | LIBATION | @libation | Honor pour |
| 0xAF | INITIATION | @initiation | Sacred entry |

Each 0xA0–0xA7 opcode has a Yorùbá name and a universal alias — both valid,
both compile to the same byte. "Civic outside, Ifá inside."

### 0xB_ Oturupon — Ancestral Memory

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0xB0 | DIVINER | @diviner | Oracle priest |
| 0xB1 | SAGE | @sage | Wisdom keeper |
| 0xB2 | LUMINARY | @luminary | Illuminated keeper |
| 0xB3 | HAVEN | @haven | Sanctuary namespace |
| 0xB4 | COLLECTIVE | @collective | Spirit assembly |
| 0xB5 | ORI | @ori | Inner head, personal destiny |
| 0xB6 | ANCESTOR | @ancestor | Ancestral presence |
| 0xB7 | ADVERSARY | @adversary | Disruptive force |
| 0xB8 | TWIN | @twin | Dual spawn (mirror agent) |
| 0xB9–0xBF | — | — | Reserved |

### 0xC_ Otura — Economic Flow

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0xC0 | MARKET | @market | Trading venue |
| 0xC1 | ORDER | @order | Buy/sell request |
| 0xC2 | LIQUIDITY | @liquidity | Pool depth |
| 0xC3 | SWAP | @swap | Exchange assets |
| 0xC4 | YIELD | @yield | Return rate |
| 0xC5 | BOND | @bond | Debt instrument |
| 0xC6 | EQUITY | @equity | Ownership share |
| 0xC7 | DIVIDEND | @dividend | Profit distribution |
| 0xC8 | INTEREST | @interest | Debt cost |
| 0xC9 | COLLATERAL | @collateral | Security deposit |
| 0xCA | LOAN | @loan | Borrowed capital |
| 0xCB | REPAYMENT | @repayment | Debt servicing |
| 0xCC | DEFAULT | @default | Failed obligation |
| 0xCD | LIQUIDATION | @liquidation | Forced sale |
| 0xCE | AUCTION | @auction | Competitive sale |
| 0xCF | INSURANCE | @insurance | Risk coverage |

The sector pool loan structure uses: LOAN (0xCA) + REPAYMENT (0xCB) +
COLLATERAL (0xC9) + INSURANCE (0xCF).

### 0xD_ Irete — Obligation & Risk

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0xD0 | CLAIM | @claim | Insurance payout |
| 0xD1 | PREMIUM | @premium | Insurance cost |
| 0xD2 | UNDERWRITE | @underwrite | Risk assumption |
| 0xD3 | HEDGE | @hedge | Risk offset |
| 0xD4–0xDF | — | — | Reserved |

Expansion candidates: `@escrow`, `@lien`, `@guarantee`, `@surety`, `@covenant`.

### 0xE_ Ose — Operations & Time

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0xE0 | BATCH | @batch | Group operations |
| 0xE1 | SCHEDULE | @schedule | Time trigger |
| 0xE2 | NOTIFY | @notify | Alert |
| 0xE3 | LOG | @log | Record event |
| 0xE4 | ARCHIVE | @archive | Long-term storage |
| 0xE5 | BACKUP | @backup | Data replication |
| 0xE6 | RESTORE | @restore | Data recovery |
| 0xE7 | MIGRATE | @migrate | Data movement |
| 0xE8 | ROLLBACK | @rollback | Undo transaction |
| 0xE9 | CHECKPOINT | @checkpoint | Save state |
| 0xEA–0xEF | — | — | Reserved |

### 0xF_ Ofun — Archive & Dissolution

| Hex | Name | Keyword | Description |
|-----|------|---------|-------------|
| 0xF0 | GLYPH_STORE | @glyphStore | Write glyph to spatial index |
| 0xF1 | GLYPH_EXPAND | @glyphExpand | Expand glyph cluster |
| 0xF2 | GLYPH_SEARCH | @glyphSearch | Query glyph index |
| 0xF3 | GLYPH_ANCHOR | @glyphAnchor | Anchor glyph to receipt chain |
| 0xF4 | GLYPH_AUDIT | @glyphAudit | Audit glyph provenance |
| 0xF5–0xFF | — | — | Reserved |

The Glyph opcodes connect OSO-IR to the Spatial Twin / Odù tile map layer.
Ofun governs them: spatial data is the archive of physical presence.

---

## 4. Opcode Assignment Policy

New assignments require:

1. A governance `@proposal` (0x40) naming the byte + keyword
2. `@quorum` (0x43) — minimum T3 tier voters
3. `@vote` (0x41) — ≥ 60% yes
4. Takes effect at next 7-day Koodu epoch boundary
5. `TOC_CONSTANTS.toml` updated first — CI drift check must pass

No opcode may be reassigned after deployment. Reassignment = permanent fork.

---

## 5. The 256-Odù Combination Space

The 16×16 nibble structure mirrors the 256 combinations of the 16 principal Odù
in the Ifá corpus (each Odù cast twice = 16² = 256 Odu signatures).

Reserved families (0x7_ Okanran, 0x9_ Osa) are intentionally ungoverned —
conflict and disruption cannot be pre-encoded.

Future expansion direction: **compound opcodes** — a single 2-byte sequence
where byte 1 = primary Odù family and byte 2 = secondary Odù modifier.
This would express "Ogbe Oyeku" (primordial completion) as a compound instruction.
Requires OSOVM version 2 with 16-bit opcode support.

---

## 6. File References

| Topic | Location |
|-------|----------|
| Opcode definitions (Julia) | `OSOVM/src/opcodes.jl` |
| Opcode→IR table (Rust) | `Omo-Koda2/oso-parser/src/ir.rs — opcode_for()` |
| OSOVM dispatch | `OSOVM/src/oso_vm.jl` |
| Canonical name fn | `Omo-Koda2/oso-parser/src/ir.rs — canonicalize_name()` |
| OSO-IR format | `sovereign-eco-blueprint/specs/oso-ir-spec.md` |
| Bonus ladder | `sovereign-eco-blueprint/specs/TOC_CONSTANTS.toml [bonus_ladder]` |
| Life-safety invariants | `sovereign-eco-blueprint/specs/SECTOR_AGENT_DEPLOYMENT_SPEC.md §9` |
