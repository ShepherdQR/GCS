---
task_id: 2026-05-25-gcs-solver-ui-requirements-architecture
status: complete
request: "Research GCS solver UI needs from expert and user perspectives, persist the findings, and adjust the UI architecture design with a change record."
scope: docs
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-architecture-steward
  - gcs-python-gui-builder
affected_contracts:
  - viewer_bridge read-only projection
  - diagnostics evidence projection
  - session_runtime command/history boundary
  - Python GUI orchestration boundary
affected_paths:
  - docs/research/20260525/
  - docs/architecture/
  - docs/agentic/tasks/2026-05-25-gcs-solver-ui-requirements-architecture.md
  - docs/completed-tasks/2026-05-25-gcs-solver-ui-requirements-architecture/
required_evidence:
  - source-aware-research-report
  - architecture-adjustment-record
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# GCS Solver UI Requirements Architecture

## Scope

Research the solver-facing needs of the GCS UI from three viewpoints:

- top mathematician: mathematical structure, degeneracy, rank, gauge, and proof
  evidence;
- computer scientist: module boundaries, provenance, replay, performance, and
  inspectable state;
- GCS user: sketching, diagnosing, repairing, replaying, and exporting scenes.

Produce a durable Markdown research report, compare the findings against the
current UI architecture, and update architecture documentation with an explicit
adjustment record.

## Non-Goals

- Do not rewrite the local GUI implementation in this task.
- Do not change solver runtime, numeric behavior, scene schema, fixtures, or
  C++ contracts.
- Do not introduce browser, HTTP, web asset, or external viewer dependencies.

## Context To Read

- `.codex/skills/gcs-ui-design-steward/SKILL.md`
- `.codex/skills/gcs-architecture-steward/SKILL.md`
- `.codex/skills/gcs-python-gui-builder/SKILL.md`
- `docs/architecture/README.md`
- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/72-ui-aesthetic-roadmap.md`
- `docs/architecture/73-gcs-visual-taste-guide.md`
- `docs/architecture/10-system/system-topology.md`
- `docs/architecture/10-system/current-to-target-map.md`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/visualizer.py`

## Acceptance Gates

- The research report separates external source evidence, project-local
  evidence, and GCS-specific inference.
- UI requirements are expressed as solver-facing capabilities, not decorative
  visual preferences.
- The architecture adjustment preserves solver/UI dependency direction.
- The adjustment record states decisions, affected docs, deferred work, and
  acceptance criteria for implementation.
- Validation covers the task card and completed-task archive.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md --min-score 30
```

## Evidence Bundle

Produced:

- `docs/research/20260525/gcs-ui-requirements/01-advanced-ui-and-gcs-solver-requirements.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/README.md`
- `docs/completed-tasks/2026-05-25-gcs-solver-ui-requirements-architecture/README.md`
- `docs/completed-tasks/README.md`

Document linkage check:

```bat
rg -n "Solver Evidence Workbench|Phase 11|Phase 12|gcs-ui-architecture-adjustment|advanced-ui-and-gcs" docs\architecture docs\research\20260525\gcs-ui-requirements docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md
```

Observed result:

- expected research, architecture-record, README, convention, and development
  plan links were found.
- Phase 11 and Phase 12 backlog entries were found in
  `77-ui-design-development-plan-report.md`.

Validation:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md --min-score 30
git diff --check -- docs\architecture\README.md docs\architecture\75-ui-design-system-conventions.md docs\architecture\77-ui-design-development-plan-report.md docs\architecture\92-gcs-ui-architecture-adjustment-record.md docs\research\20260525\gcs-ui-requirements\01-advanced-ui-and-gcs-solver-requirements.md docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md
```

Observed result:

- task-card validation passed.
- completed-task validation passed.
- closure score passed at 35/40.
- diff check passed; Git reported only CRLF normalization warnings for existing
  docs.

## Residual Risks

- External UI/GCS sources may not map perfectly onto this project's staged C++
  and Python architecture; the report must label such mapping as inference.
- Implementation feasibility remains unproven until a later GUI increment adds
  the proposed workbench surfaces and runs visual QA.
