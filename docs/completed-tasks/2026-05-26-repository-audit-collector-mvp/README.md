---
task_id: 2026-05-26-repository-audit-collector-mvp
status: complete
session_goal: "Implement the first repository audit collector MVP from the repository audit architecture plan."
archive_target: docs/completed-tasks/2026-05-26-repository-audit-collector-mvp
experience_links:
  - none
---

# Repository Audit Collector MVP

## Task Objective

Implement the first local repository audit collector so GCS can generate a
deterministic JSON snapshot of tracked files, classify artifacts, join module
inventory, and run small repository-shape policy checks.

## Scope And Non-Goals

In scope:

- Add `tools/repository_audit/` with a standard-library Python package.
- Define snapshot, file metric, module metric, counting contract, Git info, and
  finding dataclasses.
- Collect tracked files through Git with quote-path disabled.
- Classify files into the architecture-defined artifact classes.
- Join module source, contract-test, and skill coverage from
  `module_inventory.json`.
- Add `collect` and `check` CLI commands.
- Add focused unit tests.

Out of scope:

- No default quality-gate enforcement.
- No report, diff, historical trend, or external scanner adapter yet.
- No solver, runtime, IO, viewer, fixture, or scene schema behavior changed.

## Interaction Summary

After the Git branch stitch and PR audit permission-policy work, the remaining
visible audit task was `2026-05-26-repository-audit-collector-mvp`. A collector
draft already existed in the worktree, so this task completed the missing test
and closure layer, then validated the collect/check flow.

## Work Completed

- Added repository audit CLI at `tools/repository_audit/repository_audit.py`.
- Added package modules for models, path classification, collection, and policy
  checks.
- Added deterministic snapshot writing with sorted JSON keys.
- Added policy findings for unknown artifact classes, tracked build output,
  missing module interfaces, missing implementations, and missing contract
  tests.
- Added tests for artifact-class coverage, non-ASCII path normalization,
  module inventory join, tracked build-output errors, and stable snapshot JSON.

## Files And Artifacts

- `tools/repository_audit/README.md`: command summary and MVP scope notes.
- `tools/repository_audit/repository_audit.py`: CLI entrypoint.
- `tools/repository_audit/README.md`: user-facing command summary and MVP
  boundary.
- `tools/repository_audit/gcs_repository_audit/models.py`: typed snapshot
  dataclasses.
- `tools/repository_audit/gcs_repository_audit/classify.py`: path
  classification and language hints.
- `tools/repository_audit/gcs_repository_audit/collect.py`: tracked-file
  collection, file metrics, grouping, module join, and JSON writing.
- `tools/repository_audit/gcs_repository_audit/policy.py`: initial policy
  findings.
- `tests/tools/test_repository_audit.py`: focused unit coverage.
- `docs/agentic/tasks/2026-05-26-repository-audit-collector-mvp.md`: task
  card.

## Evidence

```text
python -m unittest tests.tools.test_repository_audit
Ran 5 tests.
OK

python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json
Repository audit snapshot written: var\repository-audit\latest.snapshot.json (790 files, 142737 text lines, 2 findings)

python tools\repository_audit\repository_audit.py check --snapshot var\repository-audit\latest.snapshot.json
Repository audit findings: 0 errors, 2 warnings
[warning] unknown-artifact-class: docs/current-model.md
[warning] unknown-artifact-class: python/requirements.txt

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-collector-mvp.md
[OK] task-card: docs/agentic/tasks/2026-05-26-repository-audit-collector-mvp.md passed

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py audit-pr --base HEAD --head HEAD --include-worktree --task-card docs/agentic/tasks/2026-05-26-repository-audit-collector-mvp.md --completed-archive docs/completed-tasks/2026-05-26-repository-audit-collector-mvp --output docs/agentic/pr-audits/2026-05-26-repository-audit-collector-mvp.json --force
wrote docs/agentic/pr-audits/2026-05-26-repository-audit-collector-mvp.json

python tools\agentic_design\agentic_toolkit.py validate-pr-audit docs\agentic\pr-audits\2026-05-26-repository-audit-collector-mvp.json
[OK] pr-audit: docs/agentic/pr-audits/2026-05-26-repository-audit-collector-mvp.json passed
```

## Decisions

- Keep the first collector standard-library only because it should run in local
  restricted environments.
- Make JSON the canonical output because future reports, diffs, gates, and
  metrics can all project from it.
- Keep warnings non-failing in `check` because the first baseline still needs
  classification tuning.
- Use `module_inventory.json` for module ownership because it is already the
  source of truth for agentic design tooling.

## Skipped Checks And Risks

- Full C++ build, CTest, and CLI were skipped because this task changed support
  tooling only. Residual risk is limited to repository-audit behavior and is
  covered by focused Python tests.
- The collector currently counts physical lines for a whitelist of text
  extensions; comment/code/blank splitting is not implemented.
- The two current warnings need a later classification or exemption decision.

## Follow-Up

- Add Markdown report generation from snapshots.
- Add diff mode for PR/task deltas.
- Add optional `--include-repository-audit` quality-gate integration after a
  few accepted snapshots.
- Decide how to classify `docs/current-model.md` and
  `python/requirements.txt`.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-26-repository-audit-collector-mvp`
- Related experience:
  - none
- Skill, eval, fixture, or tool update needed: future repository-audit report
  and diff commands.
