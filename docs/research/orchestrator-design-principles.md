# Orchestrator Design Principles — Evidence-Based Extraction

**Date:** 2026-05-29
**Status:** Design Principles Document
**Sources:** 7 academic papers (arXiv), Google I/O 2026, GCS E002 experience report, GCS infrastructure audit

---

## Principle 1: Task-Structure-First Architecture Selection

**Source:** Kim et al. (2025) — "Towards a Science of Scaling Agent Systems" (arXiv:2512.08296)

The orchestrator's first decision must be: **is this task parallel-decomposable or sequentially-dependent?**

| Task Type | Multi-Agent Effect | Recommended Architecture |
|---|---|---|
| Parallel-decomposable (independent subtasks with clean interfaces) | Up to +80.9% improvement | Orchestrator-Workers (parallel dispatch) |
| Sequentially-dependent (each step depends on prior output) | −39% to −70% degradation | Single agent or Prompt Chaining |
| Mixed (exploration + execution) | Bimodal: −35% to +9.2% | Single agent for exploration, parallel for execution |

**Rule:** The orchestrator MUST classify task dependency structure before choosing agent count. Misclassification is the #1 source of multi-agent performance collapse.

**Prediction power:** The Kim et al. framework predicts optimal architecture for unseen tasks with 87% accuracy (MAE = 0.071). An orchestrator that does not perform this classification is architecturally incomplete.

---

## Principle 2: The 3–5 Agent Golden Ratio

**Source:** Kim et al. (2025); Chen et al. (2026) — "Phase Transition for Budgeted Multi-Agent Synergy" (arXiv:2601.17311)

Beyond 3–4 agents, coordination cost dominates computational resource, and marginal returns turn negative. This is not an infrastructure limitation — it is a fundamental property of the coordination topology.

| Agent Count | Coordination Overhead | Effective Throughput |
|---|---|---|
| 1 | 0% | 100% |
| 2–3 | 5–15% | 85–95% |
| 4–5 | 15–30% | 70–85% |
| 6–10 | 30–60% | 40–70% |
| 11–50 | 60–90% | 10–40% |
| 51–100 | 90–98% | 2–10% |

**Rule:** Default to 1 agent. Scale to 2–3 when clear parallelism exists. Never exceed 5 without explicit justification rooted in task decomposability.

**The phase transition:** Multi-agent systems exhibit sharp phase transitions — they can help, saturate, or COLLAPSE under fixed inference budgets. The α_ρ scalar (communication fidelity × correlation × fan-in) determines the regime. An orchestrator operating near the phase boundary without awareness is dangerous.

---

## Principle 3: Context Isolation Is the Primary Value, Not Parallelism

**Source:** Claude Code sub-agent architecture docs; Anthropic Harness evolution (Gen 1→3)

The literature converges: the primary value of multi-agent architectures in current LLM systems is **context window isolation**, not computational parallelism.

A single agent's reasoning quality degrades measurably at 50–60% context utilization ("context rot"). Sub-agents solve this by giving each subtask a clean context window — but the token multiplier is approximately **7× for Agent Teams** and **3–4× for sub-agents**.

**Rule:** Design around context boundaries, not roles or org charts. Split when context pollution threatens reasoning quality — not because the architecture diagram looks like a team structure.

**Anti-pattern:** "Let's have a planner agent, a coder agent, a tester agent, and a reviewer agent" — this is role-based splitting. Correct: "The codebase exploration output is 400K tokens and adding implementation would push past 60% context utilization → split here."

---

## Principle 4: Diversity Beats Quantity

**Source:** Yang et al. (2026) — "Understanding Agent Scaling via Diversity" (arXiv:2602.03794)

**2 diverse agents** (different models, prompts, tools) can match or exceed **16 homogeneous agents**. Information-theoretic bound: MAS performance is limited by intrinsic task uncertainty, not agent count.

**Rule:** When scaling agent count, prioritize heterogeneity (different models, system prompts, tool sets, perspectives). Adding identical agents adds coordination cost without adding capability.

**Practical implication:** Use Haiku for exploration/grep-heavy work, Sonnet for implementation, Opus for coordination and review. Three heterogeneous agents outperform eight homogeneous Sonnet agents.

---

## Principle 5: Manager Quality Determines Team Performance

**Source:** Liu (2026) — "Can AI Models Direct Each Other?" (arXiv:2603.26458)

| Configuration | SWE-bench Score |
|---|---|
| Strong single agent | 60% |
| Strong manager + weak worker | 62% (marginal gain) |
| Weak single agent | 44% |
| Weak manager + weak worker | **42%** (worse than alone!) |

**Rule:** Never use a weaker model as orchestrator than the workers it manages. "Structure without substance is pure overhead." The orchestrator must be at least as capable as its strongest worker.

**Root cause:** Current models are trained as monolithic agents. Delegation, scoped execution, and mode-switching are skills absent from training distributions. The orchestrator's system prompt must compensate for this training gap with explicit delegation templates.

---

## Principle 6: Error Amplification Is Topology-Dependent

**Source:** Kim et al. (2025)

| Architecture | Error Amplification |
|---|---|
| Independent (no verification) | 17.2× |
| Centralized (manager review) | 4.4× |
| Decentralized (peer review) | Intermediate |

**Rule:** Every multi-agent architecture MUST include a centralized verification step. Independent agents without cross-review amplify errors catastrophically.

**Practical implication:** After workers complete, the orchestrator MUST cross-read outputs for consistency before synthesizing. This is not optional — it is the difference between 4.4× and 17.2× error amplification.

---

## Principle 7: Fixed Pipelines for Known Control Flow; LLM Choice for Semantic Judgment

**Source:** GCS E002 Pattern 8 (Deterministic Workflow Agents); Anthropic "Building Effective Agents"

When the control flow is known in advance (e.g., session close: audit → archive → evaluate → commit), encode it as a fixed pipeline. Reserve LLM-driven routing for points where semantic judgment is required (e.g., "does this session contain reusable experience?").

**Rule:** If you can write the control flow as a numbered list, it should be a fixed pipeline. If the decision requires understanding the content of outputs, it should be an LLM judgment.

**Anti-pattern:** An orchestrator that uses LLM calls to decide "what's the next step?" when the steps are always the same.

---

## Principle 8: The Orchestrator Owns Synthesis; Workers Own Bounded Artifacts

**Source:** GCS E002 Pattern 7 (Orchestrator-Workers)

The orchestrator's responsibilities:
- Task decomposition (what are the independent subtasks?)
- Quality gate (did each worker produce valid output?)
- Cross-worker consistency check (do outputs contradict each other?)
- Synthesis (merge outputs into coherent whole)
- Final report quality

Workers' responsibilities:
- Produce ONE bounded artifact each
- Include evidence (tool outputs, test results, file paths)
- Report failures honestly (don't fabricate success)
- Stay within scoped context (don't explore beyond assigned boundary)

**Rule:** The orchestrator NEVER does worker-level work. Workers NEVER synthesize across other workers' outputs. Boundary violation is the primary failure mode.

---

## Principle 9: Clean Interfaces Enable Scale

**Source:** Google Antigravity 2.0 OS demo (I/O 2026)

Google's 93-agent demo succeeded because OS components have **clean, stable interfaces** — memory management, file systems, and device drivers communicate through well-defined APIs with minimal shared state.

**Rule:** Before spawning parallel workers, verify that each worker's output has a well-defined interface (file path, schema, API contract). If workers must read each other's intermediate state, they are not truly parallel — use sequential chaining instead.

**The merge-at-end pattern:** Workers operate independently for the full duration, and the orchestrator merges only at completion. This is the pattern that enabled 93-agent scale. Without it, inter-worker coordination would have consumed the entire token budget.

---

## Principle 10: Zero Path Coupling for Portability

**Source:** GCS infrastructure audit (2026-05-29)

The GCS `session-close-orchestrator` is deeply coupled to:
- `C:\Users\QR\.claude\projects\C--Codes-AI-GCS-A\memory\` (user-specific, OS-specific, project-specific)
- `tools/agentic_design/agentic_toolkit.py` (GCS-specific tooling)
- `mcp__ccd_session__mark_chapter` (CCD platform MCP tool)
- `docs/completed-tasks/`, `docs/agentic/`, `docs/reports/` (GCS conventions)

**Rule for portable orchestrators:**
1. **No hardcoded absolute paths** — use `{project_root}` as the only anchor
2. **No project-specific tooling in core logic** — tool dependencies must be declared in a configuration section
3. **No platform-specific MCP tools** — use only standard Claude Code tools (Agent, Skill, TaskCreate, Bash, Read, Write, Edit, Glob, Grep)
4. **Configurable path conventions** — document the expected directory structure but allow override
5. **Self-contained** — a single SKILL.md that can be dropped into any project's `.claude/skills/` directory

---

## Principle 11: Explicit Dispatch, Not Prose Convention

**Source:** GCS infrastructure audit (2026-05-29)

In GCS, 5 skills reference other skills in prose ("also use X", "pair with Y"), but **no skill programmatically invokes another skill via the `Skill` tool**. The coordination relies entirely on Claude Code's auto-invocation based on description matching — a mechanism that is invisible, non-deterministic, and breaks when skills are moved to a different project.

**Rule:** An orchestrator MUST use explicit tool calls (`Skill`, `Agent`) to dispatch to workers, not prose conventions. "Then invoke the code-reviewer skill" is fragile; `Skill({skill: "code-reviewer", args: "..."})` is durable.

**Exception:** When the worker is a Claude Code built-in agent type (Explore, Plan), use the `Agent` tool with explicit `subagent_type` and `prompt`.

---

## Principle 12: Evidence-Gated Completion

**Source:** GCS E001 task-scoped-session-closer; Anthropic Harness Gen 2 (Evaluator agent)

Every worker output must include verifiable evidence (tool outputs, test results, file paths, diffs). The orchestrator must verify evidence before accepting worker output. Synthesis without verification is the mechanism behind 4.4×–17.2× error amplification.

**Rule:** Workers produce evidence. Orchestrator verifies evidence. Only verified outputs enter synthesis.

**Minimum evidence per worker:**
1. What tool calls were made
2. What outputs were produced
3. What files were changed (with paths)
4. What tests were run (with results)
5. What was NOT done (explicit non-goals)
6. What risks remain

---

## Principle 13: Failure Is Contained, Not Amplified

**Source:** Kim et al. (2025); Chen et al. (2026)

Multi-agent architectures amplify errors. The orchestrator must contain failures:

1. **Per-worker timeout** — if a worker exceeds its token budget, terminate and report, don't retry indefinitely
2. **Independent worker contexts** — a worker crash must not corrupt other workers' state
3. **Partial success acceptance** — if 4 of 5 workers succeed, the orchestrator can proceed with 4 outputs and flag the gap
4. **No cascading retries** — a failed worker is not re-dispatched to another worker; the orchestrator decides whether to retry, reassign, or accept the gap

**Rule:** The orchestrator's error handling is more important than its success handling. A system that works perfectly when everything succeeds but collapses on one failure is not production-grade.

---

## Summary: The 13 Principles

| # | Principle | Source |
|---|---|---|
| 1 | Task-structure-first: classify parallel vs. sequential before choosing architecture | Kim et al. (2025) |
| 2 | 3–5 agent golden ratio: never exceed 5 without explicit decomposability justification | Kim et al. (2025); Chen et al. (2026) |
| 3 | Context isolation is the primary value, not parallelism | Anthropic Harness; Claude Code docs |
| 4 | Diversity beats quantity: 2 diverse agents ≥ 16 homogeneous | Yang et al. (2026) |
| 5 | Manager quality determines team performance: never use weaker orchestrator | Liu (2026) |
| 6 | Error amplification is topology-dependent: centralized verification is mandatory | Kim et al. (2025) |
| 7 | Fixed pipelines for known control flow; LLM choice for semantic judgment | GCS E002; Anthropic |
| 8 | Orchestrator owns synthesis; workers own bounded artifacts | GCS E002 Pattern 7 |
| 9 | Clean interfaces enable scale: verify interface contracts before parallel dispatch | Google I/O 2026 |
| 10 | Zero path coupling: no hardcoded paths, no platform-specific MCP tools | GCS audit (2026) |
| 11 | Explicit dispatch: use Skill/Agent tools, not prose conventions | GCS audit (2026) |
| 12 | Evidence-gated completion: verify before synthesis | GCS E001; Anthropic Harness Gen 2 |
| 13 | Failure is contained, not amplified: per-worker timeout, partial success, no cascading retries | Kim et al. (2025); Chen et al. (2026) |

---

## References

1. Kim et al. — "Towards a Science of Scaling Agent Systems" — [arXiv:2512.08296](https://arxiv.org/abs/2512.08296)
2. Chen et al. — "Phase Transition for Budgeted Multi-Agent Synergy" — [arXiv:2601.17311](https://arxiv.org/abs/2601.17311)
3. Yang et al. — "Understanding Agent Scaling via Diversity" — [arXiv:2602.03794](https://arxiv.org/abs/2602.03794)
4. Liu — "Can AI Models Direct Each Other?" — [arXiv:2603.26458](https://arxiv.org/abs/2603.26458)
5. Zheng et al. — "AgentCgroup" — [arXiv:2602.09345](https://arxiv.org/abs/2602.09345)
6. Gelvan et al. — "Implicit Context Compression for SE Agents" — [arXiv:2605.11051](https://arxiv.org/abs/2605.11051)
7. Dente et al. — "Constraint Decay" — [arXiv:2605.06445](https://arxiv.org/abs/2605.06445)
8. Anthropic — "Building Effective Agents" — [anthropic.com/engineering](https://www.anthropic.com/engineering/building-effective-agents)
9. Google I/O 2026 — Antigravity 2.0 & Gemini 3.5 Flash — [TechCrunch](https://techcrunch.com/2026/05/19/with-gemini-3-5-flash-google-bets-its-next-ai-wave-on-agents-not-chatbots/)
10. GCS E002 — Session and Agent Best-Practice Patterns Report
11. GCS Infrastructure Audit — Multi-Agent Coordination Analysis (2026-05-29)
12. Claude Code Sub-agents Guide — [Tembo (2026)](https://www.tembo.io/blog/claude-code-subagents)
