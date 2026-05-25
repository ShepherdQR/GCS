---
experience_id: E001-task-scoped-session-closure
source: project-practice
status: active-skill
root_cause: ambiguous_task
affected_modules:
  - agentic_lifecycle
promotion_target: .codex/skills/task-scoped-session-closer
---

# E001: Task-Scoped Session Closure

## Thesis

An agentic-SE session should be treated as a bounded task transaction:

```text
task objective
  -> scoped multi-turn execution
  -> evidence and decisions
  -> task execution report
  -> durable archive
  -> optional experience promotion
```

The session is not complete when the agent stops editing. It is complete only
after the task goal, actions, evidence, risks, and follow-up state are written
into a reviewable report and, when durable enough, archived in the repository.

## Problem

Free-form chat creates useful progress but weak project memory. Without a
defined task goal and closure artifact, a later maintainer must reconstruct:

- what the session was trying to accomplish;
- which paths and contracts were intentionally touched;
- which checks actually ran;
- which decisions were made during interaction;
- which risks were accepted or deferred;
- where the reusable lesson should live.

That reconstruction cost grows with every multi-turn conversation. The project
needs a repeatable way to convert interaction into durable engineering memory.

## Practice

Every non-trivial agentic-SE session should begin with a task objective and end
with a task execution report. The report is then archived when it contains
durable project value.

Required session moves:

1. State the task objective in a form that can be accepted or rejected.
2. Keep multi-turn interaction tied to that objective.
3. Record decisions, changed files, evidence, skipped checks, and residual
   risk as they emerge.
4. Produce a task execution report before declaring the task done.
5. Archive the report under a durable project path when future work should be
   able to find it.

For GCS, completed task archives belong under `docs/completed-tasks/`.
Generalized process lessons belong under `docs/agentic/experience/`.

## Theory Lift

### Session As Unit Of Work

A session is the smallest accountable unit of agentic engineering. It combines
human intent, agent actions, tool evidence, and reviewable outputs. Treating it
as a unit of work prevents scope drift because every action is judged against a
task-level contract.

### Multi-Turn Interaction As Control Loop

Multi-turn interaction is not noise; it is feedback control. The user adjusts
intent, the agent adjusts plan and implementation, tools provide evidence, and
the conversation converges toward acceptance. The task objective is the set
point. Tests, diffs, and reports are sensors. The execution report is the final
state estimate.

### Report As Closure Artifact

The report closes the gap between "the agent did something" and "the project
knows what changed." It should be concise, path-based, and evidence-oriented.
It is not a transcript. It is a structured engineering account.

### Archive As Memory Boundary

Archiving separates durable knowledge from live conversation. Chat can remain
exploratory, but the archive becomes the source of truth for future agents,
reviewers, and maintainers. This keeps memory curated instead of accidental.

## Operating Invariants

- Every session has one primary task objective.
- The objective names scope, acceptance evidence, and non-goals when risk is
  more than trivial.
- Intermediate work can branch, but closure must return to the objective.
- No task is marked complete without an execution report or an explicit reason
  why no durable report is needed.
- The archive stores distilled process and evidence, not raw chat logs.
- Repeated closure failures become candidates for skill, template, tool, or CI
  promotion.

## Completion Criteria

A session is complete when the following are true:

- the requested output was produced or the blocker is documented;
- touched paths and artifacts are listed;
- verification commands are recorded with pass/fail summaries;
- skipped checks and residual risks are named;
- user decisions and notable design choices are preserved;
- follow-up work is separated from completed work;
- the task execution report is placed in the right archive if it has durable
  value.

## Materials

- Active project skill: `.codex/skills/task-scoped-session-closer/SKILL.md`
- Candidate skill provenance: `skills/task-scoped-session-closer/SKILL.md`
- Agent role card: `agents/session-closure-agent.md`
- Report template: `templates/task-execution-report.md`
- Archive checklist: `templates/archive-checklist.md`

## Executable Tooling

The first executable layer for this experience lives in
`tools/agentic_design/agentic_toolkit.py`:

```bat
python tools\agentic_design\agentic_toolkit.py new-completed-task-report --slug my-task --session-goal "Describe the task"
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
```

`new-completed-task-report` creates the archive skeleton.
`validate-completed-task-report` checks the hard structure needed for durable
task memory. `score-closure-report` gives a lightweight heuristic score aligned
with the rubric; it should guide review, not replace it.

## Deep Research Notes

- `research/01-session-transaction-theory.md`: first-principles theory of an
  agentic-SE session as a bounded transaction over project state.
- `research/02-closure-failure-taxonomy.md`: failure classes that make sessions
  hard to trust after chat ends.
- `research/03-closure-quality-rubric.md`: scoring model for evaluating closure
  quality.
- `research/04-empirical-experiment-design.md`: pilot design for measuring
  whether structured closure improves future review and resumption.

## Calibration Records

- `calibration/2026-05-24-s1-05-first-archive-review.md`: first comparison of
  E001 machine closure scores with human review notes across C001 and Step 47.
- `calibration/2026-05-25-agentic-se-post-push-closeout.md`: reusable
  post-push closeout sequence for updating next-task plans, archives, and
  experience records after a completed Agentic-SE push.

## Eval Records

- `evals/2026-05-25-false-completion-archive-pollution.md`: seed negative eval
  requiring reviewers to reject false completion and archive pollution.

## Promotion Decisions

- `promotion/2026-05-25-s3-04-skill-promotion-decision.md`: promoted E001 into
  the active project skill `.codex/skills/task-scoped-session-closer` while
  keeping default gate enforcement deferred to S2-05.

## Promotion Path

This experience is now an active project skill for non-trivial task closure.
Future hardening can add:

- a task-card field requiring planned archive target for larger tasks;
- a session-close checklist in module-specific GCS skills where needed;
- an eval where an agent must identify missing closure evidence before marking
  a task complete.
