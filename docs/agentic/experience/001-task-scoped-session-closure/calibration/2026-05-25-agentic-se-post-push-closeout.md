---
record_type: e001_closure_calibration
task_id: 2026-05-25-agentic-se-next-direction-closeout
status: complete
updated: 2026-05-25
reviewed_archives:
  - docs/completed-tasks/2026-05-25-s2-04-legacy-artifact-policy/README.md
  - docs/completed-tasks/2026-05-25-s2-05-agentic-default-gate-decision/README.md
  - docs/completed-tasks/2026-05-25-agentic-se-next-direction-closeout/README.md
---

# Agentic-SE Post-Push Closeout Calibration

## Purpose

This record extracts the reusable lesson from the post-push Agentic-SE
closeout session. The useful pattern was not another quality gate. It was the
sequence that turns a finished implementation push into durable next-step
memory:

```text
verify pushed state
  -> update the next-direction plan
  -> archive the session
  -> capture the reusable practice
  -> validate the archive itself
  -> push a scoped documentation commit
```

## Observed Session Pattern

The session started after S2-04 and S2-05 had already landed on `master`. The
user asked for three follow-up outputs: write the next Agentic-SE direction
into the plan, summarize the session into completed tasks, and analyze reusable
experience.

The important control move was to treat that request as a closure task in its
own right. Without a separate closeout record, the project would know that
S2-04/S2-05 landed, but future agents would not know which Agentic-SE direction
was intended next or what practice made the closeout repeatable.

## Reusable Practice

Use a post-push closeout when a user asks to continue after a completed
implementation or policy push.

Required moves:

1. Check the pushed branch/worktree state before editing.
2. Write the next direction into the active plan, not only the final chat
   response.
3. Create a completed-task archive for the closeout if it changes roadmap or
   lifecycle state.
4. Store reusable learning under `docs/agentic/experience/` when the pattern
   can help future sessions.
5. Validate the closeout task card and archive through explicit include gates.
6. Commit only the closeout paths.

## Boundary

This practice should not become mandatory ceremony for tiny status answers or
single-line fixes. It applies when the closeout changes project memory:
roadmaps, next-task queues, completed-task archives, experience records, or
quality-gate policy.

## E001 Rubric Feedback

This session reinforces three E001 dimensions:

| Dimension | Lesson |
| --- | --- |
| Archive usefulness | A pushed implementation is not fully resumable until the next queue and archive index are also updated. |
| Learning promotion | A reusable closeout sequence belongs in the experience area before it becomes a new skill or gate. |
| Follow-up separation | Next Agentic-SE tasks should be written as ordered candidates with exit conditions, not mixed into completed-work summaries. |

## Future Gate Candidate

Do not add a hard validator yet. A useful future check would be a lightweight
completed-task warning when a roadmap file changes but no archive or follow-up
section names the next task. That warning should wait for more examples.
