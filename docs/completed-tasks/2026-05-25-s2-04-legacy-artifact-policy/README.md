---
task_id: 2026-05-25-s2-04-legacy-artifact-policy
status: complete
session_goal: "Define legacy Agentic artifact migration and exemption policy before default gate decisions."
archive_target: docs/completed-tasks/2026-05-25-s2-04-legacy-artifact-policy
experience_links:
  - none
---

# S2-04 Legacy Artifact Policy

## Task Objective

Complete S2-04 by defining how legacy task cards, completed-task reports, and
low-risk no-archive work are classified before any default Agentic artifact
gate enforcement.

## Scope And Non-Goals

In scope:

- add an explicit legacy artifact policy;
- document completed-task archive labels and gate treatment;
- update the opt-in gate policy with S2-04 state;
- produce the first post-policy opt-in gate cycle.

Out of scope:

- no migration of the whole historical archive tree;
- no default gate behavior change;
- no solver/runtime/IO/viewer behavior change;
- no unrelated UI/item4 files from another worktree.

## Interaction Summary

The user asked to execute Agentic-SE plan steps 1, 2, and 3. This first step
implemented S2-04 so S2-05 can make a default-enforcement decision without
turning legacy archives into a broad cleanup project. A parallel read-only
agent reviewed the policy boundary and recommended explicit labels for current,
migratable, narrative, low-risk, and parallel-session artifacts.

## Work Completed

- Added `docs/agentic/legacy-artifact-policy.md`.
- Added completed-task index guidance for `validator-clean`, `migrated`,
  `legacy-exempt`, `low-risk-no-archive`, and `parallel-session-pending`.
- Updated `docs/agentic/quality-gate-opt-in-policy.md` so legacy artifacts
  reference the S2-04 policy instead of an unresolved future step.
- Created and validated this S2-04 task card and archive.
- Ran the S2-04 task through explicit task-card and completed-report include
  gates.

## Files And Artifacts

- `docs/agentic/legacy-artifact-policy.md`: S2-04 policy source of truth.
- `docs/completed-tasks/README.md`: archive label and gate-treatment summary.
- `docs/agentic/quality-gate-opt-in-policy.md`: S2-04 status and default
  behavior clarification.
- `docs/agentic/tasks/2026-05-25-s2-04-legacy-artifact-policy.md`: task card.
- `docs/completed-tasks/2026-05-25-s2-04-legacy-artifact-policy/README.md`:
  this archive.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-s2-04-legacy-artifact-policy.md
[OK] task-card passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy\README.md
[OK] completed-task-report passed.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy\README.md --min-score 30
Closure score: 38/40.

python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-s2-04-legacy-artifact-policy.md --include-completed-reports docs\completed-tasks\2026-05-25-s2-04-legacy-artifact-policy
All requested quality gates passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs validation passed.
```

## Decisions

- Classify old artifacts rather than forcing bulk migration.
- Require migration only when a new task uses a legacy artifact as active
  evidence.
- Treat `2026-05-25-agentic-se-roadmap-items-1-2-3-5` as useful
  pre-policy rehearsal evidence, not one of the two official post-policy
  S2-05 cycles.
- Exclude parallel-session artifacts from current-task gate evidence until the
  owning session lands or hands off.

## Skipped Checks And Risks

- Full CMake build and CTest were skipped because this task changes Agentic SE
  policy documentation only.
- Historical archives remain mixed-format by design. The risk is controlled by
  explicit labels and migration triggers rather than broad validation.

## Follow-Up

- S2-05 should use this task and the S2-05 decision task as two post-policy
  opt-in cycles.
- Future migration tasks should record why a legacy artifact became active
  evidence.
- A future current-task default gate needs an explicit current-artifact
  declaration mechanism.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-25-s2-04-legacy-artifact-policy`
- Related experience:
  - none
- Skill, eval, fixture, or tool update needed: S2-05 default-gate decision.
