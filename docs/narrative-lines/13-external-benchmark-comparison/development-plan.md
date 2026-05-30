# 13 — External Benchmark/Comparison

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`
Weakness plan: `docs/agentic/narrative-weakness-development-plan-20260530.md`

## Current Level

**Strong but split (3.5)**

## Current State

External comparison plan, benchmark criteria, feasibility matrix, B1 expected
outputs, D2 JSON summary, and B2 candidate review exist. The intellectual
framework for comparison is solid.

## Main Gap

No executable external baseline run exists yet. All comparison work is
analytical, not empirical.

## Weakness Root Cause

No executable external baseline run exists.

## Evidence Artifact

B1 expected outputs, external comparison plan, feasibility matrix, and B2
candidate review.

## Promotion Gate

Produce the first optional external baseline run or source-level comparison
note.

## Next Move

Decide and document the first optional SolveSpace or FreeCAD external adapter.

## Development Plan

### Phase 1: Close Smallest Feedback Loops (next 2-4 weeks)

1. Decide external adapter path (P1.3 from weakness plan):
   - Choose either SolveSpace (application-level comparison) or FreeCAD
     Sketcher (solver-level comparison) as the first external adapter target,
     or explicitly defer with dated rationale.
   - If chosen: write a one-paragraph scope (what GCS scenes map to what
     external inputs, what outputs are compared).
   - If deferred: specify what condition would trigger reconsideration.
2. Add B2 expected-output files for B2-01 and B2-02 microbenchmarks
   (P3.2 from weakness plan).

### Phase 3: Benchmark Execution (next 4-12 weeks, depends on P1.3)

3. Run the chosen external solver on a subset of GCS fixtures or a common
   benchmark scene.
4. Compare output against GCS output on the same scene.
5. Write a comparison note (not a benchmark claim) recording:
   - What was compared
   - What was comparable
   - What was not
   - What differences mean
6. Store the note at `docs/architecture/benchmarks/` with links to raw outputs.

### Long-term (12+ weeks)

7. If the first external baseline is informative, select a second external
   solver for comparison.
8. Build a benchmark table that summarizes comparison results across solvers,
   always using "difference" language rather than ranking.

## Dependencies

- Fixture corpus (04): B2 fixtures are the comparison input.
- Solver evidence (01): GCS output is the comparison baseline.
- Release/packaging (12): reproducible builds ensure comparison integrity.

## Related

- Arc 4: Product And Adoption
- `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`
- `docs/architecture/98-benchmark-candidate-selection-criteria.md`
- `docs/agentic/narrative-weakness-development-plan-20260530.md` (P1.3, P3.1, P3.2)
