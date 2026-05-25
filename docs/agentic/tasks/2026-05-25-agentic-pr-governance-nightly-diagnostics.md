---
task_id: 2026-05-25-agentic-pr-governance-nightly-diagnostics
status: complete
request: "Research enterprise agentic software-governance practice, improve GCS PR audit design, and install a safe nightly immune-diagnostics workflow."
scope: docs
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - gcs-session-runtime-steward
  - gcs-diagnostics-certification-steward
  - gcs-scene-generation-engineer
  - task-scoped-session-closer
affected_contracts:
  - Agentic PR audit governance
  - Nightly immune diagnostics workflow
  - Agentic evidence and closure artifacts
affected_paths:
  - docs/research/20260525/agentic-pr-governance/
  - docs/agentic/pr-audit-governance.md
  - docs/agentic/nightly-immune-diagnostics.md
  - docs/agentic/tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics.md
  - docs/completed-tasks/2026-05-25-agentic-pr-governance-nightly-diagnostics/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
  - run-quality-gates with explicit task and completed-report includes
human_gate_required: false
human_gate_reason: ""
---

# Agentic PR Governance And Nightly Diagnostics

## Scope

Research current public practice from leading AI software-agent providers and
use it to improve GCS governance around exploratory PRs, PR audit, and nightly
immune diagnostics.

The durable outputs are a source-aware research report, detailed subtopic
reports, GCS PR audit design, GCS nightly immune-diagnostics design, a Codex
nightly automation, and a completed-task archive.

## Non-Goals

- Do not change solver, IO, scene, viewer, or runtime behavior code.
- Do not create an unattended automation that merges, force-pushes, or deletes
  branches.
- Do not treat external vendor patterns as project policy until mapped to GCS
  contracts and lifecycle rules.
- Do not promote generated scenes into `fixtures/scene/` during this task.

## Context To Read

- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/quality-gate-opt-in-policy.md`
- `docs/architecture/61-agentic-module-framework.md`
- `docs/architecture/62-module-agents.md`
- `docs/architecture/63-target-contract-interface-implementation-test-design.md`
- `docs/architecture/65-agentic-implementation-tooling.md`
- `docs/architecture/69-ci-ready-quality-gates.md`
- `docs/completed-tasks/2026-05-24-scene-auto-explorer-design-implementation-plan/README.md`

## Acceptance Gates

- The research report has a source register and distinguishes vendor facts from
  GCS-specific inferences.
- PR audit governance defines risk tiers, required evidence, review subjects,
  forbidden unattended actions, and exploratory-PR handling.
- Nightly immune diagnostics defines deterministic dated outputs, stage gates,
  defect taxonomy, repair boundaries, failure recovery, and summary artifacts.
- The automation prompt is self-contained and forbids unattended merge/push.
- The task card and completed-task archive validate through the Agentic tools.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md --include-completed-reports docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- Branch created: `codex/agentic-pr-governance-nightly`.
- Research report written:
  `docs/research/20260525/agentic-pr-governance/README.md`.
- Subtopic reports written:
  `docs/research/20260525/agentic-pr-governance/subtopics/`.
- PR audit governance written:
  `docs/agentic/pr-audit-governance.md`.
- Nightly diagnostics design written:
  `docs/agentic/nightly-immune-diagnostics.md`.
- Codex automation created:
  `gcs-nightly-immune-diagnostics`, daily `02:30 Asia/Shanghai`, worktree
  execution.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md`: passed after status/specialist-agent metadata fix.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics\README.md --min-score 30`: passed, 37/40.
- `python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --include-task-cards docs\agentic\tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics.md --include-completed-reports docs\completed-tasks\2026-05-25-agentic-pr-governance-nightly-diagnostics`: passed.

## Residual Risks

- External vendor documentation changes quickly; the report records source dates
  and should be refreshed before converting recommendations into default gates.
- The first nightly automation run may reveal missing local command
  dependencies or long runtime; the design requires explicit failure summaries.
