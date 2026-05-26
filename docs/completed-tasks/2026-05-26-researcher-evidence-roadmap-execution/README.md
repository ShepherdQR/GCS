---
task_id: 2026-05-26-researcher-evidence-roadmap-execution
status: complete
session_goal: "Complete the next seven Narrative map steps: D2 JSON classifier, D3 replay package, B1 expected outputs, R1 researcher preview, researcher README route, Narrative Map v2, Figure 95 refresh, and push scoped changes."
archive_target: docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution
experience_links:
  - docs/product/demos/d2-diagnostic-classification/README.md
  - docs/product/demos/d3-replay-evidence/README.md
  - docs/architecture/benchmarks/b1-diagnostic-classification/README.md
  - docs/product/releases/r1-researcher-preview-20260526.md
  - docs/architecture/95-gcs-narrative-map.md
---

# Researcher Evidence Roadmap Execution

## Task Objective

Complete the seven next Narrative map steps so the project moves from a
researcher-audience decision to an executable researcher evidence route.

## Scope And Non-Goals

In scope:

- D2 JSON diagnostic classifier.
- D3 replay evidence package.
- B1 expected-output files.
- R1 researcher-preview release note and package smoke automation.
- README researcher route and contribution boundary.
- Narrative Map v2 evidence routes and promotion gates.
- Figure 95 baseline refresh.
- Validation, archive, scoped commit, and push.

Out of scope:

- Solver/runtime/IO/viewer/CMake behavior changes.
- Public binary, installer, or broad CAD-product release.
- External solver execution.
- B2 benchmark promotion.
- Staging unrelated OpusTime, report, token-economics research, or
  token-economics archive files.

## Interaction Summary

The user asked to complete the next seven Narrative map steps and push when
appropriate. The batch treated researchers as the primary audience and focused
on turning weak external-legibility lines into runnable or inspectable
evidence.

## Work Completed

- Added `tools/product_demo/diagnostic_classification.py`.
- Added B1 expected-output files under
  `docs/architecture/benchmarks/b1-diagnostic-classification/`.
- Generated D2 JSON evidence at
  `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json`.
- Added D3 replay evidence package and generated replay JSON under
  `docs/product/demos/d3-replay-evidence/artifacts/`.
- Added `tools/product_demo/r1_package_smoke.py`.
- Added R1 researcher-preview release note and generated package-smoke JSON.
- Expanded the root README researcher route and added a researcher contribution
  boundary.
- Upgraded the Narrative map to v2 evidence routes and promotion gates.
- Refreshed Figure 95 YAML, SVG, and PNG review render.
- Updated product, architecture, demo, release, benchmark, and metrics docs.

## Files And Artifacts

- `tools/product_demo/diagnostic_classification.py`: D2/B1 classifier.
- `tools/product_demo/r1_package_smoke.py`: R1 smoke automation.
- `docs/architecture/benchmarks/b1-diagnostic-classification/`: B1 expected
  outputs.
- `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json`:
  D2 JSON run output.
- `docs/product/demos/d3-replay-evidence/`: replay evidence demo package.
- `docs/product/releases/r1-researcher-preview-20260526.md`: release note.
- `docs/product/releases/artifacts/r1-researcher-preview-smoke-20260526.json`:
  R1 smoke output.
- `docs/product/researcher-contribution-boundary.md`: contribution scope.
- `README.md`: researcher route.
- `docs/architecture/95-gcs-narrative-map.md`: Narrative Map v2 update.
- `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.svg`:
  refreshed Figure 95 SVG.
- `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.review.png`:
  refreshed Figure 95 PNG review render.

## Evidence

```text
python tools\product_demo\diagnostic_classification.py --output docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json
[OK] D2 diagnostic classification: 5/5 cases passed -> docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json

out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json
Status: AcceptedWithWarnings
Accepted: true
gluing.accepted
runtime.commit

python tools\product_demo\r1_package_smoke.py --output docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json
[OK] R1 package smoke: 7/7 checks passed -> docs/product/releases/artifacts/r1-researcher-preview-smoke-20260526.json

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution/README.md passed

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-evidence-roadmap-execution\README.md --min-score 30
Closure score: 36/40 for docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution/README.md

[xml](Get-Content -Path docs\architecture\70-visualization\assets\figure95-narrative-line-level-baseline-20260526.svg -Raw) | Out-Null
Get-Content docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json -Raw | ConvertFrom-Json | Out-Null
Get-Content docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json -Raw | ConvertFrom-Json | Out-Null
[OK] svg and json artifacts parsed
```

## Decisions

- D2 expected outputs live under `docs/architecture/benchmarks/` so benchmark
  criteria remain reviewable documentation.
- D2 and R1 automation live under `tools/product_demo/` because they collect
  evidence for product demos rather than changing solver behavior.
- R1 is named "researcher preview" and explicitly excludes installer,
  broad-compatibility, GUI-first, performance, and CAD feature-parity claims.
- Narrative Map v2 adds evidence artifacts and promotion gates instead of
  adding more abstract narrative prose.
- Figure 95 scores moved weak external lines upward only where executable or
  inspectable evidence now exists.

## Skipped Checks And Risks

- CMake build and CTest were skipped because this batch did not change solver,
  runtime, IO, viewer, fixture, or build behavior.
- D2 and R1 scripts depend on the local `out/build/clang-ninja/GCS.exe`.
- B1 expected outputs are internal GCS report expectations, not external
  benchmark results.
- D3 replay evidence is field-checked by R1 smoke, but not yet schema-checked
  by a dedicated replay validator.
- The completed-task index also has unrelated token-economics work in the
  working tree; staging must keep this task scoped.

## Follow-Up

- Add a schema-aware replay evidence checker.
- Add an external-baseline feasibility matrix.
- Review B1 expected outputs for B2 research microbenchmark candidates.
- Add a D5 Solver Evidence Workbench screenshot package after visual QA.
- Capture the first external researcher review or contribution as an
  archive-backed example.
- Exercise E-GOV-001, E-GOV-002, and E-GOV-008 in real task archives before
  validator design.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-26-researcher-evidence-roadmap-execution/`
- Task card:
  `docs/agentic/tasks/2026-05-26-researcher-evidence-roadmap-execution.md`
- Session learning:
  - experience: candidate, because this batch demonstrates how to turn weak
    narrative-map lines into executable researcher evidence.
  - skill: no immediate promotion; existing architecture, quality, and closure
    skills were sufficient.
  - agent: no immediate promotion; future agent work should wait for external
    review or repeated replay/benchmark maintenance examples.
