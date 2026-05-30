# IO Round-Trip Pipeline — Development Plan

**Status**: proposed
**Priority**: P1
**Owner**: gcs-io-adapter-steward

## Purpose

Verify that scene data survives serialization round-trips without corruption:
JSON → solver text format → re-parse → re-solve, and compare results.
Ensures format converters, parsers, and serializers are lossless.

## Toolchain Needed

### `tools/solver_testing/pipelines/roundtrip.py`

```
RoundTripTester
├── round_trip_json(scene) → RoundTripResult
│   ├── scene → gcs-0.3 JSON → parse → compare digests
│   └── check: geometry values, constraint values, IDs preserved
├── round_trip_text(scene) → RoundTripResult
│   ├── scene → custom_text_v1 → parse → compare
│   └── check: float precision preserved to 1e-12
├── round_trip_solve(scene) → RoundTripResult
│   ├── solve(original) → solve(round_tripped)
│   └── compare: status, rank, residual norm identical
├── test_corpus(fixture_paths, formats) → RoundTripReport
│   ├── per-fixture: which formats pass/fail
│   └── aggregate: format-level pass rates
└── generate_report(report) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/roundtrip.py \
  --fixtures fixtures/scene/ \
  --formats json,text \
  --solve-check \
  --output roundtrip_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `roundtrip.py` — JSON + text round-trip test | 150行 |
| 2 | Solve-comparison mode | 100行 |
| 3 | Corpus batch runner | 50行 |
| 4 | CLI + report | 50行 |

**Total**: ~350 lines
