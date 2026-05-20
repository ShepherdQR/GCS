---
name: gcs-python-gui-builder
description: Project-specific workflow for the GCS local Python visualization interface. Use when editing python/gcs_viz, tkinter dialogs, matplotlib views, engine_bridge, platform_gui, visualizer behavior, history replay UI, or local GUI behavior.
---

# GCS Python GUI Builder

## Start Here

Use this skill for `python/gcs_viz/` work. Read
`references/python-gui-map.md` before changing the GUI flow, visualizer, or
engine bridge.

## Product Direction

The project direction is local desktop GUI, not web. Prefer `tkinter` plus
`matplotlib` TkAgg, embedded canvases, and zero server/browser dependencies.

## UI Rules

- Keep the main interface in `platform_gui.py`: left controls, right embedded
  figure, status/log area, and actions.
- Keep view rendering in `visualizer.py`. Prefer functions that draw onto a
  provided `matplotlib.figure.Figure` so the same renderer can be embedded or
  tested.
- Keep modal input details in `screens/dialogs_tk.py`.
- Use status/log messages for normal warnings, solve results, and validation
  feedback. Avoid disruptive `messagebox` calls for routine flow.
- After graph edits, refresh tables, refresh canvas, and update status
  consistently.
- Record user-visible topology or value changes into `graph.history` when they
  should replay later.

## Integration Rules

- Do not launch browsers, HTTP servers, external image viewers, or web assets
  from GUI code.
- Keep the C++ bridge in `engine_bridge.py`; GUI code should call bridge
  methods instead of constructing solver command lines in random handlers.
- Keep Python scene read/write behavior aligned with C++ IO when editing JSON,
  behavior, or history.
- Treat `platform.py` textual code as legacy compatibility unless the user
  explicitly asks to improve it.

## Validation

Use lightweight import and serialization checks when GUI windows cannot be
opened:

```bat
python -m pip install -r python\requirements.txt
set PYTHONPATH=%CD%\python
python -m gcs_viz --help
```

For visual changes, manually run `scripts\start_gui.cmd` when the environment
can display windows.
