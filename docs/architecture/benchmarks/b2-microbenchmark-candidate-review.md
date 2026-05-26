# B2 Microbenchmark Candidate Review

Status: active
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This review decides which current B1 diagnostic-classification cases are ready
to become B2 research microbenchmarks.

B2 is narrower than D2. D2 proves that the classifier can sort several
diagnostic classes. B2 should test one durable solver-semantics claim per
fixture with fixed expected report fields.

## Source Register

| Source | Used for | Confidence |
| --- | --- | --- |
| `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` | B-level definitions and external positioning. | High |
| `docs/architecture/98-benchmark-candidate-selection-criteria.md` | C2/C3 promotion rules. | High |
| `docs/architecture/benchmarks/b1-diagnostic-classification/expected/` | Current expected report fields. | High |
| `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json` | Latest B1 run result: 5/5 cases passed. | High |
| `docs/architecture/benchmarks/external-baseline-feasibility-matrix.md` | External execution boundary. | High |

## Current Evidence

The latest D2 artifact reports five passing B1 cases:

```text
schema: gcs.product_demo.d2_diagnostic_summary.v1
case_count: 5
passed_count: 5
all_passed: true
```

That is enough to review candidates. It is not enough to freeze an external
comparison benchmark.

## Candidate Decisions

| Candidate | Current role | B2 decision | Rationale | Missing before C3 |
| --- | --- | --- | --- | --- |
| `fixtures/scene/verification/lgs/well_constrained.txt` | Accepted B1 classification. | Promote as B2-01 candidate. | It isolates accepted solve evidence: rank report, residual report, `gluing.accepted`, and `runtime.commit`. | Freeze expected report fields and add migration policy. |
| `fixtures/scene/verification/lgs/under_constrained.txt` | Under-constrained rank/nullity evidence. | Promote as B2-02 candidate. | It is the strongest research microbenchmark because the claim is specific: under-constrained scenes should preserve rank/nullity evidence while remaining accepted-with-warnings. | Add explicit expected nullity fields to the B2 contract. |
| `fixtures/scene/verification/lgs/over_constrained.txt` | Expected numeric failure. | Defer. | Current evidence is useful, but `runtime.numeric_failure` is not yet a clean semantic over-constraint taxonomy. Promoting now could confuse implementation incompleteness with theory. | Add a report code that separates inconsistent constraints from generic numeric failure. |
| `fixtures/scene/verification/io/malformed.txt` | Malformed input parse failure. | Keep in B1/IO only. | It is important for product honesty, but it tests input validation rather than solver semantics. | If promoted, route it through an IO-adapter benchmark track instead of B2. |
| `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | Singular blocked commit counterexample. | Candidate after minimization or explicit large-case rationale. | It demonstrates `NumericallySingular` and `runtime.post_local_diagnostics_blocked`, but it is large for a microbenchmark. | Produce a smaller singular scene or record why the large scene is the minimal known witness. |

## Proposed B2 Set

| B2 ID | Fixture | Research claim | Expected status |
| --- | --- | --- | --- |
| B2-01 | `fixtures/scene/verification/lgs/well_constrained.txt` | Accepted local solve emits rank, residual, gluing, and commit evidence. | `AcceptedWithWarnings` |
| B2-02 | `fixtures/scene/verification/lgs/under_constrained.txt` | Under-constrained accepted scene preserves explicit rank/nullity evidence. | `AcceptedWithWarnings` |
| B2-03 seed | singular counterexample or smaller successor | Singular local diagnostics block durable commit instead of hiding failure. | `NumericallySingular` or blocked diagnostic status |

## Non-Promotions

- `over_constrained.txt` stays B1 until the diagnostic taxonomy is sharper.
- `malformed.txt` stays an IO honesty case, not a solver microbenchmark.
- No B2 case is an external benchmark yet. External comparison requires the
  executable or documentation-only posture recorded in the feasibility matrix.

## Next Work

1. Add B2 expected-output files for B2-01 and B2-02.
2. Decide whether B2-03 should be the existing singular counterexample or a
   smaller generated witness.
3. Add one B2 runner only after the expected-output contract is written.
4. Translate exactly one B2 scenario into the first external baseline format
   after a local SolveSpace or FreeCAD setup decision.
