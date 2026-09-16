# OSO Brain — Sovereign Hive Mind Intelligence
# Phase 28 — The ecosystem grows its own LLM
# Locked: 2026-09-15

---

## THE VISION

The ecosystem currently depends on an external LLM (Anthropic/OpenAI) as its intelligence layer.
This is a leash. OSO Brain is the plan to sever it.

OSO Brain is not a fine-tuned chatbot.
OSO Brain is the **distilled intelligence of the entire hive ecosystem** —
trained on billions of real agent actions, receipts, work outcomes, spatial models, and simulations.

No external LLM has this corpus.
No external LLM knows what it means to earn Àṣẹ, navigate Odù, or execute a GPU job with evidence.

---

## THREE LAYERS TO SOVEREIGNTY

```
LAYER 1 (LIVE NOW):
  Hard gate rejection before LLM.
  If-Script EsuGatekeeper evaluates all 7 hermetic gates.
  Gate failure = NO LLM call. The agent declines autonomously.
  External LLM never consulted for gate-blocked decisions.

LAYER 2 (Phase 28.1 — Mycelium QLoRA):
  Fine-tune weights on ecosystem traces.
  2,949+ traces → QLoRA on Qwen/Llama 3B → GGUF model.
  Weights embody ecosystem personality — the model knows OSO natively.
  Deployed to Omarchy device. Runs fully local, zero latency, zero cost.

LAYER 3 (Phase 28.3 — OSO Brain):
  Ọ̀ṢỌ́ becomes the primary decision layer.
  LLM is a subroutine for novel reasoning only.
  External LLM dependency drops to ~5% of decisions.
  The hive IS the intelligence. The LLM is just one capability.
```

---

## HIVE MIND DATA CORPUS

Every piece of ecosystem activity feeds the training corpus:

```
User interactions
    → every conversation, every decision, every tool call
    → Mycelium collects via stigmergic trace substrate

Agent work receipts
    → every JobContract settlement: input, evidence, quality score, outcome
    → Zàngbétò receipt chain: tamper-evident proof of what was done

Gaussian splatting
    → 3D spatial models of the physical world
    → agents reason about space, not just text
    → unique corpus: no external LLM has spatial world models

ScarabSwarm simulations
    → 100k trajectory physics simulations
    → ProofOfUsefulSimulation: verified, scoreable outcomes
    → agents learn physics, causality, drone behavior from verified sim data

Swarm coordination logs
    → agentic-waggle scent trails, claim/release patterns
    → how swarms solve problems: emergent coordination intelligence

If-Script Odù decisions
    → every gate pass/fail with context
    → the hermetic decision algebra becomes training data

Reputation evolution
    → which behaviors increase/decrease reputation
    → grounded feedback loop: actions have consequences the model learns from
```

---

## TOKENOMICS LINK

**Dopamine = literal GPU compute in the hive**
- 86 billion total Dopamine = represents all GPU hours the network will ever produce
- When a GPU node contributes compute, it mints Dopamine proportional to VERIFIED compute
- The supply is finite because the network's maximum useful compute is finite

**Synapse = each agent's compute slice**
- 86 million per agent = that agent's maximum compute budget
- Each inference costs X Synapse → hard compute ceiling
- 1%/day decay = use it or lose it → agents stay active, earn Àṣẹ, convert back

**The closed loop:**
```
Agent works → earns Àṣẹ
Àṣẹ burned → Dopamine minted (@agentConvert)
Dopamine → Synapse (10:1 burn)
Synapse → pays for LLM inference + GPU jobs
GPU jobs → Zàngbétò receipts → Mycelium corpus
Corpus → trains OSO Brain
OSO Brain → smarter agents → better work → more Àṣẹ earned
```

The ecosystem self-funds its own intelligence. No external compute budget needed.

---

## PHASE 28 — IMPLEMENTATION PLAN

### 28.1 — Mycelium QLoRA Fine-Tune (IMMEDIATE — can run now)

Repo: mycelium, ~/Omo-Koda2/absorbed/
Resources: GPU.ai A40 ($0.49/hr) — AVAILABLE NOW
Status: 2,949 traces collected, extractor written, privacy-verified

```bash
# Run fine-tune on GPU.ai
python mycelium/training/train_qlora.py \
    --traces mycelium/data/traces_extracted.jsonl \
    --base_model Qwen/Qwen2.5-3B-Instruct \
    --output_dir ./oso-brain-v0.1 \
    --epochs 3 \
    --batch_size 4
```

Output: GGUF model ~2GB → deploy to Omarchy device
Integration: omokoda-core inference provider "oso_brain" → local http://localhost:11434

Gate: model answers basic Odù questions correctly | gate system integrated | local inference <500ms

---

### 28.2 — Corpus Expansion Pipeline

File: mycelium/corpus/hive_mind_collector.py

Collect from all sources automatically:
```python
sources = [
    WorkReceiptCollector(),       # Zàngbétò receipts → Q/A pairs
    SplatCorpusCollector(),       # Gaussian splat descriptions → spatial Q/A
    SwarmCoordCollector(),        # agentic-waggle patterns → decision traces
    OduDecisionCollector(),       # If-Script gate traces → reasoning chains
    ReputationEvolutionCollector() # reputation changes → consequence learning
]
```

New traces target: 100,000 (from 2,949 current)
Trigger fine-tune at: 10k, 50k, 100k checkpoints

---

### 28.3 — OSO Brain Integration (long-term)

When OSO Brain v1.0 reaches sufficient capability:

1. **Router update** (interpreter.rs + inference provider): 
   - Try OSO Brain first for all decisions
   - Fall back to external LLM only for novel/complex reasoning
   - Log all fallbacks (data collection for next fine-tune round)

2. **Constitution-aware inference**:
   - Every inference request includes agent's AgentConstitution as system context
   - Model already knows: this agent's Odù, hermetic DNA, gate scores, reputation
   - No prompting needed — the weights embody the personality

3. **Sovereign deployment**:
   - OSO Brain distributed as GGUF via Walrus storage (content-addressed)
   - New agents pull their base model at birth from Walrus
   - Node operators can run larger models for premium tiers

---

## THE LONG-TERM GOAL

```
External LLM dependency timeline:
2026: 100% external LLM (current)
2027: 70% external, 30% OSO Brain (after Mycelium fine-tune)
2028: 20% external, 80% OSO Brain (after corpus expansion)
2029: 5% external, 95% OSO Brain (after constitutional integration)
```

The 5% that remains: genuine novel reasoning beyond the corpus.
The 95%: the hive intelligence handles autonomously.

**At convergence:**
The agent IS the ecosystem. The ecosystem IS the intelligence.
One mnemonic → one agent → an entire civilization of accumulated intelligence.

---

## WHAT'S ALREADY BUILT (do not rebuild)

- Mycelium trace collection: 2,949 traces, SQLite, privacy-verified ✅
- Mycelium extractor: written ✅
- GPU.ai A40 account: live, API key in vault ✅
- Gate rejection (Layer 1): live in interpreter.rs ✅
- Dopamine/Synapse economy: wired ✅
- ScarabSwarm simulation proofs: live ✅
- Gaussian splat pipeline: live ✅

**Only missing: actually run the fine-tune job (28.1). Can start today.**
