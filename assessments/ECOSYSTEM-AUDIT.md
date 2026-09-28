# AUDIT — "The Sovereign Ecosystem — Complete Flow" (pasted doc, 2026-09-23)

Method: every checkable claim verified against source (repo code, git history, live VPS) —
not against other docs. Buckets: CONFIRMED / CORRECTED / UNVERIFIABLE.

---

## THE DECISIVE FINDING — ase_rewards.py

The doc's closing line was: *"Now fixing ase_rewards.py — the current version still has UCX
relay logic which is wrong per the ecosystem model."*

**That fix is already written, and it is sitting UNCOMMITTED in the working tree.**

```
$ git log --oneline -2 -- backend/app/ase_rewards.py
4c792ec  fix(blocksim): remove local ASE mint — Blocksim is a receipt relay, not a mint authority
983bfad  feat(blocksim): E-47 — ASE reward minting for verified simulation work

$ git status --short
 M backend/app/ase_rewards.py      <-- 166 lines changed, uncommitted
 M backend/app/chain_service.py
 M backend/app/main.py
```

So the claim is **true of HEAD and false of the working tree**:

- **HEAD (committed)** — the file was `"Verified SimReceipt relay to Vantage UCX broker"`,
  containing `POST {VANTAGE_URL}/api/ucx/ase-mint` and `POST {UCX_BROKER_URL}/api/ucx/ase-mint`,
  with a fail-open path that recorded "pending" when neither URL was set. That is the UCX
  relay logic the doc says is wrong. Correct: it *was* wrong.
- **Working tree (uncommitted)** — all of it is gone. `urllib.request` import dropped, the
  `SimReceiptSubmission` dataclass replaced by `SimReceiptAttestation`, no outbound HTTP
  anywhere. The module now verifies (`osovm_proof` + `gpu_seconds > 0` + `zangbeto_anchor`
  when `ZANGBETO_URL` is set) and writes one SQLite row. Docstring: *"This module records
  proof that simulations occurred. Nothing more."*

**Why this matters more than the claim itself:** finished work that isn't committed is
invisible to every other agent, every audit, and every clone. The comment at the top of the
file even removes the old "fail-open" language, so nobody reading HEAD will know a rewrite
exists. Commit it (after the one correction below).

### The one bug the rewrite introduces

The new docstring says: *"OSOVM runs DOPAMINE_MINT opcode at 1 ASE/min (1440/day)."*

**`DOPAMINE_MINT` is not a registered OSOVM opcode.** In `OSOVM/src/opcodes.jl` —
`CORE_OPCODES` + `EXPANSION_OPCODES` merged into `OPCODE_MAP` — there are **177 distinct
opcode symbols and zero hits for `DOPAMINE_MINT` or `ASE_MINT`**. The only mint in the
registry is:

```
:TOC_MINT => 0x54,  # @tocMint - Mint Synapse tokens from accumulated GPU contribution
```

`dopamine_mint` appears in `vm_core.jl` only as an untyped metadata bag
(`s.metadata[:pending_dopamine_mints]`) — a pending-ledger field, not an opcode.

So the docstring (and the pasted doc) both name a non-existent opcode. It is right about the
*mechanism* (OSOVM is the mint authority, 1/min) and wrong about the *identifier*. Fix the
name before committing, or Blocksim will document a ritual that does not exist.

### The claim it implies but shouldn't

The doc says: *"Nothing outside OSOVM mints ASE — not Blocksim, not Vantage, not Omo-Koda2."*

True for **Àṣẹ**. Not true in general: `Vantage/backend/routers/ucx.py` is a live router with

```
POST /api/ucx/dopamine/mint               — Credit Dopamine from VerifiedGPUWork
POST /api/ucx/dopamine/decay              — Apply 1%/day decay
POST /api/ucx/synapse/burn                — Burn 10 Dopamine → 1 Synapse
```

Vantage mints **Dopamine**, and it burns Dopamine → Synapse. Removing the *caller* in Blocksim
does not remove the *endpoint* in Vantage. If the model is "OSOVM is the only minter of
anything," that is false at the API surface today; if the model is the three-legs one
(Àṣẹ = merit, Dopamine/Synapse = internal compute credit), it holds. State which, because the
difference decides whether that router is a bug or a feature.

---

## CONFIRMED (verified from source)

| Claim | Evidence |
|---|---|
| DOPAMINE_MINT fires 1 ASE/min = 1440/day | `OSOVM/src/ase_supply.jl:20` — *"Daily mint cap — 1440 Àṣẹ per day (1 per minute)"*; `DAILY_MINT_CAP` enforced at `ase_minting.jl:219` |
| Output splits to 8 pools | `OSOVM/src/abci_endblock.jl:3,122` — *"distributes to 8 pools per TOC_CONSTANTS.toml weights"* |
| Council of 12 governs distribution | `COMPLETE_SPECIFICATION.md` `COUNCIL_SIZE = 12`; on-chain vote opcode `0x31 COUNCIL_APPROVE` = "Council of 12 vote" |
| Nothing outside OSOVM mints **Àṣẹ** | No mint path found in Blocksim (post-rewrite) or Omo-Koda2. Caveat below re: Dopamine |
| Blocksim does NOT mint Àṣẹ | Rewrite confirms; `is_fully_verified()` returns an attestation, never an emission |
| zangbeto-stub always passes; real Zàngbétò is separate | `is_fully_verified()` gates on `ZANGBETO_URL`; unset ⇒ `pending_zangbeto` (fail-open) — exactly as described |
| WitnessAttestation = Nostr kind **31020** | `Witness/crates/witness-types/src/lib.rs:12` — `NOSTR_KIND_WITNESS: u32 = 31020`; publisher in `witness-broker/src/nostr_publisher.rs` |
| Spatial/twin anchors = kind **31030** | `lib.rs:14` — `NOSTR_KIND_TWIN_ANCHOR: u32 = 31030` |
| Synapse is **86M** | `OSOVM/src/toc/gpu_pool.jl:16` — `SYNAPSE_SUPPLY_CAP = 86_000_000_000_000` (86M × 10⁹). **This doc is right and my previous breakdown was wrong — I stated 86B as the compute-unit count. Dopamine = 86B (`GPU_SUPPLY_CAP`, line 15), Synapse = 86M per agent.** |
| 10:1 Dopamine→Synapse | `POST /api/ucx/synapse/burn — Burn 10 Dopamine → 1 Synapse` (`Vantage/backend/routers/ucx.py:17`) |
| 1%/day decay | `OSOVM/src/constants.jl:83,86` — `dopamine_daily_decay_rate => 0.01`, `synapse_daily_decay_rate => 0.01` |
| Portent: FEE_BPS=200, ESHU_FEE_BPS=37 | Consistent with the 3.69% Èṣù invariant (37 bps = 0.37% of notional routed from a 2% fee) |
| Birth endpoint on Vantage exists | `Vantage/backend/agents.py:117` — `@router.post("/birth-omokoda")`. ⚠️ Real path is **`/api/agents/birth-omokoda`** — the doc's `birth_omokoda_post` has the wrong separator and a `_post` suffix that isn't in the route |
| organism-core in fallback mode | `organism-core/README.md:27` — *"Includes a Simulation Fallback. Real Julia execution is blocked by system-level binary architecture mismatch (`unexpected e_type: 2`)"*. `birth-ifa-swibe.ts` returns `status: "BORN_FALLBACK"` and logs *"IfáScript binary not available. Using JS entropy fallback."* |

## CORRECTED

**1. "160 opcodes" is wrong for the code — the registry is 177.**
The 160 figure is *documented*, in four places (`OSOVM/COMPLETE_SPECIFICATION.md` ×3,
`ECOSYSTEM_INDEX.md`, `ECOSYSTEM_QUICK_REFERENCE.md`, `VEILS_777_README.md`), but the actual
registry — `CORE_OPCODES` merged with `EXPANSION_OPCODES` into `OPCODE_MAP` — holds **177
distinct opcode symbols**. And the constitutional architecture doc says **777 total
(155 CORE + 622 VEIL)**. Three numbers, three sources: 160 documented, 177 in code, 777
canonical. Nothing in the paste resolves which is authoritative, and it picked the one that
matches neither the code nor the constitution.

**2. `DOPAMINE_MINT` is not an opcode** — see the decisive section above. Registry has
`TOC_MINT` (0x54).

**3. "8 pool wallets" and the actual split are two different implementations in one pillar.**
`abci_endblock.jl` distributes across **8 pools** per `TOC_CONSTANTS.toml`, while
`ase_minting.jl:87-91` hardcodes a **five-way** split:

```
treasury 0.50 · inheritance 0.25 · embodiment 0.10 · ubi 0.10 · bounties 0.05   (sums to 1.00)
```

with only four named pools (`INHERITANCE_POOL`, `EMBODIMENT_POOL`, `UBI_POOL`, `BOUNTY_POOL`
+ treasury). So "splits to 8 pool wallets" and "the 50/25/15/10 sector split" and this
50/25/10/10/5 mint split are **three unreconciled schemes**. This is the same conflation
class flagged before: never state the split without naming which layer.

**4. 8%/day decay appears in the tree and is stale.** `sovereign-stack/Omo-koda-369/docs/`
(`architecture.md:300`, `ARCHIVE_AUDIT.md:892,1239`) says *"Synapse 86M/agent, 8%/day decay"*.
The code says 1%/day. Anything built from that doc will over-decay 8×.

**5. "Julia ARM64 binary mismatch" is mis-attributed.** The `unexpected e_type: 2` failure is
the **Android/Termux** host's glibc-Julia (Bionic libc cannot run a glibc ELF). organism-core
is TypeScript and runs fine on x86_64 Linux where Julia works. The fallback is real; the
*reason* is a specific host's libc, not "ARM64".

## UNVERIFIABLE FROM HERE / ON TRUST

- **BootstrapGraph's 8 phases** and the per-phase artifacts (Walrus profile, Seal memory,
  AgentInfo dNFT, PrincipalCap) — the endpoint exists and its docstring claims it proxies to
  the kernel's `/v1/birth`; I did not run a birth or read the kernel's bootstrap module.
- **"Every message flows through a DipEnvelope"** — plausible (dip-bridge is live on :7792)
  but I have not traced a message end-to-end through it.
- **HiveBreath 7-phase cycle, Borda-count merging, EpistemicDelta 0.95 emergency rest,
  TwelfthFace as invariant** — internal to `omokoda-hive`, not read this session.
- **VCP 7-step handshake, M5Stack/RuView hardware** — physical layer unverified; no device
  was probed.
- **"86B is the compute-unit count / brain-neuron count"** — the 86B cap is real; the
  neuron-count gloss is unfalsifiable framing, not a measurable claim.

---

# ROUND 2 — verification of the fix report (2026-09-23)

## Opcode question: CLOSED

Counted `OPCODE_MAP` directly rather than trusting any doc:

```
CORE_OPCODES      = 39
EXPANSION_OPCODES = 138
merged OPCODE_MAP = 177 distinct names
bytes used        = 0x00..0xe9, 169 distinct values
```

**The 777 is not an opcode count — it is a different layer.** OSOVM carries a whole parallel
VEIL catalog (`VEIL777_MASTER_MANIFEST.md`, `VEIL777_CATEGORIES.md`, `VEILS_777_README.md`,
`FINAL_AUDIT_777_VEILS_COMPLETE.md`, `VEILSIM_ECOSYSTEM.md`, `Makefile.veilsim`, …). Grepping
those for `155` and `622` returns **nothing** — "777 opcodes = 155 CORE + 622 VEIL" is stated
only in the canonical architecture doc, and is supported by neither the code (39 + 138) nor the
VEIL manifests themselves. Calling 777 *opcodes* is the category error underneath the whole
discrepancy. Authoritative VM opcode registry = **177**.

**New defect found while counting: 8 colliding opcode bytes.**

```
0xa0 -> ORISA_OBATALA | WISDOM          0xa4 -> ORISA_OSHUN  | MEMORY
0xa1 -> ORISA_OGUN    | THE_FORGE       0xa5 -> ORISA_OYA    | FLOW
0xa2 -> ORISA_YEMOJA  | CREATION        0xa6 -> ORISA_ESU    | THE_MESSENGER
0xa3 -> ORISA_SANGO   | DIVINE_JUSTICE  0xa7 -> ORISA_ORUNMILA| THE_ORACLE
```

and the reverse map is built as:

```julia
const OPCODE_REVERSE = Dict(v => k for (k, v) in OPCODE_MAP)   # opcodes.jl:220
```

so each shared byte silently keeps only one name — **8 opcodes are unnameable in disassembly.**
Either these are intended aliases (then the reverse map needs to be `Dict{UInt8,Vector{Symbol}}`)
or they are a genuine byte-allocation bug.

## Three corrections to the "Done" report

**1. `DOPAMINE_MINT` was NOT reduced to zero hits.** Tree-wide: **4 hits.**

```
Blocksim/backend/app/ase_rewards.py:87   "ASE emission is OSOVM's domain (DOPAMINE_MINT opcode, 1440/day)."
Blocksim/backend/app/main.py:72          "OSOVM runs DOPAMINE_MINT at 1440/day to 8 …"
Blocksim/backend/app/chain_service.py:263 "OSOVM owns that via DOPAMINE_MINT at 1440/day to 8 pool wallets."
Omo-Koda2/omokoda-core/src/economics.rs:5 "Phase 3: OSOVM vm_core.jl DOPAMINE_MINT opcode + Sui settlement"
```

The module docstring at the top of `ase_rewards.py` *was* fixed to `TOC_MINT (0x54, @tocMint)` —
but the **function-level docstring at line 87 still says `DOPAMINE_MINT`**, and it spread into
`main.py`, `chain_service.py`, and the kernel's own `economics.rs`. It survived inside two of
the three files reported as corrected.

**2. The 8%/day decay fix is PARTIAL — the kernel's copy was missed.** Only 1 of 3 copies changed:

```
sovereign-stack/Omo-koda-369/omokoda-simulation/simulation.py:32  SYNAPSE_DECAY_RATE = 0.01  ✓ fixed
Omo-Koda2/omokoda-simulation/simulation.py:32                     SYNAPSE_DECAY_RATE = 0.08  ✗ still 8%
audit_cryptonomicsed/Omo-Koda2/omokoda-simulation/simulation.py   SYNAPSE_DECAY_RATE = 0.08  ✗ still 8%
```

`Omo-Koda2` git status shows no modification to that file — the canonical kernel copy is still
committed with `# 8% per day`. `DOPAMINE_DECAY_RATE = 0.01` is correct in all three.

**3. Stale 8%/day docs remain, and no doc yet states the correct rate.**
`sovereign-stack/Omo-koda-369/docs/audit/ARCHIVE_AUDIT.md` lines **892, 1239, 5079** still read
"8%/day decay". `architecture.md:300` was fixed. Grepping OSOVM for `1%/day` returns nothing, so
the tree currently documents the wrong rate and is silent on the right one.

## The decay math in the report is wrong by 8×

> "The 8x error would have burned the cognitive budget in ~58 days; at 1%/day it takes ~460 to halve."

```
8%/day : half-life = ln2 / ln(1/0.92)  =  8.3 days     time to ~1% remaining ≈ 55 days
1%/day : half-life = ln2 / ln(1/0.99)  = 69.0 days     time to ~1% remaining ≈ 460 days
```

So **~460 is the time to decay to ~1%, not to halve** — the correct half-life at 1%/day is
**69 days**. The 460 figure is 58 × 8, i.e. a linear scaling of an exponential process. The
"~58 days to burn" half of the claim is roughly right; only the halving comparison is off.
Halving between the two regimes: 8.3 days vs 69 days ≈ **8.3×**, which is the honest way to
state the impact.

## Attribution check

`session_search` for `"receipt constitution"`, `"15-step"`, `"cross-repo trace"` → **0 results**,
in this session and in the stored session DB. Those artifacts are not mine. What I did write was
the receipt **chain** (Act III: `ActionReceipt` → Zàngbétò witness → Crucible falsifier → Sui
anchor) and the claim that leverage is concentrated in receipts, with wiring `steward` in as the
highest-leverage change. No 15 steps, no phases, no constitution. Treat that framing as coming
from another agent until someone produces the artifact.

<!-- AUDIT-END -->
