# Long-Term Agentic SE Plan

Snapshot: 2026-05-24.

## Purpose

This plan describes the long-term target for GCS agentic software engineering.
It complements the near-term execution plan. The near-term plan makes current
agents useful. This plan defines the eventual operating system around the GCS
solver project.

## Thesis

GCS should not become an uncontrolled code-writing loop. It should become a
repository that steadily improves its own instructions, contracts, tests,
fixtures, docs, skills, and tools as humans and agents encounter real work.

The C++ solver remains deterministic runtime truth. Agents are an engineering,
review, documentation, and maintenance layer around it.

## Long-Term Architecture

```text
human intent
  -> task card
  -> risk and ownership routing
  -> architecture steward
  -> module specialist agents
  -> implementation session
  -> executable evidence
  -> independent review
  -> archive and experience record
  -> skill, fixture, eval, tool, or doc improvement
```

## Horizon 1: Full Lifecycle Substrate

Goal: every non-trivial agentic-SE task has a visible lifecycle.

Planned capabilities:

- task-card creation and validation;
- execution-plan creation for high-risk work;
- evidence bundle format;
- completed-task archive with closure scoring;
- task-to-archive cross-links;
- low-risk chat-only entry criteria;
- roadmap updates at the end of PDCA cycles.

Exit criteria:

- two or more real engineering tasks complete the full loop;
- future agents can resume from archives without raw chat;
- roadmap state and implementation state are synchronized.

## Horizon 2: Agentic Execution And Review Loop

Goal: implementation work is routed, performed, and reviewed through explicit
agents and quality expectations.

Planned capabilities:

- architecture-steward routing by default;
- module-agent reports for solver contract work;
- independent review agent for important diffs;
- review rubrics by change type;
- negative fixture and report-code review expectations;
- clear human gates for high-risk semantic changes.

Exit criteria:

- agent-authored changes include executable evidence and residual risks;
- independent review catches contract drift or missing tests before merge;
- module skills are updated only from repeated or high-severity evidence.

## Horizon 3: Institutional Agents Become Operational

Goal: standing role-level agents become verifiable project institutions.

Planned capabilities:

- core institutional agents have prompt/template/example/eval packages;
- fuzzy-role generator produces candidate or seed packages from vague input;
- candidate roles are periodically reassessed from real closures;
- role promotion is evidence-based;
- institutional roles can hand off to module agents, experience records, and
  architecture docs without ownership confusion.

Priority roles:

- `刀匠: 淬炼-锻打`: experience distillation and skill-candidate extraction.
- `裁缝: 裁剪-缝合`: multi-session chronology and resumption context.
- `验收官: 举证-放行`: independent evidence review.
- `复盘官: 归因-修复`: blameless failure learning.
- `值夜官: 巡检-告警`: scheduled drift and health inspection.
- `舵手: 分派-收束`: manager-style orchestration for broad decomposable work.

Exit criteria:

- no institutional role is promoted without real artifact evidence;
- role evals include refusal cases;
- new roles are generated through the documented pipeline, not invented ad hoc.

## Horizon 4: Self-Evolution Loop

Goal: repeated failures and review findings become durable improvements.

Planned capabilities:

- experience records from CI failures, human review, agent errors, and
  production-like use;
- promotion decisions: skill, fixture, contract test, architecture doc, tool,
  or no action;
- eval fixtures for module-agent planning and review;
- before/after evidence for each self-evolution improvement.

Exit criteria:

- repeated agent mistakes produce skill or eval updates;
- high-severity escapes produce tests or tools;
- anecdotes do not become permanent rules without evidence.

## Horizon 5: CI, Maintenance, And Scheduled Agents

Goal: routine maintenance becomes agent-assisted while preserving human control.

Planned agents:

- CI triage agent: classifies failed checks and proposes task cards.
- Fixture drift agent: detects changed golden reports or digests.
- Dependency audit agent: checks forbidden imports and third-party metadata.
- Roadmap sync agent: compares roadmap, completed work, and current progress.
- Regression reproducer: turns reports into minimal fixtures.

Exit criteria:

- scheduled agents write evidence but do not silently mutate solver semantics;
- protected branches still require human approval;
- network, dependency, and destructive actions remain permissioned.

## Governance Rules

- Agents may propose broadly; they execute only within explicit task scope.
- No lower solver module may import UI, IO, CLI, process, GUI, or agentic
  infrastructure.
- No agent may introduce a third-party dependency without governance evidence.
- No high-risk semantic change is accepted without tests or a recorded
  exception.
- No memory is authoritative unless it is committed to repository-visible docs,
  skills, fixtures, tests, or tool metadata.
- No agent self-approves or self-merges high-risk changes.

## Long-Term Metrics

Track these trends, not vanity counts:

| Metric | Why it matters |
| --- | --- |
| task-card to completed-archive rate | measures lifecycle discipline |
| build and CTest pass rate on agent work | measures executable quality |
| independent review findings per task | measures whether agents learn |
| repeated mistakes promoted to evals/tools | measures self-evolution |
| stale roadmap items | measures memory hygiene |
| high-risk tasks with explicit human gates | measures autonomy safety |
| fixture coverage for regressions | measures solver reliability |

## Final Target

GCS reaches mature agentic SE when:

- every non-trivial task starts from structured intent;
- every important change ends with executable evidence;
- every repeated failure is either rejected as noise or promoted into durable
  memory;
- standing institutional agents help the project remember, review, recover, and
  improve;
- humans keep final authority over product intent, solver semantics,
  dependencies, and merge decisions.
