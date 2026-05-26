# D2 Diagnostic Classification Demo

Status: active
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Claim

GCS can expose different diagnostic classes through command-line evidence:
accepted-with-warning, under-constrained evidence, over-constrained numeric
failure, malformed input, and singular post-local diagnostics.

This is a researcher-facing demo. It is less about a polished interaction and
more about whether the system preserves enough structured evidence to study
failure modes.

## Classification Matrix

| Class | Scene | Command result | Evidence to inspect |
| --- | --- | --- | --- |
| Accepted current smoke | `fixtures/scene/verification/lgs/well_constrained.txt` | `Status: AcceptedWithWarnings`, exit 0 | rank 3, residual norm 0, commit accepted |
| Under-constrained evidence | `fixtures/scene/verification/lgs/under_constrained.txt` | `Status: AcceptedWithWarnings`, exit 0 | low rank and nonzero nullity remain visible |
| Over-constrained or inconsistent solve | `fixtures/scene/verification/lgs/over_constrained.txt` | `Status: Failed`, nonzero exit | `runtime.numeric_failure`, rollback |
| Malformed input | `fixtures/scene/verification/io/malformed.txt` | load failure, nonzero exit | `io.parse.entity_count` |
| Singular blocked commit | `fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json` | `Status: NumericallySingular`, nonzero exit | `runtime.post_local_diagnostics_blocked` |

## Commands

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\well_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\under_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\over_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\io\malformed.txt
out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
```

Automated JSON summary:

```bat
python tools\product_demo\diagnostic_classification.py --output docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json
```

Current artifact:

- `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json`

Expected-output files:

- `docs/architecture/benchmarks/b1-diagnostic-classification/expected/`

## Evidence Excerpts

Accepted current smoke:

```text
Input: fixtures\scene\verification\lgs\well_constrained.txt
Status: AcceptedWithWarnings
Accepted: true
runtime.post_local_diagnostics.rank_report: rank 3, variables 9, residuals 3, nullity 6
gluing.accepted: All local sections are compatible within boundary tolerance.
runtime.commit: Runtime committed the verified proposed state.
```

Under-constrained evidence:

```text
Input: fixtures\scene\verification\lgs\under_constrained.txt
Status: AcceptedWithWarnings
Accepted: true
runtime.post_local_diagnostics.rank_report: rank 1, variables 6, residuals 1, nullity 5
runtime.post_local_diagnostics.rank_report: rank 0, variables 3, residuals 0, nullity 3
```

Over-constrained or inconsistent solve:

```text
Input: fixtures\scene\verification\lgs\over_constrained.txt
Status: Failed
Accepted: false
numeric_engine.solve_local: Error
runtime.numeric_failure: Damped Gauss-Newton step failed to reduce the residual.
Obstruction: runtime.numeric_failure - Damped Gauss-Newton step failed to reduce the residual.
```

Malformed input:

```text
Failed to load scene: fixtures\scene\verification\io\malformed.txt
io.parse.entity_count: Failed to read entity count.
```

Singular blocked commit:

```text
Input: fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
Status: NumericallySingular
Accepted: false
runtime.obstruction_report: runtime.post_local_diagnostics_blocked
runtime.rollback: Post-local-solve diagnostics blocked commit.
Obstruction: runtime.post_local_diagnostics_blocked - Post-local-solve diagnostics blocked commit.
```

## Research Interpretation

The current CLI already preserves useful diagnostic evidence, but some labels
are not yet final research-grade taxonomy:

- accepted scenes can still carry warning-level post-local diagnostics;
- under-constrained status is currently inferred from rank and nullity evidence
  rather than a distinct top-level status;
- over-constrained and inconsistent cases may currently surface as numeric
  failure when the nonlinear engine cannot reduce residual;
- singular counterexamples are first-class assets when they include obstruction
  evidence and metadata.

## Acceptance

A reviewer can run the command set and classify each scene without relying on
hidden GUI state or raw chat context.

## Next Upgrade

Promote this package when the D2 JSON summary is checked by release smoke and
the B1 expected-output files survive a fresh build without changes.
