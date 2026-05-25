---
task_id: 2026-05-25-ui-phase7-diagnostics-overlay
status: complete
request: "Continue after Phase 6 and implement the next UI diagnostics overlay node, pushing at validation checkpoints."
scope: implementation
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-architecture-steward
  - gcs-python-gui-builder
affected_contracts:
  - Python viewer_bridge constraint-state projection
  - Python GUI solve-report diagnostic focus projection
  - Matplotlib renderer constraint-state styling
affected_paths:
  - docs/architecture/77-ui-design-development-plan-report.md
  - docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md
  - python/gcs_viz/viewer_bridge.py
  - python/gcs_viz/platform_gui.py
  - python/gcs_viz/visualizer.py
  - tests/tools/test_gcs_viz_history_replay.py
  - docs/agentic/tasks/2026-05-25-ui-phase7-diagnostics-overlay.md
  - docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/
required_evidence:
  - diagnostic-projection-tests
  - ui-qa
  - syntax-compile
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# UI Phase 7 Diagnostics Overlay

## Scope

Implement the Phase 7 diagnostics overlay described in
`docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`.

This task extends the Phase 6 focus projection path with conservative
constraint states so solve results can become visible in the viewport without
moving solver truth into the renderer.

## Non-Goals

- Do not add residual magnitudes, conflict sets, redundancy sets, or repair
  drafts.
- Do not change C++ solver contracts, scene schemas, history schemas, or IO
  behavior.
- Do not add new rendering dependencies.
- Do not claim per-constraint states when solver output only provides aggregate
  counts.

## Context To Read

- `.codex/skills/gcs-ui-design-steward/SKILL.md`
- `.codex/skills/gcs-python-gui-builder/SKILL.md`
- `.codex/skills/gcs-architecture-steward/SKILL.md`
- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`
- `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py`

## Acceptance Gates

- `viewer_bridge.py` owns pure constraint-state projection helpers.
- `platform_gui.py` builds diagnostic focus from solve output only when
  constraint IDs can be identified; otherwise states remain `unknown`.
- `visualizer.py` renders supplied `satisfied`, `violated`, and `unknown`
  states in 3D, graph, and three-view modes.
- Diagnostic legend entries appear only when diagnostic states are present.
- Projection and fallback behavior are tested without importing Tk.
- The task archive validates and scores above the closure threshold.

## Verification Plan

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
python tools\ui_qa\gcs_ui_qa.py
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py'), Path('python/gcs_viz/visualizer.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase7-diagnostics-overlay.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md --min-score 30
```

## Evidence Bundle

Produced:

- `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py`
- `tests/tools/test_gcs_viz_history_replay.py`
- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/README.md`
- `docs/completed-tasks/README.md`

Focused tests:

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
```

Observed result:

- 15 tests passed.

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
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py'), Path('python/gcs_viz/visualizer.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
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
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase7-diagnostics-overlay.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md --min-score 30
```

Observed result:

- task-card validation passed.
- completed-task validation passed.
- closure score passed at 36/40.

## Residual Risks

- Manual desktop visual verification may remain blocked by missing
  `matplotlib` in the active interpreter.
- Current text output may not contain stable constraint IDs; this task must
  degrade to `unknown` until structured reports arrive.
