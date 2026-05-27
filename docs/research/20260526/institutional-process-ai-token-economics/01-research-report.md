# Institutional Process AI Tasks And Token Economics

Date: 2026-05-26

Scope: current public practice from leading AI companies, influential
developer-practitioners, management consulting firms, and academic research on
agentic software engineering, context management, evaluation, governance, and
process redesign. The report is tuned to the GCS problem: agentic-SE work is
increasingly institutional and process-heavy, and those tasks burn many tokens
while repeatedly operating on documents.

## Executive Summary

The frontier consensus is that agentic-SE is moving from "AI writes code" to
"AI participates in an engineered workflow." OpenAI Codex, Claude Code, GitHub
Copilot cloud agent, and Google Cloud agent architecture guidance all emphasize
scoped tasks, repository-native instructions, tools, state, guardrails,
observability, and review. That means the real unit of work is no longer a
single prompt. It is a governed task with context, tools, permissions, tests,
logs, and a reviewable result.

The token waste seen in institutional/process tasks is a symptom of state being
held in the wrong place. Long chat histories, repeated runbook excerpts, copied
task-card templates, pasted source lists, and hand-written closure reports are
all attempts to use context as a process database. The research direction is
clear: externalize state into memory, skills, protocols, manifests, source
registers, traces, and harnesses, then load only the parts needed for the
current decision.

Management consulting reports point in the same direction from the organization
side. McKinsey says value comes when organizations redesign workflows, track
KPIs, train by role, and create feedback mechanisms. BCG and Bain frame
agentic AI as workflow redesign, not incremental automation. Deloitte warns
that agent risk compounds across decision chains and interfaces, especially
with long-context memory and broader system access.

The strongest developer-practitioner pattern is disciplined aggression:
delegate more work to agents, but keep humans responsible for intent,
architecture, review, security, and learning. Simon Willison argues that coding
agents require skilled operators and warns about the private-data,
untrusted-content, external-communication risk triangle. Addy Osmani's
"70 percent problem" captures the production gap: agents can create plausible
first drafts quickly, while edge cases, security, integration, and review
remain hard. Thorsten Ball's cheap-code framing and Karpathy's Software 3.0
framing both imply that context, verification, and maintainability become more
valuable as generation becomes cheaper.

For GCS, the conclusion is practical: keep the lifecycle, but lower its token
cost through a process-AI operating layer. Build task-specific context packs,
structured ledgers, section-aware document tools, local evals, and token/value
metrics. Do not solve the problem by deleting governance. Solve it by making
governance machine-assisted, compact, and evidence-driven.

## Source Register

| Source | Date/version | Used for | Confidence |
| --- | ---: | --- | --- |
| [OpenAI, A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf) | accessed 2026-05-26 | Agent definition, use-case fit, tools, orchestration, guardrails | High |
| [OpenAI, Introducing Codex](https://openai.com/index/introducing-codex/) | 2025-05-16 | Isolated software-engineering tasks, logs, tests, PR review | High |
| [OpenAI, Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) | 2026-02-02, Windows update 2026-03-04 | Multi-agent command center and long-running task supervision | High |
| [OpenAI, Codex generally available](https://openai.com/index/codex-now-generally-available/) | 2025-10-06 | Team adoption, SDK, admin controls, analytics, context management | High |
| [OpenAI, Prompt caching](https://platform.openai.com/docs/guides/prompt-caching) | accessed 2026-05-26 | Static-prefix caching, cache metrics, cost/latency reduction | High |
| [Anthropic, Claude Code best practices](https://code.claude.com/docs/en/best-practices) | accessed 2026-05-26 | Explore-plan-code, CLAUDE.md, session/context management, subagents | High |
| [Anthropic, Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching) | accessed 2026-05-26 | Prefix matching, cache invalidation, compaction cost, subagent cache behavior | High |
| [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 2024-12-19 | Workflows versus agents, orchestrator-workers, evaluator-optimizer | High |
| [GitHub, Copilot cloud agent task best practices](https://docs.github.com/en/copilot/tutorials/cloud-agent/get-the-best-results) | accessed 2026-05-26 | Issue-like prompts, PR iteration, repository instructions, build/test guidance | High |
| [Google Cloud, Choose agentic AI architecture components](https://cloud.google.com/architecture/choose-agentic-ai-architecture-components) | last reviewed 2025-11-24 | Architecture selection by complexity, latency, cost, memory, persistent state | High |
| [Google DeepMind, AlphaEvolve](https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) | 2025-05-14 | Coding-agent loop for algorithm discovery and multi-objective verification | High |
| [McKinsey, The State of AI: Rewiring to Capture Value](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-how-organizations-are-rewiring-to-capture-value) | 2025-03-12 | Workflow redesign, governance, training, feedback, KPI best practices | High |
| [McKinsey, Seizing the Agentic AI Advantage](https://www.mckinsey.com/capabilities/quantumblack/our-insights/seizing-the-agentic-ai-advantage) | 2025-06-13 | GenAI paradox, agentic AI CEO playbook | High |
| [BCG, How Agentic AI Is Transforming Enterprise Platforms](https://www.bcg.com/publications/2025/how-agentic-ai-is-transforming-enterprise-platforms) | 2025-10-13 | Versioned change management, shadow rollout, tool hardening, kill switches | High |
| [BCG, Agents Accelerate the Next Wave of AI Value Creation](https://www.bcg.com/publications/2025/agents-accelerate-next-wave-of-ai-value-creation) | 2025 | Workflow rebuild, business context fabric, 10/20/70-style people/process emphasis | High |
| [BCG, The Widening AI Value Gap](https://www.bcg.com/assets/2025/the-widening-ai-value-gap.pdf) | 2025 | Value gap, end-to-end workflow reshaping, human orchestration | High |
| [Bain, Building the Foundation for Agentic AI](https://www.bain.com/insights/building-the-foundation-for-agentic-ai-technology-report-2025/) | 2025 | Structural enterprise shift, systems/data/governance readiness | High |
| [Bain, State of the Art of Agentic AI Transformation](https://www.bain.com/insights/state-of-the-art-of-agentic-ai-transformation-technology-report-2025/) | 2025 | Context, data, safety, collaboration, cross-system orchestration | High |
| [Deloitte, The Agentification of the Enterprise](https://www.deloitte.com/content/dam/assets-zone3/us/en/docs/services/consulting/2025/agentic-ai-enterprise-adoption-guide.pdf) | 2025 | Nonlinear risk, memory exposure, decision-chain risk, human override | High |
| [SWE-bench](https://arxiv.org/abs/2310.06770) | 2023, revised 2024 | Real-world code task benchmark and long-context challenge | High |
| [SWE-agent](https://arxiv.org/abs/2405.15793) | 2024 | Agent-computer interface as performance lever | High |
| [AI Agents That Matter](https://arxiv.org/abs/2407.01502) | 2024 | Cost-aware, non-accuracy-only agent evaluation critique | High |
| [Practical Considerations for Agentic LLM Systems](https://arxiv.org/abs/2412.04093) | 2024 | Planning, memory, tools, control flow as design categories | Medium-high |
| [Survey on Evaluation of LLM-based Agents](https://arxiv.org/abs/2503.16416) | 2025, revised 2026 | Evaluation trends and gaps in cost-efficiency, safety, robustness | Medium-high |
| [Agentic Software Engineering](https://arxiv.org/abs/2509.06216) | 2025 | SE for humans/agents, ACE/AEE, merge-readiness packs, human callbacks | Medium-high |
| [Agentic Coding Manifests study](https://arxiv.org/abs/2509.14744) | 2025 | Repository manifests as operational context and rules | Medium-high |
| [Externalization in LLM Agents](https://arxiv.org/abs/2604.08224) | 2026 | Memory, skills, protocols, harnesses as externalized cognition | Medium |
| [Memory for Autonomous LLM Agents](https://arxiv.org/abs/2603.07670) | 2026 | Write-manage-read memory loop and latency/privacy realities | Medium |
| [Dive into Claude Code](https://arxiv.org/abs/2604.14228) | 2026 | Context compaction, permissions, skills, subagents, worktree isolation | Medium |
| [Agentic Agile-V](https://arxiv.org/abs/2605.20456) | 2026-05-19 | Conversation-to-contract gate and evidence-bundle acceptance model | Medium |
| [Simon Willison, Coding agents require skilled operators](https://simonwillison.net/2025/Jun/18/coding-agents/) | 2025-06-18 | Skilled operator and review loop thesis | High |
| [Simon Willison, Lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) | 2025-06-16 | Agent security risk: private data, untrusted content, outbound comms | High |
| [Zed/Addy Osmani, AI's 70% Problem](https://zed.dev/blog/ai-70-problem-addy-osmani) | 2025-11-06 | Prototype-to-production gap and review bottleneck | Medium-high |
| [Thorsten Ball, How might AI change programming?](https://registerspill.thorstenball.com/p/how-might-ai-change-programming) | 2025-01-30 | Cheap writing/rewriting, CONTEXT.md, AI-shaped technical debt | High |
| [Karpathy/Y Combinator, Software Is Changing Again](https://rosetta.to/u/ycombinator/andrej-karpathy-software-is-changing-again) | 2025-06 | LLMs as operating systems, context windows as memory, deficits and prompt injection | Medium |
| [Hamel Husain, Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/index.html) | 2024/2025 | Scoped tests, failure-driven evals, continuous update | High |
| `docs/architecture/95-agentic-session-efficiency-governance.md` | local, 2026-05-26 | GCS outcome/token metrics and session efficiency schema | High |
| `docs/agentic/agentic-organization-operating-map.md` | local, 2026-05-26 | GCS agentic operating layers and evidence contract | High |
| `docs/agentic/lifecycle-runbook.md` | local | Task lifecycle, task cards, validation, closure | High |
| `docs/agentic/institutional-agent-registry-and-scorecard.md` | local, 2026-05-26 | Institutional-agent maturity and promotion discipline | High |

## Findings

### 1. The Frontier Unit Is A Governed Workflow, Not A Prompt

OpenAI's agent guide defines agents around independent workflow completion with
tools and guardrails. Codex applies this to software engineering by running
scoped tasks in isolated environments with repository context, command output,
tests, and reviewable changes. Claude Code, GitHub Copilot cloud agent, and
Google Cloud architecture guidance all point to the same pattern: the agent is
part of a larger workflow runtime.

Implication for process tasks:

- A task card, source register, evidence bundle, and archive are not overhead
  in themselves. They are the workflow runtime.
- Token waste appears when the runtime is not compiled into reusable structures
  and the LLM must repeatedly reconstruct the workflow from prose.
- The correct question is not "can we skip documentation?" but "which parts of
  documentation are state, which are instructions, and which are final reports?"

### 2. The Token Problem Is An Externalization Failure

The 2026 externalization literature frames practical agent progress as moving
hard cognitive burdens out of the model and into memory stores, skills,
protocols, and harnesses. This is exactly the failure mode in token-heavy
institutional tasks: the model is asked to carry process history, role policy,
source provenance, task state, validation commands, and closure judgment inside
the context window.

Better externalization targets:

| Burden currently held in chat | Better external form |
| --- | --- |
| "What is the task and risk?" | Task card frontmatter and task-state JSON |
| "Which sources support the claim?" | Source register with claim tags |
| "What changed and what passed?" | Evidence ledger |
| "What should be loaded next?" | Context pack manifest |
| "How do we close this task?" | Archive generator plus validator |
| "What did we learn?" | Experience candidate or eval candidate |

This is not anti-LLM. It is pro-agent. Strong agents become more reliable when
state and procedure are externalized into objects they can inspect and update.

### 3. Repository Manifests Are Valuable, But They Must Stay Small

OpenAI, GitHub, and Anthropic all recommend repository-native instruction
files such as `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, and
path-scoped instruction files. The manifest study of Claude Code repositories
finds that these files commonly carry operational commands, technical notes,
and architecture guidance.

The trap is always-on bloat. Claude Code's best practices explicitly warn that
large `CLAUDE.md` files can degrade performance because they load every
session. Claude Code's prompt caching documentation explains why stable
prefixes matter: changing system prompt, tool definitions, model, effort, or
MCP shape can invalidate cached context. OpenAI's prompt-caching guidance is
similar: put stable content early, variable content later, and monitor cache
hit metrics.

Best-practice synthesis:

- Keep always-on repository instructions short.
- Put rarely used domain knowledge behind skills, path-specific rules, or
  retrieval.
- Prefer stable prompt prefixes for recurring process work.
- Treat compaction as a deliberate boundary between tasks, not an emergency
  after the context is saturated.
- Use context packs to load exactly what the task needs.

### 4. Process Redesign Beats Faster Document Generation

McKinsey's state-of-AI work emphasizes workflow redesign, governance ownership,
role-based training, feedback mechanisms, roadmaps, KPIs, and trust. BCG's AI
value-gap report says meaningful value comes from reshaping and reinventing
core workflows end to end, not isolated use cases. Bain calls agentic AI a
structural shift that requires systems, data, governance, interoperability,
security, and accountability. Deloitte warns that agentic risks scale
nonlinearly across decision chains and interfaces.

This matters because many process AI tasks are disguised workflow-redesign
tasks. When an agent repeatedly edits Markdown task cards, archives, reports,
roadmaps, and indexes, it is not only "writing docs." It is operating the
project's control plane.

Therefore:

- The process layer needs product management, not just prompting.
- Institutional tasks need owners, trigger conditions, schemas, validators, and
  decommissioning rules.
- Human oversight should focus on high-value judgment: scope, risk, source
  quality, claims, and irreversible actions.

### 5. Evidence Bundles Are The Antidote To Vague Autonomy

SWE-bench shows real software tasks require long-context understanding,
multi-file coordination, execution environments, and complex reasoning.
SWE-agent shows agent-computer interfaces can materially improve agent
performance. "AI Agents That Matter" warns that accuracy-only leaderboards can
make agents needlessly complex and costly. Agent-evaluation surveys point to
gaps in cost-efficiency, safety, robustness, and fine-grained evaluation.

The practical answer is evidence bundles:

- task intent and constraints;
- files and sources read;
- commands run;
- results and failures;
- changed files;
- skipped checks and why;
- human gates;
- residual risks;
- follow-up tasks.

Evidence bundles also reduce future token use because future agents can read a
compact structured record instead of raw chat history.

### 6. Skilled Operators Remain Central

Simon Willison's "skilled operator" framing is especially important for GCS:
coding agents work when a person with domain understanding gives a clear task,
understands the tools, reviews the result, and iterates. Addy Osmani's "70
percent problem" says agents can produce plausible first drafts quickly, while
edge cases, security, integration, and maintainability still require disciplined
engineering. Thorsten Ball argues that cheap code changes programming because
writing and rewriting certain code becomes inexpensive, but he also asks
whether `CONTEXT.md`-style files and AI-shaped technical debt will emerge.
Karpathy frames LLMs as a new operating-system-like layer with context windows
as memory, but with hallucination, jagged intelligence, amnesia, and prompt
injection risks.

For institutional/process tasks, the skilled operator is not typing every
report. The operator is designing the process so the agent cannot waste a large
context window redoing the same clerical moves.

### 7. Security And Permissions Are Process-Economic Issues

Security controls reduce risk, but they also reduce wasted work. Willison's
private-data plus untrusted-content plus external-communication pattern is a
clear boundary for agent capability design. BCG recommends kill switches,
strict schemas, safe defaults, allow lists, timeouts, spending caps, sandbox
testing, and shadow rollouts. Deloitte stresses human override and dynamic
audits.

In process-heavy agentic-SE, permission ambiguity causes token waste:

- the agent stops repeatedly to ask about low-risk actions;
- the agent over-explains why it cannot do something;
- the agent performs long analysis before discovering an action is forbidden;
- the agent creates broad reports because the exact permitted surface is
  unclear.

A good permission model is therefore both safer and cheaper.

### 8. GCS Is Ahead On Discipline But Exposed To Process Token Cost

GCS already has substantial agentic infrastructure:

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/agentic/agentic-organization-operating-map.md`
- `docs/architecture/95-agentic-session-efficiency-governance.md`
- `docs/agentic/institutional-agent-registry-and-scorecard.md`
- `docs/reports/session-efficiency/2026-05-26/README.md`
- task cards, completed-task archives, institutional agents, and validators

This is a strength. It also creates the current problem: as the lifecycle gets
more complete, each session must read and update more process artifacts.

The GCS-specific bottleneck is not missing process. It is insufficient process
compilation:

- task state is mostly Markdown, not machine-addressable enough;
- source registers are per-report, not reusable across reports;
- archive generation is still partly manual;
- context is selected by human/agent reading, not by a context-pack tool;
- token telemetry exists conceptually but is not automatically joined to task
  state;
- institutional-agent promotion is disciplined, but role outputs are still
  prose-heavy.

## Best-Practice Synthesis

### Design Principles

1. Workflow first, agent second.
2. Use deterministic tools for deterministic document operations.
3. Externalize state before expanding context.
4. Keep always-on instructions short and stable.
5. Use task-specific context packs instead of whole-doc dumps.
6. Make every recurring process artifact structured enough to validate.
7. Evaluate local workflows, not only model capability.
8. Measure token cost against accepted durable output.
9. Preserve human gates for irreversible, high-risk, external, or protected
   actions.
10. Promote process rules only from repeated evidence or severe near misses.

### What To Stop Doing

- Pasting full runbooks into every task.
- Asking the LLM to rediscover repository structure from scratch.
- Treating generated Markdown volume as progress.
- Letting source registers exist only inside one finished report.
- Creating new institutional roles before the workflow has examples, refusal
  behavior, and an output contract.
- Comparing token efficiency across unrelated task classes.

### What To Start Doing

- Generate a context pack at task start.
- Maintain a task-local evidence ledger.
- Use section-aware tools for index/archive updates.
- Reuse source registers by URL/path and claim tag.
- Track task-class-specific token/value metrics.
- Convert repeated closure/report patterns into validators and scaffolding.
- Keep a "hot state" file that summarizes only the current task state.

## Implications For GCS

GCS should treat institutional/process AI tasks as a first-class engineering
surface. The desired system is a small operating layer around the existing
lifecycle:

```text
task card
  -> context pack
  -> evidence ledger
  -> deterministic doc updates
  -> validation
  -> archive scaffold
  -> learning/eval candidate
  -> session-efficiency record
```

This keeps the repo's evidence culture while reducing the need for the model to
carry the whole project bureaucracy in live context.

## Open Questions

- How much token telemetry can the current Codex runtime expose automatically,
  and how much must stay manual or unknown?
- Should GCS create a portable repository-level `AGENTS.md`, or keep `.codex`
  skills plus `docs/agentic` as the canonical instruction layer and generate
  tool-specific manifests from them?
- Which document updates are safe to automate immediately: completed-task
  index entries, source registers, evidence ledgers, task-card evidence, or
  session-efficiency records?
- What minimum eval set would catch process-agent failures such as invented
  causality, unsupported source claims, bloated context packs, and premature
  role promotion?

