# PATTERN MINING — XiaomiMiMo/MiMo-Code + deepseek-ai/deepseek-harness

For the sovereign ecosystem. Per standing doctrine: **patterns are extracted, not tools adopted.**
Deployment viability is secondary and does not lead. Every fact below is from source
(GitHub API, cloned trees, repo docs), 2026-09-23.

---

## 0. WHAT THEY ACTUALLY ARE

| | MiMo-Code | deepseek-harness |
|---|---|---|
| Repo | `XiaomiMiMo/MiMo-Code` | `deepseek-ai/deepseek-harness` |
| Stars / forks | 13,439 / 1,391 | **234,257 / 28,151** |
| Language | TypeScript (Bun) | TypeScript (pnpm, node ^22.19 \|\| >=24) |
| License | MIT **+ `USE_RESTRICTIONS.md` rider** | MIT, clean (generated THIRD_PARTY_NOTICES) |
| Created / pushed | 2026-06-10 / today | 2026-08-13 / today |
| Open issues | 1,069 | **0** |
| Self-description | "Where Models and Agents Co-Evolve" | "Everything is a Plugin." |

**MiMo-Code is a hard fork of OpenCode.** It still carries `"name": "opencode"` and
`repository: https://github.com/anomalyco/opencode` in `package.json`; it renamed the channel
env vars to `MIMOCODE_CHANNEL` / `MIMOCODE_VERSION`. Its own README says so explicitly:

> *"MiMoCode is built as a fork of OpenCode. It keeps all core OpenCode capabilities (multiple
> providers, TUI, LSP, MCP, plugins) and adds persistent memory, intelligent context management,
> subagent orchestration, goal-driven autonomous loops, compose workflows, and self-improvement
> via dream/distill."*

Your `~/opencode` is at commit `17166b271` from **Jun 26 2026** — ~3 months stale. So MiMo-Code
is worth reading for two reasons at once: **Xiaomi's additions, and what upstream OpenCode did in
the three months since your clone.**

**deepseek-harness is a plugin harness on vendored Cordis** (IoC/DI container, vendored into the
tree and rescoped to `@deepseek-ai/cordis`). `vendor/README.md` states the reason plainly: the
framework is vendored *"so that the harness fully owns its framework layer (auditable, patchable,
pinned)."*

---

## 1. CAPABILITY SEAMS — the direct answer to your device-agnostic rule

deepseek-harness's `docs/capability-seams.md` is an auto-generated graph of every service in the
system, split into three kinds: **core spine service**, **swappable capability seam**, or
**bundle/composition point**. Every seam is one declaration with N providers:

```
ctx.llm                 LLM adapter registry       → llm-deepseek | llm-pi-ai | llm-replay
ctx.sessionPersistence  durable session storage    → session-persistence-jsonl | …-sqlite
ctx.storage             non-session storage hub    → storage-json | storage-sqlite | storage-domain
ctx.credentials         credential seam            → credentials-local
ctx.settings            user-settings seam         → settings-file
ctx.sessionTelemetry    telemetry seam             → session-telemetry-otel
ctx.tokenMeter          replay token measurement
ctx.toolResultPruner    model-free tool-result pruning
ctx.invariants          package-owned invariant registry
```

**Why this is the single most transferable pattern for your stack:** your HARD RULE is that
everything is universal — the agent may be on a computer, an iPhone, a MIDI device, an SBC — and
your ecosystem currently answers that with per-platform forks (Fold4 vs VPS vs Mac, three
`simulation.py` copies, two `omokoda-canonical` variants). A seam/provider split answers it with
**one declaration and a chosen provider at composition time**, which is exactly "per-platform
bespoke > generic" without duplicating the body of the code.

Note `llm-replay` as a *provider of the LLM seam* — a fake is a first-class provider, not a mock
sprinkled into tests. That is how they keep keyless CI meaningful.

---

## 2. "VERIFY THE WORLD, NOT THE SELF-REPORT" — your receipt problem, already solved on paper

This ecosystem's most-repeated failure (agents whose summaries contradict their own acceptance
scripts; contracts ≠ runtime; status docs ≠ status) is a **named section heading** in
`docs/testing.md`:

```
## Prefer the real implementation over a mock
## Verify the world, not the self-report
## Test the real entry path
```

and the policy text under it:

> *"A no-key test proves plumbing; only a with-key run proves the agent works against a real
> model. Highest-value are **smoke tests** that boot the real example, send one prompt, and check
> the world — they catch the **'green unit tests, broken product'** class that mocks cannot."*

Their evidence discipline, in their words: *"Match evidence to the surface: focused tests for
behavior, snapshots for model or user output, `doc-sync` for docs, build/hygiene and built smokes
for published paths, and real-API e2e for provider behavior."*

**This is the pattern to port into the receipt chain.** `ActionReceipt` today is produced by the
kernel and audited by hand. deepseek-harness's version of the same problem is: every non-trivial
change must add a **keyless scenario that boots the real entry path**, and the gate is
`test:snapshot`, not the author's summary. Your Zàngbétò step is that gate — and the rule to
import is *no self-report is admissible evidence; only a replayed real entry path is.*

Their `docs/defensive-patterns.md` opens with the framing that makes it stick: *"each pattern
below is a class of defect that actually shipped or nearly shipped here, stated as the rule that
prevents its recurrence."* Compare with your `docs/` — your hard-won lessons live in skill
pitfalls.) **A "defect classes that actually shipped" file is worth more than a bug list.**

---

## 3. GENERATED DOCS — the structural cure for "status docs ≠ status"

`docs/capability-seams.md` and `THIRD_PARTY_NOTICES.md` both carry:

> `<!-- Generated by scripts/gen-doc-graphs.ts - do not edit by hand. -->`

The architecture page is a **build artifact rendered from the code graph**. It cannot drift,
because drift means the generator fails. Your ecosystem's biggest recurring wound is exactly
drift: `BLOCKCHAIN_IMPLEMENTATION_CHECKLIST.md` claiming 11% against green code, port tables
saying 7778 when the process says 7780, "7 laws at every layer" when the gates run neutral DNA.

**Port this**: generate the port→process map, the opcode registry table, and the daemon roster
from the system itself (`ss -ltnp` + `/proc/*/cmdline` + `systemctl`), commit the generator, and
mark the output "do not edit by hand." Then a stale table is impossible rather than merely
discouraged.

---

## 4. PER-PACKAGE INVARIANT REGISTRY

From `packages/AGENTS.md`:

> *"**Every package owns `./invariant`.** Register the manifest name; check an event/data relation
> or give empty installers package-specific `No runtime invariant:` reasons. Generated
> companions, unexplained empties, and ignored reporters fail `verify-package-invariants`."*

And the rule that gives it teeth:

> *"**Runtime invariants assert owned relationships.** Check authoritative event streams or mutable
> data, not service or method presence, plugin metadata or effects, or fixed pure examples.
> Without a plausible relationship, an explained empty companion is correct."*

**An empty invariant must be *explained*, and the explanation is machine-checked.** That is a
precise, cheap mechanism for your pillars: every repo declares the invariant it owns (or states
why it owns none), and a gate fails on silence. It would have caught "Omo-Koda2 runs on :7777"
the day it stopped being true.

---

---

## 5. MiMo — PERSISTENT MEMORY, TWO TIERS + ONE INDEX

From the README, the whole design in four bullets:

- **Project memory (`MEMORY.md`)** — persistent project knowledge, rules, architecture decisions
- **Session checkpoint (`checkpoint.md`)** — structured state snapshots **maintained automatically
  by the checkpoint-writer subagent**
- **Scratch notes (`notes.md`)** — temporary area
- **Task progress (`tasks/<id>/progress.md`)** — per-task logs

Backed by **SQLite FTS5** full-text search, injected automatically on session resume.

**The two structural choices worth stealing:**

1. **Checkpoint maintenance is a *subagent*, not a hook.** A dedicated agent owns keeping the
   structured snapshot current. Your ecosystem has REM pruning phases driven by cron
   (`sabbath-agent-maintenance`); the subagent owns *state capture*, cron owns *pruning*.
2. **Four tiers by lifetime, not one blob.** Your memory layer has six implementations
   (Mycelium, GlyphIndex/mnemopi, minipae/NIP-AE, Synapse/NIP-30, Memora, Triune) and they all
   conflate durable knowledge with transient state. MiMo's split — durable rules / structured
   checkpoint / scratch / per-task progress — is the taxonomy your six systems are each
   approximating.

---

## 6. MiMo — DREAM & DISTILL (the best pattern in either repo)

- **`/dream`** — *"scans recent session traces, extracts persistent knowledge into project memory,
  and **removes outdated entries**"*
- **`/distill`** — *"discovers repeated manual workflows in recent work and **packages
  high-confidence candidates into reusable skills, subagents, or commands**"*

This is the automatic closure of the experience→skill loop. It is the same shape as your
Hermes skill workflow, except yours is manual (`skill_manage` after a difficult task) and theirs
is a command over session traces. **`/distill` is the piece your ecosystem is missing**: you have
~400 local directories, 40+ skills and an ecosystem full of repeated manual workflows, and no
mechanism that notices a workflow was done three times and promotes it.

Combined with §3 (generated docs) and §4 (invariants), this is a three-part anti-entropy kit:
**dream** prunes knowledge, **distill** promotes workflows, **generate** keeps docs true.

---

## 7. MiMo — `/goal` WITH AN INDEPENDENT JUDGE

> *"The `/goal` command sets a stopping condition for a session. When the agent tries to stop, an
> **independent judge model** evaluates the conversation to decide whether the condition is truly
> satisfied — preventing premature **'optimistic stops'** during autonomous work."*

Note the shape: the worker declares itself done, and a **different model** adjudicates. That is
the same architecture as the TypeSafe/Jev verification case from earlier in this session, and the
same one your receipt chain needs. Three independent arrivals at "the author's self-report is not
evidence": deepseek-harness (verify the world), MiMo (independent judge), TypeSafe (typed
probability instead of prose). That convergence is the strongest signal in this whole evaluation.

---

## 8. MiMo — WORKFLOWS AS DETERMINISTIC SCRIPTS

> *"Workflows are deterministic JavaScript scripts that orchestrate multiple agents in a sandboxed
> runtime. Unlike agent conversations, workflows encode fixed phase sequences with **bounded
> retries and automatic parallelization** — fire-and-forget execution with no user interaction
> required."*

Four built-ins, and two are directly reusable as recipes:

| Workflow | Phases | Note |
|---|---|---|
| `compose` | Brainstorm → Design → Implement → Verify → Review → Report → Merge | auto-parallelizes into isolated **git worktrees**, TDD per task |
| `deep-research` | Brief → Plan → Research → Reflect → Write → Review | parallel angles, convergent, resumable via **file checkpoints** |
| `fact-check` | Plan → Search → Extract → Group → Crosscheck → Report | **3-juror adversarial vote** per claim |
| `research-experiment` | Baseline → Loop → Audit → Report | iterates hypothesize→implement→evaluate→keep/revert, **audits for metric gaming** |

"Fire-and-forget with no user interaction" is exactly your cron surface, and `research-experiment`
(a fixed-budget evaluation command + explicit editable-file scope + a metric-gaming audit) is a
ready-made template for autonomous optimization on your own repos. The 3-juror vote is a cheaper
version of your Twelve Thrones.

---

## 9. MiMo — CONTEXT ECONOMICS (concrete, portable numbers)

- **Budgeted injection**: a token budget controls how much checkpoint/memory/notes enter context,
  **with importance ranking**.
- **Adjustable compaction point**: `compaction.max_context` per model, with wildcards
  (`"anthropic/*": "300K"`, longest pattern wins), values as tokens / `"1M"` / `"50%"`.
- **The defensive detail worth copying verbatim:** *"The value is always clamped to what the
  provider actually accepts, so it can only lower the compaction point, never raise it."*
  A config that can only be more conservative than the hardware is a good invariant.
- **And the honest reasoning behind it:** *"The advertised window is not always what you get. The
  same model can have a different usable window depending on how you reach it — a subscription, a
  direct API key, or a reseller — so a catalog figure of 1M does not mean your route serves 1M."*
  You have hit exactly this: a Gemini key that authenticates but is out of credit, a Groq key that
  403s a UA it dislikes. **Catalog capability ≠ delivered capability** is the same family as
  contracts ≠ runtime.
- Claimed cache discipline: *"up to 99% same-session and 95% cross-session cache hit rates."*

---

## 10. MiMo — FREEZE THE TOOL SET PER SESSION

> *"After the first message the mode locks: Build and Plan can still switch between each other,
> but Compose is isolated once entered — **keeping the skill/tool set fixed from session start
> significantly improves tool-call reliability.**"*

One sentence, immediately actionable for Hermes-side work: don't mutate the tool/skill set
mid-session if you want reliable tool calls.

Related: skill selection uses **exact name → localized alias → BM25 relevance**, auto-loads
high-confidence matches, and ranks the uncertain ones for the agent to judge. Mentioning ≥2 skills
in one message auto-injects a **multi-skill orchestration plan**.

---

## 11. MiMo — VOICE (maps onto your existing voice stack)

`/voice` = real-time streaming input via **TenVAD** (VAD) + **MiMo ASR** (segmented on pauses,
transcribed incrementally into the input). The org also ships `MiMo-V2.5-ASR` (338★, Apache-2.0)
and `MiMo-Audio` (1,082★, Apache-2.0). You already run `stt-relay`, `Vantage-Voice-` (S2S PWA)
and `speech-to-speech` — this is a live alternative for the STT leg and, more usefully, a
**reference for incremental/pause-segmented transcription** rather than batch STT.

---

## 12. MiMo — THE HONEST SECURITY SECTION

`SECURITY.md` says something most projects won't:

> *"**No Sandbox** — MiMoCode does **not** treat its permission system as a security sandbox.
> Permissions help users review and control actions, but they are not an isolation boundary. If you
> need isolation, run MiMoCode in a disposable container, virtual machine, or similarly restricted
> environment."*

Your ecosystem makes the same category error: the 5-tier permission model sits in the `act` path
as if it were an enforcement boundary. It is a *review* mechanism. Isolation is the sandbox
(`ares-code-sandbox`, CubeSandbox microVMs) — and on Termux/Android there is no isolation
available at all, which is why the phone must never be a sandbox host. State it the way they do.

Also a good default to copy: *"By default it binds to a loopback address… refuses to bind to a
non-loopback address without a password unless the user explicitly overrides."*

---

## WHAT NOT TO TAKE

- **Don't adopt either as a pillar.** Both are developer-facing coding agents. You already run
  OpenCode in the pipeline (Gitea → oh-my-pi → OpenCode → OpenShip → Vantage); adding a fork of it
  as a dependency buys a Chinese vendor's release cadence, an OAuth/telemetry surface, and a
  1,069-issue backlog for capabilities you'd be reimplementing anyway.
- **Don't build on deepseek-harness's on-disk formats.** Its own AGENTS.md: *"Backends reject old
  on-disk formats. SQLite uses monotonic `SCHEMA_VERSION`; `dsh-session` keeps
  `SESSION_FORMAT_VERSION` at `0` with no compatibility promise."* Pre-release stance, breakable by
  design — fine to read, unsafe to depend on.
- **Don't copy the framework-vendoring approach.** Rescoping Cordis into `@deepseek-ai/*` is a
  legitimate move *for a company that intends to publish the framework layer*. It would be a
  maintenance millstone for you; take the seam/provider **idea**, not the vendor-and-rescope
  machinery.
- **Don't take MiMo's compose curriculum as-is.** Fourteen built-in skills is a curriculum for
  weaker models; with frontier models they themselves recommend the single compact
  `/compose-next` contract instead. You already have `spec-to-phased-build-plan`; merge, don't
  duplicate.

## LICENSE GATES (checked, per standing rule)

- **MiMo-Code: MIT *plus* `USE_RESTRICTIONS.md`.** The rider forbids use *"for any military
  purpose"* and, critically for you, *"to use Xiaomi MiMoCode in a manner that **autonomously
  executes high-risk actions without appropriate human oversight or authorization**"*, plus
  *"access, interact with, scrape, or automate any third-party platform or service in violation of
  any applicable laws, policies, or authorization requirements."*
  → **Pattern extraction is fine. Vendoring MiMo-Code code into an autonomous execution path
  (ares-autotrade, the 36-daemon fleet, the darknet scrapers) is not**, on their own terms.
  The LICENSE file does keep upstream attribution (`Copyright (c) 2025 opencode`).
- **deepseek-harness: MIT, clean**, no use-restriction rider, generated third-party notices. Safe
  for code-level reuse; still don't depend on its formats.

## ALSO WORTH A LOOK (from the org sweeps, not asked about)

`XiaomiMiMo/mimoagent` — a deliberately small agent (AGENTS.md is 14 KB vs MiMo-Code's 65 MB tree) —
the cheapest place to read their agent loop. `XiaomiMiMo/MiMo-Skills` (MIT) — droppable skill set.
`XiaomiMiMo/uni-agent` — long-horizon agent training. `deepseek-ai/Engram` (4,695★, Apache-2.0) —
memory; relevant to your fragmentation problem. `deepseek-ai/awesome-deepseek-agent` (6,136★) —
ecosystem index.

## THE THREE TO STEAL, IF YOU ONLY TAKE THREE

1. **Verify the world, not the self-report** → make it the Zàngbétò rule, with a keyless replay of
   the real entry path as the only admissible evidence (§2).
2. **Dream & Distill** → the automatic experience→skill loop you don't have; pairs with your
   existing cron pruning (§6).
3. **Generated docs** → render the port map / opcode table / daemon roster from the system itself
   so drift is impossible instead of discouraged (§3).

<!-- SECTION-END -->
