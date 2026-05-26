---
task_id: 2026-05-26-researcher-audience-narrative-stage
status: complete
session_goal: "Advance all next-stage narrative-line tasks, set researchers as primary audience, persist D1/D2 demos, release readiness, external comparison, benchmark criteria, governance eval seeds, narrative map updates, and push scoped changes."
archive_target: docs/completed-tasks/2026-05-26-researcher-audience-narrative-stage/
experience_links:
  - docs/product/researcher-audience-strategy.md
  - docs/product/demos/d1-cli-smoke/README.md
  - docs/product/demos/d2-diagnostic-classification/README.md
  - docs/architecture/97-external-solver-comparison-and-benchmark-plan.md
  - docs/agentic/evals/governance/README.md
---

# Researcher-Audience Narrative Stage

## Task Objective

Complete the next narrative-stage batch by making solver and
geometric-constraint researchers the primary audience, then turning the
relative weak narrative lines into concrete researcher-facing artifacts.

## Scope And Non-Goals

In scope:

- Researcher primary-audience strategy.
- D1 CLI smoke demo package with command and replay evidence.
- D2 diagnostic classification demo package with expected positive and
  negative examples.
- Release-readiness and package-smoke criteria.
- External solver comparison and benchmark candidate selection criteria.
- Prompt-level governance eval seeds for unrelated dirty staging, audit
  approval overclaim, and institutional-agent promotion overclaim.
- Narrative map and Figure 95 baseline refresh.
- Task card, completed-task archive, validation, scoped commit, and push.

Out of scope:

- Solver, runtime, IO, viewer, fixture, CMake, or test behavior changes.
- Public release claim or packaging implementation.
- Frozen benchmark promotion.
- Executable external solver integrations.
- Staging unrelated `docs/research/OpusTime/OpusTime.md` or
  `docs/reports/report_/` changes.

## Interaction Summary

The user asked to continue the next-stage tasks, explicitly define the primary
audience as researchers, and push when the batch was complete. The work
targeted the weak axis from the narrative map: product legibility, release
readiness, external comparison, benchmark discipline, governance evals, and
researcher-facing distribution.

## Work Completed

- Set the primary audience to solver and geometric-constraint researchers.
- Added D1 CLI smoke and D2 diagnostic classification demo packages.
- Persisted D1 replay evidence under the demo artifact directory.
- Added a release-readiness checklist with R0/R1/R2/R3 modes and R1
  researcher-preview gates.
- Added a researcher audience strategy that defines jobs, message hierarchy,
  non-positioning, and adoption path.
- Added external solver comparison and benchmark planning, grounded in
  source-linked SolveSpace, FreeCAD Sketcher, FreeCAD GCS, and Siemens D-Cubed
  references.
- Added benchmark candidate selection criteria so benchmark claims require
  expected outputs and solver evidence.
- Added prompt-level governance eval seeds for E-GOV-001, E-GOV-002, and
  E-GOV-008.
- Refreshed the narrative map, Figure 95 source YAML, SVG, and PNG review
  baseline to show the post-batch maturity levels.
- Updated product, architecture, agentic, demo, metrics, and completed-task
  indexes.

## Files And Artifacts

- `docs/product/researcher-audience-strategy.md`: primary audience decision
  and adoption narrative.
- `docs/product/release-readiness-checklist.md`: R0/R1/R2/R3 readiness ladder.
- `docs/product/demos/d1-cli-smoke/README.md`: D1 smoke demo package.
- `docs/product/demos/d1-cli-smoke/artifacts/g1-replay-evidence.report.json`:
  persisted replay evidence generated from `g1.txt`.
- `docs/product/demos/d2-diagnostic-classification/README.md`: D2 diagnostic
  classification demo package.
- `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`:
  external comparison and benchmark plan.
- `docs/architecture/98-benchmark-candidate-selection-criteria.md`: benchmark
  candidate selection criteria.
- `docs/agentic/evals/governance/`: governance eval seed directory.
- `docs/architecture/95-gcs-narrative-map.md`: refreshed levels, weakness
  analysis, and next task queue.
- `docs/architecture/70-visualization/narrative-line-level-baseline-20260526.md`:
  refreshed baseline brief.
- `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.svg`:
  refreshed editable figure.
- `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.review.png`:
  refreshed PNG review figure.
- `tools/architecture_visualization/specs/figure95-narrative-line-level-baseline.yaml`:
  Figure 95 source data.
- `docs/agentic/tasks/2026-05-26-researcher-audience-narrative-stage.md`:
  task card.
- `docs/completed-tasks/2026-05-26-researcher-audience-narrative-stage/README.md`:
  this archive.

## Evidence

```text
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
Status: AcceptedWithWarnings
Accepted: true
runtime.post_local_diagnostics.rank_report: rank 3, variables 6, free 6, frozen 0, residuals 3, nullity 3
runtime.post_local_diagnostics.residual_report: residuals 3, norm 0.000000, max 0.000000
gluing.accepted: All local sections are compatible within boundary tolerance.
session_runtime.commit: Ok

out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d1-cli-smoke\artifacts\g1-replay-evidence.report.json
[OK] replay evidence report written after the artifact directory was available.

out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\well_constrained.txt
Status: AcceptedWithWarnings
Accepted: true

out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\under_constrained.txt
Status: AcceptedWithWarnings
Accepted: true

out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\over_constrained.txt
Status: Failed
Accepted: false
runtime.numeric_failure

out\build\clang-ninja\GCS.exe fixtures\scene\verification\io\malformed.txt
Failed to load scene
io.parse.entity_count

out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
Status: NumericallySingular
Accepted: false
runtime.post_local_diagnostics_blocked

[xml](Get-Content -Path docs\architecture\70-visualization\assets\figure95-narrative-line-level-baseline-20260526.svg -Raw) | Out-Null; Write-Output "[OK] svg xml parsed"
[OK] svg xml parsed

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-researcher-audience-narrative-stage.md
[OK] task-card: docs/agentic/tasks/2026-05-26-researcher-audience-narrative-stage.md passed

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md
[OK] completed-task-report: docs/completed-tasks/2026-05-26-researcher-audience-narrative-stage/README.md passed

python tools\agentic_design\agentic_toolkit.py validate-docs
[OK] docs: module design coverage passed

python tools\agentic_design\agentic_toolkit.py validate-inventory
[OK] inventory: structured module inventory passed

python tools\agentic_design\agentic_toolkit.py validate-skills
[OK] skills: all module skills passed

python tools\agentic_design\agentic_toolkit.py check-dependencies
[OK] dependencies: import boundaries passed

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-researcher-audience-narrative-stage\README.md --min-score 30
Closure score: 34/40 for docs/completed-tasks/2026-05-26-researcher-audience-narrative-stage/README.md
```

Figure 95 PNG review render was visually checked after refresh; rows, score
labels, and the relative weakness queue fit inside the canvas.

## Decisions

- The primary audience is solver and geometric-constraint researchers, not
  general CAD users, makers, or enterprise buyers.
- Researcher adoption should begin from evidence semantics: CLI behavior,
  diagnostics, replay, benchmark criteria, and reproducibility.
- External comparison should judge GCS on evidence and diagnostic semantics,
  not CAD feature breadth.
- Benchmark candidate promotion requires expected outputs and repeatable
  reports before public claims.
- Governance evals remain prompt-level seeds until they have enough real
  archives to justify validator candidates.
- Figure 95 numeric scores are visual aids; textual levels in the narrative
  map remain the source of truth.

## Skipped Checks And Risks

- Build and CTest were skipped because this batch changed only documentation,
  demo notes, governance eval seeds, and visual artifacts.
- D1/D2 demos are still command-line packages rather than a polished UI
  walkthrough.
- The release checklist defines readiness but does not implement packaging.
- External comparison is a source-grounded plan, not an executed benchmark
  result.
- Benchmark criteria are in place, but no B1 expected-output file set is frozen
  yet.
- The governance eval seeds are not automatic gates.

## Follow-Up

- Add a D2 diagnostic classification script that emits JSON summary evidence.
- Add a D3 replay evidence package using the D1 replay report as seed input.
- Add B1 expected-output files for benchmark candidate fixtures.
- Add package smoke automation and an R1 researcher-preview release note.
- Draft researcher-facing README expansion and contribution boundary.
- Decide which external baselines are executable locally and which remain
  documentation-only comparisons.
- Exercise E-GOV-001, E-GOV-002, and E-GOV-008 against real task archives
  before designing validators.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-26-researcher-audience-narrative-stage/`
- Related active docs:
  - `docs/architecture/95-gcs-narrative-map.md`
  - `docs/product/researcher-audience-strategy.md`
  - `docs/product/release-readiness-checklist.md`
  - `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`
  - `docs/architecture/98-benchmark-candidate-selection-criteria.md`
  - `docs/agentic/governance-eval-roadmap.md`
- Session learning:
  - experience: candidate, because this batch converts a weak narrative map
    into a researcher-audience execution package.
  - skill: no immediate promotion, because existing architecture, quality, and
    closure skills already cover the workflow.
  - agent: no immediate promotion, because governance evals need more archive
    examples before a new institutional agent should be created.
- Revisit promotion after the D2 JSON script, D3 replay package, and B1
  benchmark expected-output files close.
