# AI Agentic Software Engineering — Token Efficiency Research Report

**Date**: 2026-05-28
**Scope**: US/EU AI industry analysis of token output-to-input ratio optimization in agentic SE
**Sources**: Anthropic, Google DeepMind, OpenAI, Microsoft Research, Stevens Institute, ICSE 2026, arXiv papers, community research

---

## Executive Summary

The AI coding industry crossed a watershed in 2025–2026. Token costs shifted from a minor billing concern to a **systemic engineering challenge** threatening the viability of agentic coding. The flat-rate subsidy era ended — GitHub Copilot, Anthropic, and Google all migrated to usage-based billing. At the same time, research breakthroughs demonstrated that token consumption can be reduced **84–98.7%** while improving agent performance **+54%**. The winners in agentic SE will not be those with the most powerful models, but those who build the best **token allocation and context management infrastructure**.

---

## 1. The Token Cost Crisis

### 1.1 Scale of the Problem

| Event | Detail |
|-------|--------|
| **Claude Code top user** | 7.7B tokens in 30 days on a $200 plan — equivalent to ~$50,000 in compute costs |
| **Cursor price spiral** | 5 consecutive price increases and feature cuts after users exploited flat-rate tiers |
| **Anthropic ban (Apr 2026)** | Third-party agents banned from Claude Pro/Max — heavy users saw costs rise up to 50× |
| **GitHub Copilot (Jun 2026)** | Flat-rate → token-based AI Credits; zero free fallback after credits exhausted |
| **Google internal growth** | 500B → 3T tokens/day (Mar→May 2026); 7× YoY cross-product increase |
| **OpenAI projected burn** | ~$14B in 2026; hyperscalers investing $650B in AI infrastructure |

### 1.2 Root Cause: The Agentic Consumption Paradigm

Agentic systems differ fundamentally from chat: they execute long chains of reasoning, tool calls, self-correction loops, and multi-agent delegation. A single agentic task can consume **15× more tokens than a chat interaction**. Every tool definition, every round-trip context pass, every failed attempt compounds.

---

## 2. The Marginal Token Allocation Framework (Zhu, UIUC 2026)

A foundational theoretical contribution: agentic systems should be designed as **marginal token allocation economies**.

### Core Equation

```
Marginal Benefit = Marginal Cost + Latency Cost + Risk Cost
```

### Four-Layer Architecture

| Layer | Mechanism | What It Prices | Key Failure Mode |
|-------|-----------|----------------|------------------|
| **Demand** | Model router | Task value vs. compute cost | Over-routing to expensive models |
| **Action** | Agent policy (plan/act/verify) | Risk price | Over-delegation, under-verification |
| **Supply** | Serving stack (prefill/decode/KV cache) | Latency price | Congestion, cache misuse |
| **Capital** | Training pipeline (RL rollouts) | Future capability | Stale rollouts |

### Key Insight

Each layer currently optimizes with **different shadow prices**, leading to globally irrational allocation. The fix: a **common price vector** shared across all layers — welfare economics applied to token allocation.

---

## 3. Prompt Caching: The Foundation (90% Cost Reduction)

### 3.1 Anthropic Prompt Caching

| Metric | Improvement |
|--------|-------------|
| Cost reduction | Up to **90%** |
| Latency reduction | Up to **85%** |
| Cache write cost | 25% more than base input price |
| Cache read cost | Only **10%** of base input price |
| Cache TTL | 5 minutes (resets on read) |

Cache checkpoint markers inserted into prompts allow subsequent requests reusing the same prefix to load cached model state instead of recomputing. Claude Code automatically enables prompt caching.

### 3.2 Speculative Prompt Caching (May 2025)

Cache warming begins **while the user is still typing**, before query submission. Benchmark results on SQLite source files:

| Mode | Time to First Token |
|------|---------------------|
| Standard caching | 20.87s |
| Speculative caching | **1.94s** (90.7% improvement) |

### 3.3 Multi-Level Caching Architecture

| Level | Scope | Benefit |
|-------|-------|---------|
| **L1: Session** | Single conversation | Immediate cache reuse within session |
| **L2: Project** | CLAUDE.md, skill defs, project docs | Cross-session reuse within project |
| **L3: Enterprise** | Shared knowledge bases | Organization-wide cache sharing |

L3 enables "whole-codebase memory" — 12× faster prompt processing in 100K-line codebases.

---

## 4. Context Engineering: The Decisive Battleground

### 4.1 Evolution Path

```
Prompt Engineering → RAG → Embedding Search → Grep/LSP → Agentic Search → Context Engineering
```

Anthropic formally introduced Context Engineering (Sep 2025) with four pillars:

| Strategy | Performance Gain | Token Reduction |
|----------|-----------------|-----------------|
| Context Editing alone | +29% | −84% |
| Context Editing + Memory Tool | +39% | −84% |
| Full Context Engineering (all 4) | **+54%** | **−84%** |

### 4.2 The Four Pillars: Write-Select-Compress-Isolate

| Pillar | What It Does | Example |
|--------|-------------|---------|
| **Write** | Curate what enters context | Compact CLAUDE.md, rules as "always/never/when-then" |
| **Select** | Retrieve only what's needed | Progressive disclosure; lazy-load skills/agents on trigger |
| **Compress** | Remove stale/duplicate content | Auto-clean completed tool calls, stale data when near token limits |
| **Isolate** | Separate concerns into sub-contexts | Sub-agents with minimal context inheritance |

### 4.3 The Compression Paradox (Ustynov, Apr 2026)

Counterintuitive finding: **shorter is not always cheaper**.

| Format | Input Tokens | Total Session Tokens | Result |
|--------|-------------|---------------------|--------|
| Human-Readable logs | 8,072 | 18,900 | Baseline |
| Compressed (abbreviated) | 6,695 (−17%) | **31,600 (+67%)** | Much worse |

Compressing meaningful content shifts interpretative burden to the model's **reasoning phase**, where it must reconstruct lost semantics. The goal is **semantic density** — eliminate zero-information tokens while preserving high-semantic-value ones.

### 4.4 1M Token Wall

SWE-rebench research: models hit a **clear performance ceiling around 1 million tokens** — performance degrades past this point regardless of what the context window technically supports. Bigger windows don't help; better context engineering does.

---

## 5. Model Selection & Routing: 40–77% Savings

### 5.1 The Tiered Model Strategy

| Task Type | Model | Cost/Task | Use For |
|-----------|-------|-----------|---------|
| File names, simple summaries, deterministic ops | Haiku / Gemini Flash | ~$0.03 | 60–70% of all calls |
| General coding, refactoring, standard features | Sonnet / GPT-4o | ~$0.24 | Everyday development |
| Architecture, critical code, deep reasoning | Opus + Thinking | ~$1.20 | Critical path only |

### 5.2 The SAG Finding (ICSE 2026): Dual-Model Beats Monolithic

| Configuration | Success Rate | Token Usage |
|--------------|-------------|-------------|
| o4-mini + GPT-4.1-mini | **84.4%** | 17,956 |
| GPT-5 + GPT-5 | 75.6% | 99,400 |

**Separating reasoning models from action models** achieved higher success with **5.5× fewer tokens**. Uniformly applying stronger models is counterproductive.

### 5.3 Routing Decision Framework

| Strategy | Savings | Risk |
|----------|---------|------|
| Conservative (route unclear to capable model) | 30–50% | Lowest |
| Balanced | 40–60% | Low |
| Aggressive (cheap model for all simple-seeming tasks) | 50–77% | One bad answer destroys trust |

---

## 6. Multi-Agent Economics

### 6.1 The Google/MIT Finding (Dec 2025)

180 controlled experiments across GPT, Gemini, and Claude families with standardized token budgets:

| Scenario | Result |
|----------|--------|
| **Parallelizable tasks** (e.g., financial analysis) | +80.9% boost with centralized multi-agent |
| **Sequential/dependent tasks** (e.g., coding) | 39–70% **worse** with any multi-agent setup |
| **Coding tasks** | Few truly parallelizable subtasks; multi-agent generally underperforms |

### 6.2 Token Efficiency: Single vs. Multi-Agent

| Architecture | Tasks per 1,000 Tokens |
|-------------|----------------------|
| Single agent | **67** |
| Centralized multi-agent | 21 (less than 1/3) |
| Hybrid teams | 14 |

### 6.3 When Multi-Agent Makes Sense

- Truly independent parallel subtasks (concurrent test writing for isolated modules)
- Research/exploration tasks with no shared state
- Subcomponents with zero dependencies on each other
- Single-agent success rate below 45%

### 6.4 The 45% Saturation Rule

> If a single agent already achieves >45% success on a task, adding more agents brings diminishing or negative returns.

### 6.5 Anthropic's Position

> "Most coding tasks involve fewer truly parallelizable tasks than research, and LLM agents are not yet great at coordinating and delegating to other agents in real time."

---

## 7. Tool Schema Overhead & Compression

### 7.1 The Problem

A single MCP tool definition costs **300–500 tokens**. 28 tools can consume ~11,000 tokens — overflowing an 8K context window entirely. Claude Code's 50+ built-in tools plus 25 skills and 14 agents compound this overhead.

### 7.2 TSCG — Tool-Schema Compression (Sakizli, May 2026)

Deterministic, rule-based compression of JSON Schema tool definitions:

| Metric | Result |
|--------|--------|
| Token reduction | 44–68% (conservative: ~50%) |
| Binary enablement at 8K context | +20.5pp exact match boost |
| Frontier scaling | JSON overflows at ~494 tools; compressed remains operational beyond 800 |

### 7.3 Code Execution Mode (Anthropic, Nov 2025)

A paradigm shift: instead of loading 50 tool definitions (~50K tokens) into context, agents write code that calls tools directly in a sandbox:

| Mode | Token Usage | Result |
|------|------------|--------|
| Traditional tool calling | 150K+ tokens | Tools in context, data re-passed |
| Code execution mode | ~2K tokens | **98.7% reduction** |

Data flows directly between tools in the sandbox, never entering the AI context window.

---

## 8. Compression Strategies Taxonomy

| Strategy | Token Savings | Technique | Maturity |
|----------|--------------|-----------|----------|
| **Prompt caching** | ~90% input cost | Cache checkpoints, speculative warming | GA (Anthropic, Bedrock, Vertex) |
| **Code execution mode** | 98.7% | Sandbox tool execution, data stays in sandbox | GA (Anthropic MCP) |
| **Tool-schema compression** | 44–68% | Rule-based JSON Schema compression (TSCG) | Research (arXiv May 2026) |
| **Task-aware model routing** | 68% | Neural controller routes to quantized models (AgentCompress) | Research (arXiv Jan 2026) |
| **Multi-agent batching** | 42–68% | Quality-gated granularity control (Agent Capsules) | Research (arXiv May 2026) |
| **Conversation summarization** | 40–60% | Cheap model summarizes old messages | Production |
| **Autonomous agent compression** | 23–57% | Agent decides when to compress (Focus) | Research (arXiv Jan 2026) |
| **Instruction distillation** | 30–40% | Shorthand system prompts (Caveman method) | Production |
| **Semantic caching** | Variable | GPTCache/Redis for similar prompts | Production |
| **Batch API processing** | ~50% | 24h turnaround batch endpoints | GA (all major providers) |
| **Structured output (JSON mode)** | 15–25% | Request data, not prose | GA |

---

## 9. Seven Critical Token-Wasting Patterns

Community research from a ~2M token Claude Code project identified these patterns:

| # | Pattern | Tokens Wasted | Fix | Savings |
|---|---------|--------------|-----|---------|
| 1 | **Implementing without checking existing code** | 70K | `grep` first (100 tokens) vs. agent exploration (40K) | 97% |
| 2 | **Uncoordinated agent swarms** | 300K | Sequential coordination; avoid parallel edits of same files | 93% |
| 3 | **Building without testing** | 124K | Test after every 1 file change | 92% |
| 4 | **Language mismatch after compacting** | +20% overhead | Detect language from user messages, not system locale | 20% |
| 5 | **Lost critical context after compacting** | 80K per repeat | Persist preferences/warnings in CLAUDE.md or memory | 100% |
| 6 | **Parallel file collisions** | 15K per conflict | File locking or agent awareness systems | — |
| 7 | **Overengineering** | 112K | Start small, iterate incrementally | — |

### Community Golden Rules

| Rule | Rationale |
|------|-----------|
| CHECK FIRST, BUILD SECOND | `grep` > agent exploration (100 vs. 40K tokens) |
| TEST IMMEDIATELY | 1 file → test → continue (prevents 124K wasted on broken builds) |
| ASK USER | Faster than reading 50 files when context is unclear |
| GREP > AGENT for simple lookups | Avoids unnecessary sub-agent spawning |
| START SMALL | Iterate; don't build everything at once |
| MATCH MODEL TO TASK | Haiku for exploration, Sonnet for implementation, Opus for validation |
| PERSIST CRITICAL CONTEXT | Store user preferences, known failures, and "NEVER do X" rules in CLAUDE.md |

---

## 10. CLAUDE.md & Context File Optimization

### 10.1 Research Findings

Research (arXiv:2602.11988) shows redundant context files reduce task success by ~3% and increase inference cost by +20% and reasoning tokens by +22%.

### 10.2 Target Metrics

| Metric | Target |
|--------|--------|
| Always-loaded context (CLAUDE.md) | < 100 lines / < 2KB |
| On-demand context files | 2–3 files, < 60 lines each |
| Rules format | "always/never/when-then" (actionable constraints, not descriptions) |

### 10.3 What Belongs vs. What Doesn't

| Include in CLAUDE.md | Exclude (discoverable from config) |
|----------------------|----------------------------------|
| Bash commands Claude can't guess | Build/test/lint commands (in package.json) |
| Non-obvious gotchas & architectural constraints | Code style rules (use linters) |
| Business rules agents can't infer | Directory trees, env var lists |
| Security conventions not enforced by tooling | Anything in config files |

### 10.4 Progressive Disclosure Over Upfront Loading

SkillsBench research (arXiv:2602.12670):
- Focused skills outperform comprehensive ones by **+18.8pp vs. −2.9pp**
- 2–3 skills is optimal; 4+ shows diminishing returns
- **Self-generated procedures hurt performance (−1.3pp)** vs. human-curated (+16.2pp)

---

## 11. Google's Approach: Cheap Tokens at Scale

### 11.1 Gemini 3.5 Flash Economics

| Metric | Value |
|--------|-------|
| Token output speed | 4× faster than other frontier models (12× in Antigravity) |
| Input pricing | $1.50/M tokens (~50% less than comparable models) |
| Context window | 1M tokens for long-chain agent tasks |
| Enterprise savings | >$1B/year for 80% migration from full model to Flash |

### 11.2 The 93-Agent OS Build

Google demonstrated 93 agents building a working OS in 12 hours using 2.6B tokens — costing **less than $1,000**. The key: Flash models + centralized orchestration + batched state.

---

## 12. The Experience Compression Spectrum

A unifying framework (arXiv:2604.15877) positioning compression at four levels:

| Level | Type | Compression Ratio | Example |
|-------|------|-------------------|---------|
| **L0** | Raw traces | 1:1 | Full conversation transcript |
| **L1** | Episodic memory | 5–20× | Summarized session outcome |
| **L2** | Procedural skills | 50–500× | Reusable skill definition |
| **L3** | Declarative rules | 1,000×+ | "Never edit X without Y" rule |

The "missing diagonal": no systems currently support adaptive cross-level compression that promotes knowledge from episodes → skills → rules automatically. This is the next frontier.

---

## 13. Key Takeaways

| # | Finding | Impact |
|---|---------|--------|
| 1 | **Prompt caching is the foundation** — 90% input cost reduction, 85% latency reduction | Must structure all stable context for cacheability |
| 2 | **Context Engineering > Prompt Engineering** — +54% performance, −84% tokens with full methodology | Write-Select-Compress-Isolate |
| 3 | **Model routing saves 40–77%** — 60–70% of calls can use cheap models | Tier tasks by complexity |
| 4 | **Multi-agent is overrated for coding** — single agents are 3× more token-efficient | Reserve multi-agent for truly independent subtasks |
| 5 | **Tool-schema compression is infrastructure** — 44–68% reduction, enables 800+ tools | Compress tool definitions; use code execution mode |
| 6 | **CLAUDE.md < 100 lines** — redundant context hurts performance +3%, costs +20% more | Only encode what agents cannot discover |
| 7 | **The subsidy era is ending** — plan for 3× cost increases | Build cost-resilient architectures now |
| 8 | **Progressive disclosure > upfront loading** — 2-3 focused skills optimal | Lazy-load skills and agents on trigger |
| 9 | **Check first, build second** — grep (100 tokens) vs. agent exploration (40K tokens) | 400× savings per lookup |
| 10 | **Semantic density > compression** — shorter is not always cheaper | Eliminate boilerplate, preserve meaning |

---

## References

### Academic Papers
- Zhu, S. (2026). "Agentic AI Systems Should Be Designed as Marginal Token Allocators." [arXiv:2605.01214](https://arxiv.org/html/2605.01214v1)
- Ustynov. (2026). "Beyond Human-Readable: Rethinking Software Engineering Conventions for the Agentic Development Era." [arXiv:2604.07502](https://arxiv.org/html/2604.07502v1)
- Sakizli, F. (2026). "Tool-Schema Compression Enables Agentic RAG Under Constrained Context Budgets." [arXiv:2605.26165](https://arxiv.org/html/2605.26165v1)
- SAG/ICSE 2026. "Setup AGent: A Dual-Model LLM Agent for Autonomous End-to-End Java Project Configuration."
- Google Research, DeepMind & MIT. (2025). "Towards a Science of Scaling Agent Systems."
- AgentCompress. (2026). "Task-Aware Compression for Affordable LLM Agents." [arXiv:2601.05191](https://arxiv.org/abs/2601.05191)
- Experience Compression Spectrum. (2026). "Unifying Memory, Skills, and Rules in LLM Agents." [arXiv:2604.15877](https://arxiv.org/html/2604.15877v1)
- Agent Capsules. (2026). "Quality-Gated Granularity Control for Multi-Agent LLM Pipelines." [arXiv:2605.00410](https://arxiv.org/html/2605.00410v1)
- Acon — Microsoft Research. (2025). "Optimizing Context Compression for Long-horizon LLM Agents." [arXiv:2510.00615](https://arxiv.org/html/2510.00615)
- Focus. (2026). "Autonomous Context Compression." [arXiv:2601.07190](https://arxiv.org/abs/2601.07190)
- SkillsBench. (2026). [arXiv:2602.12670](https://arxiv.org/abs/2602.12670)
- "Do Context Files Help?" (2026). [arXiv:2602.11988](https://arxiv.org/abs/2602.11988)

### Industry & Community
- Anthropic. "Prompt Caching with Claude." [claude.com/blog/prompt-caching](https://claude.com/blog/prompt-caching)
- Anthropic. "Speculative Prompt Caching Cookbook." [platform.claude.com](https://platform.claude.com/cookbook/misc-speculative-prompt-caching)
- Anthropic. "Context Engineering Revolution." (Sep 2025)
- Anthropic. "MCP Code Execution — 98.7% Token Reduction." (Nov 2025)
- Claude Code Community. "7 Critical Token-Wasting Patterns (700K+ tokens saved)." [GitHub #13579](https://github.com/anthropics/claude-code/issues/13579)
- Claude Code Community. "Lazy-Loading Architecture for Token Optimization (~70% reduction)." [GitHub #19105](https://github.com/anthropics/claude-code/issues/19105)
- Stevens Institute. "The Hidden Economics of AI Agents: Managing Token Costs and Latency Trade-offs." [online.stevens.edu](https://online.stevens.edu/blog/hidden-economics-ai-agents-token-costs-latency/)
- Morph. "Claude Code Best Practices: The 2026 Guide." [morphllm.com](https://www.morphllm.com/claude-code-best-practices)
- Morph. "Context Engineering: Why More Tokens Makes Agents Worse." [morphllm.com](https://www.morphllm.com/context-engineering)
- InfoQ. "AI Coding 2025 Year-End Review: Context Engineering as Decisive Battleground." [infoq.cn](https://www.infoq.cn/article/5lxt9ibO77f3HKbITN5s)
- dev.to. "Your CLAUDE.md Is Wasting Tokens." [dev.to](https://dev.to/abdlrahmansaberabdo/your-claudemd-is-wasting-tokens-and-its-probably-not-helping-3jdh)
- dev.to. "How to Cut AI API Costs by 55% in 2026." [dev.to](https://dev.to/xujfcn/how-to-cut-ai-api-costs-by-55-in-2026-a-developers-practical-guide-4jac)
- dev.to. "The End of All-You-Can-Eat AI: How April 2026 Killed the Flat-Rate Era." [dev.to](https://dev.to/ppiova/the-end-of-all-you-can-eat-ai-how-april-2026-killed-the-flat-rate-era-for-developers-5260)
- Google I/O 2026. "Agent Economics at Scale." [sohu.com](https://www.sohu.com/a/1025335827_117182)
- aicosts.ai. "The Claude Code Subagent Cost Explosion: 887K Tokens/Min Crisis." [aicosts.ai](https://www.aicosts.ai/blog/claude-code-subagent-cost-explosion-887k-tokens-minute-crisis)
