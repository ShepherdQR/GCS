# E002 Research Report: Session And Agent Best-Practice Patterns

Research snapshot: 2026-05-24.

## Research Question

What session and agent operating patterns should GCS treat as durable best
practice, and how does the user-named E002 pattern, "阶段-步骤-总结-更新-提交-继续",
fit into that pattern system?

## Source Base

Primary and near-primary sources used:

- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic, Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code common workflows](https://code.claude.com/docs/en/common-workflows)
- [Claude Code worktrees](https://code.claude.com/docs/en/worktrees)
- [OpenAI Agents SDK guide](https://developers.openai.com/api/docs/guides/agents)
- [OpenAI, A practical guide to building agents](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [OpenAI Codex workflows](https://developers.openai.com/codex/workflows)
- [OpenAI Codex app worktrees](https://developers.openai.com/codex/app/worktrees)
- [Google ADK workflow agents](https://adk.dev/agents/workflow-agents/)
- [Google ADK multi-agent systems](https://adk.dev/agents/multi-agents/)
- [Microsoft Agent Framework group chat orchestration](https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/group-chat)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
- [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/abs/2303.17651)
- [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091)
- Existing GCS E001 material under `docs/agentic/experience/001-task-scoped-session-closure/`

## Executive Synthesis

The literature and tool documentation converge on one principle: reliable
agentic work is not "one big prompt". It is a controlled sequence of small
loops, each with clear state, tool evidence, review gates, and durable memory.

Anthropic's pattern taxonomy gives the broad control-flow vocabulary: prompt
chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer,
and more autonomous agents. OpenAI's agent guidance adds the runtime layer:
model, tools, instructions, run loops, guardrails, human intervention, and
handoffs. Claude Code and Codex documentation add the software-engineering
layer: read-only planning, worktree isolation, stepwise iteration, review, and
commit or PR governance. The research papers add cognitive loops: plan first,
act with observations, refine, and preserve lessons.

E002 is the long-horizon session-control pattern that connects these layers. It
turns a large agentic task into a sequence of reviewable steps nested inside
phases. Each step ends with summary, plan update, scoped commit, and next-step
declaration. Each phase ends with summary and downstream replanning. This makes
the plan adaptive without making it formless.

## Pattern Axes

Session and agent patterns can be classified along six axes:

| Axis | Question | Failure If Missing |
| --- | --- | --- |
| Scope | What is the unit of accountable work? | Chat drift and unclear done state. |
| Control flow | Who decides the next action? | Either brittle fixed scripts or chaotic autonomy. |
| Evidence | What grounds the next decision? | Hallucinated progress and untested changes. |
| Memory | What survives context loss? | Repeated rediscovery and broken handoffs. |
| Isolation | Which filesystem, branch, tools, and permissions are in play? | Conflicting edits and contaminated diffs. |
| Governance | Who can approve risky actions or merge work? | Agents overstepping authority. |

E002 primarily strengthens scope, evidence, memory, and governance inside long
sessions. It also supports isolation by requiring step-scoped commits.

## Pattern Catalogue

### 1. Task-Scoped Session Closure

Mechanism: Define one task objective, execute against it, then close with a
durable report and archive.

Best use: Any non-trivial GCS session.

Risk controlled: Work that is useful in the moment but lost to future agents.

GCS status: Promoted as E001.

E002 relationship: E001 is the outer transaction. E002 is the nested execution
loop inside a large E001 task.

### 2. Read-Only Reconnaissance And Plan Mode

Mechanism: Explore the codebase or docs first, using read-only operations, then
propose a plan before editing.

Best use: Complex changes, unfamiliar code, reviews, or tasks where a wrong
first edit is expensive.

Risk controlled: Premature implementation and architecture misunderstanding.

Source signal: Claude Code describes plan mode as useful for codebase
exploration, complex changes, and safe review. Codex workflow docs similarly
recommend local planning before long delegated work.

GCS rule: Use before changing solver semantics, IO schemas, session runtime,
agentic lifecycle docs, or any cross-module contract.

### 3. Phase-Step Summary-Update-Commit-Continue

Mechanism: Divide future work into phases. Divide each phase into steps. After
each step, summarize, update the rest of the phase, commit the step, and declare
the next step. After each phase, summarize and replan later phases.

Best use: Long research, architecture, refactor, fixture-generation, and
multi-artifact documentation work.

Risk controlled: Stale plans, unbounded diffs, and impossible resumption.

GCS status: Promoted here as E002.

Why it matters: A phase is only a hypothesis until a step creates evidence. E002
forces the hypothesis to be updated after every observation.

### 4. Prompt Chaining With Gates

Mechanism: Break a task into fixed steps where each model call consumes the
previous step's output, with checks between steps.

Best use: A known pipeline such as outline -> review -> draft -> verify, or
schema migration -> round trip -> validation report.

Risk controlled: Overloaded prompts and hidden intermediate failures.

GCS rule: Use when the step order is known up front and each stage can produce
a concrete artifact.

### 5. Routing And Specialist Dispatch

Mechanism: Classify the input or subtask and dispatch it to the right specialist
prompt, model, skill, or module agent.

Best use: Tasks whose categories are known and have different standards, such
as kernel contract work versus IO adapter work.

Risk controlled: One generic agent trying to satisfy incompatible conventions.

GCS rule: Route by owning module, affected contract, risk, and evidence type.

### 6. Parallelization: Sectioning And Voting

Mechanism: Run independent subtasks in parallel, or run multiple attempts and
aggregate the result.

Best use: Research breadth, independent review dimensions, fixture variants,
visual QA across viewports, or competing design alternatives.

Risk controlled: Serial bottlenecks and single-perspective blind spots.

Cost: More tokens, more merge coordination, and higher need for artifact
boundaries.

GCS rule: Use worktrees or read-only subagents for parallel write-capable work.

### 7. Orchestrator-Workers

Mechanism: A central agent decomposes the task dynamically, delegates to worker
agents, and synthesizes their results.

Best use: Complex work where required subtasks are not known in advance, such
as broad research, multi-file coding, or incident triage.

Risk controlled: A single agent running out of context or missing specialized
perspectives.

GCS rule: The orchestrator owns synthesis and final report quality. Workers own
bounded artifacts and evidence.

### 8. Deterministic Workflow Agents

Mechanism: Use explicit sequential, parallel, or loop workflows whose execution
order is defined by code rather than an LLM.

Best use: Repeatable pipelines with stable control flow, such as validate docs,
generate fixtures, run contract tests, or render figures.

Risk controlled: LLMs making unnecessary orchestration decisions.

GCS rule: If the control flow is known, encode it as a tool or script. Reserve
LLM choice for semantic judgment.

### 9. Group Chat Or Council Review

Mechanism: Multiple agents participate in one shared conversation, coordinated
by a speaker-selection strategy.

Best use: Multi-perspective analysis, iterative critique, and decision review
where shared context is helpful.

Risk controlled: Single-reviewer bias.

Risk introduced: Shared context can create groupthink and token bloat.

GCS rule: Prefer council review for design decisions and rubric-based critique,
not for parallel file editing.

### 10. ReAct: Reason-Act-Observe

Mechanism: Interleave reasoning, tool actions, and observations from the
environment.

Best use: Tasks where external state matters: tests, file inspection, command
output, browser behavior, schemas, and generated artifacts.

Risk controlled: Untethered reasoning and hallucinated progress.

GCS rule: Treat tool output, tests, diffs, rendered artifacts, and schema
reports as observations that can revise the plan.

### 11. Plan-And-Solve

Mechanism: First produce a plan that decomposes the task, then solve according
to the plan.

Best use: Multi-step reasoning where missing steps are common.

Risk controlled: Skipping subtasks and premature answer generation.

GCS rule: E002 extends this by requiring the plan to be revised after each
step, not only created at the beginning.

### 12. Evaluator-Optimizer

Mechanism: A generator creates an output, an evaluator critiques it against
criteria, and the generator revises.

Best use: Scientific figures, prose reports, UI polish, solver diagnostics
wording, and other outputs with clear quality rubrics.

Risk controlled: First-draft quality and self-satisfaction.

GCS rule: Use an independent reviewer or rubric when failure cost is high.

### 13. Self-Refine

Mechanism: The same model produces feedback on its own output and iteratively
refines it.

Best use: Low-risk refinement where external evidence is limited and a separate
reviewer is unavailable.

Risk controlled: One-shot output quality.

Risk introduced: Self-critique can miss the same blind spot as the original
draft.

GCS rule: Self-refine can improve wording, but contract semantics need external
evidence or independent review.

### 14. Reflexion And Episodic Memory

Mechanism: Convert feedback or failure signals into verbal memory that improves
future attempts.

Best use: Repeated task families, recurring CI failures, review corrections,
and agent mistakes.

Risk controlled: Repeating the same failure after the immediate context is gone.

GCS rule: Durable lessons become experience records, templates, skills, evals,
or tool gates.

### 15. Worktree, Branch, Commit, And PR Isolation

Mechanism: Separate writable sessions by filesystem and branch. Use commits and
PRs as reviewable state boundaries.

Best use: Parallel agent work, risky changes, and any task with independent
review or merge needs.

Risk controlled: Cross-session file collisions, branch confusion, and polluted
diffs.

GCS rule: E002 step commits should be path-scoped when the worktree is dirty.
Parallel write-capable agents should use separate worktrees.

### 16. Guardrails And Human Gates

Mechanism: Attach checks to inputs, outputs, tools, or high-risk actions; pause
for human judgment when thresholds or risk levels require it.

Best use: Mutating operations, irreversible actions, security-sensitive flows,
or semantic changes that need human approval.

Risk controlled: Agent autonomy exceeding the trust boundary.

GCS rule: Treat solver semantics, schema migrations, third-party dependencies,
destructive git actions, and broad refactors as gate-worthy.

### 17. Artifact-Backed Handoff

Mechanism: Store subtask output in durable files or structured artifacts, then
pass references rather than relying only on conversational summaries.

Best use: Long sessions, context compaction, parallel research, generated
fixtures, visual reports, and scientific figure pipelines.

Risk controlled: Lossy handoff and "telephone game" summaries.

GCS rule: Prefer markdown reports, JSON manifests, generated QA reports,
contract test logs, or task archives as handoff state.

## Recommended Pattern Set For GCS

| Mode | Use It When | Required Artifact |
| --- | --- | --- |
| E001 task transaction | Any non-trivial session | Completed-task report or explicit no-archive reason. |
| E002 phase-step continuation | Work spans phases or multiple artifacts | Phase plan, step summary, update, commit, next declaration. |
| Read-only reconnaissance | Scope is unclear or risky | Findings and proposed plan. |
| Module-specialist routing | A contract-owning module is affected | Task card naming owner and specialist skills. |
| Worktree-parallel specialist | Multiple write-capable agents run at once | Separate worktree, branch, and step/PR evidence. |
| Evaluator-optimizer review | Quality criteria are explicit | Reviewer notes or rubric result. |
| ReAct evidence loop | Tools and tests can observe reality | Command output, diff, render, or test evidence. |
| Guardrail/human gate | Action is high-risk or irreversible | Approval, blocker, or escalation note. |
| Artifact memory handoff | Context may be lost or compressed | Durable report, manifest, or template. |
| Experience promotion | A repeated lesson appears | Experience record plus promotion target. |

## E002 Protocol Detail

E002 should be used when the first plan is too coarse to be trusted for the
whole task. The step loop is:

```text
declare step
  -> produce artifact
  -> verify minimally useful evidence
  -> summarize result
  -> update remaining steps
  -> commit exact step boundary
  -> declare next step
```

The phase loop is:

```text
phase plan
  -> step loops
  -> phase summary
  -> downstream replanning
  -> next phase start
```

This is not just "make a plan". It is a governance rule for when plans may
change and how the change becomes visible.

## Anti-Patterns

| Anti-Pattern | Symptom | E002 Countermeasure |
| --- | --- | --- |
| Stale roadmap | Later steps still reflect assumptions disproved by an earlier step. | Mandatory phase update after each step. |
| Giant diff | Many unrelated artifacts appear in one commit. | Step-sized artifacts and path-scoped commits. |
| Summary theater | Headings exist but do not say what changed or what was learned. | Step summary must alter or explicitly confirm the remaining plan. |
| Hidden blocker | Agent stops after a problem without durable handoff. | Blocked step record plus next decision needed. |
| Context-only memory | The only record is in chat. | Durable artifact, report, or manifest. |
| Parallel collision | Two agents edit the same checkout or branch. | Worktree isolation and branch governance. |
| Ungated autonomy | Agent performs risky mutation because the next step said so. | Guardrail and human-gate checks before high-risk action. |

## Promotion Recommendations

1. Treat E002 as promoted experience immediately for long documentation and
   research tasks.
2. Add an optional phase-step section to future task-card templates when a task
   has more than one phase.
3. Extend completed-task scoring later to reward intermediate step summaries
   and scoped commits.
4. Consider a project skill after E002 is used successfully in at least two
   substantial tasks.
5. Keep E002 lightweight for small work; the value is in reducing resumption
   cost and review risk.

## Step 1 Summary

This research step established a project-local pattern catalogue and located
E002 inside it as the long-horizon continuation discipline. The remaining work
for this first E002 promotion is to connect the report to executable templates,
then validate and commit the new experience folder.

## Update To Remaining Phase 1 Steps

No new research source is needed for this initial promotion. The next step
should create the reusable template and agent role card, then update the
experience library index.
