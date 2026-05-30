# Cache-Hit Diagnosis Experiment

This directory is the stable index for the cache-hit diagnosis experiment.

The complete experiment package now lives in:

- `cache-hit-rate-full-lite-pilot/`

Use that subfolder for the experiment report, plan, runbook, run data, and
pilot artifacts. The root directory remains as a small navigation layer so
older references to `docs/research/20260530/cache-hit-diagnosis-experiment/`
still land at the correct experiment family.

## Package Contents

| Path | Purpose |
|---|---|
| `cache-hit-rate-full-lite-pilot/README.md` | Detailed experiment report: process, implementation, key data, and conclusions. |
| `cache-hit-rate-full-lite-pilot/experiment-plan.md` | Original experiment plan and decision rules. |
| `cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md` | Eight paired Full/Lite runbook and recording instructions. |
| `cache-hit-rate-full-lite-pilot/experiment-runs.csv` | Recorded run data: 16 runs, 8 complete pairs. |
| `cache-hit-rate-full-lite-pilot/pilot-artifacts/` | Per-run evidence artifacts. |

## Current Result

The completed pilot recorded 8 paired Full/Lite task classes. Aggregate evidence
classified the pilot as `redundant-overhead`, but the durable conclusion is
task-class-specific rather than global:

- Lite is promising for low-risk audit, inventory, and module-map work.
- Full remains important for GUI, environment-sensitive, and validation-heavy
  work after the Python GUI Lite lane produced the only validation failure and
  defect/reopen signal.

The closure archive is:

- `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md`
