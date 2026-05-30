# Cross-Solver Compare Pipeline — Development Plan

**Status**: proposed
**Priority**: P2
**Owner**: gcs-benchmark-steward

## Purpose

Compare GCS solver results against external solvers (if available) on a shared
benchmark set. Measure agreement on solved/unsolved status, rank estimates,
and residual norms. Produce comparison reports with source citations.

## Toolchain Needed

### `tools/solver_testing/pipelines/cross_solver_compare.py`

```
CrossSolverComparer
├── load_benchmark_set(path) → list[BenchmarkScene]
│   └── each scene has: standard format (e.g., gcs-0.3 JSON)
├── solve_with_gcs(scene) → SolverResult
├── solve_with_external(scene, solver_spec) → SolverResult
│   └── solver_spec: {name, command, input_converter, output_parser}
├── compare_results(gcs_result, external_result) → ComparisonPoint
│   ├── status_agree: both solved or both failed
│   ├── rank_agree: rank estimates within tolerance
│   ├── residual_agree: residual norms within tolerance
│   └── gcs_only / external_only: only one solver succeeded
├── compare_corpus(corpus, solvers) → ComparisonReport
│   ├── agreement_rate: % of scenes where solvers agree
│   ├── gcs_advantage: scenes only GCS solves
│   └── external_advantage: scenes only external solves
└── generate_comparison_report(report) → dict
```

### External Solver Adapter Interface
```python
@dataclass
class ExternalSolverSpec:
    name: str
    command: list[str]
    input_converter: Callable[[dict], str]  # scene → solver input
    output_parser: Callable[[str], SolverResult]  # solver output → result
    source_citation: str  # URL or paper reference
```

### CLI
```bash
python tools/solver_testing/pipelines/cross_solver_compare.py \
  --benchmark fixtures/benchmark/ \
  --solvers external_solvers.json \
  --output comparison_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `cross_solver_compare.py` — comparison engine | 150行 |
| 2 | External solver adapter interface + registry | 100行 |
| 3 | Agreement statistics | 100行 |
| 4 | CLI + report | 50行 |

**Total**: ~400 lines
