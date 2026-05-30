# Session Output Summary — 2026-05-31

Session: Pipeline experiments fix cycle
Date: 2026-05-31
Status: closed

## One-Sentence Summary

Three-round parallel pipeline experiment cycle: discovered 10 issues, fixed 8 across 7 source files, established stable suite at 9/10 exit 0, and created pipeline defect register.

## Deliverables

| # | Deliverable | Type | Files | Status |
|---|------------|------|-------|--------|
| 1 | Experiment 001 report | docs | `docs/reports/pipeline-experiments/001.../README.md` | done |
| 2 | Round 1 fixes (6 bugs) | code | `run.py`, `scene_gen.py`, `diagnostics_cert.py`, `contract_compliance.py`, `repo_audit.py` | done |
| 3 | Experiment 002 report | docs | `docs/reports/pipeline-experiments/002.../README.md` | done |
| 4 | Round 2 fixes (4 bugs) | code | `regression.py`, `benchmark.py`, `stability.py`, `scene_gen.py` | done |
| 5 | Experiment 003 report | docs | `docs/reports/pipeline-experiments/003.../README.md` | done |
| 6 | Defect register | docs | `docs/reports/pipeline-experiments/defect-register.md` | done |
| 7 | Pipeline experiments index | docs | `docs/reports/pipeline-experiments/README.md` | done |

## Verification Gates

| Gate | Result |
|------|--------|
| All 10 pipelines run without crash | 9/10 exit 0 (1 needs external setup) |
| Diagnostic certification | 6/6 PASS |
| Regression pipeline | 2 scenes, 0 regressions |
| Benchmark pipeline | 2 scenes benchmarked |
| Contract compliance | 656 → 142 violations |
| Python syntax check | Clean |
| All commits pushed | 6 commits on `codex/cache-hit-pilot-completion-20260531` |

## Cross-Round Evolution

| Metric | R1 | R2 | R3 |
|--------|----|----|-----|
| Exit 0 | 6/10 | 9/10 | 9/10 |
| Blocking crashes | 5 | 1 | 1 |
| Diagnostic pass | 4/6 | 6/6 | 6/6 |
| Contract violations | 656 | 152 | 142 |
| Pipelines with summary | 2/10 | 4/10 | 6/10 |

## Narrative Line Impact

| Narrative line | Before | After | Change |
|----------------|--------|-------|--------|
| Pipeline quality gates | 5 pipelines crash on default run | 9/10 run cleanly | Major improvement |
| Diagnostic coverage | 4/6 negative test cases pass | 6/6 pass | Complete |
| Contract compliance signal | 656 false positives drown real issues | 142 → usable signal | Significant noise reduction |
| Pipeline result visibility | 2 pipelines print summaries | 6 pipelines print summaries | Improved |
| Experiment discipline | No experiment folder | 3 experiments + defect register | Established |

## Token Benefit

| Metric | Value |
|--------|-------|
| Total Tokens | 226,953 |
| Cache Hit Rate | 99.0% |
| Estimated Cost | $0.18 |
| Lines Changed | +69,610 / -505 (branch total) |
| Commits | 8 |
| BEI Composite | 0.61 (B) |

## Commits

```
a1bf45a docs: add experiment 003 — 10-pipeline stable smoke test
aae607f docs: add pipeline defect register with 6 open + 10 closed issues
5f65d18 fix: resolve 4 issues from pipeline experiment 002
0bd7bbb docs: add experiment 002 — 10-pipeline post-fix smoke test
5380c55 docs: move pipeline experiment into dedicated folder structure
7b55b95 fix: add default configs to pipeline runner, fix 4 blocking bugs in 6 files
```
