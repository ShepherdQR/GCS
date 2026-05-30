# Cache-Hit Rate Full/Lite Pilot Report

Date: 2026-05-31

Owner: `gcs-token-audit-steward` with `task-scoped-session-closer`

## Executive Summary

This experiment tested whether GCS-A's unusually high cache-hit rate mainly
signals redundant process overhead or healthy institutional context reuse. The
pilot used eight paired Full/Lite task classes, one dedicated run per lane, and
recorded session-level token telemetry plus manual audit-quality scores.

The aggregate classification is `redundant-overhead`: Lite used substantially
fewer input tokens while preserving most audit quality. The practical conclusion
is not a global Lite default. It is a task-class split:

- Lite is supported for low-risk audit, inventory, and module-map tasks that
  meet acceptance gates.
- Full remains required for GUI, environment-sensitive, and validation-heavy
  work until more Lite evidence closes the risk gap.

## Experiment Question

GCS-A had a very high cache-hit signal. The experiment asked whether this was:

1. **Redundant process overhead**: repeated process documents, skills, and
   closure rituals are being cached and replayed without enough task value.
2. **Healthy institutionalization**: stable context, validated conventions, and
   reusable governance state are preventing rework and improving auditability.

The experiment therefore compared a normal **Full** lane with a reduced-context
**Lite** lane while keeping hard governance gates intact.

## Experiment Package

| Artifact | Path |
|---|---|
| Experiment plan | `experiment-plan.md` |
| Eight-pair runbook | `pilot-runbook-8-pairs.md` |
| Run data | `experiment-runs.csv` |
| Per-run artifacts | `pilot-artifacts/` |
| Generated summary | `docs/reports/token-audit/cache-hit-diagnosis-20260530/pilot-summary.md` |
| Closure archive | `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md` |

## Baseline

The experiment started from the frozen token/cache baseline at
`docs/reports/token-audit/cache-hit-diagnosis-20260530/`.

Baseline facts recorded by the experiment plan:

| Metric | Value |
|---|---:|
| Sessions | 38 |
| Input tokens | 4,316,938 |
| Output tokens | 1,124,782 |
| Cache read tokens | 317,049,728 |
| Legacy cache hit rate | 98.66% |
| DeepSeek estimated raw hit rate | 99.53% |
| Output/input token leverage ratio | 26.06% |
| Estimated cold-load overhead ratio | 34.33% |

Cost was excluded from decision rules because stored USD cost fields contained
outlier-scale records and still need normalization.

## Experimental Design

The pilot used eight matched task pairs. Each pair had one Full lane run and
one Lite lane run. Runs were intentionally separate sessions so each row could
be recorded from Codex Desktop token-count telemetry.

### Full Lane

The Full lane used the current institutional process:

- read the relevant durable context;
- invoke applicable GCS stewardship;
- preserve the existing task-card boundary;
- capture validation evidence;
- name residual risk and auditability notes.

### Lite Lane

The Lite lane reduced context width while preserving hard gates:

- read only target files and minimal command output;
- invoke only directly necessary skill context;
- run the smallest acceptance command that proves the artifact;
- keep the report compact;
- record failures honestly.

Lite was explicitly reduced-context governance, not no-governance execution.

## Implementation Process

1. Created the experiment plan and baseline.
2. Implemented `tools/token_audit/cache_hit_experiment.py` as a stdlib-only
   fallback runner.
3. Added `record-jsonl` support so Codex Desktop session JSONL telemetry could
   be converted into experiment rows without modifying transcripts or the
   token-audit database.
4. Defined the eight-pair runbook.
5. Ran 16 dedicated task sessions, one per pair/lane.
6. Appended the run rows to `experiment-runs.csv`.
7. Regenerated `pilot-summary.md` and `pilot-summary.json`.
8. Closed the pilot with a completed-task archive.
9. Packaged the whole experiment into this subfolder for future review.

## Pair Matrix

| Pair | Full lane | Lite lane | Classification |
|---|---|---|---|
| `docs-index-1` | Contracts index | Solver-pipeline index | `mixed-or-inconclusive` |
| `token-diagnostic-1` | High-cache diagnostic | Recent-session diagnostic | `mixed-or-inconclusive` |
| `repo-audit-1` | Docs-scope audit | Tools-scope audit | `mixed-or-inconclusive` |
| `task-card-audit-1` | Diagnosis task-card audit | Implementation task-card audit | `redundant-overhead` |
| `completed-archive-audit-1` | Diagnosis archive audit | Implementation archive audit | `mixed-or-inconclusive` |
| `fixture-inventory-1` | JSON fixture readiness inventory | Basic fixture inventory | `redundant-overhead` |
| `python-gui-smoke-1` | Bridge/facade GUI smoke | Screen/module GUI smoke | `healthy-institutionalization` |
| `cpp-module-map-1` | Kernel/numeric module map | IO/session module map | `redundant-overhead` |

## Key Data

| Metric | Full | Lite | Delta |
|---|---:|---:|---:|
| Runs | 8 | 8 | 16 total |
| Complete pairs | 8 | 8 | 8 total |
| Input tokens | 4,689,553 | 2,199,491 | Lite saved 53.1% |
| Output tokens | 46,128 | 24,906 | Lite was shorter |
| Average audit score | 4.375 | 4.188 | Lite down 4.3% |
| Average BEI proxy | 0.712 | 0.653 | Lite down 8.3% |
| Validation pass rate | 100.0% | 87.5% | Lite had one failure |
| Defect/reopen count | 0 | 1 | Lite had one defect |

Classification counts:

| Classification | Count |
|---|---:|
| `redundant-overhead` | 3 |
| `healthy-institutionalization` | 1 |
| `mixed-or-inconclusive` | 4 |

## Pair-Level Findings

| Pair | Lite input savings | Audit delta | BEI delta | Defect delta | Interpretation |
|---|---:|---:|---:|---:|---|
| `completed-archive-audit-1` | 71.2% | -11.1% | -5.8% | 0 | Strong token savings, but audit drop narrowly exceeded the 10% threshold. |
| `cpp-module-map-1` | 52.7% | 0.0% | 0.5% | 0 | Clean Lite win for low-risk module mapping. |
| `docs-index-1` | -23.6% | 0.0% | -1.8% | 0 | Lite used more input tokens; no policy signal. |
| `fixture-inventory-1` | 80.0% | 12.5% | 8.2% | 0 | Strong Lite win for low-risk fixture inventory. |
| `python-gui-smoke-1` | 50.5% | -20.0% | -56.6% | 1 | Full lane protected against environment-sensitive validation failure. |
| `repo-audit-1` | 67.2% | -11.1% | -5.3% | 0 | Good savings, but audit drop narrowly exceeded the threshold. |
| `task-card-audit-1` | 49.0% | 0.0% | 0.8% | 0 | Clean Lite win for task-card audit. |
| `token-diagnostic-1` | 5.8% | 0.0% | -0.6% | 0 | Savings were below the 25% redundant-overhead threshold. |

## Main Conclusions

1. The aggregate signal supports `redundant-overhead` for this low-risk pilot.
   Lite saved 53.1% input tokens while audit score dropped only 4.3% and BEI
   proxy dropped 8.3%.
2. The policy should be task-class-specific. Low-risk task-card audits, fixture
   inventories, and C++ module maps are good Lite candidates.
3. Full-lane context still matters when validation depends on environment,
   runtime dependencies, GUI imports, or broad module responsibility. The
   Python GUI Lite run produced the only validation failure and defect signal.
4. Audit-score thresholds need reviewer calibration. Two mixed pairs missed the
   redundant-overhead threshold by only about 1.1 audit-percentage points.
5. BEI remains a proxy. The experiment is useful for process review, but BEI
   and cost should not become hard gates until cost normalization and baseline
   calibration are repaired.

## Recommended Policy Direction

Use Lite by default only for low-risk tasks that have narrow acceptance gates
and no environment-sensitive dependency:

- compact task-card audits;
- small fixture inventories;
- module file maps;
- narrow docs or index updates after the relevant file set is known.

Keep Full as default for:

- GUI smoke checks;
- Python environment or dependency-sensitive work;
- solver/runtime/IO behavior changes;
- medium or high-risk validation-heavy work;
- tasks whose failure would change public project state or policy.

## Remaining Risks

- Audit scores were manually assigned and need second-reviewer calibration.
- The sample has only one pair per task class.
- DeepSeek cache creation tokens are not reported directly, so write-cost
  economics still use the existing 39,000-token estimate.
- Stored USD cost fields remain excluded until normalized.
- Lite defaults should not be promoted globally from this pilot.

## Reproduction

Regenerate the summary from this package:

```bat
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

Validate the current packaging task:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-experiment-package-report.md
```
