# Solver Regression Pipeline — Development Plan

**Status**: proposed
**Priority**: P0
**Owner**: gcs-cpp-solver-maintainer

## Purpose

Run solver on a fixture corpus, compare results against a stored baseline,
detect regressions (previously-solvable scenes that now fail, or output
changes beyond tolerance).

## Toolchain Needed

### `tools/solver_testing/pipelines/regression.py`

```
BatchRunner
├── load_fixture_corpus(path) → list[scene]
├── solve_all(scenes, solver) → list[SolveResult]
├── load_baseline(baseline_path) → dict[scene_id, BaselineResult]
├── compare_results(current, baseline, tolerance) → list[Regression]
│   ├── status_changed: solved→failed, failed→solved
│   ├── rank_changed: rank estimate outside tolerance
│   ├── residual_grew: residual norm increased > 10%
│   └── new_scenes: in current but not baseline
└── generate_report(regressions) → RegressionReport
```

### Baseline Format
```json
{
  "baseline_id": "v1",
  "created_at": "...",
  "solver_version": "...",
  "results": {
    "<scene_id>": {
      "status": "solved",
      "rank_estimate": 9,
      "residual_norm": 1.2e-8,
      "duration_ms": 45
    }
  }
}
```

### CLI
```bash
python tools/solver_testing/pipelines/regression.py \
  --corpus fixtures/scene/ \
  --baseline tools/solver_testing/baselines/v1.json \
  --tolerance 1e-6
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `regression.py` — BatchRunner + compare engine | 250行 |
| 2 | Baseline schema + save/load | 100行 |
| 3 | CLI wiring | 50行 |
| 4 | Smoke test on existing fixture corpus | — |

**Total**: ~400 lines
