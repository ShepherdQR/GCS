# Experience Forging Note: Step 47 Lifecycle Execution

Date: 2026-05-24

Role: `刀匠: 淬炼-锻打`

Status: reusable

## Source Scope

- Session/task: Step 47 deterministic runtime replay evidence export.
- Time range: 2026-05-24 lifecycle execution.
- Source artifacts:
  - `docs/agentic/tasks/2026-05-24-step-47-runtime-replay-evidence-export.md`
  - `docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md`
  - `docs/architecture/66-implementation-execution-roadmap.md`
  - `docs/architecture/67-current-progress-and-next-steps.md`
  - `docs/architecture/68-forward-execution-plan-2026-05-24.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Step 47 created a high-risk task card before code changes, added runtime export DTOs and tests, passed build, CTest, CLI smoke, and full quality gates, then closed with architecture and archive updates. |
| Decisions | Keep the first export in `session_runtime`; keep CLI/GUI consumption as Step 48; keep JSON scene `history` untouched; skip `裁缝` because the user explicitly requested that. |
| Preferences | The project prefers real lifecycle evidence over backfilled narratives and wants institutional agents to produce concrete artifacts. |
| Hypotheses | Step 47 is a strong sample for S1-03 checklist design and E001 closure scoring, but that still needs a later review pass. |
| Open questions | Whether Step 48 should expose the report first through CLI, viewer bridge, or a small report adapter. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| High-risk implementation needs a task card before edits. | Runtime, IO, history, evidence, or contract ownership can drift. | Create and validate a task card with scope, non-goals, owner, gates, and human-gate reason before touching code. | Do not fabricate task cards after the fact for already-finished work. | `docs/agentic/tasks/2026-05-24-step-47-runtime-replay-evidence-export.md` | Low-risk chat-only work may use lighter entry criteria once S1-04 defines them. |
| Producer and consumer steps should be split when ownership is fragile. | A feature introduces a new report contract and a tempting UI/CLI output path. | Implement the producer contract first, then register the consumer path as the next step. | Do not add scene IO, CLI, GUI, and runtime behavior in one closure just to feel complete. | Step 47 completion and Step 48 registration in `docs/architecture/66-implementation-execution-roadmap.md` | If a user asks explicitly for end-to-end UI output in the same task, split only after confirming acceptance criteria. |
| Sandbox failures are infrastructure evidence, not semantic failures. | Build or CTest fails because generated files or logs need access outside the default sandbox. | Rerun the same required gate with escalation and record the reason. | Do not reinterpret permission failures as product regressions. | Step 47 task card and completed-task evidence bundle | Real compiler, test, or CLI failures still require diagnosis and fixes. |
| Institutional-agent use must honor explicit omissions. | The lifecycle normally includes multiple roles but the user excludes one. | Run useful remaining roles and record the omission as intentional scope. | Do not silently create a timeline artifact when `裁缝` is excluded. | Completed-task non-goals and risks | If the user later asks for timeline reconstruction, treat it as a fresh task. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| Every lifecycle sample should immediately create both `刀匠` and `裁缝` outputs. | The user explicitly skipped `裁缝`, and a forced timeline artifact would violate scope. | At least two samples where timeline stitching was requested and proved useful. |
| Runtime replay export should be written into JSON scene `history` for convenience. | Step 46 and Step 47 evidence preserve runtime reports and scene construction history as separate domains. | A future explicit IO migration design with stable scene action payloads. |
| Full quality gates always run cleanly inside the default sandbox. | Step 47 needed escalation for build output and CTest log access. | A sandbox configuration change or dedicated writable build/log paths. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

This sample should feed S1-03's task-to-archive checklist. The lesson is not a
new skill yet; it is a concrete checklist rule set for high-risk lifecycle
execution.

## Follow-Up

- Use this note when designing S1-03 task-to-archive checklist.
- Use this archive and note in S1-05/S3-01 closure-rubric review.
- Keep `裁缝` deferred until the user asks for timeline stitching or two
  related lifecycle samples need causal reconstruction.
