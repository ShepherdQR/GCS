---
task_id: 2026-05-25-ui-phase6-focus-projection
status: complete
request: "Add the next UI step to the plan, implement Phase 6 focus projection, and push at a validated node."
scope: implementation
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-architecture-steward
  - gcs-python-gui-builder
affected_contracts:
  - Python viewer_bridge focus projection
  - Python GUI table-selection orchestration
  - Viewer focus rendering input
affected_paths:
  - docs/architecture/77-ui-design-development-plan-report.md
  - docs/architecture/93-ui-phase6-focus-projection-work-plan.md
  - python/gcs_viz/viewer_bridge.py
  - python/gcs_viz/platform_gui.py
  - tests/tools/test_gcs_viz_history_replay.py
  - docs/agentic/tasks/2026-05-25-ui-phase6-focus-projection.md
  - docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/
required_evidence:
  - focus-projection-tests
  - python-compileall
  - platform-gui-import
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# UI Phase 6 Focus Projection

## Scope

Implement the Phase 6 interaction primitive described in
`docs/architecture/93-ui-phase6-focus-projection-work-plan.md`.

This task makes table selection and replay share a pure focus projection path
so later diagnostic overlays, constraint-manager filters, and repair drafts can
reuse the same UI-neutral contract.

## Non-Goals

- Do not add canvas hit testing.
- Do not add diagnostic states or residual overlays.
- Do not change scene JSON, history schemas, solver behavior, C++ contracts, or
  IO adapters.
- Do not add a browser, HTTP server, web asset, or external viewer dependency.

## Context To Read

- `.codex/skills/gcs-ui-design-steward/SKILL.md`
- `.codex/skills/gcs-python-gui-builder/SKILL.md`
- `.codex/skills/gcs-architecture-steward/SKILL.md`
- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `tests/tools/test_gcs_viz_history_replay.py`

## Acceptance Gates

- `viewer_bridge.py` owns pure focus projection helpers for table selection and
  history replay.
- `platform_gui.py` binds rigid-set, geometry, and constraint table selection to
  canvas focus without moving solver truth into Tk handlers.
- Replay focus has precedence while replay is active.
- View changes and refreshes preserve table-selection focus outside replay.
- Focus projection tests run without importing Tk.
- The task archive validates and scores above the closure threshold.

## Verification Plan

```bat
python -m compileall -q python\gcs_viz
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay
$env:PYTHONPATH="$PWD\python"; python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md --min-score 30
```

## Evidence Bundle

Produced:

- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `tests/tools/test_gcs_viz_history_replay.py`
- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/README.md`
- `docs/completed-tasks/README.md`

Focused tests:

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
```

Observed result:

- 10 tests passed.

UI QA:

```bat
python tools\ui_qa\gcs_ui_qa.py
```

Observed result:

- UI QA checks passed.
- Existing advisory contrast warnings were reported.
- Headless render was skipped because `matplotlib` is missing in the active
  interpreter.

Syntax check:

```bat
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
```

Observed result:

- syntax compile passed without writing pycache.

Compile/import limitations:

```bat
python -m compileall -q python\gcs_viz
```

Observed result:

- failed to write existing `__pycache__` files due local permission errors.

```bat
$env:PYTHONPATH="$PWD\python"; python -B -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
```

Observed result:

- failed before executing GUI code because `matplotlib` is not installed in the
  active interpreter.

Task validation:

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md --min-score 30
```

Observed result:

- task-card validation passed.
- completed-task validation passed.
- closure score passed at 36/40.

## Residual Risks

- Manual desktop GUI visual verification may be skipped if the environment
  cannot display Tk windows; pure projection and import checks should still
  cover the contract.
- Selection focus is a UI projection only; it is not persisted to scene files
  and should not be treated as durable solver state.
