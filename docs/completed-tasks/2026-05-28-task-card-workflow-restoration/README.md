---
task_id: 2026-05-28-task-card-workflow-restoration
status: complete
session_goal: "Diagnose why task card workflow stopped, implement three-layer defense to restore it."
archive_target: docs/completed-tasks/2026-05-28-task-card-workflow-restoration
---

# Task Card Workflow Restoration

## Task Objective

Analyze why the GCS task card (计划卡) pattern stopped producing new cards after
2026-05-26, then implement a three-layer defense to restore the plan-then-act
workflow.

## Root Cause Analysis

Three decisions combined to cause the drift:

1. **S2-05 opted out of default enforcement** (2026-05-25): task-card validation
   was explicitly kept opt-in, citing the lack of a current-task artifact
   declaration mechanism
2. **Lifecycle runbook Step 1.5 created a broad low-risk escape hatch**: many
   tasks could be classified as not needing a persisted card
3. **Governance execution queue shifted focus from docs to tooling**: the
   pattern became "implement → archive directly" rather than "create card →
   implement → archive"

Evidence: 67 task cards from 2026-05-24 to 2026-05-26, zero from 2026-05-27.
The ONLY draft card was `2026-05-24-agentic-operating-layer.md` — the
foundational card about the task card system itself.

## What Changed

### Layer 1: Code Gate (agentic_toolkit.py)

- New `.claude/current-task` file: `new-task-card --write` auto-sets it,
  `run-quality-gates` auto-reads it
- `read_current_task()`, `write_current_task()`, `clear_current_task()` helpers
- `--require-task-card` flag for strict CI enforcement
- Auto-detection: when `.claude/current-task` exists, task-card validation is
  included in quality gates automatically — no `--include-task-cards` needed

### Layer 2: Behavior Instruction (CLAUDE.md)

- New "Task Card Requirement" section with concrete command
- Explicit trivial-vs-nontrivial boundary
- Placed adjacent to Agentic Toolkit commands for discoverability

### Layer 3: Process Gate (session-close-orchestrator)

- New Step 0: Task Card Gate
- Auto-creates task card from session metadata when missing (not hard-blocking)
- Updates draft cards to complete, fills evidence bundles

### Bug Fix: token_audit/cli.py

- `db import --force` was missing `DELETE FROM chapters` before deleting
  sessions, causing FOREIGN KEY constraint failure
- Added chapters table deletion to the cascade

### Documentation

- `docs/agentic/default-agentic-gate-decision.md`: S2-05 Amendment section
  documenting the current-task declaration mechanism and updated enforcement
  posture
- `docs/agentic/tasks/2026-05-28-task-card-workflow-restoration.md`: this
  session's task card (auto-created at closeout, proving the new flow)

## Evidence

| Check | Result |
|-------|--------|
| `new-task-card --write` writes `.claude/current-task` | Verified |
| `run-quality-gates` auto-detects from `.claude/current-task` | Verified |
| `run-quality-gates --require-task-card` fails without card | Verified |
| Python syntax (`ast.parse`) | Passed |
| `db import --force` with chapters FK fix | Passed (10 imported) |

## Decisions

| Decision | Rationale |
|----------|-----------|
| Auto-create task card at closeout (not hard-block) | Prevents deadlock while establishing the norm |
| `.claude/current-task` as a flat key-value file (not JSON) | Simplicity; one file, one pointer |
| Keep `--require-task-card` opt-in for now | Needs calibration on real CI branches first |
| `2026-05-24-agentic-operating-layer.md` left as draft | It was a meta-card about the system; the system is now operational |

## Token Benefit Summary

| Metric | Value |
|--------|-------|
| Scope | Root cause analysis + 3-layer implementation + bug fix |
| Files Changed | 5 (+126/-5 lines in main commit) + 2 (archive + task card) |
| Commits | 1 (cbaf7ef), + archive commit pending |

## Experience / Skill / Agent Evaluation

| Material | Decision | Reason |
|----------|----------|--------|
| Experience | candidate | The "three-layer defense" pattern (code gate + behavior instruction + process gate) for lifecycle drift is reusable. Recorded here; needs a second instance before forging. |
| Skill | no | No skill change needed — the orchestrator already covers closeout. |
| Agent | no | No new agent role needed. |

## Follow-up

- [ ] Calibrate `--require-task-card` on two non-documentation CI branches
- [ ] Update `2026-05-24-agentic-operating-layer.md` from draft to complete
- [ ] Observe whether future sessions naturally follow the "task card first" pattern
