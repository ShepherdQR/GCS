# External Solver Adapter Decision

Status: active
Date: 2026-05-30
Primary audience: solver and geometric-constraint researchers
Parent: P1.3 from [Narrative Weakness Development Plan](../../agentic/narrative-weakness-development-plan-20260530.md)

## Purpose

Choose the first external solver adapter target or explicitly defer. This
decides direction, not implementation schedule.

## Decision

**FreeCAD Sketcher is the first external solver adapter target.**
Comparison is through its Python API (FreeCADCmd), not GUI interaction, and is
scoped to a single B2 microbenchmark scene with report-field comparison, not a
benchmark suite.

## Rationale

- **Diagnostic vocabulary alignment.** FreeCAD Sketcher source docs expose
  conflict, redundancy, malformed-constraint, and partially-redundant taxonomies
  that map to GCS diagnostic report codes. Comparing report semantics is GCS's
  differentiation. SolveSpace docs describe numerical convergence and
  under-constrained least-squares behavior but do not expose a comparable
  diagnostic taxonomy, so the comparison would reduce to final coordinates.
- **Automation path exists.** FreeCADCmd provides a Python API that can create
  sketches, add constraints, and read solver status programmatically, without a
  GUI. SolveSpace's headless path is undocumented; its library is described as
  coupled with the application code. A headless Python adapter reduces
  integration friction for comparison automation.
- **Research value.** Comparing GCS's typed diagnostic evidence (rank, residual,
  gluing, obstruction, rollback) against FreeCAD's sketch diagnostics produces
  more useful comparison evidence for researchers than comparing final geometry
  against SolveSpace's least-squares output.
- **SolveSpace is not ruled out.** It remains a valid second comparison path.
  The choice of FreeCAD first reflects diagnostic depth over application breadth
  for the initial external evidence, not a judgment on SolveSpace's solver
  quality.

## Scope

**What the first adapter compares**: One GCS B2-02 microbenchmark scene
(`under_constrained.txt`) translated to an equivalent FreeCAD sketch. The
adapter reads GCS report fields (rank/nullity evidence, status code, residual
summary) and FreeCAD Sketcher diagnostics (DoF count, constraint conflict
status, redundancy flags), then writes a comparison note recording what was
comparable, what was not, and what differences mean.

**What is explicitly NOT compared**: CAD feature breadth, UI responsiveness,
large-scene performance, sketch repair quality, or commercial integration.
FreeCAD is run as a solver diagnostic baseline, not as a CAD benchmark
competitor.

## Implementation Notes

A minimal adapter is a Python script (no C++ changes) that:

1. Loads a FreeCAD document, creates a sketch matching the B2-02 scene (points
   with under-constrained geometry).
2. Runs the FreeCAD solver via `Sketch.solve()` or equivalent API.
3. Reads diagnostic fields: constraint status, DoF count, any conflict or
   redundancy indicators.
4. Writes a comparison note to
   `docs/architecture/benchmarks/` with raw output preserved.

The adapter does NOT need to handle all GCS constraint types, all entity types,
or multi-body scenes. One scene, one comparison note.

## Caveats

- This is a decision about which path to pursue first, not a commitment to a
  particular benchmark result or a claim of diagnostic superiority.
- FreeCAD is not currently installed in this environment. The adapter is blocked
  on environment setup, which is a separate decision.
- This decision does not prevent future SolveSpace or D-Cubed comparisons. It
  only sequences them.
- No CI integration is implied. The adapter is a developer tool until proven
  reproducible.

## Predecessors

- [External Solver Comparison and Benchmark Plan](../97-external-solver-comparison-and-benchmark-plan.md)
- [External Baseline Feasibility Matrix](external-baseline-feasibility-matrix.md)
- [B2 Microbenchmark Candidate Review](b2-microbenchmark-candidate-review.md)
