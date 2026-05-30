# Cache-Hit Diagnosis Baseline - 2026-05-30

## Purpose
This baseline freezes the current GCS-A token/cache economics state before running the cache-hit diagnosis experiment. It is intended to distinguish redundant process overhead from healthy institutionalization in later A/B runs.

## Source And Caveats
- Source database: `tools/token_audit/audit.db`.
- Query mode: read-only SQLite; `python -m tools.token_audit` was not usable in the current runtime because optional CLI dependencies were missing (`click` / `yaml`).
- DeepSeek sessions report `cache_creation_tokens = 0`; estimated raw cache-hit metrics use the existing 39,000-token cacheable-prefix estimate from `tools/token_audit/metrics_engine.py`.
- Stored `total_cost_usd_micro` has outlier-scale values in this checkout, so this baseline treats USD cost as unreliable and uses token counts plus relative cost proxies for the experiment.
- Repository audit baseline snapshot: `repository-audit-baseline.json` in this directory.

## Git Baseline
- Branch: `codex-cache-hit-diagnosis-20260530-run2`
- HEAD: `00f9cc9b8564cce7c6bb03787da370c918746a43`
- Worktree note: the checkout already contains unrelated untracked agent/config artifacts and a pre-existing `.claude/skills/orchestrator/SKILL.md` modification; this task will stage only scoped experiment files.

## Aggregate Token Baseline
| Metric | Value |
|---|---:|
| Sessions | 38 |
| Turns | 1210 |
| Tool calls | 1548 |
| Edits | 337 |
| Input tokens | 4,380,119 |
| Output tokens | 1,140,477 |
| Cache read tokens | 326,080,768 |
| Cache creation tokens | 0 |
| Stored USD cost | unreliable; excluded |
| Average BEI | 0.339 |
| Legacy cache hit rate | 98.67% |
| DeepSeek estimated raw hit rate | 99.55% |
| Output/input TLR | 26.04% |
| Estimated cold-load overhead ratio, 39k/session | 33.83% |

## Distribution Signals
| Signal | Value |
|---|---:|
| median_tlr | 7.76% |
| median_legacy_cache_hit_rate | 89.38% |
| median_bei | 0.368 |
| zero_cache_sessions | 11 |
| high_cache_sessions_legacy_ge_95pct | 15 |
| low_tlr_sessions_lt_2pct | 11 |
| short_high_overhead_sessions_sclor39_ge_50pct | 17 |

## Task-Type Split
| Task type | Sessions | Input | Output | Cache read | Legacy hit | Est raw hit | TLR | Avg BEI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unclassified | 16 | 2,083,973 | 616,997 | 171,048,576 | 98.80% | 99.64% | 29.61% | 0.434 |
| ops | 8 | 201,709 | 196 | 0 | 0.00% | 0.00% | 0.10% | 0.163 |
| feature | 6 | 597,241 | 148,057 | 34,481,920 | 98.30% | 99.33% | 24.79% | 0.331 |
| process | 5 | 1,339,890 | 373,278 | 120,424,576 | 98.90% | 99.84% | 27.86% | 0.275 |
| research | 3 | 157,306 | 1,949 | 125,696 | 44.42% | 51.79% | 1.24% | 0.305 |

## Baseline Interpretation
- The project-level cache-hit rate is genuinely very high under both the legacy and estimated raw formulas.
- The aggregate output/input ratio is healthy, but median TLR and low-TLR counts show that short process/ops sessions can still be overhead-heavy.
- USD cost should not be used as a decision signal until the cost field is normalized; use token-count deltas and BEI/SER/audit-score deltas for this experiment.
- The baseline does not decide redundancy versus institutionalization; that requires comparing Full and Lite process lanes on matched tasks with audit quality and rework outcomes.
