# 3–5 Agent Orchestration: Concrete Patterns, Architectures, and Evidence

**Date:** 2026-05-29
**Status:** Deep Research Report
**Sources:** 12 academic papers (arXiv), 4 industry frameworks, Google I/O 2026, Anthropic Harness

---

## Executive Summary

This report examines **five concrete 3–5 agent orchestration patterns** drawn from US and European research (2025–2026), each with verifiable architecture, benchmark results, and documented failure modes. The evidence converges on a central finding: **coordination architecture matters more than model choice**, and the difference between a well-architected 3-agent team and an unstructured 5-agent swarm can be the difference between +80.9% improvement and 17.2× error amplification.

---

## Pattern 1: The Profiling Pipeline — PerfOrch (4 Agents)

**Source:** Qi et al. (2025, revised 2026) — "Multi-LLM Orchestration for High-Quality Code Generation"
**arXiv:** [2510.01379](https://arxiv.org/abs/2510.01379)
**Institution:** Independent researchers (US/China collaboration)
**Agent Count:** 4

### Architecture

```
Problem → [Categorization Agent] → [Generation Agent] → [Debugging Agent] → [Refinement Agent] → Solution
              │                        │                      │                      │
              └── Memory Module ───────┴── Memory Module ─────┴── Memory Module ─────┘
                   (Ranking Matrix by Language × Category)
```

### Agent Roles

| Agent | Responsibility | Model Selection |
|---|---|---|
| **Categorization** | Classify problem by language (Python/Java/C++/Go/Rust) and algorithmic category (DP, string, graph, etc.) | Fixed classifier |
| **Generation** | Produce initial code solution | Top-ranked LLM for that {language, category} pair |
| **Debugging** | Identify faults, apply corrections | Top-ranked LLM for debugging that {language, category} |
| **Refinement** | Optimize for performance (speed, memory) | Top-ranked LLM for optimization that {language, category} |

### Key Innovation: The Ranking Matrix

Each agent maintains a **Memory module** — a ranking matrix with rows = programming language, columns = problem category. Each cell contains an ordered list of LLMs ranked by empirically measured performance on that specific {language, category, stage} combination.

The matrix is built via **offline profiling**: every candidate LLM is evaluated on a training split, recording pass@1 for generation, bug-fix rate for debugging, and speedup for refinement. At runtime, the system performs O(1) lookup to route each problem to the best-performing model for each stage.

**Cross-benchmark generalization:** The matrix, built solely on HumanEval-X profiling, transferred zero-shot to the unseen EffiBench-X benchmark — proving that "complementary-strength patterns are properties of the models, not artifacts of a specific problem distribution."

### Concrete Results

| Metric | Value |
|---|---|
| HumanEval-X avg. pass@1 | **97.19%** (2,500 problems, 5 languages) |
| EffiBench-X avg. pass@1 | **95.83%** |
| Improvement over best single model | **+1.22 to +14.58 pp** (range across languages) |
| Problems with faster execution | **61–90%** of solved problems |
| Mean execution speedup | **4.7–29.9%** |
| Token cost vs. exhaustive multi-model eval | **~50%** |

### Design Lessons

1. **Per-stage model routing beats majority voting.** Rather than running N models on every problem and voting, PerfOrch routes each stage to the single best model for that {language, category, stage} — achieving better results at half the token cost.
2. **Offline profiling enables zero-shot transfer.** The ranking matrix generalizes across benchmarks because model strengths are stable properties.
3. **The pipeline enforces quality at each stage.** A weak generation can be rescued by strong debugging; a correct-but-slow solution can be accelerated by refinement. No single model needs to be best at everything.

### Failure Modes

- Pipeline is strictly sequential — no parallelism possible
- Ranking matrix requires upfront profiling investment
- If the Categorization agent misclassifies, all downstream routing is wrong
- No cross-stage learning (Debugging doesn't inform future Generation routing)

---

## Pattern 2: Execution-Grounded Team — AgentForge (5 Agents)

**Source:** Anonymous authors (2026) — "AgentForge: Execution-Grounded Multi-Agent LLM Framework for Autonomous Software Engineering"
**arXiv:** [2604.13120](https://arxiv.org/abs/2604.13120)
**Institution:** US-based (open-source on GitHub: `raja21068/AutoCodeAI`)
**Agent Count:** 5

### Architecture

```
                    ┌─────────────────────────────────┐
                    │         Shared Memory            │
                    │  (Repository State + Execution   │
                    │   Results + Agent Outputs)       │
                    └──┬────────┬────────┬────────┬───┘
                       │        │        │        │
                  ┌────▼───┐ ┌──▼────┐ ┌─▼─────┐ ┌▼──────┐
                  │Planner │ │ Coder │ │Tester │ │ Critic│
                  │        │ │       │ │       │ │       │
                  └────────┘ └──┬────┘ └───┬───┘ └───────┘
                                │           │
                                └─────┬─────┘
                                      │
                              ┌───────▼───────┐
                              │    Debugger    │
                              └───────┬───────┘
                                      │
                              ┌───────▼───────┐
                              │ Docker Sandbox │ ← MANDATORY gate
                              │  (execution    │
                              │   verification)│
                              └───────────────┘
```

### Agent Roles

| Agent | Responsibility | Input | Output |
|---|---|---|---|
| **Planner** | Decompose task, devise high-level strategy | Task description, repo state | Structured plan |
| **Coder** | Generate code changes per the plan | Plan, repo state | Code diff |
| **Tester** | Write and run tests against proposed changes | Code diff, repo state | Test results |
| **Debugger** | Diagnose failures, propose fixes | Test failures, code diff | Fix diff |
| **Critic** | Review for quality, correctness, spec adherence | All outputs, repo state | Review verdict |

### Key Innovation: Mandatory Execution Grounding

The Docker sandbox is **not optional**. Every code change must survive sandboxed execution before propagation. The paper formalizes this as "a stronger supervision signal than next-token likelihood." Prior systems either simulated execution or treated verification as optional — AgentForge makes it the central architectural constraint.

The process is an **iterative decision process over repository states**: agents propose → sandbox validates/rejects → state advances → agents propose again. This creates a tight feedback loop where execution reality, not model confidence, determines whether code is accepted.

### Coordination: Shared Memory, Not Message Passing

All five agents read from and write to a shared memory space (repository state + execution results + agent outputs). There is no point-to-point messaging, no orchestration overhead, no "telephone game" degradation. Each agent sees the full context of what every other agent has produced.

### Concrete Results

| Metric | Value |
|---|---|
| SWE-Bench Lite resolution | **40.0%** |
| Improvement over single-agent baselines | **+26–28 points** |
| Ablation: execution feedback only | Significant independent contribution |
| Ablation: role decomposition only | Significant independent contribution |
| Combined (full AgentForge) | Both contributions are additive |

### Design Lessons

1. **Execution grounding is the strongest supervision signal available.** Model confidence scores and next-token likelihood are weak proxies for correctness. A Docker sandbox that runs the actual code provides ground truth.
2. **Shared memory eliminates coordination overhead.** Five agents in shared memory have lower coordination cost than three agents passing messages.
3. **Role decomposition and execution feedback are independent value drivers.** The ablation study proves they contribute separately — you get both benefits, not one subsuming the other.
4. **The Critic is the quality backstop.** Even with execution grounding, code that runs can still be wrong (incorrect logic, missed edge cases). The Critic catches what execution doesn't.

### Failure Modes

- Shared memory can become a bottleneck if not pruned (all agents see all history)
- Docker sandbox startup latency adds to iteration time
- The Planner's initial decomposition is critical — if it misses a subtask, no downstream agent can compensate
- Critic can become a rubber stamp if the model is too weak relative to the Coder

---

## Pattern 3: Orchestrator-Worker with Memory — Anthropic Multi-Agent Harness (4 Agents)

**Source:** Anthropic (March 2026) — Internal engineering blog + Code w/ Claude SF 2026
**Agent Count:** 4 (Planner → Implementer → Reviewer → Executor)

### Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Shared Memory System                 │
│            (Episodic Memory + Project Context)        │
└──────────────────────────────────────────────────────┘
         │                  │                  │
┌────────▼────┐   ┌────────▼────┐   ┌────────▼────┐
│   Planner   │   │ Implementer │   │   Reviewer   │
│ (Architect) │   │   (Coder)   │   │  (QA Gate)   │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └────────┬────────┴────────┬────────┘
                │                 │
         ┌──────▼──────┐   ┌──────▼──────┐
         │  Executor   │   │  Checkpoint  │
         │ (Deployment)│   │  & Rollback  │
         └─────────────┘   └─────────────┘
```

### Agent Roles

| Agent | Responsibility | Key Constraint |
|---|---|---|
| **Planner** | Decompose requirements, create technical spec, design architecture | Does NOT write code |
| **Implementer** | Write code following the plan, handle full-stack implementation | Must reference plan in every output |
| **Reviewer** | Review for security, quality, architecture compliance, best practices | Independent — never the same model instance as Implementer |
| **Executor** | Run deployment, execute tests, verify runtime behavior | Gate: blocks propagation on failure |

### Key Innovation: Episodic Memory + Checkpointed Rollbacks

The shared memory system persists across multi-hour autonomous workflows. Unlike AgentForge's transient shared memory (one task), Anthropic's harness maintains **episodic memory** — the system remembers what worked and what failed across multiple tasks.

**Checkpointed rollbacks**: Before each major code change, the system checkpoints repository state. If the Reviewer or Executor rejects a change, the system can roll back to the last known-good state rather than attempting to patch forward from a broken state.

**Tool usage limits**: Guardrails prevent infinite loops — each agent has a maximum tool call budget, and exceeding it triggers a forced checkpoint and human escalation.

### Concrete Results

| Metric | Value |
|---|---|
| Frontend development speedup | **~40%** vs. single-agent |
| Error reduction | **25%** vs. single-agent |
| Autonomous workflow duration | Multi-hour (exact figures not public) |
| Context management | Episodic memory eliminates "context rot" over long sessions |

### Design Lessons

1. **Episodic memory is the differentiator for long-running work.** AgentForge's shared memory works for one task; Anthropic's episodic memory works across tasks.
2. **Checkpoint before change, not after failure.** Rollback to known-good is cheaper than forward-patching from broken.
3. **The Reviewer must be an independent agent.** "A single AI reviewing its own work is like a developer merging their own PR without review" — this is the adversarial pairing principle.
4. **Tool budgets prevent infinite loops.** Without explicit limits, agents can cycle indefinitely on hard problems.

### Failure Modes

- Episodic memory can accumulate stale context if not pruned
- Checkpoint frequency trades safety against latency (too frequent = slow; too infrequent = large rollbacks)
- Planner-Implementer divergence: the Implementer may drift from the plan without the Planner noticing until Review time

---

## Pattern 4: Adversarial Pairing + Self-Improving Loops — Software Factory (Variable, Core 4)

**Source:** ZenML LLMOps Database / Owner Platform (2026) — Multiple case studies
**Scale:** Built a Notion-like app (Memo) with 375 PRs, 88% autonomous

### Architecture

```
┌──────────────────────────────────────────────────┐
│                 Automation Auditor               │ ← Self-improving meta-loop
│          (Runs nights/weekends, optimizes         │
│           the factory infrastructure itself)      │
└──────────────────────────────────────────────────┘
                       │ (reads performance data)
                       ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Planner  │   │  Builder │   │ Reviewer │   │ Deployer │
│          │   │          │   │(Adversary)│   │          │
└────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
     │              │              │              │
     └──────────────┴──────────────┴──────────────┘
                       │
               ┌───────▼───────┐
               │  GitHub as    │
               │  State Engine │
               │ (Issues, PRs, │
               │  CI/CD)       │
               └───────────────┘
```

### Core 4 Agents + Meta-Agent

| Agent | Responsibility | Adversarial Pair? |
|---|---|---|
| **Planner** | Requirements → technical spec → issue creation | Paired with: Reviewer reviews the plan |
| **Builder** | Code implementation, PR creation | Paired with: Reviewer reviews every PR |
| **Reviewer** (Adversary) | Challenges every output with no prior context; ~70-75% confidence threshold | Central adversarial agent |
| **Deployer** | Merge, deploy, monitor | Paired with: Reviewer audits post-deploy |
| **Automation Auditor** (Meta) | Analyzes agent performance, optimizes factory infrastructure | Runs asynchronously |

### Key Innovation: Adversarial Architecture

**Every generative agent action is challenged by a separate agent with no prior context.** The Reviewer receives only the output artifact and the original specification — not the chain of reasoning that produced it. This prevents the Reviewer from being "talked into" accepting flawed work by a persuasive chain of thought.

The confidence threshold (~70-75%) means the Reviewer doesn't need to be certain — it only needs to flag concerns. This is a lower bar than "prove it's wrong" and catches more issues.

### Key Innovation: The Self-Improving Meta-Loop

The **Automation Auditor** is an agent that analyzes the agents themselves. It runs during off-peak hours (nights/weekends), reads all PRs, reviews, and deployment outcomes, and suggests improvements to:
- Agent prompts (the Planner's spec template, the Reviewer's checklist)
- Quality gates (confidence thresholds, required checks)
- Infrastructure (CI pipeline steps, test coverage gaps)

This turns the factory from a static system into a **self-improving system** — the agents get better over time without human intervention.

### Concrete Results

| Metric | Value |
|---|---|
| Total PRs merged | **375** |
| Fully autonomous PRs | **88%** |
| Median issue close time | **38 minutes** |
| CI pass ratio | **~98%** |
| Code generated | **50,000+ lines, 300+ PRs in 2 weeks** |
| Human role shift | From writing code → maintaining factory, prompt engineering, verification |

### Design Lessons

1. **Adversarial review with no prior context is the strongest quality signal.** The Reviewer that hasn't seen the reasoning chain is harder to fool.
2. **The meta-agent (Automation Auditor) is the force multiplier.** A self-improving factory compounds its gains over time.
3. **GitHub as state engine eliminates sync issues.** Rather than maintaining separate task trackers, the factory uses Issues, PRs, and CI as the single source of truth.
4. **Confidence thresholds, not binary decisions.** A 70-75% threshold for flagging concerns is more robust than requiring certainty.

### Failure Modes

- Adversarial agent can become overly conservative, blocking valid work
- Meta-agent can over-optimize for metrics that don't capture real quality
- GitHub API rate limits can throttle high-throughput factories
- Self-improving loops can drift from original design intent over many iterations

---

## Pattern 5: Coordination Configurations — The Pareto Frontier (5 Configurations Tested)

**Source:** Nechepurenko & Shuvalov (May 2026) — "Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems"
**arXiv:** [2605.03310](https://arxiv.org/abs/2605.03310)
**Institution:** Independent researchers (European)
**Scale:** 100 Polymarket binary markets, claude-opus-4-6, 5 coordination configurations

### The Five Configurations Tested

The experiment controlled ALL variables (same model, same tools, same per-call output cap, same prompt template) and varied ONLY the coordination architecture:

```
Configuration A: Independent Ensemble
  ┌─ Agent 1 ─┐
  ┌─ Agent 2 ─┼──→ Aggregate (average/vote) ──→ Decision
  ┌─ Agent 3 ─┘
  Agents work independently, no communication, outputs aggregated

Configuration B: Peer-Critique Debate
  Agent 1 ──→ Agent 2 critiques ──→ Agent 1 revises ──→ Agent 2 critiques ──→ ...
  Iterative back-and-forth between peers

Configuration C: Orchestrator-Specialist
  Orchestrator ──→ Specialist A (research)
               ──→ Specialist B (analysis)
               ──→ Specialist C (verification)
               ──→ Orchestrator synthesizes
  Central coordinator delegates to specialists

Configuration D: Sequential Pipeline
  Stage 1 ──→ Stage 2 ──→ Stage 3 ──→ Stage 4 ──→ Output
  Linear handoff between stages, each adding value

Configuration E: Consensus Alignment
  Agent 1 ──┐
  Agent 2 ──┼──→ Deliberation ──→ Consensus ──→ Decision
  Agent 3 ──┘
  Agents deliberate until reaching agreement
```

### Core Finding: The Production Failure Baseline

**Multi-agent systems fail in production at 41–87%,** and **79% of failures are due to coordination defects**, not base-model capability. This is the problem the paper set out to measure systematically.

### Key Result: Simple Beats Complex

The two configurations that dominated the **cost-quality Pareto frontier** were:

1. **Independent Ensemble** (Configuration A) — Best quality per unit cost
2. **Sequential Pipeline** (Configuration D) — Best quality overall when cost is less constrained

The more complex patterns (Peer-Critique Debate, Orchestrator-Specialist, Consensus Alignment) consumed more tokens but did NOT produce better decisions. The coordination overhead of complex patterns outweighed any benefit from structured interaction.

### Methodology Highlights

- **Murphy decomposition of Brier score**: Separated calibration (how accurate are confidence estimates?) from discriminative power (how well does the system distinguish outcomes?)
- **Total compute per question treated as endogenous**: Cost was measured as an architectural output, not an external variable
- **Bootstrap power-projection**: Statistical power analysis to determine how many questions needed for significance
- **Live replication**: Parallel deployment on Foresight Arena under web-search conditions

### Design Lessons

1. **Simple coordination dominates the Pareto frontier.** Independent ensembles and sequential pipelines beat peer-critique, orchestrator-specialist, and consensus alignment on cost-quality.
2. **Coordination is an architectural layer, not an implementation detail.** Varying only the coordination pattern (same model, same tools) produced dramatically different outcomes.
3. **79% of failures are coordination, not capability.** Investing in better coordination architecture yields higher returns than investing in better models.
4. **The "more coordination = better" assumption is false.** Complex coordination patterns consumed more tokens without producing better decisions.

### Failure Modes by Configuration

| Configuration | Primary Failure Mode |
|---|---|
| Independent Ensemble | Aggregation method (average/vote) can dilute strong individual insights |
| Peer-Critique Debate | Endless debate cycles; agents talk each other into worse decisions |
| Orchestrator-Specialist | Orchestrator becomes bottleneck; specialist outputs degrade through summarization |
| Sequential Pipeline | Errors compound; no recovery from early-stage mistakes |
| Consensus Alignment | Groupthink; agents converge to mediocre consensus rather than best answer |

---

## Cross-Pattern Synthesis: What the Evidence Says

### The 3-Agent Sweet Spot

Across all five patterns, **3 agents emerge as the most common effective configuration:**

| Pattern | Core Agent Count | Why 3? |
|---|---|---|
| PerfOrch | 4 (but 3 core: Gen → Debug → Refine) | Categorization is lightweight routing, not an agent |
| AgentForge | 5 (but Coder+Tester+Debugger form core loop; Planner and Critic are bookends) | The inner loop is 3 agents |
| Anthropic Harness | 4 (but Executor is operational, not cognitive) | Planner → Implementer → Reviewer is the cognitive core |
| Software Factory | 4 + meta | Builder → Reviewer (adversarial pair) + Planner → Deployer |
| Nechepurenko | Independent Ensemble and Sequential Pipeline dominated | Both use 3-4 stages |

### The Two Dimensions of Agent Architecture

All effective patterns can be classified along two axes:

```
                  Sequential Dependency
                  Low ←────────────→ High

Parallel    │  Independent Ensemble   │  (rarely effective —
            │  (Pattern 5, Config A)  │   parallel agents
            │                         │   can't share state)
            │                         │
Coordination│─────────────────────────│──────────────────
            │                         │
            │  Orchestrator-Worker    │  Sequential Pipeline
Sequential  │  (Pattern 3, Harness)   │  (Pattern 1, PerfOrch)
            │                         │  (Pattern 5, Config D)
            │                         │
            │  Shared Memory Team     │
            │  (Pattern 2, AgentForge)│
            ▼                         ▼
```

### When Each Pattern Excels

| Task Type | Best Pattern | Example |
|---|---|---|
| Well-defined stages, known quality criteria per stage | **Sequential Pipeline** (Pattern 1) | Code gen → debug → optimize |
| Complex task, unclear subtask boundaries | **Shared Memory Team** (Pattern 2) | SWE-bench issues |
| Long-running, multi-session work | **Orchestrator-Worker + Episodic Memory** (Pattern 3) | Multi-day feature development |
| Quality-critical, high-cost-of-failure | **Adversarial Pairing** (Pattern 4) | Security, infrastructure, production code |
| Decision-making under uncertainty | **Independent Ensemble** (Pattern 5, Config A) | Forecasting, analysis, architecture decisions |

### The Anti-Patterns (Confirmed by Evidence)

| Anti-Pattern | Evidence Against |
|---|---|
| **Peer-Critique Debate without time limit** | Nechepurenko: consumed more tokens, produced worse decisions |
| **Orchestrator as summarizer (not synthesizer)** | Nechepurenko: specialist outputs degraded through summarization |
| **Consensus-seeking deliberation** | Nechepurenko: groupthink converged to mediocre consensus |
| **Homogeneous agent teams** | Yang et al. (2026): 2 diverse agents ≥ 16 homogeneous |
| **Multi-agent for sequential tasks** | Kim et al. (2025): −39% to −70% degradation |
| **Multi-agent without centralized verification** | Kim et al. (2025): 17.2× error amplification |

---

## Design Decision Tree

```
Task received
  │
  ├─ Subtasks have clean interfaces, no shared state?
  │   └─ YES → Independent Ensemble (Pattern 5, Config A)
  │        Agent count: 3–5
  │        Key rule: Aggregate outputs, don't debate
  │
  ├─ Subtasks form a clear pipeline (each stage adds value)?
  │   └─ YES → Sequential Pipeline (Pattern 1)
  │        Agent count: 3–4 stages
  │        Key rule: Gate at each stage; no forward propagation on failure
  │
  ├─ Task is complex, subtask boundaries unclear?
  │   └─ YES → Shared Memory Team (Pattern 2)
  │        Agent count: 3–5
  │        Key rule: Execution grounding is mandatory
  │
  ├─ Task spans multiple sessions, needs persistent memory?
  │   └─ YES → Orchestrator-Worker + Episodic Memory (Pattern 3)
  │        Agent count: 3–4
  │        Key rule: Checkpoint before change, not after failure
  │
  ├─ Quality-critical, high cost of failure?
  │   └─ YES → Adversarial Pairing (Pattern 4)
  │        Agent count: 2 per function (generator + adversary)
  │        Key rule: Adversary sees output only, not reasoning chain
  │
  └─ Decision-making under uncertainty?
      └─ YES → Independent Ensemble (Pattern 5, Config A)
           Agent count: 3
           Key rule: Murphy decomposition separates calibration from discrimination
```

---

## References

### Academic Papers
1. Qi et al. — "Multi-LLM Orchestration for High-Quality Code Generation (PerfOrch)" — [arXiv:2510.01379](https://arxiv.org/abs/2510.01379)
2. Anonymous — "AgentForge: Execution-Grounded Multi-Agent LLM Framework" — [arXiv:2604.13120](https://arxiv.org/abs/2604.13120)
3. Nechepurenko & Shuvalov — "Coordination as an Architectural Layer for LLM-Based Multi-Agent Systems" — [arXiv:2605.03310](https://arxiv.org/abs/2605.03310)
4. Kim et al. — "Towards a Science of Scaling Agent Systems" — [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)
5. Chen et al. — "Phase Transition for Budgeted Multi-Agent Synergy" — [arXiv:2601.17311](https://arxiv.org/abs/2601.17311)
6. Yang et al. — "Understanding Agent Scaling via Diversity" — [arXiv:2602.03794](https://arxiv.org/abs/2602.03794)
7. Liu — "Can AI Models Direct Each Other?" — [arXiv:2603.26458](https://arxiv.org/abs/2603.26458)
8. AdaptOrch — "Task-Adaptive Multi-Agent Orchestration" — [arXiv:2602.16873](https://arxiv.org/abs/2602.16873)
9. LATTE — "Adaptive Task Graphs for Agent Teams" — [arXiv:2605.06320](https://arxiv.org/abs/2605.06320)
10. "More Capable, Less Cooperative?" — [arXiv:2604.07821](https://arxiv.org/abs/2604.07821)
11. CRAFT — "Grounded Multi-Agent Coordination Under Partial Information" — [arXiv:2603.25268](https://arxiv.org/abs/2603.25268)
12. LIFE Survey — "Beyond Individual Intelligence" — [arXiv:2605.14892](https://arxiv.org/abs/2605.14892)

### Industry Sources
13. Anthropic — Multi-Agent Harness (March 2026) + Code w/ Claude SF 2026
14. Software Factory / Owner Platform — Multiple case studies (ZenML LLMOps Database, 2026)
15. Agent Council — [github.com/andrewvaughan/agent-council](https://github.com/andrewvaughan/agent-council)
16. MorphLLM — "Multi-Agent Orchestration: Patterns That Work (and 3 That Don't)" (April 2026)
