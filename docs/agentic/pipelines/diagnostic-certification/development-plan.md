# Diagnostic Certification Pipeline — Development Plan

**Status**: proposed
**Priority**: P1
**Owner**: gcs-diagnostics-certification-steward

## Purpose

Verify that the solver produces correct diagnostic output for known-bad inputs.
Construct scenes with specific errors (negative distance, degenerate geometry,
over-constrained, under-constrained) and assert the solver reports the expected
error codes and diagnostic messages.

## Toolchain Needed

### `tools/solver_testing/pipelines/diagnostics_cert.py`

```
DiagnosticsCertifier
├── build_negative_corpus() → list[(scene, expected_diagnostic)]
│   ├── negative_distance: Distance constraint with value < 0
│   ├── invalid_angle: Angle constraint outside [0, π]
│   ├── degenerate_line: Line with zero direction vector
│   ├── degenerate_plane: Plane with zero normal vector
│   ├── over_constrained: more constraints than DOFs
│   └── under_constrained: fewer constraints than needed
├── certify_scene(scene, expected) → CertResult
│   ├── parse solver output for Status, obstruction_report
│   ├── extract diagnostic codes
│   └── match against expected
├── certify_corpus(corpus) → CertReport
│   ├── passed: diagnostic matches expected
│   ├── failed: diagnostic missing or wrong
│   └── coverage: which error types are tested
└── generate_cert_report(report) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/diagnostics_cert.py \
  --corpus tools/solver_testing/corpora/negative/ \
  --strict \
  --output cert_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `diagnostics_cert.py` — certifier engine | 150行 |
| 2 | Negative corpus builder (6 error types) | 150行 |
| 3 | Solver output diagnostic parser | 50行 |
| 4 | CLI + report | 50行 |

**Total**: ~400 lines
