# Agentic-SE Dimensions And Metrics Research Report

Research snapshot: 2026-05-24.

## Executive Summary

Agentic software engineering is not simply "using an AI to write code." The
useful unit is a controlled engineering system: scoped intent, repository
knowledge, isolated execution, tool access, tests, reviews, traces, security
boundaries, and a learning loop that improves the repository after repeated
friction.

The strongest current public patterns converge on the same design:

- tasks run in configured, isolated environments with build and test evidence;
- complex work is planned before editing and important plans live in the
  repository;
- multi-agent work helps when the work can be decomposed, but hurts when
  communication overhead breaks sequential reasoning;
- agent skill, tool, memory, and permission layers are security-critical;
- benchmark scores alone are weak evidence; project-local gates and fresh
  regression fixtures matter more;
- speed metrics must be paired with stability, review, and human-control
  metrics.

This report proposes ten dimensions for running an agentic-SE project and the
core indicators that should be tracked in each dimension.

## Source Basis

External sources used:

- [OpenAI, Introducing Codex](https://openai.com/index/introducing-codex/):
  isolated task environments, repository instructions, terminal and test
  evidence, and human review.
- [OpenAI, Harness engineering](https://openai.com/index/harness-engineering/):
  in-repository knowledge stores, checked-in execution plans, feedback loops,
  and environment design as the new engineering work.
- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents):
  orchestrator-workers and evaluator-optimizer workflows.
- [Anthropic Claude Code common workflows](https://code.claude.com/docs/en/common-workflows):
  plan-before-editing workflow for complex or risky changes.
- [GitHub Copilot cloud agent docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent):
  custom instructions, MCP, hooks, custom agents, skills, and memory.
- [Google Research, scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/):
  multi-agent coordination helps parallelizable tasks but can degrade
  sequential work.
- [Google, secure AI agents](https://research.google/pubs/an-introduction-to-googles-approach-for-secure-ai-agents/):
  human controllers, limited powers, and observable actions/plans.
- [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/):
  skills as an execution layer and security risk surface.
- [DORA software delivery metrics](https://dora.dev/guides/dora-metrics/):
  throughput and instability metrics, with caution against gaming metrics.
- [OpenAI, SWE-bench Verified limitations](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/):
  benchmark contamination and flawed tests as a warning against relying on
  public benchmark scores alone.

Local GCS sources used:

- `docs/agentic/README.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/agile-pdca-roadmap.md`
- `docs/agentic/long-term-agentic-se-plan.md`
- `docs/architecture/66-implementation-execution-roadmap.md`
- `docs/architecture/67-current-progress-and-next-steps.md`
- `docs/architecture/68-agentic-se-lifecycle-self-evolution.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `docs/architecture/69-ci-ready-quality-gates.md`

## Measurement Principles

Agentic-SE metrics should be used as a control panel, not as a scoreboard.

- Pair speed with stability. Track delivery throughput, but always pair it
  with failure, rework, and review burden.
- Prefer project-local evidence. Public SWE benchmarks are useful background,
  but local contracts, fixtures, CI gates, and review findings are the real
  acceptance evidence.
- Measure lifecycle conversion, not isolated agent output. A patch without
  task context, tests, review, and archive is not mature agentic-SE work.
- Track leading and lagging indicators. A missing task card is a leading risk;
  a failed CI gate is a lagging symptom.
- Keep metrics falsifiable. Every "learning" metric should point to a skill,
  fixture, test, tool, or doc change that can be inspected.

## Dimension Model

### 1. Strategic Task Portfolio

Question: Are agents being assigned the right work, with clear value and risk?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Agent-suitable task ratio | Leading | Share of backlog items that are scoped enough for agent execution. |
| High-risk task pre-plan coverage | Guardrail | Share of high-risk tasks with a task card, execution plan, and human gate before edits. |
| Value evidence per task | Leading | Whether the task names product, research, quality, maintenance, or speed value. |
| Task batch size | Leading | Size of a change in files, modules, and behavioral surface. Smaller is usually safer. |
| Completed value rate | Lagging | Share of tasks that close with evidence and an archive, not only code changes. |

Healthy signal: agents handle scoped implementation, tests, docs, fixtures, and
maintenance tasks while humans retain intent, architecture, and high-risk
semantic decisions.

### 2. Lifecycle Discipline

Question: Does work move through a visible request-to-closure loop?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Task-card coverage | Leading | Non-trivial tasks with persisted task cards. |
| Plan-before-edit compliance | Guardrail | Risky work has read-only planning before code changes. |
| Acceptance-gate completeness | Leading | Task cards name build, test, review, and artifact checks. |
| Evidence-bundle completion | Lagging | Completed work records commands, outputs, failures, and skipped checks. |
| Archive-link coverage | Lagging | Completed tasks are discoverable from task cards and index pages. |
| Closure score | Lagging | Heuristic score for whether the task state transfers to future agents. |

Healthy signal: future agents can resume from repository artifacts without
reading raw chat history.

### 3. Repository Knowledge And Memory

Question: Can agents discover the right context without hidden memory?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Knowledge entry-point coverage | Leading | README, architecture map, skills, runbooks, and task templates exist. |
| Context retrieval success | Leading | An agent can find owning docs, tests, commands, and boundaries in one pass. |
| Staleness rate | Lagging | Docs or skills contradict implementation, tests, or current roadmap. |
| Repeated-question rate | Lagging | Same repository context must be rediscovered repeatedly. |
| Memory promotion rate | Lagging | Useful lessons are promoted into docs, skills, evals, tools, or tests. |

Healthy signal: hidden assistant memory is helpful but not authoritative; durable
truth lives in versioned repo artifacts.

### 4. Architecture And Contract Substrate

Question: Are agents changing public contracts instead of smuggling semantics
through UI, scripts, or prose?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Module ownership clarity | Guardrail | Every change has an owning module or boundary. |
| Dependency-boundary pass rate | Guardrail | Lower mathematical modules do not import runtime, IO, viewer, UI, or agentic infrastructure. |
| Structured report coverage | Leading | Public behavior changes expose stable IDs, report codes, subjects, and state versions. |
| Contract-test coverage for behavior changes | Guardrail | New behavior is protected by contract tests or an explicit exception. |
| Negative fixture ratio | Leading | Risky behavior has invalid, obstruction, singular, malformed, or regression fixtures. |

Healthy signal: agents work against typed contracts and reusable fixtures, so
reviewers can verify semantics without trusting prose.

### 5. Harness, Tools, And Execution Environment

Question: Can the agent reliably observe, act, test, and stop in the local
engineering environment?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Environment setup success | Leading | Build/test toolchain can be configured deterministically. |
| Command reproducibility | Guardrail | Build, test, lint, and validation commands are documented and runnable. |
| Sandbox/isolation coverage | Guardrail | Agent tasks run with scoped filesystem, network, dependency, and destructive-action controls. |
| Tool failure diagnosis time | Lagging | Time from failed command to classified cause. |
| Tooling standard-library ratio | Leading | Support tools avoid unnecessary dependencies unless governed. |

Healthy signal: the harness makes success and failure observable; it does not
depend on brittle ad hoc manual steps.

### 6. Agent Orchestration And Skill System

Question: Is work routed to the right specialist and coordinated at the right
level of decomposition?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Routing accuracy | Leading | Task owner and specialist agents match affected modules. |
| Skill validation pass rate | Guardrail | Physical skills have names, descriptions, prompts, and no placeholders. |
| Handoff completeness | Leading | Specialist output includes assumptions, contracts, files, tests, and risks. |
| Parallelization yield | Lagging | Parallel agents reduce cycle time without increasing review defects. |
| Sequential-penalty incidents | Lagging | Multi-agent decomposition caused inconsistency, duplicated work, or lost reasoning context. |

Healthy signal: a central steward routes complex work, while specialist agents
operate on narrow, independent boundaries.

### 7. Verification, Evals, And Quality Gates

Question: Can the project distinguish correct work from convincing-looking
work?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Full gate pass rate | Guardrail | Build, contract tests, docs validation, dependency audit, fixture gates, and CLI smoke pass. |
| Focused gate usage | Leading | Agents run narrow tests before broad gates. |
| Public evidence-chain coverage | Guardrail | Cross-module evidence paths are protected by named sentinel tests. |
| Eval freshness | Leading | Agent evals include recent failure modes and are not only generic prompts. |
| Benchmark dependence ratio | Risk | Share of acceptance claims based on public benchmarks rather than local tests. |
| Flake rate | Lagging | Failing or inconsistent checks not caused by code changes. |

Healthy signal: every important agent output has executable evidence, and evals
adapt to observed failures.

### 8. Security, Permissions, And Governance

Question: Are agent powers limited, observable, and approved at the right time?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Human-gate compliance | Guardrail | High-risk changes require explicit human approval or documented exception. |
| Permission escalation log completeness | Guardrail | Network, destructive, dependency, and protected-path actions are recorded. |
| Third-party decision coverage | Guardrail | New dependencies have policy evidence before adoption. |
| Skill-risk review coverage | Leading | Skills and tools are reviewed as execution-layer security surfaces. |
| Secret/network incident count | Lagging | Agent or tool attempted to expose secrets, fetch unapproved data, or bypass policy. |
| Audit-trace completeness | Lagging | Action plans, commands, file changes, and review outcomes can be reconstructed. |

Healthy signal: agent autonomy is bounded by controller, capability, and
observability contracts.

### 9. Observability And Evidence Traceability

Question: Can reviewers and future agents reconstruct what happened?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Trace schema adoption | Leading | Agent work records task, tools, commands, artifacts, and decisions. |
| Report-code stability | Guardrail | Public failures use stable machine-readable codes. |
| Decision-log coverage | Leading | Important tradeoffs are recorded where future agents will look. |
| Evidence citation density | Lagging | Claims in closure reports point to commands, tests, files, or generated artifacts. |
| Replayability | Lagging | A future agent can rerun the relevant test or regenerate the artifact. |

Healthy signal: "I think it works" is replaced by inspectable evidence,
deterministic outputs, and stable report IDs.

### 10. Learning And Self-Evolution

Question: Does the project improve its own instructions, tests, and tools after
real mistakes?

Core indicators:

| Metric | Type | What It Means |
| --- | --- | --- |
| Experience-record capture rate | Leading | Repeated omissions and high-severity escapes become records. |
| Promotion decision coverage | Leading | Each lesson is classified as no action, skill, doc, fixture, test, eval, or tool. |
| Before/after validation rate | Guardrail | Promoted lessons include evidence that the new gate catches the old failure. |
| Recurrence rate | Lagging | Same failure appears after a lesson was promoted. |
| Rule inflation rate | Risk | Number of permanent rules added without repeat evidence or severity justification. |

Healthy signal: the repository becomes easier for the next agent because real
friction is distilled into durable, testable memory.

## Cross-Dimension Dashboard

Minimum dashboard for an agentic-SE project:

| Area | First Metrics To Track |
| --- | --- |
| Lifecycle | task-card coverage, archive-link coverage, closure score, cycle time |
| Quality | full gate pass rate, focused-test pass rate, public evidence-chain pass rate, flake rate |
| Architecture | dependency-boundary pass rate, contract-test coverage, negative fixture coverage |
| Security | human-gate compliance, permission escalation count, dependency-decision coverage |
| Orchestration | routing accuracy, handoff completeness, parallelization yield |
| Learning | experience capture, promotion decisions, recurrence rate |
| Delivery | DORA-style change lead time, deployment/release frequency, recovery time, change fail rate, rework rate |

## Anti-Metrics

Avoid optimizing these in isolation:

- number of agent sessions;
- number of generated lines;
- number of PRs without review-burden and failure data;
- public benchmark rank without local task fit;
- number of skills or institutional agents without evals;
- number of rules added after one anecdote;
- full-gate frequency if agents stop running focused diagnostics first.

## Core Conclusion

Mature agentic-SE is a repository-centered control system. The agent is only
one component. The real leverage comes from making intent, context, contracts,
tools, tests, review, security controls, traces, and learning artifacts visible
and executable. The healthiest projects will not ask "how many agents do we
have?" They will ask: "Can a bounded agent change the system, prove it, be
reviewed, and leave the project easier for the next bounded agent?"
