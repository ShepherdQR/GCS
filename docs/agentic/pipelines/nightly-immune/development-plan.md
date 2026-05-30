# Nightly Immune Diagnostic Pipeline — Development Plan

**Status**: proposed
**Priority**: P3
**Owner**: night-watch (institutional agent)

## Purpose

Comprehensive nightly health check across ALL modules: build, CTest, Python
compile check, fixture integrity, task card staleness, contract consistency,
defect library summary, and repository audit. Produces a single health dashboard.

## Toolchain Needed

### `tools/solver_testing/pipelines/nightly_immune.py`

```
NightlyImmunePipeline
├── check_build() → BuildStatus
│   └── run scripts/build_clang_ninja.cmd, capture result
├── check_ctest() → CTestStatus
│   └── run ctest, parse pass/fail/skip counts
├── check_python_compile() → PyCompileStatus
│   └── python -m compileall -q python/gcs_viz tools/
├── check_fixture_integrity() → FixtureStatus
│   └── run fixture_library_gate.py
├── check_task_staleness() → TaskStatus
│   └── scan docs/agentic/tasks/ for tasks past deadline
├── check_contract_consistency() → ContractStatus
│   └── run cross-reader agent on docs vs code
├── check_defect_summary() → DefectStatus
│   └── run defect_store.summary()
├── aggregate_all_checks() → HealthDashboard
│   ├── overall: pass / warn / fail
│   ├── per_check: status + details
│   └── trend: compared to last N nights
└── generate_dashboard(dashboard) → dict + markdown
```

### CLI
```bash
python tools/solver_testing/pipelines/nightly_immune.py \
  --checks all \
  --output nightly_dashboard.json \
  --dashboard-md docs/agentic/nightly-runs/$(date +%Y-%m-%d)/dashboard.md
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `nightly_immune.py` — check orchestration engine | 150行 |
| 2 | Individual check adapters (build, ctest, py, fixture) | 100行 |
| 3 | Dashboard aggregation + trend comparison | 50行 |
| 4 | CLI + markdown dashboard output | 50行 |

**Total**: ~350 lines
