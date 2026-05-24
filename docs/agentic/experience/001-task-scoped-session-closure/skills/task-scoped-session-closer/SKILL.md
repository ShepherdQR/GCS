---
name: task-scoped-session-closer
description: Use when an agentic-SE session needs a clear task objective, multi-turn execution discipline, final task execution report, and durable archive handoff before the task is considered complete.
---

# Task-Scoped Session Closer

## Purpose

Keep an agentic engineering session accountable from task intake through final
archive. Use this skill for non-trivial work, long-running conversations,
multi-step implementation, review follow-up, or any task whose decisions should
survive beyond the chat.

## Workflow

1. Define the task objective.
   - Name the requested outcome.
   - Name in-scope and out-of-scope paths when useful.
   - Name required evidence or the reason evidence is not applicable.

2. Execute in bounded turns.
   - Keep updates tied to the task objective.
   - Record decisions as they become stable.
   - Avoid expanding scope without making the new scope explicit.

3. Collect closure evidence.
   - Changed files or produced artifacts.
   - Commands run and pass/fail summaries.
   - Checks skipped, with reason and risk.
   - Residual risks and follow-up tasks.

4. Write the task execution report.
   - Use `templates/task-execution-report.md` or a compatible format.
   - Summarize the process; do not paste raw chat logs.
   - Link to durable repository paths.

5. Archive after reporting.
   - Put completed task reports under `docs/completed-tasks/`.
   - Put generalized process lessons under `docs/agentic/experience/`.
   - Keep reports concise enough that future agents can actually use them.

## Required Report Sections

- Task objective.
- Scope and non-goals.
- Work completed.
- Files or artifacts changed.
- Evidence and commands.
- Decisions made.
- Skipped checks and residual risks.
- Follow-up work.
- Archive location.

## Guardrails

- Do not mark a non-trivial task complete only because edits were made.
- Do not archive raw chat transcripts as project memory.
- Do not hide unresolved risk in optimistic summary language.
- Do not promote a one-off anecdote into a skill or architecture rule unless
  the project has evidence that the lesson is durable.

## Output Standard

The final user-facing response can be short, but the durable report should be
complete enough for an independent reviewer to answer: what was attempted,
what changed, how it was checked, and what remains uncertain.
