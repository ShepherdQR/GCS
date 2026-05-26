# GCS Agentic Metrics Dashboard

Status: baseline
Snapshot date: 2026-05-26

## Purpose

This dashboard tracks whether the GCS agentic organization is becoming more
reliable, legible, and reviewable. It is intentionally lightweight: update it
after non-trivial lifecycle tasks or during a periodic agentic-SE review.

The dashboard is not a scoreboard. It is a control panel for evidence quality,
workflow health, and narrative maturity.

## Current Baseline

| Area | Current level | Evidence | Next target |
| --- | --- | --- | --- |
| Task-card discipline | Strong for recent non-trivial work | Recent research and narrative tasks have task cards. | Keep 100% coverage for non-trivial tasks or explicit chat-only exception. |
| Completed-task archives | Strong for recent work | Recent non-trivial tasks have validated archives. | Keep index discoverability and closure score for substantial tasks. |
| Closure quality | Strong | `ai-organization-frontier-research` scored 38/40. | Record closure score for each non-trivial archive. |
| Docs validation | Strong | `validate-docs` passes. | Keep passing after architecture or agentic doc changes. |
| Inventory validation | Strong | `validate-inventory` is part of the expected gate. | Run for scoped architecture/agentic batches. |
| Skill validation | Strong | Project skills are the routing layer. | Run after skill or steward-related work. |
| Dependency boundary | Strong | `check-dependencies` is part of the expected gate. | Keep mathematical layers free of UI/IO/agentic dependencies. |
| Product/user narrative | Initial and strengthening | Product brief, demo ladder, contributor path, and first demo package exist. | Add behavior-rich D1 and D2 demo packages. |
| Metrics trend history | Initial | This dashboard is the first active baseline. | Add timestamped updates after important closures. |
| Permission/governance telemetry | Developing | Permission policy, PR governance, threat matrix, and governance eval roadmap exist. | Add prompt-level evals before validator candidates. |

## Metrics To Update

| Metric | Source | Desired direction |
| --- | --- | --- |
| Non-trivial task-card coverage | `docs/agentic/tasks/` and completed-task archives | 100% or explicit exception |
| Completed archive coverage | `docs/completed-tasks/` and index | 100% for non-trivial tasks |
| Closure score | `score-closure-report` output | >= 30 for non-trivial current archives |
| Validation pass rate | agentic toolkit commands | Passing after scoped changes |
| Focused-test usage | task-card evidence bundles | Present for behavior changes |
| Full quality-gate usage | task-card and archive evidence | Run when implementation scope justifies it |
| Review findings | completed-task archive or PR audit | Captured and classified |
| Repeated failure capture | experience records or evals | Captured after second occurrence or high severity |
| Permission escalation count | task-card and archive evidence | Recorded for high-risk actions |
| Unrelated dirty work avoided | git status and commit scope | 100% for commits |

## Current Snapshot

| Item | Value | Notes |
| --- | ---: | --- |
| Active narrative-line research bundle | 1 | `docs/research/20260526/ai-organization-frontier/` |
| New narrative map | 1 | `docs/architecture/95-gcs-narrative-map.md` |
| New product/user brief | 1 | `docs/product/gcs-product-user-brief.md` |
| New fixture corpus maturity ladder | 1 | `docs/architecture/96-fixture-corpus-maturity-ladder.md` |
| New demo ladder | 1 | `docs/product/gcs-demo-ladder.md` |
| New permission threat matrix | 1 | `docs/agentic/permission-threat-matrix.md` |
| New contributor path | 1 | `docs/product/20-minute-contributor-path.md` |
| New agentic organization operating map | 1 | `docs/agentic/agentic-organization-operating-map.md` |
| New institutional-agent scorecard | 1 | `docs/agentic/institutional-agent-registry-and-scorecard.md` |
| New governance eval roadmap | 1 | `docs/agentic/governance-eval-roadmap.md` |
| New product demo package directory | 1 | `docs/product/demos/` |
| Active metrics dashboard | 1 | This document |
| Known unrelated dirty file in current session | 1 | `docs/research/OpusTime/OpusTime.md`; do not stage for narrative commits. |

## Update Rule

Update this dashboard when any of these occur:

- a non-trivial task closes;
- a high-risk task uses a human gate;
- a completed-task archive scores below 30;
- default quality-gate behavior changes;
- a new institutional agent, skill, eval, or governance rule is promoted;
- a release, onboarding, or public-facing narrative milestone is created.

## Evidence Fields For Future Updates

Use this compact format:

```text
Date:
Task:
Task card:
Archive:
Closure score:
Focused checks:
Broad checks:
Skipped checks:
Permission escalations:
Unrelated dirty files preserved:
Follow-up:
```

## Near-Term Targets

| Target | Owner | Acceptance |
| --- | --- | --- |
| Keep narrative-plan task scoped | architecture steward | Commit excludes unrelated OpusTime edit. |
| Add corpus maturity ladder | quality and scene-generation stewards | Fixture levels map to acceptance evidence. |
| Add demo ladder | viewer bridge and architecture stewards | CLI, replay, report, and workbench demos are ordered. |
| Add permission threat matrix | governance owner | Private data, untrusted content, outbound comms, writes, branch actions, and network/dependencies are mapped. |
| Add onboarding path | architecture steward | New reviewer can build, run, inspect evidence, and read the thesis in one sitting. |
| Add D1 and D2 demo packages | product and quality stewards | User-visible demos include command evidence and expected outcomes. |
| Add external comparison plan | architecture and product stewards | GCS can explain its position against solver alternatives. |
