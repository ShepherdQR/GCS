---
task_id: 2026-05-26-repository-audit-diff-mode
status: complete
session_goal: "Persist and execute the next repository-audit statistics plan by adding diff mode."
archive_target: docs/completed-tasks/2026-05-26-repository-audit-diff-mode
experience_links:
  - none
---

# Repository Audit Diff Mode

## Task Objective

Add deterministic diff mode to the repository-audit tool so GCS can compare
two saved snapshots or two committed Git revisions and quantify repository
shape changes.

## Scope And Non-Goals

In scope:

- Add a typed `RepositoryAuditDiff` model.
- Add snapshot-to-snapshot comparison for totals, groups, files, and findings.
- Add Git revision collection for committed snapshots.
- Add `repository_audit.py diff`.
- Add focused tests for added, removed, modified, group delta, and stable JSON
  output.
- Persist the task card, architecture note update, and completed-task archive.

Out of scope:

- No rename detection.
- No historical trend dashboard.
- No default quality-gate enforcement.
- No external scanner adapters.
- No solver, runtime, IO, viewer, fixture, or scene schema behavior changed.

## Interaction Summary

The user asked to persist the remaining audit-statistics plan and continue
execution. The chosen next node was diff mode because it is the foundation for
per-task repository-shape deltas, future trend reports, quality-gate
integration, and session-efficiency joins.

## Work Completed

- Added `tools/repository_audit/gcs_repository_audit/diff.py`.
- Added `RepositoryAuditDiff`, `NumericDelta`, `GroupMetricDelta`,
  `FileMetricDelta`, and `FindingDelta`.
- Added committed-revision snapshot collection through Git tree reads.
- Added CLI support:
  - `diff --base-snapshot ... --head-snapshot ... --output ...`
  - `diff --base <rev> --head <rev> --output ...`
- Updated repository-audit README commands.
- Updated the repository-audit architecture Phase 3 implementation note.
- Added focused unit coverage.

## Files And Artifacts

- `tools/repository_audit/gcs_repository_audit/diff.py`: diff computation and
  stable JSON writer.
- `tools/repository_audit/gcs_repository_audit/models.py`: diff dataclasses and
  schema version.
- `tools/repository_audit/gcs_repository_audit/collect.py`: committed revision
  snapshot collection.
- `tools/repository_audit/repository_audit.py`: `diff` command.
- `tools/repository_audit/README.md`: diff command examples and scope update.
- `tests/tools/test_repository_audit.py`: focused diff tests.
- `docs/architecture/94-repository-audit-statistics-architecture.md`: Phase 3
  implementation note.
- `docs/agentic/tasks/2026-05-26-repository-audit-diff-mode.md`: task card.

## Evidence

```text
python -m unittest tests.tools.test_repository_audit
Ran 8 tests.
OK

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-diff-mode.md
[OK] task-card: docs/agentic/tasks/2026-05-26-repository-audit-diff-mode.md passed

python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\diff-head-prev.json
Repository audit diff written: var\repository-audit\diff-head-prev.json (13 changed files, 1104 text-line delta, 0 added findings, 0 removed findings)

python tools\repository_audit\repository_audit.py check
Repository audit findings: 0 errors, 0 warnings

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-repository-audit-diff-mode\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-repository-audit-diff-mode/README.md passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-repository-audit-diff-mode\README.md --min-score 30
Closure score: 38/40
Passed the configured minimum.
```

## Decisions

- Keep diff output JSON-only for the first node because downstream reports,
  quality gates, and dashboards should project from one canonical artifact.
- Support saved snapshots and Git revisions so the same diff engine can serve
  local baselines, task evidence, and future PR workflows.
- Report renames as remove plus add for now because robust rename detection
  belongs to a later Git-aware projection.
- Use the current `module_inventory.json` for revision snapshots. Historical
  inventory-at-revision support can be added if module ownership drift becomes
  a real analysis need.

## Skipped Checks And Risks

- Full C++ build, CTest, and CLI were skipped because this task changed Python
  support tooling and documentation only.
- Revision snapshot collection reads committed Git trees; it does not represent
  uncommitted worktree edits.
- Diff output can become large on broad repository changes; later report
  projections should summarize top deltas rather than pasting every file into
  Markdown.

## Follow-Up

- Add a Markdown projection for `RepositoryAuditDiff`.
- Add trend report generation from a series of accepted snapshots or diffs.
- Add opt-in quality-gate integration once several diff samples are accepted.
- Join diff outputs with future session-efficiency records.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-26-repository-audit-diff-mode`
- Related experience:
  - none
- Skill, eval, fixture, or tool update needed: future diff Markdown renderer
  and trend reporter.
