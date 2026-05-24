# Task-To-Archive Checklist

Status: S1-03 complete.

Use this checklist for non-trivial GCS work, especially high-risk solver,
runtime, IO, viewer, quality-gate, or institutional-agent tasks. It is meant to
be short enough to use during a real implementation turn and strict enough to
prevent false closure.

## Entry Rule

Create a persisted task card when any of these are true:

- the task touches solver contracts, report codes, runtime commit or replay,
  IO schemas, quality gates, or public CLI/viewer behavior;
- the task spans more than one module, workstream, or institutional-agent role;
- the task will need a completed-task archive to resume later;
- the user asks for a plan, lifecycle execution, commit, or durable process
  update.

Tiny low-risk edits may stay chat-only only when S1-04's low-risk table allows
it.

## Checklist

| Check | Required Evidence | Done When |
| --- | --- | --- |
| Classify | Scope, risk, owner, affected contracts | The task card names the owning module or institutional agent. |
| Gate | Human-gate reason for high-risk work | High-risk task cards explain why the user request authorizes execution. |
| Boundaries | Non-goals and refused ownership | The task says what will not be changed. |
| Context | Skills and source docs read | Relevant module skills and architecture docs are named. |
| Implementation | Smallest scoped durable change | Code/docs stay inside named ownership boundaries. |
| Focused Verification | Narrow tests or validators | Tests cover the changed contract before broad gates. |
| Full Verification | Build, CTest, quality gate, or explicit skip | Skips are explained as scope decisions, not treated as passes. |
| Evidence Bundle | Commands plus interpreted result | The task card records pass/fail outcomes after commands run. |
| Archive | Completed-task report and index link | Non-trivial work has a validated archive. |
| Score | Closure score or no-score reason | E001 score is recorded for non-trivial archives. |
| Learn | Experience, checklist, eval, or no-promotion reason | Process learning is explicit and evidence-bound. |
| Roadmap | Next task or step is updated | Roadmaps stop pointing at completed work. |
| Commit Scope | Staged files inspected | The commit includes only scoped files and avoids unrelated dirty work. |

## Checked Example: Step 47

| Check | Step 47 Result |
| --- | --- |
| Classify | High-risk runtime replay evidence export task card created at `docs/agentic/tasks/2026-05-24-step-47-runtime-replay-evidence-export.md`. |
| Gate | Human gate recorded because the user explicitly requested Step 47 execution. |
| Boundaries | JSON scene `history`, IO schemas, and `裁缝` were out of scope. |
| Context | Runtime, C++ solver, scene behavior, quality, and architecture context were read. |
| Implementation | `RuntimeReplayEvidenceExport` and deterministic runtime export API added in `session_runtime`. |
| Focused Verification | `SessionRuntimeContract|ViewerBridgeContract` passed 21/21. |
| Full Verification | Build, full CTest 113/113, CLI smoke, and `run-quality-gates` passed. |
| Evidence Bundle | Task card evidence section records commands and pass summaries. |
| Archive | `docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md` validated and indexed. |
| Score | Closure score recorded as 37/40. |
| Learn | `刀匠` forging note created under institutional-agent examples. |
| Roadmap | Step 47 marked complete; Step 48 registered; S1-03 moved next. |
| Commit Scope | Step 47 remained separable from unrelated dirty worktree changes. |

## Failure Signals

- Evidence is written as a plan but never replaced with actual command output.
- A completed-task archive lacks index discoverability.
- A roadmap still points at a task that the implementation already completed.
- A role output invents causality or generalizes from one sample without a
  provisional label.
- A commit stages unrelated dirty files because they were nearby.

When any failure signal appears, stop closing the task and fix the lifecycle
record before moving on.
