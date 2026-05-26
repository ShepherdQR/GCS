# External Solver Comparison And Benchmark Plan

Status: seed
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This plan defines how GCS should compare itself against external geometric
constraint solving systems without making premature superiority claims.

GCS should be positioned as a research workbench for evidence-rich diagnostics,
local-to-global semantics, and fixture-backed solver behavior. It should not
claim to compete with mature CAD systems on modeling breadth, UI polish,
commercial support, or performance.

## Source-Grounded Baselines

| Baseline family | Why it matters | Source-grounded facts | Comparison posture |
| --- | --- | --- | --- |
| SolveSpace | Open-source parametric 2D/3D CAD and solver reference. | SolveSpace describes constraints as equations solved numerically with a modified Newton method, with least-squares behavior for under-constrained sketches and initial-position dependence for multiple solutions. Source: [SolveSpace technology](https://solvespace.com/tech.pl). | Compare diagnostic report semantics and reproducible fixture evidence, not CAD feature breadth. |
| FreeCAD Sketcher | Widely used open-source CAD sketcher with visible DoF concepts. | FreeCAD docs describe a 2D sketcher where constraints limit degrees of freedom and a solver supports interactive exploration of sketch DoF. Source: [FreeCAD Sketcher Workbench](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Sketcher_Workbench.md). | Compare how under/over-constrained evidence is exposed and preserved. |
| FreeCAD GCS internals | Open implementation with conflict/redundancy diagnostics in source docs. | FreeCAD source docs expose sketch APIs around conflicting, malformed, partially redundant, and redundant constraints. Source: [FreeCAD Sketcher::Sketch](https://freecad.github.io/SourceDoc/d9/d9b/classSketcher_1_1Sketch.html). | Compare report taxonomy and benchmark inspectability. |
| Siemens D-Cubed 2D DCM | Commercial component baseline for production sketch solving. | Siemens describes D-Cubed 2D DCM as a widely adopted 2D geometric constraint solver, with sketch status feedback including under- and over-constrained geometry. Source: [Siemens D-Cubed 2D DCM](https://www.siemens.com/en-us/products/plm-components/d-cubed/2d-dcm/). | Treat as industry capability reference, not directly reproducible benchmark unless public fixtures and outputs are available. |

## GCS Differentiation Hypothesis

GCS should be evaluated on:

- explicit local-to-global evidence;
- typed reports for rank, residual, gluing, obstruction, rollback, and commit;
- counterexamples preserved as first-class assets;
- benchmark candidate criteria that include unsupported and failing cases;
- agentic workflow evidence that makes solver development reproducible.

GCS should not yet be evaluated on:

- CAD modeling completeness;
- UI productivity;
- commercial integration;
- large-scene performance;
- robust user-facing sketch repair.

## Benchmark Levels

| Level | Name | Purpose | Entry criteria |
| --- | --- | --- | --- |
| B0 | Smoke scenes | Prove the CLI and report path. | One accepted small scene and one expected failure. |
| B1 | Diagnostic classification | Distinguish accepted, under-constrained evidence, over-constrained failure, malformed input, and singular blocked commit. | D2 demo package has command evidence, expected-output files, and JSON summary. |
| B2 | Research microbenchmarks | Small fixed scenes designed to test one semantic claim. | Each scene has expected status, report fields, and source rationale. |
| B3 | Corpus benchmarks | A frozen set covering fixture maturity levels. | Each fixture has provenance, category, expected output, and migration policy. |
| B4 | External comparison benchmarks | Same claims compared against external solver behavior when reproducible. | Publicly reproducible setup and output interpretation. |

## Comparison Dimensions

| Dimension | GCS metric | External observation |
| --- | --- | --- |
| Constraint coverage | Constraint types and scene classes supported. | Which entities and constraints are documented by the baseline. |
| Diagnostic taxonomy | Status, obstruction code, rank/nullity, residuals, rollback. | Whether baseline exposes comparable status or diagnostics. |
| Reproducibility | Command transcript, fixture path, expected output fields. | Whether external setup can be rerun from public inputs. |
| Failure honesty | Expected nonzero exits and counterexample metadata. | Whether failures are explained, hidden, or UI-only. |
| Local-to-global evidence | Covers, boundary agreement, gluing reports. | Whether comparable decomposition evidence is available. |
| Research extensibility | How easily new scenes and report expectations can be added. | Open API, source access, or documented library boundary. |

## First Benchmark Candidate Set

The first candidate set should come from existing GCS scenes:

| Candidate | Role | Current expected status |
| --- | --- | --- |
| `fixtures/scene/basic/g1.txt` | B0 accepted smoke | `AcceptedWithWarnings` |
| `fixtures/scene/verification/lgs/well_constrained.txt` | B1 accepted classification | `AcceptedWithWarnings` |
| `fixtures/scene/verification/lgs/under_constrained.txt` | B1 rank/nullity evidence | `AcceptedWithWarnings` with under-constrained evidence |
| `fixtures/scene/verification/lgs/over_constrained.txt` | B1 expected failure | `Failed`, `runtime.numeric_failure` |
| `fixtures/scene/verification/io/malformed.txt` | B1 malformed input | parse failure |
| `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | B1 singular blocked commit | `NumericallySingular`, `runtime.post_local_diagnostics_blocked` |

## Research Questions

1. Can GCS express diagnostic evidence that a researcher can inspect without
   the GUI?
2. Can GCS preserve failing and singular cases as stable research assets?
3. Can local-to-global evidence explain why a solve was committed, rolled back,
   or blocked?
4. Can a future benchmark compare report semantics instead of only final
   coordinates?
5. Can GCS distinguish unsupported theory gaps from numeric failure?

## Current B1 Evidence

- Expected outputs:
  `docs/architecture/benchmarks/b1-diagnostic-classification/expected/`
- D2 classifier:
  `tools/product_demo/diagnostic_classification.py`
- Current D2 JSON artifact:
  `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json`

## Near-Term Tasks

1. Decide which external baselines can be run locally and which remain
   literature or documentation comparison only.
2. Add one comparison table for each baseline family.
3. Promote no scene to B2 until it passes the benchmark candidate criteria in
   `docs/architecture/98-benchmark-candidate-selection-criteria.md`.
4. Add schema-aware checks for replay evidence and B1 expected-output files.

## Source Links

- [SolveSpace technology](https://solvespace.com/tech.pl)
- [SolveSpace library](https://solvespace.com/library.pl)
- [FreeCAD Sketcher Workbench](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Sketcher_Workbench.md)
- [FreeCAD Sketcher::Sketch source docs](https://freecad.github.io/SourceDoc/d9/d9b/classSketcher_1_1Sketch.html)
- [Siemens D-Cubed 2D DCM](https://www.siemens.com/en-us/products/plm-components/d-cubed/2d-dcm/)
