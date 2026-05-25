---
name: task-scoped-session-closer
description: Project-specific closure workflow for non-trivial GCS agentic-SE work. Use when a task needs a persisted task card, completed-task archive, evidence bundle, closure score, roadmap update, commit/push handoff, or when work touches quality gates, fixtures, architecture docs, institutional-agent artifacts, repository cleanup, or multi-step implementation. Do not use for tiny chat-only/status/typo work allowed by the lifecycle runbook low-risk boundary.
---

# Task-Scoped Session Closer

## Start Here

Use this skill to close non-trivial GCS work as durable project memory. The
goal is not ceremony. The goal is that a future agent can resume from the repo
without reconstructing raw chat.

Read only what the task needs:

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/agentic/quality-gate-opt-in-policy.md` for Agentic artifact gates
- `docs/agentic/experience/001-task-scoped-session-closure/README.md`

## Entry Rule

Use full task-scoped closure when any of these are true:

- the user asks for `/plan`, a durable plan, repository cleanup, commit, push,
  or continued multi-step execution;
- the work touches solver/runtime/IO/viewer behavior, quality gates, fixtures,
  architecture docs, agentic lifecycle policy, or institutional-agent artifacts;
- a future task depends on the decision, evidence, or roadmap state;
- the change is medium or high risk under the lifecycle runbook.

Do not force a completed-task archive for tiny low-risk work that the runbook
allows to remain chat-only or commit-note-only.

## Workflow

1. Classify the task.
   - Name scope, risk, owner, affected paths, and non-goals.
   - Create a task card before substantial edits when work is non-trivial.

2. Execute within the task boundary.
   - Keep updates tied to the objective.
   - Preserve unrelated dirty worktree changes.
   - Record decisions when they become stable.

3. Verify.
   - Run focused validators or tests for the changed surface.
   - Use full quality gates only when the scope justifies them.
   - Record skipped checks as risk, not as passes.

4. Archive.
   - Create `docs/completed-tasks/<date-slug>/README.md`.
   - Link the task card, changed files, evidence, decisions, risks, and
     follow-up.
   - Add an experience or institutional-agent note when a reusable lesson was
     learned.

5. Score and index.
   - Run `validate-completed-task-report`.
   - Run `score-closure-report --min-score 30` for non-trivial archives.
   - Update `docs/completed-tasks/README.md` and relevant roadmaps.

6. Commit and push when requested or when a PDCA cycle is complete.
   - Stage only scoped files.
   - Commit with a concise message.
   - Push the current branch if the user has authorized direct push.

## Useful Commands

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\<task>.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\<task>\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\<task>\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Guardrails

- Do not mark a non-trivial task complete only because files changed.
- Do not archive raw chat logs.
- Do not hide unresolved risk in optimistic summary language.
- Do not validate all legacy archives unless a migration or exemption policy is
  in scope.
- Do not let the closure process override module-specific steward skills.

## Required Output

At close, the durable archive should let an independent reviewer answer:

- what was attempted;
- what changed;
- what evidence ran;
- what decisions were made;
- what risks remain;
- what task should happen next.
