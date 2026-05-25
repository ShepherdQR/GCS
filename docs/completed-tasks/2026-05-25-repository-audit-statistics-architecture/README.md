---
task_id: 2026-05-25-repository-audit-statistics-architecture
status: complete
session_goal: "Research mature repository audit/statistics practices and persist a GCS-specific repository audit architecture."
archive_target: docs/completed-tasks/2026-05-25-repository-audit-statistics-architecture
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/
---

# Repository Audit Statistics Architecture

## Task Objective

Produce a durable source-aware research report on mature repository audit and
statistics practices, capture a lightweight GCS repository baseline, and define
a GCS-specific architecture for reproducible file, LOC, module, fixture,
documentation, and evidence-growth reporting.

## Scope And Non-Goals

In scope:

- internet-backed research using official or authoritative sources;
- GCS architecture and quality-gate boundary review;
- current Git-tracked file and line-count baseline;
- a proposed repository audit data model, command surface, storage policy, and
  phased implementation plan;
- task-card and completed-task closure.

Out of scope:

- implementation of `tools/repository_audit`;
- changes to C++ solver behavior, scene schemas, fixtures, or Python GUI code;
- default quality-gate enforcement for repository audit findings;
- committing unrelated local edits.

## Interaction Summary

The user first asked for a plan to research how famous projects audit codebase
statistics such as LOC and file counts, then requested execution and push. The
work used `source-aware-research-report`, `gcs-architecture-steward`,
`gcs-contract-tools-steward`, and `task-scoped-session-closer` guidance.
External research covered GitHub Linguist, cloc, tokei, SonarQube, CNCF
DevStats/project health, CHAOSS, OpenSSF Scorecard, GitHub Code Scanning,
OWASP Dependency-Check, Chromium PRESUBMIT/checkdeps/CODEOWNERS, and the Linux
Kernel History Report.

Project context was read from architecture topology, verification strategy,
quality gates, module inventory, agentic tooling, and contract-tool guidance.
A lightweight GCS baseline was collected with Git tracked files only and
`core.quotepath=false` so non-ASCII tracked paths were not corrupted by Git's
quoted octal path output.

## Work Completed

- Created a scoped task card for repository audit/statistics architecture work.
- Wrote a source-aware research report with source register, comparative
  patterns, GCS baseline statistics, recommendations, and open questions.
- Wrote a durable architecture proposal for a repository audit support-tool
  package, canonical JSON snapshot schema, artifact classes, module joins,
  policy checks, report shape, storage policy, quality-gate integration, and
  implementation phases.
- Updated the architecture README to index the new architecture note.
- Created this completed-task archive and updated the completed-task index.

## Files And Artifacts

- `docs/research/20260525/repository-audit-statistics/README.md`: source-aware
  research report and GCS baseline.
- `docs/architecture/94-repository-audit-statistics-architecture.md`: proposed
  repository audit/statistics architecture.
- `docs/architecture/README.md`: index entry for the new architecture note.
- `docs/agentic/tasks/2026-05-25-repository-audit-statistics-architecture.md`:
  task card for this work.
- `docs/completed-tasks/2026-05-25-repository-audit-statistics-architecture/README.md`:
  completed-task archive.
- `docs/completed-tasks/README.md`: completed-task index entry.

## Evidence

External source research:

```text
Web research completed.
Covered source families:
- GitHub Linguist and repository-language docs.
- cloc and tokei source repositories.
- SonarQube metric definitions.
- CNCF project health, DevStats, and Kubernetes Project Journey Report.
- CHAOSS metrics lifecycle.
- OpenSSF Scorecard and checks documentation.
- GitHub Code Scanning and CODEOWNERS docs.
- OWASP Dependency-Check.
- Chromium PRESUBMIT and checkdeps.
- Linux Foundation Linux Kernel History Report.
Result: source register recorded in research report.
```

GCS baseline collection:

```text
git -c core.quotepath=false ls-files
Result: 738 tracked files in the sampled workspace baseline.

PowerShell text scan over whitelisted text extensions
Result: 711 scanned text files and approximately 115,318 physical text lines.
```

Architecture docs validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed
```

Document linkage check:

```text
rg -n "Repository Audit|repository-audit-statistics|94-repository" docs\architecture docs\research\20260525\repository-audit-statistics docs\agentic\tasks\2026-05-25-repository-audit-statistics-architecture.md
Result: expected research, architecture, task-card, and README links found.
```

Task-card validation was run before final evidence text was added:

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-repository-audit-statistics-architecture.md
Initial result: failed only because an affected-contracts template placeholder remained.
Fix: replaced placeholder with RepositoryAuditSnapshot.
```

## Decisions

- The canonical repository audit output should be JSON; Markdown reports are
  human-readable projections.
- The audit layer belongs in support tooling, preferably
  `tools/repository_audit`, with orchestration hooks in `agentic_toolkit.py`.
- GCS audit categories must separate solver source, app shell, viewer Python,
  tooling, contract tests, fixtures, architecture docs, research docs, agentic
  process docs, completed-task archives, Codex skills, generated stores, and
  visual assets.
- Initial checks should be mostly warning-level and opt-in until baseline
  history exists.
- External tools such as cloc, tokei, github-linguist, Scorecard, CodeQL, and
  SCA scanners should be optional adapters, not default local dependencies.

## Skipped Checks And Risks

- Full `run-quality-gates` was skipped because this task changed only research,
  architecture, task-card, and archive documentation.
- No implementation tests were run because `tools/repository_audit` was not
  implemented in this task.
- The GCS baseline numbers will drift after this task is committed because the
  report and archive files themselves add Markdown lines.
- `cloc`, `tokei`, and `scc` were not available in the local environment, so
  the baseline uses a PowerShell/Git tracked-file scan rather than a dedicated
  LOC parser.
- Existing unrelated dirty worktree entry `docs/research/OpusTime/OpusTime.md`
  was observed and intentionally left untouched.

## Follow-Up

Recommended next implementation task:

```text
Title: Repository audit collector MVP

Goal:
Implement tools/repository_audit with a deterministic collect command that
emits RepositoryAuditSnapshot JSON from Git tracked files, classifies artifact
classes, joins module_inventory.json, handles non-ASCII paths, and includes
focused unit tests. Do not add default quality-gate enforcement yet.
```

Later work:

- add Markdown report generation;
- add diff mode against a base revision;
- add opt-in `--include-repository-audit` gate;
- evaluate `.gitattributes` alignment for GitHub Linguist;
- decide whether `.codex_scene_generation_store/` should stay tracked or move
  toward promoted fixture-only storage.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-repository-audit-statistics-architecture/`
- Task card:
  `docs/agentic/tasks/2026-05-25-repository-audit-statistics-architecture.md`
- Research report:
  `docs/research/20260525/repository-audit-statistics/README.md`
- Architecture note:
  `docs/architecture/94-repository-audit-statistics-architecture.md`
- Related experience:
  `docs/agentic/experience/001-task-scoped-session-closure/`
- Skill, eval, fixture, or tool update needed:
  no immediate skill update; future implementation should use
  `gcs-contract-tools-steward` and `gcs-quality-steward`.
