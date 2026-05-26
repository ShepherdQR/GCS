---
task_id: 2026-05-26-researcher-evidence-roadmap-execution
status: complete
request: "Complete the next seven Narrative map steps: D2 JSON classifier, D3 replay package, B1 expected outputs, R1 researcher preview, researcher README route, Narrative Map v2, Figure 95 refresh, and push scoped changes."
scope: release
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-quality-steward
  - task-scoped-session-closer
affected_contracts:
  - none
affected_paths:
  - README.md
  - docs/architecture/
  - docs/product/
  - docs/agentic/
  - tools/product_demo/
  - tools/architecture_visualization/specs/
required_evidence:
  - D2 diagnostic classification JSON run
  - R1 package smoke JSON run
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

# Researcher Evidence Roadmap Execution

## Scope

Complete the next seven Narrative map steps:

1. add a D2 diagnostic classification script that emits JSON summary evidence;
2. add a D3 replay evidence package;
3. add expected-output files for the B1 benchmark candidate set;
4. add R1 researcher-preview release note and package smoke automation;
5. expand the researcher-facing README route and contribution boundary;
6. upgrade the Narrative map to v2 evidence routes and promotion gates;
7. refresh Figure 95 after the closed weak-axis tasks.

## Non-Goals

- Do not change solver, runtime, IO, viewer, fixture, CMake, or CTest behavior.
- Do not claim public release readiness or external benchmark superiority.
- Do not promote any B1 candidate to B2 or a frozen external benchmark.
- Do not stage unrelated `docs/research/OpusTime/OpusTime.md`,
  `docs/reports/report_/`, or
  `docs/agentic/tasks/2026-05-26-institutional-process-ai-token-economics.md`.

## Acceptance Gates

- D2 script runs the current B1 diagnostic cases and writes a stable JSON
  summary under the D2 demo package.
- B1 expected-output files exist before the script claims a case passed.
- D3 replay package points to an inspectable replay evidence artifact.
- R1 release note and smoke automation describe researcher-preview readiness
  without claiming broad release support.
- README gives researchers a direct path from thesis to D1/D2/D3/B1/R1.
- Narrative map v2 names evidence artifacts and promotion gates for every
  narrative line.
- Figure 95 reflects the post-execution maturity levels and new weak queue.

## Verification Plan

```bat
python tools\product_demo\diagnostic_classification.py --output docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json
python tools\product_demo\r1_package_smoke.py --output docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-researcher-evidence-roadmap-execution.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md --min-score 30
```

## Evidence Bundle

- `python tools\product_demo\diagnostic_classification.py --output docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json`
  returned `[OK] D2 diagnostic classification: 5/5 cases passed`.
- `out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json`
  returned `Status: AcceptedWithWarnings`, `Accepted: true`,
  `gluing.accepted`, and `runtime.commit`.
- `python tools\product_demo\r1_package_smoke.py --output docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json`
  returned `[OK] R1 package smoke: 7/7 checks passed`.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-researcher-evidence-roadmap-execution.md`
  passed after scope was set to `release`.
- `python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md`
  passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-inventory` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-skills` passed.
- `python tools\agentic_design\agentic_toolkit.py check-dependencies` passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md --min-score 30`
  returned closure score `36/40` after final evidence insertion.
- Figure 95 SVG, D2 JSON, and R1 JSON artifacts parsed successfully.

## Residual Risks

- D2 and R1 automation depend on the local `out/build/clang-ninja/GCS.exe`
  executable.
- B1 expected outputs are internal GCS report expectations, not cross-solver
  comparison results.
- R1 is a researcher-preview evidence route, not a general package manager,
  installer, or public binary release.
