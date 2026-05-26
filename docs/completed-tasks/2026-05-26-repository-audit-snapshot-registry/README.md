---
task_id: 2026-05-26-repository-audit-snapshot-registry
status: complete
session_goal: "Add accepted repository-audit snapshot registry support, persist the first accepted baseline, validate, and close the task."
archive_target: docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/
experience_links:
  - docs/architecture/94-repository-audit-statistics-architecture.md
---

# Repository Audit Snapshot Registry

## Task Objective

Finish the accepted snapshot registry layer for repository-audit statistics so
durable baselines are separated from local scratch snapshots and can be indexed
from committed revisions.

## Scope And Non-Goals

In scope:

- Add committed-revision snapshot collection support.
- Add accepted snapshot manifest discovery.
- Generate a durable repository-audit registry index.
- Persist the first accepted baseline manifest and snapshot.
- Classify tracked `docs/product/**` files as `product_doc`.
- Validate the focused repository-audit tests and task archive.

Out of scope:

- Default quality-gate enforcement.
- External scanners.
- Historical chart rendering.
- Solver/runtime/IO/viewer behavior changes.

## Interaction Summary

The working tree already contained the registry implementation draft and first
accepted baseline artifacts. This closeout verified that the files belong to
the current AI governance and repository-audit arc, completed the missing
archive, and included the registry in the push scope.

## Work Completed

- Added `collect --revision` for committed-revision snapshots.
- Added `gcs_repository_audit.registry` for accepted manifest loading and
  Markdown index rendering.
- Added CLI `index` command for `docs/reports/repository-audit/README.md`.
- Added focused unit coverage for accepted snapshot registry rendering.
- Updated repository-audit architecture and README docs.
- Added `product_doc` classification so tracked product-facing docs do not
  appear as unknown audit findings.
- Persisted `docs/reports/repository-audit/2026-05-26/manifest.json` and
  `snapshot.json`.

## Files And Artifacts

- `tools/repository_audit/gcs_repository_audit/registry.py`: manifest loading
  and registry index rendering.
- `tools/repository_audit/repository_audit.py`: `collect --revision` and
  `index` CLI support.
- `tools/repository_audit/gcs_repository_audit/classify.py`: `product_doc`
  artifact classification.
- `tools/repository_audit/README.md`: accepted snapshot usage examples.
- `tests/tools/test_repository_audit.py`: registry rendering test.
- `docs/reports/repository-audit/2026-05-26/manifest.json`: accepted baseline
  manifest.
- `docs/reports/repository-audit/2026-05-26/snapshot.json`: accepted baseline
  snapshot.
- `docs/reports/repository-audit/README.md`: generated accepted snapshot
  registry.
- `docs/architecture/94-repository-audit-statistics-architecture.md`:
  architecture update for registries.

## Evidence

```text
python -m unittest tests.tools.test_repository_audit
Ran 11 tests.
OK

python tools\repository_audit\repository_audit.py collect --revision HEAD --output docs\reports\repository-audit\2026-05-26\snapshot.json
Repository audit snapshot written: docs\reports\repository-audit\2026-05-26\snapshot.json (825 files, 149448 text lines, 0 findings)

python tools\repository_audit\repository_audit.py report --snapshot docs\reports\repository-audit\2026-05-26\snapshot.json --output docs\reports\repository-audit\2026-05-26\README.md
Repository audit report written: docs\reports\repository-audit\2026-05-26\README.md

python tools\repository_audit\repository_audit.py index --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\README.md
Repository audit index written: docs\reports\repository-audit\README.md (1 accepted snapshots)

python tools\repository_audit\repository_audit.py check
Repository audit findings: 0 errors, 0 warnings

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-snapshot-registry.md
[OK] task-card: docs/agentic/tasks/2026-05-26-repository-audit-snapshot-registry.md passed

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-repository-audit-snapshot-registry\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/README.md passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-repository-audit-snapshot-registry\README.md --min-score 30
Closure score: 38/40
Passed the configured minimum.

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed
```

## Decisions

- Accepted baselines should point at committed revisions, not dirty worktree
  state.
- `docs/reports/repository-audit/` is the durable accepted snapshot boundary.
- `var/repository-audit/` remains local scratch and should not be treated as
  persistent evidence.
- Registry support remains explicit; it is not a default quality gate.
- `docs/product/**` is a product-facing documentation surface and should be
  counted as `product_doc`, not left as `unknown`.

## Skipped Checks And Risks

- Build, CTest, and UI checks are skipped because the change is a Python
  support tool and documentation update.
- The first registry has only one accepted snapshot, so trend cadence policy
  remains future work.
- The dated human report was regenerated from the accepted snapshot in this
  task, but chart and cadence policy remain future work.

## Follow-Up

- Add chart output after at least two accepted baselines exist.
- Add an accepted-trend command that consumes the registry directly.
- Join repository-audit deltas with future session-efficiency records.
- Decide recurring cadence for accepted snapshots.
- Decide whether repository-audit should be selected in quality gates only for
  milestone releases or also for every phase close.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/`
- Related architecture:
  `docs/architecture/94-repository-audit-statistics-architecture.md`
- Skill, eval, fixture, or tool update needed:
  - No new skill. Continue under `gcs-contract-tools-steward`.
