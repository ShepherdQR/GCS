---
example_id: 2026-05-25-ui-workbench-phase6-7-pilot
experience_id: E002-phase-step-summary-update-commit-continue
status: evidence
source_task:
  - docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/README.md
  - docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/README.md
---

# UI Workbench Phase 6-7 Pilot

## Lesson

For GUI work that depends on a local desktop stack, the safest step boundary is
often not "make the UI visible." It is:

```text
pure projection contract
  -> no-Tk tests
  -> GUI orchestration hook
  -> renderer consumes supplied state
  -> documented environment-limited visual check
```

This lets the project advance UI architecture even when the current interpreter
cannot import GUI dependencies such as `matplotlib`.

## Evidence

The session completed two UI steps:

- Phase 6 moved focus construction into `python/gcs_viz/viewer_bridge.py` and
  connected table selection to the canvas through `platform_gui.py`.
- Phase 7 added conservative `constraint_states` projection and had
  `visualizer.py` render only supplied `satisfied`, `violated`, or `unknown`
  states.

Both steps used:

- a detailed phase work plan under `docs/architecture/`;
- a task card under `docs/agentic/tasks/`;
- no-Tk unit tests in `tests/tools/test_gcs_viz_history_replay.py`;
- UI QA via `tools/ui_qa/gcs_ui_qa.py`;
- a completed-task archive with skipped-check risk recorded;
- a path-scoped commit and branch push.

## What Worked

- The pure projection boundary kept solver truth out of Tk widgets and
  Matplotlib drawing helpers.
- The renderer changes stayed simple because they consumed explicit focus or
  diagnostic state instead of parsing solver output.
- The phase-step loop made the next step obvious: Phase 6 enabled Phase 7, and
  Phase 7 made Phase 8's contrast/accessibility work concrete.
- Environment blockers did not become false failures: missing `matplotlib` and
  `__pycache__` write errors were recorded as degraded checks while no-write
  syntax checks and pure tests still covered the changed contracts.

## Reusable Rule

When a GUI task is blocked from full desktop verification, do not skip
verification. Split the work so the semantic projection is testable without the
GUI runtime, and record the visual/runtime check as residual risk until the
environment is ready.

## Follow-Up Candidate

Phase 8 can use this pilot to decide whether UI QA should gain a first-class
"environment-limited visual check" result type, separating dependency gaps from
semantic projection failures.
