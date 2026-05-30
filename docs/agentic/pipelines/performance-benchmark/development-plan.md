# Performance Benchmark Pipeline — Development Plan

**Status**: proposed
**Priority**: P2
**Owner**: gcs-benchmark-steward

## Purpose

Measure solver performance metrics (duration, iterations, memory, convergence)
across a fixture corpus. Store results in a trend database for tracking
performance changes over time and detecting regressions.

## Toolchain Needed

### `tools/solver_testing/pipelines/benchmark.py`

```
BenchmarkRunner
├── warmup_solve(scene, n=3) → None  (JIT/cache warmup)
├── timed_solve(scene, n=5) → BenchmarkPoint
│   ├── duration_ms: median of N runs
│   ├── duration_std: standard deviation
│   ├── iterations: solver iterations
│   └── convergence_rate: if available
├── benchmark_corpus(corpus, config) → list[BenchmarkPoint]
├── load_trend_db(db_path) → TrendDB
├── append_trend(db, points) → None
├── detect_regressions(db, threshold) → list[Regression]
│   ├── duration_regression: >20% slower than baseline
│   └── failure_regression: previously fast, now slow/fail
└── generate_benchmark_report(points, trends) → dict
```

### Trend DB Schema (SQLite)
```sql
CREATE TABLE benchmarks (
    id INTEGER PRIMARY KEY,
    scene_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    solver_version TEXT,
    duration_ms REAL,
    iterations INTEGER,
    status TEXT,
    residual_norm REAL
);
CREATE INDEX idx_scene_time ON benchmarks(scene_id, timestamp);
```

### CLI
```bash
python tools/solver_testing/pipelines/benchmark.py \
  --corpus fixtures/scene/ \
  --warmup 3 --runs 5 \
  --trend-db tools/solver_testing/benchmarks/trend.db \
  --regression-threshold 1.2 \
  --output benchmark_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `benchmark.py` — timed solve + statistics | 150行 |
| 2 | Trend DB schema + save/load/query | 150行 |
| 3 | Regression detection | 50行 |
| 4 | CLI + report | 50行 |

**Total**: ~400 lines
