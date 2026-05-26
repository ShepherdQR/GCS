# B1 Diagnostic Classification Expected Outputs

Status: active
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This directory defines the first B1 expected-output set for GCS diagnostic
classification. These files are not performance benchmarks and do not compare
GCS against external solvers. They define the current internal evidence that a
researcher should see when running the D2 diagnostic classification demo.

## Contract

Each `*.expected.json` file is consumed by
`tools/product_demo/diagnostic_classification.py` and records:

- fixture path;
- diagnostic classification;
- expected process exit code;
- expected top-level status and acceptance flag when the CLI reaches runtime;
- required report or obstruction codes;
- known limitations that prevent overclaiming.

## Candidate Set

| Case | Fixture | Classification |
| --- | --- | --- |
| `b1-well-constrained` | `fixtures/scene/verification/lgs/well_constrained.txt` | accepted current smoke |
| `b1-under-constrained` | `fixtures/scene/verification/lgs/under_constrained.txt` | under-constrained rank/nullity evidence |
| `b1-over-constrained` | `fixtures/scene/verification/lgs/over_constrained.txt` | over-constrained numeric failure |
| `b1-malformed-input` | `fixtures/scene/verification/io/malformed.txt` | malformed input parse failure |
| `b1-singular-blocked-commit` | `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | singular post-local diagnostics block |

## Promotion Boundary

This B1 set may move toward B2 only after expected outputs are stable across a
fresh build and the external-comparison plan names which baselines are
executable locally versus documentation-only.
