# Next Queue And Forward Plan

Snapshot: 2026-05-24.

## Purpose

This document is the durable handoff for the next GCS agentic-SE queue after
S1-05, Step 49, and the git worktree protocol work. It does not replace the
roadmaps. It condenses the live queue, follow-on waves, and guardrails into one
place so a future session can resume without mining the chat transcript.

## Current Baseline

- Step 47 completed the first full lifecycle sample for runtime replay evidence
  export.
- Step 48 completed the replay evidence consumer path and S1-03
  task-to-archive checklist.
- Step 49 completed the saved replay evidence report artifact and S1-05 archive
  review.
- The git worktree protocol task installed the workspace-boundary rule and
  `new-worktree-task` helper for future parallel Codex sessions.
- `master` was ahead of `origin/master` by the Step 48, Step 49, and git
  worktree protocol commits before this plan/archive closeout.

Committed baseline before this closeout:

- `5496bd2 feat: expose replay evidence consumer`
- `1e46f1a feat: save replay evidence reports`
- `128d4e4 feat: add agentic worktree protocol`

Useful anchors:

- `docs/agentic/agile-pdca-roadmap.md`
- `docs/agentic/near-term-agent-plan.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/architecture/68-forward-execution-plan-2026-05-24.md`
- `docs/architecture/67-current-progress-and-next-steps.md`
- `docs/completed-tasks/2026-05-24-step-47-runtime-replay-evidence-export/README.md`
- `docs/completed-tasks/2026-05-24-step-48-replay-consumer-and-s1-03-checklist/README.md`
- `docs/completed-tasks/2026-05-24-s1-05-step-49-replay-report-artifact/README.md`
- `docs/completed-tasks/2026-05-24-git-worktree-protocol/README.md`

## Immediate Queue

| Order | Task | Primary line | Why now | Exit condition |
| --- | --- | --- | --- | --- |
| 1 | S3-02 negative E001 eval | Institutional/process | E001 now has real positive archives; it needs at least one failure case to prevent false closure. | One failing/passing eval note for false completion or archive pollution. |
| 2 | S1-04 low-risk chat-only boundary | Institutional/process | The lifecycle should say which tiny tasks can avoid completed-task archives. | Entry-criteria table added to the lifecycle runbook. |
| 3 | Step 50 replay evidence report workflow review | Engineering | Step 49 produced saved reports; use them once before adding another consumer surface. | GUI, diagnostics, or report-only direction selected with rationale. |
| 4 | S2-01 opt-in gate design | Tooling/process | Enforcement should wait until S3-02 and S1-04 clarify what should be caught. | Gate policy proposal for opt-in checks, no default enforcement yet. |
| 5 | S4-05 institutional-agent reassessment | Institutional/process | The seed agents now have real examples, but new agents should come from evidence rather than naming enthusiasm. | Candidate table updated after additional real closures. |

## Task Notes

### S3-02 Negative E001 Eval

Goal: add a realistic negative eval that catches either false completion or
archive pollution.

Recommended path:

- Use `docs/agentic/evals/` or the E001 experience folder.
- Include one accepted closure example and one rejected/polluted example.
- State what the evaluator must refuse or downgrade.
- Keep this as evaluation evidence first; do not make it a default gate until
  it catches a real failure mode cleanly.

Evidence:

- Eval note exists.
- Positive and negative cases are distinguishable.
- `validate-docs` passes.

### S1-04 Low-Risk Chat-Only Boundary

Goal: define when a task may stay in chat or PR notes without a completed-task
archive.

Recommended path:

- Update `docs/agentic/lifecycle-runbook.md`.
- Add an entry-criteria table with examples of chat-only tasks, archive-required
  tasks, and escalation triggers.
- Cross-check `task-to-archive-checklist.md` so the checklist remains compact.

Evidence:

- Runbook includes the table.
- Checklist still names the archive gate for non-trivial tasks.
- `validate-docs` passes.

### Step 50 Replay Evidence Report Workflow Review

Goal: decide whether saved replay evidence reports should feed GUI review,
diagnostics packaging, or remain CLI/report artifacts only.

Recommended path:

- Generate or inspect a saved Step 49 report artifact from representative
  fixtures.
- Identify the first real reviewer need.
- Add the smallest consumer contract only if justified.
- Do not alter JSON scene `history` or scene schema in this step.

Evidence:

- Direction selected with rationale.
- Any new consumer preserves runtime replay report semantics.
- Scene construction history remains separate.

### S2-01 Opt-In Gate Design

Goal: design but do not force agentic artifact checks.

Recommended path:

- Propose `--include-task-cards` and `--include-completed-reports` style gates
  for `agentic_toolkit.py`.
- Specify legacy exemptions and new-report behavior.
- Use S3-02 and S1-04 results before choosing default severity.

Evidence:

- Design note or task card exists.
- No default enforcement is introduced prematurely.

### S4-05 Institutional-Agent Reassessment

Goal: decide which standing agents remain seed agents, candidate agents, or
ordinary templates.

Recommended path:

- Review real closure artifacts for Bladesmith, Tailor, Atelier Steward, and
  Art Director.
- Require fit-check evidence before creating new standing-agent directories.
- Keep fuzzy-description-to-role generation as a template pipeline until a role
  has recurring work and testable refusal behavior.

Evidence:

- Candidate table update.
- No new institutional agent without a role-card generator fit check.

## Forward Waves

| Wave | Theme | Tasks | Desired outcome |
| --- | --- | --- | --- |
| A | Closure hardening | S3-02, S1-04 | E001 can reject bad closure and the lifecycle has a sane low-risk boundary. |
| B | Replay report consumer review | Step 50 | The saved report artifact has one proven review path or a documented decision to stay report-only. |
| C | Opt-in gates | S2-01 to S2-04 | Agentic checks become runnable on demand before becoming default policy. |
| D | Institutional-agent maturation | S4-05 plus generator examples | Role packages are promoted from repeated evidence, not invented from a single name. |

## Guardrails

- Do not change JSON scene `history` or scene schema unless a separate migration
  task explicitly approves it.
- Do not make lifecycle gates default until S3-02 proves the negative eval.
- Do not create new institutional-agent directories without fit-check evidence.
- Do not include `.codex_scene_generation_store/` or
  `fixtures/scene/milestone/` in agentic plan/archive commits until those
  generated artifacts are promoted by a scene-generation task.
- Use a dedicated worktree for parallel writing sessions. The shared Local
  checkout is acceptable only for one active scoped writer or integration work.
