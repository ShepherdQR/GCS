---
task_id: 2026-05-26-next-stage-mainline-evidence
status: complete
request: "Complete the next-stage mainline tasks from the GCS narrative map and push when appropriate."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - gcs-scene-generation-engineer
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - docs/architecture/
  - docs/product/
  - docs/agentic/
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - validate-inventory
  - validate-skills
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-26 Next-Stage Mainline Evidence

## Scope

In scope:

- Execute the next-stage mainline from `docs/architecture/95-gcs-narrative-map.md`.
- Add a fixture corpus maturity ladder.
- Add a GCS demo ladder from CLI evidence to Solver Evidence Workbench.
- Add an agent permission threat matrix.
- Add a 20-minute contributor path.
- Update clean active docs where safe, while preserving unrelated dirty files.
- Validate, archive, commit, and push scoped files.

Out of scope:

- Solver/runtime/IO/viewer behavior changes.
- New fixtures, generated scenes, or code changes.
- Editing unrelated repository-audit, AI-governance, or OpusTime local work.
- Changing default quality-gate enforcement.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not stage unrelated local edits that predate this task.

## Context To Read

- `docs/architecture/95-gcs-narrative-map.md`
- `docs/product/gcs-product-user-brief.md`
- `docs/architecture/69-ci-ready-quality-gates.md`
- `docs/architecture/40-quality/verification-strategy.md`
- `docs/architecture/scene-generation-tools.md`
- `fixtures/scene/`
- `docs/agentic/agent-permission-policy.md`
- Owning skill: `gcs-architecture-steward`
- Supporting skills: `gcs-quality-steward`, `gcs-scene-generation-engineer`,
  `task-scoped-session-closer`

## Acceptance Gates

- Corpus ladder defines scene levels, promotion criteria, evidence, and next
  actions.
- Demo ladder connects existing fixtures, replay evidence, viewer workbench,
  and future public demos.
- Permission matrix maps data, untrusted content, outbound communication,
  writes, branch actions, dependencies, and destructive actions.
- Contributor path lets a reviewer build context in one sitting.
- All new docs are linked from a clean entry point or from the narrative map.
- Task card and completed-task archive validate.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-next-stage-mainline-evidence.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-next-stage-mainline-evidence\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
```

## Evidence Bundle

Commands and outcomes:

- `python tools\agentic_design\agentic_toolkit.py validate-task-card
  docs\agentic\tasks\2026-05-26-next-stage-mainline-evidence.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py
  validate-completed-task-report
  docs\completed-tasks\2026-05-26-next-stage-mainline-evidence\README.md`:
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-inventory`:
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-skills`: passed.
- `python tools\agentic_design\agentic_toolkit.py check-dependencies`:
  passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report
  docs\completed-tasks\2026-05-26-next-stage-mainline-evidence\README.md
  --min-score 30`: scored 38/40 after final evidence rewrite.

Changed files:

- `docs/architecture/96-fixture-corpus-maturity-ladder.md`
- `docs/product/gcs-demo-ladder.md`
- `docs/agentic/permission-threat-matrix.md`
- `docs/product/20-minute-contributor-path.md`
- `docs/architecture/95-gcs-narrative-map.md`
- `docs/architecture/README.md`
- `docs/product/README.md`
- `docs/product/gcs-product-user-brief.md`
- `docs/agentic/agent-permission-policy.md`
- `docs/agentic/metrics-dashboard.md`
- `docs/agentic/tasks/2026-05-26-next-stage-mainline-evidence.md`
- `docs/completed-tasks/2026-05-26-next-stage-mainline-evidence/README.md`
- `docs/completed-tasks/README.md`

## Residual Risks

- These are active planning and operating docs, not code implementation.
- Demo and corpus ladders will gain real proof only as future tasks attach
  commands, screenshots, fixture reports, and solver evidence.
- Build, CTest, and UI checks were skipped because this documentation batch
  changed no runtime, solver, fixture, or viewer behavior.
