# High-Cache Session Diagnostic - Full Lane

Run: `token-diagnostic-1-full`  
Task pair: `token-diagnostic-1`  
Lane: `Full`  
Date: 2026-05-31  
Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Scope

This diagnostic uses the cache-hit experiment runbook, frozen baseline,
first-pass diagnostic, and token-audit DB inspection to choose one recent
high-cache session and interpret its token ratios. It does not append
`experiment-runs.csv` and does not modify token-audit database rows or
historical transcripts.

## Source Context Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-plan.md`
- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/baseline.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.md`
- `.agents/skills/gcs-token-audit-steward/SKILL.md`
- `tools/token_audit/cache_hit_experiment.py`

## Environment Note

The delegated prompt named `C:\Codes\AI\GCS_A`, while the initial Codex
worktree context was `C:\Users\QR\.codex\worktrees\78a5\GCS_A`. The worktree
copy contained a zero-byte `tools/token_audit/audit.db`, so the lightweight
runner failed there with `sqlite3.OperationalError: no such table: sessions`.
The populated token-audit DB used for this diagnostic was:

`C:\Codes\AI\GCS_A\tools\token_audit\audit.db`

## Baseline Anchors

The frozen baseline reports:

| Metric | Baseline |
|---|---:|
| Sessions | 38 |
| Input tokens | 4,380,119 |
| Output tokens | 1,140,477 |
| Cache read tokens | 326,080,768 |
| Legacy cache hit rate | 98.67% |
| Estimated raw cache hit rate | 99.55% |
| Token leverage ratio | 26.04% |
| Estimated cold-load overhead ratio | 33.83% |
| Average BEI | 0.339 |

The first-pass diagnostic classified the existing evidence as mixed:
high-cache/high-TLR sessions suggest useful institutional reuse, while
zero-cache or short high-overhead sessions justify a Lite-lane pilot.

## Selected Session

Chosen session: `5cc71ca0-85ef-427e-aa1c-31b60ecb4b63`

Reason for selection: it is the most recent session returned by
`list-sessions --limit 12`, has a high cache-read total, and has strong output
leverage rather than looking like a low-output process-only run.

| Field | Value |
|---|---:|
| Started at | `2026-05-30T12:53:43.004Z` |
| Project | `GCS-A` |
| Model | `deepseek-v4-pro` |
| Input tokens | 141,061 |
| Output tokens | 50,164 |
| Cache read tokens | 13,104,000 |
| Cache creation tokens | 0 |
| Estimated cache-write tokens | 39,000 |
| BEI composite | 0.636 |

## Token Ratios

| Ratio | Formula | Value |
|---|---|---:|
| Legacy cache hit rate | cache read / (cache read + input) | 98.94% |
| Estimated raw cache hit rate | cache read / (cache read + 39,000 estimated write) | 99.70% |
| Token leverage ratio | output / input | 35.56% |
| Estimated cold-load overhead ratio | 39,000 / input | 27.65% |
| Cache-read multiplier | cache read / input | 92.89x |

## Interpretation

This session sits in the productive high-cache bucket rather than the obvious
overhead bucket. Its legacy cache hit rate is above the experiment's 95%
high-cache threshold, and its token leverage ratio is well above both the
5% high-TLR threshold and the 26.04% aggregate baseline. The BEI composite is
also above the 0.339 project baseline.

For this session, the high cache-read count appears consistent with healthy
reuse of stable GCS context: the session produced 50,164 output tokens from
141,061 input tokens, so cached context did not merely accompany a low-output
administrative action. The 27.65% estimated cold-load overhead ratio remains
large enough to matter, but it is lower than the project baseline of 33.83% and
is amortized by a strong output/input ratio.

This single session does not prove that Full-lane context is always warranted.
It does show why the experiment should not treat high cache hit as a standalone
defect: at least some recent high-cache runs combine very high reuse with
substantial output and above-baseline BEI.

## Caveats

- The source DB is local runtime telemetry, not a billing-grade API usage
  contract.
- DeepSeek rows report `cache_creation_tokens = 0`; the estimated raw cache
  hit rate uses the experiment's fixed 39,000-token cacheable-prefix estimate.
- Stored USD cost is excluded because the baseline marks local cost fields as
  unreliable in this checkout.
- The lightweight `list-sessions` output does not classify task intent, so this
  diagnostic infers productivity from token leverage and BEI rather than from a
  reviewed task transcript.
- This is one session. The pilot still needs paired Full/Lite runs before any
  process policy is promoted.

## Command Evidence

```bat
python tools\token_audit\cache_hit_experiment.py inspect-db --format json
```

Result in the populated checkout:

- `sessions`: 38
- `turns`: 1210
- `tool_calls`: 1548
- `edits`: 337
- `input_tokens`: 4,380,119
- `output_tokens`: 1,140,477
- `cache_read_tokens`: 326,080,768
- `legacy_cache_hit_rate`: 0.986745
- `estimated_raw_cache_hit_rate`: 0.995476
- `token_leverage_ratio`: 0.260376
- `estimated_cold_load_overhead_ratio`: 0.338347

```bat
python tools\token_audit\cache_hit_experiment.py list-sessions --limit 12 --format json
```

Selected row:

- `session_id`: `5cc71ca0-85ef-427e-aa1c-31b60ecb4b63`
- `started_at`: `2026-05-30T12:53:43.004Z`
- `input_tokens`: 141,061
- `output_tokens`: 50,164
- `cache_read_tokens`: 13,104,000
- `bei_composite`: 0.636451
- `token_leverage_ratio`: 0.355619

Failed default-worktree evidence:

```bat
python tools\token_audit\cache_hit_experiment.py inspect-db --format json
python tools\token_audit\cache_hit_experiment.py list-sessions --limit 12 --format json
```

Both failed in `C:\Users\QR\.codex\worktrees\78a5\GCS_A` because that checkout's
`tools/token_audit/audit.db` was zero bytes and had no `sessions` table.

## Residual Risk

The diagnostic is auditable for token ratios and baseline comparison, but it
does not inspect the underlying session transcript. A reviewer could still
reclassify the session if transcript-level evidence shows repeated tool churn,
unsupported claims, or output that was not useful despite high token leverage.

Suggested pilot scoring for this run:

| Field | Suggested value |
|---|---:|
| audit_score_0_5 | 4 |
| validation_passed | true |
| rework_turns | 0 |
| defect_or_reopen_count | 0 |
