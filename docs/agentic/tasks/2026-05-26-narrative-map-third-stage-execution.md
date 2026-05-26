---
task_id: 2026-05-26-narrative-map-third-stage-execution
status: complete
request: "Persist the next Narrative map development plan as a design document, then complete the seven next steps: replay checker, external feasibility matrix, B2 review, D5 workbench evidence package, external researcher archive, governance eval promotion, Figure 95 trend, and push scoped changes."
scope: release
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - gcs-ui-design-steward
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - docs/architecture/
  - docs/product/
  - docs/agentic/
  - tools/product_demo/
  - tools/architecture_visualization/specs/
required_evidence:
  - replay-evidence-check
  - d5-workbench-package-render
  - screenshot-baseline-check
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - validate-inventory
  - validate-skills
  - check-dependencies
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# Narrative Map Third-Stage Execution

## Scope

Persist the next Narrative map development plan as a design document and then
complete the seven planned steps:

1. add a schema-aware replay evidence checker;
2. add an external-baseline feasibility matrix;
3. review B1 expected outputs for B2 microbenchmark candidates;
4. add a D5 Solver Evidence Workbench screenshot package with visual QA;
5. capture a first external researcher review or contribution archive;
6. promote governance eval evidence from seed-only toward exercised status;
7. add Figure 95 trend artifacts.

## Non-Goals

- Do not change solver, runtime, IO, viewer, CMake, or CTest behavior.
- Do not claim D5 is a complete GUI implementation.
- Do not claim external benchmark superiority or executable parity.
- Do not stage unrelated OpusTime, report, token-economics research, or
  token-economics archive files.

## Acceptance Gates

- The design plan exists under `docs/architecture/` and maps all seven steps.
- Replay checker validates the D3 artifact and writes JSON evidence.
- External feasibility matrix separates executable, source-available,
  documentation-only, and commercial/proprietary baselines.
- B2 candidate review explicitly promotes or defers each B1 case.
- D5 package includes deterministic PNG, manifest, and screenshot-baseline QA.
- External researcher archive records a realistic first-review packet and
  follow-up without inventing an actual outside reviewer.
- Governance eval roadmap and eval seed docs reflect exercised evidence.
- Figure 95 has a trend document/spec tied to the latest maturity movement.

## Verification Plan

```bat
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
python tools\product_demo\d5_workbench_package.py --output docs\product\demos\d5-solver-evidence-workbench\artifacts\d5-workbench-evidence.png --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
python tools\ui_qa\gcs_screenshot_baseline.py --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-narrative-map-third-stage-execution.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-narrative-map-third-stage-execution\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-narrative-map-third-stage-execution\README.md --min-score 30
```

## Evidence Bundle

```text
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
[OK] replay evidence check: 17/17 checks passed -> docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json

python tools\product_demo\d5_workbench_package.py --output docs\product\demos\d5-solver-evidence-workbench\artifacts\d5-workbench-evidence.png --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
[OK] D5 workbench package rendered -> docs/product/demos/d5-solver-evidence-workbench/artifacts/d5-workbench-evidence.png (92228 bytes)
[OK] screenshot manifest -> docs/product/demos/d5-solver-evidence-workbench/artifacts/screenshot-baselines.json

python tools\ui_qa\gcs_screenshot_baseline.py --manifest docs\product\demos\d5-solver-evidence-workbench\artifacts\screenshot-baselines.json
GCS screenshot baseline checks passed (1 baselines)

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-narrative-map-third-stage-execution.md
[OK] task-card: docs/agentic/tasks/2026-05-26-narrative-map-third-stage-execution.md passed

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-narrative-map-third-stage-execution\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-narrative-map-third-stage-execution/README.md passed

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-narrative-map-third-stage-execution\README.md --min-score 30
Closure score: 36/40 for docs/completed-tasks/2026-05-26-narrative-map-third-stage-execution/README.md
```

## Residual Risks

- External-baseline feasibility is a documentation and local-environment
  assessment, not a completed cross-solver benchmark.
- D5 screenshot package is a deterministic evidence-board artifact, not a
  live GUI screenshot.
- External researcher archive is a first-review packet and self-review
  artifact until a real outside reviewer responds.
