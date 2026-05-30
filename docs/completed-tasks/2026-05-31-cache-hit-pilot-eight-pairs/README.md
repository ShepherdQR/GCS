---
task_id: 2026-05-31-cache-hit-pilot-eight-pairs
status: complete
session_goal: "Close the eight-pair Full/Lite cache-hit pilot with durable results, evidence, residual risks, and scoped Git delivery."
archive_target: docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/
---

# 2026-05-31-cache-hit-pilot-eight-pairs

## Task Objective

Close the cache-hit diagnosis pilot after all eight paired Full/Lite runs were
recorded. The archive preserves the data shape, task-class interpretation,
validation evidence, residual risks, and follow-up policy boundary so future
threads do not need raw chat context to resume the token-economics work.

## Scope And Non-Goals

**In scope**: the eight-pair pilot dataset, generated pilot summaries, new
pilot artifact files, task-card closure, completed-task archive, completed-task
index update, and focused validation for the cache-hit experiment surface.

**Out of scope**: modifying historical JSONL transcripts, editing token-audit
database rows, changing solver behavior, changing pipeline implementation
files, normalizing USD cost records, installing missing GUI dependencies, or
promoting a permanent Full/Lite policy from one pilot.

## Interaction Summary

The cache-hit experiment moved from setup into real paired execution. Earlier
work created the baseline, runner, and eight-pair runbook. Dedicated run
threads then produced 16 run rows across eight Full/Lite pairs. This closure
turn audited the current repository state, found that `experiment-runs.csv` and
`pilot-summary` were complete while the task card and progress summary still
described only the first pair, and brought the durable closeout records into
agreement with the actual data.

## Work Completed

1. Preserved the completed pilot dataset with 16 real runs and eight complete
   Full/Lite pairs.
2. Added the final six pilot artifacts for fixture inventory, Python GUI smoke,
   and C++ module mapping.
3. Refreshed the pilot summary to report `8 / 8` complete pairs.
4. Classified aggregate evidence as `redundant-overhead` with a task-class
   split rather than a global process-policy change.
5. Marked the controller task card complete and replaced first-pair-only
   evidence with the eight-pair result.
6. Updated the project progress report and completed-task index.
7. Recorded residual risk around the Python GUI Lite failure, manual scoring,
   experimental BEI proxy, and lack of second-reviewer sampling.
8. Added an orchestration audit for the multi-worker session shape and recorded
   the reusable lesson as candidate experience E007.

## Files And Artifacts

| File | Type | Status |
|---|---|---|
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-runs.csv` | pilot data | 16 runs, 8 complete pairs |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/pilot-summary.md` | generated report | refreshed |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/pilot-summary.json` | generated data | refreshed |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/fixture-inventory/basic-fixtures-lite.md` | run artifact | added |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/fixture-inventory/json-fixtures-full.md` | run artifact | added |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/python-gui-smoke/screens-lite.md` | run artifact | added |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/python-gui-smoke/bridge-modules-full.md` | run artifact | added |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/cpp-module-map/io-session-lite.md` | run artifact | added |
| `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/cpp-module-map/kernel-numeric-full.md` | run artifact | added |
| `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md` | task card | complete |
| `docs/reports/project-progress-summary-2026-05-31.md` | progress report | updated |
| `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md` | archive | added |
| `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/orchestration-audit.md` | orchestration audit | added |
| `docs/completed-tasks/README.md` | index | updated |

## Evidence

Pilot summary:

```bat
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

Result: passed before closure. The generated report records `Complete pairs:
8 / 8` and aggregate classification `redundant-overhead`.

Focused task-card and tool checks:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-31-cache-hit-pilot-eight-pairs\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-31-cache-hit-pilot-eight-pairs\README.md --min-score 30
python -m py_compile tools\token_audit\cache_hit_experiment.py
git diff --check -- docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\pilot-artifacts
```

Result: passed during closure. The completed-task validator passed, and the
closure score was `34/40`, above the required `--min-score 30` threshold.

Pilot aggregate:

| Metric | Full | Lite | Delta |
|---|---:|---:|---:|
| Input tokens | 4,689,553 | 2,199,491 | Lite saved 53.1% |
| Output tokens | 46,128 | 24,906 | Lite was shorter |
| Average audit score | 4.375 | 4.188 | Lite down 4.3% |
| Average BEI proxy | 0.712 | 0.653 | Lite down 8.3% |
| Validation pass rate | 100.0% | 87.5% | Lite had one failure |
| Defect/reopen count | 0 | 1 | Lite had one defect |

Pair classifications:

| Pair | Classification | Notes |
|---|---|---|
| `completed-archive-audit-1` | `mixed-or-inconclusive` | Lite saved tokens but audit score dropped just past the 10% threshold. |
| `cpp-module-map-1` | `redundant-overhead` | Lite saved 52.7% input with no audit or defect penalty. |
| `docs-index-1` | `mixed-or-inconclusive` | Lite used more input tokens than Full. |
| `fixture-inventory-1` | `redundant-overhead` | Lite saved 80.0% input and scored higher in this low-risk inventory slice. |
| `python-gui-smoke-1` | `healthy-institutionalization` | Lite saved tokens but missed the dependency/import failure boundary and recorded one defect. |
| `repo-audit-1` | `mixed-or-inconclusive` | Lite saved tokens but audit score dropped just past the 10% threshold. |
| `task-card-audit-1` | `redundant-overhead` | Lite saved 49.0% input with no audit or BEI penalty. |
| `token-diagnostic-1` | `mixed-or-inconclusive` | Lite savings were only 5.8%, below the decision threshold. |

## Decisions

| Decision | Rationale |
|---|---|
| Treat the aggregate as `redundant-overhead` for low-risk task classes only | Three pairs cleanly met redundant-overhead thresholds, while one pair showed a Full-lane safety win. |
| Do not promote a global Lite default yet | The pilot is enough for a task-class split review, not enough to rewrite repository process policy. |
| Keep Full mandatory for environment-sensitive GUI smoke and validation-heavy work | `python-gui-smoke-1-lite` failed validation and recorded the only defect/reopen signal. |
| Keep BEI as an experimental proxy | Rows use `bei=experimental_proxy`; the token-audit cost and BEI model still needs calibration before becoming a gate. |
| Preserve artifact-level evidence rather than raw chat logs | The run artifacts and CSV rows are sufficient to replay the pilot without transcript reconstruction. |

## Orchestration Audit

This session used a merge architecture: independent worker sessions produced
scoped artifacts, and the controller owned JSONL telemetry import, CSV row
recording, summary generation, and closure. The dedicated audit is stored at
`docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/orchestration-audit.md`.

The main orchestration lesson is that shared ledger writes must remain
controller-owned. This prevented CSV conflicts and made it possible to reject a
duplicate archive Lite worker while preserving the valid first run.

## Skipped Checks And Risks

**Skipped checks**:

- Full repository quality gates were not rerun because this closure changes
  token-audit reports, docs, and pilot artifacts only.
- No second-reviewer audit-score sampling was performed in this closure turn.
- Missing `matplotlib` was not installed; it remains recorded as the Lite GUI
  smoke failure signal.
- Historical USD cost normalization was not attempted.

**Residual risks**:

- Manual audit scores may drift without a second reviewer or rubric calibration.
- BEI values are experimental proxies and should not become policy gates yet.
- The DeepSeek cache-write estimate remains fixed at 39,000 tokens because
  cache creation tokens are not reported directly.
- Several unrelated dirty/untracked files remain outside this scoped closeout
  and must not be included in the cache-hit commit.

## Experience / Skill / Agent Evaluation

| Material | Decision | Reason / Evidence |
|---|---|---|
| Experience | candidate | The eight-pair Full/Lite pilot provides a reusable pattern for calibrating agentic process overhead by task class; recorded as E007 parallel experiment worker orchestration. |
| Skill | no | Existing `gcs-token-audit-steward` and `task-scoped-session-closer` cover the workflow; no new skill is justified from this pilot alone. |
| Agent | no | No new institutional agent is needed; the next move is policy review and second-reviewer calibration. |

## Narrative Line Coverage

| Line | Coverage |
|---|---|
| 14:primary | Converts cache-hit telemetry from a suspicious aggregate into task-class evidence for process governance. |

## Follow-Up

1. Sample at least two pairs with a second reviewer to calibrate audit scores.
2. Draft a task-class Full/Lite policy only for classes that met thresholds.
3. Keep Full required for GUI/environment-sensitive and validation-heavy tasks
   until more successful Lite evidence exists.
4. Repair token-audit cost normalization and BEI calibration before using cost
   or BEI as a hard decision gate.
5. Install/select the GUI Python environment with `matplotlib` before rerunning
   the Python GUI smoke path.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/`
- Task card:
  `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`
- Runbook:
  `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md`
- Pilot data:
  `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-runs.csv`
- Pilot summary:
  `docs/reports/token-audit/cache-hit-diagnosis-20260530/pilot-summary.md`
- Current promotion state: experience candidate only; no skill or agent
  promotion.
