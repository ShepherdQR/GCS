# Cache-Hit Diagnosis Experiment Plan

Date: 2026-05-30

Owner: task-scoped-session-closer with token-audit stewardship

## Purpose

GCS-A currently shows an unusually high cache-hit rate. This experiment tests
whether that signal mostly means:

1. redundant process overhead is being repeatedly cached and replayed; or
2. the project has a healthy institutional operating layer whose stable context
   is being reused economically.

The experiment is intentionally lightweight. It uses current token-audit
telemetry, a small paired-task pilot, and simple audit-quality scoring before
any process change is promoted.

## Baseline

The frozen baseline for this experiment is stored at:

- `docs/reports/token-audit/cache-hit-diagnosis-20260530/baseline.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/token-cache-baseline.json`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/repository-audit-baseline.json`

Baseline facts:

- Sessions: 38
- Input tokens: 4,316,938
- Output tokens: 1,124,782
- Cache read tokens: 317,049,728
- Legacy cache hit rate: 98.66%
- DeepSeek estimated raw hit rate: 99.53%
- Output/input token leverage ratio: 26.06%
- Estimated cold-load overhead ratio, 39k/session: 34.33%
- USD cost field: excluded until normalized because stored values contain
  outlier-scale records in this checkout.

## Hypotheses

### H1: Redundant Process Overhead

High cache hit is mostly caused by repeated loading of process documents,
skills, audit routines, and closure rituals that do not materially improve the
task outcome.

Expected evidence:

- Lite mode saves at least 25% input tokens or effective input cost proxy.
- Audit score drops by less than 10%.
- BEI/SER proxy drops by less than 10%.
- Rework, validation failures, and reviewer findings do not increase.

### H2: Healthy Institutionalization

High cache hit is mostly caused by stable project conventions, validated
operating rules, and reusable governance context that prevents rework and
improves auditability.

Expected evidence:

- Full mode has higher token use but improves audit score by at least 15%.
- Full mode reduces reopen/rework, validation misses, or unsupported claims.
- Full mode has better verification coverage on medium-risk tasks.
- The added token load is traceable to useful evidence, not repeated
  reconstruction.

## Experimental Lanes

### Full Lane

Use the current institutional process:

- Create a task card for non-trivial mutation.
- Invoke the relevant steward skill.
- Read the durable docs needed for the work.
- Produce validation evidence.
- Produce closure evidence when the task scope warrants it.

### Lite Lane

Use the minimum sufficient process while preserving hard gates:

- Keep mandatory task cards for non-trivial mutation.
- Invoke only the directly relevant skill.
- Read only files needed for the target acceptance gate.
- Skip broad historical archive reading unless needed for the task.
- Skip completed-task closure for tiny, low-risk work; record a commit note
  instead.

Lite mode is not no-governance mode. It is a reduced-context lane.

## Task Sample

Run 6 to 8 small, matched tasks. Use paired tasks rather than repeating the
same task twice, so the second run does not benefit from solution memory.

Recommended pairs:

| Pair | Full task | Lite task | Acceptance style |
|---|---|---|---|
| Docs | Update one short agentic doc index | Update a comparable doc index | Markdown diff + link check |
| Token audit | Produce one session diagnostic summary | Produce another comparable summary | Baseline query + short report |
| Repository audit | Produce one compact audit delta | Produce another compact audit delta | Tool output + finding count |
| Low-risk code/test | Add one narrow parser/test fixture | Add comparable fixture | Focused test or compile check |

Alternate order by pair: Full-Lite, then Lite-Full, to reduce ordering effects.

## Metrics

Record one row per session in `experiment-runs.csv`.

Primary metrics:

- `input_tokens`
- `output_tokens`
- `cache_read_tokens`
- `estimated_cache_write_tokens`
- `legacy_cache_hit_rate`
- `estimated_raw_cache_hit_rate`
- `token_leverage_ratio`
- `estimated_cold_load_overhead_ratio`
- `bei_composite`
- `audit_score_0_5`
- `validation_passed`
- `rework_turns`
- `defect_or_reopen_count`

Secondary metrics:

- repeated file reads;
- repeated validation commands without new information;
- failed or abandoned tool calls;
- number of skills invoked;
- files touched;
- task duration.

## Scoring

Use a simple 0 to 5 audit score:

| Score | Meaning |
|---:|---|
| 5 | Complete evidence, reproducible validation, scoped files, clear residual risks |
| 4 | Minor evidence gaps but reviewer can trust and replay the work |
| 3 | Adequate for low-risk work, weak for medium-risk work |
| 2 | Missing important evidence or unclear scope |
| 1 | Hard to audit; claims not well supported |
| 0 | No useful audit trail |

## Decision Rules

Classify as redundant overhead if:

- Lite saves at least 25% input tokens or estimated effective input cost; and
- audit score decreases by less than 10%; and
- BEI/SER proxy decreases by less than 10%; and
- rework and defect/reopen counts do not increase.

Classify as healthy institutionalization if:

- Full improves audit score by at least 15%; or
- Full prevents at least one validation miss, reopen, unsupported claim, or
  stale-context error; and
- the extra token use is traceable to useful context, validation, or evidence.

Classify as mixed if:

- Lite wins on docs/ops/process microtasks; and
- Full wins on medium-risk, cross-module, or validation-heavy tasks.

## First-Pass Execution

The first pass does not run new A/B work. It diagnoses the existing telemetry
and prepares the pilot:

1. Freeze the current token/cache baseline.
2. Persist this plan and the CSV template.
3. Query existing sessions for split signals: high-cache/high-TLR,
   high-cache/low-TLR, zero-cache/low-TLR, and high-overhead short sessions.
4. Write the first-pass diagnostic summary.
5. Validate task card and repository-audit health.

## Implementation Tool

Use the stdlib-only helper when the richer token-audit CLI is unavailable:

```bat
python tools\token_audit\cache_hit_experiment.py inspect-db --format json
python tools\token_audit\cache_hit_experiment.py list-sessions --limit 12 --format json
python tools\token_audit\cache_hit_experiment.py record --session-id <session-id> --run-id <run-id> --task-pair docs-1 --mode Full --task-type docs --risk low --audit-score 4 --validation-passed true --rework-turns 0 --defect-or-reopen-count 0
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

The helper reads `tools/token_audit/audit.db` but does not write to the database
or historical JSONL transcripts. It appends only to `experiment-runs.csv` when
`record` is explicitly invoked.

## Guardrails

- Do not modify historical JSONL transcripts.
- Do not modify token-audit database rows for this experiment.
- Do not use stored USD cost until cost-field normalization is repaired.
- Do not stage unrelated dirty or untracked files.
- Do not promote a permanent process change from fewer than six paired runs.

## Follow-Up

After the first 6 to 8 paired runs:

1. Compute Full vs Lite deltas.
2. Identify task classes where Lite is safe by default.
3. Identify task classes where Full remains mandatory.
4. Convert the winning rule into an agentic process policy only after review.
