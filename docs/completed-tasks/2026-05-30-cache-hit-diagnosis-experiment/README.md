---
task_id: 2026-05-30-cache-hit-diagnosis-experiment
status: complete
session_goal: "Persist a token/cache baseline, write a lightweight Full/Lite experiment plan, run a first-pass diagnostic, and prepare scoped Git delivery."
archive_target: docs/completed-tasks/2026-05-30-cache-hit-diagnosis-experiment/
---

# 2026-05-30-cache-hit-diagnosis-experiment

## Task Objective

Persist the current GCS-A token/cache economics state as a reviewable baseline,
then design and execute the first lightweight diagnostic pass for deciding
whether very high cache-hit rate indicates redundant process overhead or healthy
institutionalization.

## Scope And Non-Goals

**In scope**: task card, token/cache baseline, repository-audit baseline
snapshot, Full/Lite experiment plan, pilot CSV template, first-pass telemetry
diagnostic, completed-task archive, focused validation, and scoped Git handoff.

**Out of scope**: changing solver behavior, changing token-audit database rows,
editing historical JSONL transcripts, repairing token-audit CLI dependencies,
normalizing historical cost records, or promoting a permanent process policy
before paired-run evidence exists.

## Interaction Summary

The session started with a design request about whether high cache-hit rate was
redundancy or institutional maturity. After the user asked to persist the phase,
write the plan, execute the suggested steps, and push, the work moved into the
non-trivial lifecycle path: create and validate a task card, freeze baseline
artifacts, write the experiment plan, run first-pass telemetry bucketing, create
closure evidence, and preserve unrelated dirty files during Git handoff.

Git state was noisy during the session because `master` and existing remote
branches advanced while local untracked agent/config artifacts were present. A
fresh task branch, `codex-cache-hit-diagnosis-20260530-run2`, was created from
the current `master` head before scoped staging.

## Work Completed

1. Created and validated task card
   `docs/agentic/tasks/2026-05-30-cache-hit-diagnosis-experiment.md`.
2. Persisted the token/cache baseline as both Markdown and JSON.
3. Collected a repository-audit baseline snapshot from `HEAD`.
4. Wrote a durable experiment plan with Full and Lite process lanes, metrics,
   scoring, decision rules, and follow-up gates.
5. Added `experiment-runs.csv` so future paired runs have a consistent capture
   format.
6. Ran a first-pass diagnostic that buckets existing sessions into
   high-cache/high-TLR, short high-overhead, zero-cache/low-TLR, and mixed
   groups.
7. Recorded residual risks around token-audit CLI dependencies, DeepSeek cache
   creation gaps, unreliable stored USD cost, and unrelated dirty worktree
   artifacts.

## Files And Artifacts

| File | Type | Status |
|---|---|---|
| `docs/agentic/tasks/2026-05-30-cache-hit-diagnosis-experiment.md` | task card | validated |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/baseline.md` | baseline report | complete |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/token-cache-baseline.json` | baseline data | complete |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/repository-audit-baseline.json` | repository snapshot | generated |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.md` | diagnostic report | complete |
| `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.json` | diagnostic data | complete |
| `docs/research/20260530/cache-hit-diagnosis-experiment/README.md` | experiment plan | complete |
| `docs/research/20260530/cache-hit-diagnosis-experiment/experiment-runs.csv` | pilot template | complete |
| `docs/completed-tasks/2026-05-30-cache-hit-diagnosis-experiment/README.md` | archive | complete |
| `docs/completed-tasks/README.md` | index | updated |

## Evidence

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-30-cache-hit-diagnosis-experiment.md
```

Result: passed.

```bat
python tools\repository_audit\repository_audit.py collect --revision HEAD --output docs\reports\token-audit\cache-hit-diagnosis-20260530\repository-audit-baseline.json
```

Result: snapshot written with 1202 files, 226211 text lines, and 71 known
repository-audit findings.

```bat
python tools\repository_audit\repository_audit.py check
```

Result: 0 errors, 71 warnings. The warnings are existing unknown artifact-class
findings for tracked `.claude` agent/skill assets.

Token baseline result:

| Metric | Value |
|---|---:|
| Sessions | 38 |
| Turns | 1210 |
| Tool calls | 1548 |
| Input tokens | 4,380,119 |
| Output tokens | 1,140,477 |
| Cache read tokens | 326,080,768 |
| Legacy cache hit rate | 98.67% |
| DeepSeek estimated raw hit rate | 99.55% |
| Output/input TLR | 26.04% |
| Estimated cold-load overhead ratio | 33.83% |

## Decisions

| Decision | Rationale |
|---|---|
| Use a paired Full/Lite pilot | It avoids drawing a policy conclusion from a single aggregate cache-hit number. |
| Keep hard governance gates in Lite mode | The experiment should test context/process width, not remove mandatory safety rules. |
| Exclude stored USD cost for now | Current `total_cost_usd_micro` contains outlier-scale records; token deltas are more reliable until normalization. |
| Treat the first-pass result as mixed | Existing telemetry shows productive high-cache/high-TLR sessions and waste-suspect short low-TLR sessions. |
| Do not promote a process policy yet | Fewer than 6 to 8 paired runs would be too thin for institutional policy. |

## Skipped Checks And Risks

**Skipped checks**:

- `python -m tools.token_audit ...` CLI checks were skipped because current
  Python runtimes lack optional dependencies (`click` / `yaml`).
- Full `validate-docs` was not run because this task changed a narrow report
  surface and the worktree contains unrelated active artifacts.
- No new A/B task runs were executed in this first pass; only existing telemetry
  was diagnosed.

**Residual risks**:

- DeepSeek does not report cache creation tokens, so raw cache-write economics
  depend on the existing 39,000-token estimate.
- USD cost storage must be normalized before cost becomes a decision metric.
- Repeated read/command metrics are proxies; paired-run reviewer scoring is
  still needed.
- The current checkout contains unrelated untracked agent/config artifacts that
  remain unstaged.

## Experience / Skill / Agent Evaluation

| Material | Decision | Reason / Evidence |
|---|---|---|
| Experience | candidate | The paired Full/Lite experiment design may become reusable after 6 to 8 paired runs produce evidence. |
| Skill | no | Existing token-audit and task-closure skills cover the work; no new skill is justified from the first pass. |
| Agent | no | No new institutional agent is justified; the next step is data collection, not role promotion. |

## Narrative Line Coverage

| Line | Coverage |
|---|---|
| 14:primary | The task advances agentic token economics by freezing a baseline and defining evidence thresholds for process overhead versus institutional value. |

## Follow-Up

1. Fix or document token-audit CLI runtime dependencies.
2. Run 6 to 8 paired Full/Lite pilot tasks using `experiment-runs.csv`.
3. Normalize or recompute USD cost before using cost as a decision gate.
4. Promote Lite defaults only for task classes that meet the decision
   thresholds.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-30-cache-hit-diagnosis-experiment/`
- Task card:
  `docs/agentic/tasks/2026-05-30-cache-hit-diagnosis-experiment.md`
- Baseline report:
  `docs/reports/token-audit/cache-hit-diagnosis-20260530/baseline.md`
- Experiment plan:
  `docs/research/20260530/cache-hit-diagnosis-experiment/README.md`
- Related experience: candidate only; revisit after paired-run evidence.
- Skill, agent, eval, fixture, or tool update needed: no immediate promotion;
  future work should repair token-audit CLI dependencies and cost normalization.
