---
name: gcs-python-gui-builder
description: Local Python visualization interface for GCS. Invoke when editing python/gcs_viz, tkinter dialogs, matplotlib renderers, viewer_bridge/facade code, engine_bridge, platform_gui, visualizer behavior, scripts/start_gui.cmd, history replay UI, GUI bug fixes, or local desktop visualization behavior.
---

# GCS Python GUI Builder

## Start Here

Read `references/python-gui-map.md` before changing GUI flow, rendering,
startup, engine bridge behavior, or history replay.

If the change alters saved JSON, history action schemas, or text scene
compatibility, also use `gcs-scene-behavior-steward`. If it changes dependency
direction or durable module boundaries, also use `gcs-architecture-steward`.

## Product Direction

Prefer optimizing the existing local desktop GUI over rewriting it. Keep the
stack `tkinter` plus embedded `matplotlib` TkAgg, with no browser, HTTP server,
web assets, or external viewer dependency.

Reimplement only when the user explicitly asks, or when the current architecture
cannot support the requested workflow after a concrete boundary analysis.

## Ownership Rules

- Keep `platform_gui.py` as GUI orchestration: widgets, commands, refresh
  scheduling, status/log messages, and user actions.
- Keep `visualizer.py` as rendering code only. It should draw onto a provided
  `matplotlib.figure.Figure`, return axes when useful, and avoid Tk widgets,
  file paths, solver calls, and model mutation.
- Keep `screens/dialogs_tk.py` for modal input and focused Tk dialogs. Dialogs
  may preview read-only snapshots but should not own solver truth.
- Put reusable read-only view dispatch, summaries, and replay reconstruction in
  a viewer bridge/facade module when the logic would otherwise be duplicated
  between GUI surfaces.
- Keep C++ process invocation in `engine_bridge.py`; GUI handlers should call
  bridge methods instead of constructing solver commands inline.
- Treat `platform.py` textual code as legacy compatibility unless the user
  explicitly asks to improve it.

## Interaction Rules

- Use status/log messages for normal warnings, solve results, and validation
  feedback. Avoid disruptive `messagebox` calls for routine flow.
- After graph edits, refresh tables, refresh canvas, update status, and record
  user-visible topology/value changes into `graph.history` when replay should
  preserve them.
- Treat `Solve` history entries as markers unless the feature explicitly
  re-runs the solver during replay.
- Make startup failures actionable: distinguish missing Python, missing
  packages, import errors, missing `GCS.exe`, and renderer exceptions.

## Validation

Use the narrowest checks that cover the change:

```bat
python -m compileall -q python\gcs_viz
set PYTHONPATH=%CD%\python
python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
scripts\start_gui.cmd
```

If dependencies are missing, first install `python\requirements.txt` in the
interpreter used by `scripts\start_gui.cmd`. For visual changes, manually run
the GUI when the environment can display windows.

## Claude Code Integration

When invoked for Python GUI work:
- Use `Read` on `references/python-gui-map.md` and the target file before
  editing.
- Use `Grep` to find all callers of a GUI function before changing its
  signature.
- Use `Edit` for surgical changes; keep `platform_gui.py` as orchestration and
  `visualizer.py` as render-only.
- Use `Bash` with `python -m compileall -q python\gcs_viz` after changes.
- For visual verification, use `Bash` with `scripts\start_gui.cmd` when a
  display is available.
- Never add browser, HTTP server, or web-asset dependencies to the GUI stack.
- When changing rendering behavior, also use `gcs-viewer-bridge-steward` if
  projection contracts are affected.
