# External Baseline Feasibility Matrix

Status: active
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This matrix turns the external comparison plan into an execution decision. It
separates baselines that can be run in this local checkout from baselines that
currently support documentation or source-level comparison only.

The goal is not benchmark superiority. The goal is to make future comparison
work honest, reproducible, and bounded.

## Source Register

| Source | Used for | Confidence |
| --- | --- | --- |
| `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` | Baseline families and comparison dimensions. | High |
| `docs/architecture/98-benchmark-candidate-selection-criteria.md` | Promotion rules for C2 and external comparison candidates. | High |
| `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json` | Current GCS B1 diagnostic evidence. | High |
| `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json` | Current D3 replay-evidence checker result. | High |
| [SolveSpace technology](https://solvespace.com/tech.pl) | Solver method, under-constrained behavior, and numerical posture. | High |
| [SolveSpace library](https://solvespace.com/library.pl) | Library availability and executable/library coupling. | Medium |
| [FreeCAD Sketcher Workbench](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Sketcher_Workbench.md) | Sketcher DoF and constraint-facing behavior. | Medium |
| [FreeCAD Sketcher::Sketch source docs](https://freecad.github.io/SourceDoc/d9/d9b/classSketcher_1_1Sketch.html) | Conflict, redundancy, and sketch API taxonomy. | Medium |
| [Siemens D-Cubed 2D DCM](https://www.siemens.com/en-us/products/plm-components/d-cubed/2d-dcm/) | Commercial industry reference and public diagnostic claims. | High |

## Local Executability Check

Current local command evidence:

```text
Get-Command solvespace, SolveSpace, FreeCAD, freecad -ErrorAction SilentlyContinue

solvespace False
SolveSpace False
FreeCAD    False
freecad    False

Test-Path out\build\clang-ninja\GCS.exe
True
```

Interpretation:

- GCS is executable in this checkout.
- SolveSpace and FreeCAD are not currently available on `PATH` in this
  environment.
- Siemens D-Cubed is a commercial component reference and is not treated as a
  local executable benchmark.

## Feasibility Matrix

| Baseline | Local executable status | Public comparison status | Near-term comparison mode | Decision |
| --- | --- | --- | --- | --- |
| GCS internal B1/D2 | Executable: `out/build/clang-ninja/GCS.exe` exists. | Full local artifacts exist. | Run D2 classifier and D3 replay checker. | Active internal baseline. |
| SolveSpace application | Not detected on local `PATH`. | Public docs describe equation-based numerical solving and under-constrained least-squares behavior. | Documentation comparison now; executable comparison after local install and fixture translation. | Candidate external executable, not active yet. |
| SolveSpace library | Not built locally. | Public docs describe a library surface but also note coupling with the application code. | Source/API feasibility review before any adapter. | Defer executable adapter until install/build decision. |
| FreeCAD Sketcher | Not detected on local `PATH`. | Public docs describe Sketcher constraints, DoF, and interactive solver behavior. | Documentation/source comparison now; executable comparison requires FreeCAD or FreeCADCmd harness. | Candidate external executable after environment setup. |
| FreeCAD Sketcher internals | Not built locally. | Public source docs expose sketch diagnostics and redundancy/conflict vocabulary. | Taxonomy comparison against GCS report codes. | Active documentation/source baseline. |
| Siemens D-Cubed 2D DCM | Not publicly runnable in this checkout. | Public product page describes broad entity/constraint support and sketch status feedback. | Industry capability reference only. | Documentation-only baseline unless a licensed trial and public fixture protocol exist. |

## Comparison Readiness By Dimension

| Dimension | GCS current evidence | SolveSpace | FreeCAD Sketcher | Siemens D-Cubed |
| --- | --- | --- | --- | --- |
| Small fixture execution | D1/D2/D3 runnable locally. | Needs install and scene translation. | Needs install and macro or command harness. | Not available publicly. |
| Diagnostic taxonomy | B1 expected outputs and D2 JSON summary exist. | Docs describe convergence and under-constrained behavior, but not a matching report schema. | Docs and source docs expose DoF, conflict, and redundancy vocabulary. | Product docs mention under/over-constrained feedback. |
| Replay or transaction evidence | D3 report and checker exist. | Not identified in public docs. | Not identified in public docs for command-level replay. | Not public. |
| External reproducibility | Internal only. | Possible after local install. | Possible after local install. | Not currently reproducible from public artifacts. |
| Research comparison value | High for report semantics. | High for numerical sketch-solving posture. | High for DoF and diagnostic taxonomy. | Medium as industry reference, low for reproducible benchmark. |

## First External Comparison Sequence

1. Keep GCS B1/D2/D3 as the active internal evidence route.
2. Promote no external comparison result until the baseline executable and
   fixture translation are recorded.
3. Use SolveSpace and FreeCAD as documentation/source baselines in the next
   comparison note.
4. Add one environment setup decision before installing or requiring either
   executable.
5. Treat Siemens D-Cubed as capability context, not as a benchmark result.

## Open Questions

- Which external fixture format should GCS translate first: SolveSpace sketch,
  FreeCAD Sketcher macro, or a neutral textual scenario?
- Should external executable setup be optional developer tooling or part of a
  future benchmark CI profile?
- Which B2 microbenchmark should be translated first once the local adapter
  decision is made?
