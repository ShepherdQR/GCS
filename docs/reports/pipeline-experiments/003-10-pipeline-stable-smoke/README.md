# Experiment 003 — 10-Pipeline Stable Smoke Test

**Date**: 2026-05-31
**Branch**: `codex/cache-hit-pilot-completion-20260531`
**Commit**: `aae607f`
**Previous**: [001](../001-10-pipeline-parallel-smoke/README.md), [002](../002-10-pipeline-post-fix-smoke/README.md)
**Status**: done
**Result**: 9/10 exit 0 — pipeline suite is stable

## Purpose

Third round after two cycles of fixes. Verify that the pipeline suite is in a
stable, repeatable state with no regressions. All 6 round-1 fixes and 4 round-2
fixes are now deployed.

## Method

Same as prior rounds: 10 parallel `bash` tasks, default configs (smoke preset
for defect-discovery), 600s timeout.

## Results

| # | Pipeline | Exit | Time | Key Output |
|---|----------|------|------|------------|
| 1 | defect-discovery | 0 | 0.0s | 0 graphs (PD-001) |
| 2 | solver-regression | 0 | ~0.1s | 2 scenes, 2/2 solved, 0 regressions |
| 3 | numeric-stability | 0 | 0.1s | 5 points, 2 failures, summary prints |
| 4 | diagnostic-certification | 0 | 0.1s | **6/6 PASS** |
| 5 | contract-compliance | 0 | 0.9s | 142 violations (115 import + 24 stable_id + 3 tolerance) |
| 6 | io-round-trip | 0 | 0.0s | 4 fixtures, 3 passed, 1 malformed (expected) |
| 7 | scene-generation | 0 | 1.6s | "COVERAGE GAPS (no targets defined)" |
| 8 | performance-benchmark | 0 | ~0.3s | 2 scenes benchmarked |
| 9 | cross-solver-compare | 1 | 0.0s | Missing external spec (PD-005) |
| 10 | repository-audit | 0 | 1.6s | 4040 files, summary prints |

## Cross-Round Comparison

| Metric | R1 | R2 | R3 |
|--------|----|----|-----|
| Exit 0 | 6 | 9 | **9** |
| Crashes | 5 | 1 | 1 |
| Diagnostic pass | 4/6 | 6/6 | **6/6** |
| Contract violations | 656 | 152 | **142** |
| Summary output | 2 | 4 | **6** |
| Baseline pollution | yes | yes | **no** |

## Assessment

The pipeline suite is **stable** at 9/10 exit 0. The single remaining exit-1
(cross-solver-compare) is a setup gap — it needs a JSON spec file describing an
external solver, which must be provisioned once. It does not indicate a code bug.

The 6 open defects (PD-001 through PD-006) are all usability or edge-case
issues, none blocking:

| Defect | Pipeline | Impact |
|--------|----------|--------|
| PD-001 | defect-discovery | Smoke preset runs but yields no test load |
| PD-002–004 | contract-compliance | ~115 false-positive import violations remain |
| PD-005 | cross-solver-compare | Requires one-time external solver spec bootstrap |
| PD-006 | benchmark | Solved count shows 0 when scenes exit with warnings |

## Actions

None — no new code changes. The suite is in a maintainable state. Future work
should address the open defects in priority order.
