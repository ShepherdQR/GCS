# Python GUI Map

## Current Layout

- `python/gcs_viz/platform_gui.py`: tkinter main window, controls, status log,
  embedded figure, actions.
- `python/gcs_viz/visualizer.py`: 3D, graph, and three-view rendering helpers.
- `python/gcs_viz/viewer_bridge.py` when present: read-only view dispatch,
  summaries, replay reconstruction, and UI-neutral visualization facades.
- `python/gcs_viz/screens/dialogs_tk.py`: tkinter dialogs, including history
  replay UI.
- `python/gcs_viz/algebra.py`: Python data model, text/JSON read/write,
  behavior, history.
- `python/gcs_viz/engine_bridge.py`: bridge to the C++ executable.
- `python/gcs_viz/color_scheme.py`: shared colors.
- `python/gcs_viz/platform.py`: legacy textual interface.
- `scripts/start_gui.cmd`: current launch entry point.

## UI Direction

GCS needs a local GUI with embedded matplotlib, not a browser or web server.
Routine feedback should appear in the application status/log area. Constraint
edits should refresh the canvas and make it clear when solving is needed or has
run.

## Architecture Boundaries

- GUI code may mutate the current editable graph in response to user commands.
- Renderer code should be pure view construction over a graph snapshot.
- Viewer bridge code should be read-only and reusable from GUI dialogs,
  platform shells, and tests.
- Engine bridge code may know process paths and timeouts; renderers and dialogs
  should not.
- Scene read/write compatibility belongs in `algebra.py` and the C++ IO layer,
  not in ad hoc GUI save/load transformations.

## Common Failure Modes

- `ModuleNotFoundError`: install `python\requirements.txt` in the interpreter
  selected by `scripts\start_gui.cmd`.
- `ImportError` from `platform_gui.py`: check that dialog and renderer symbols
  imported by the main GUI actually exist.
- GUI starts but solve fails: check `GCS_EXE` or the default
  `out\build\clang-ninja\GCS.exe`.
- A script reports success after Python fails: inspect batch `ERRORLEVEL`
  handling.

## Common Checks

Search before changing UI behavior:

```bat
rg -n "messagebox|os\.startfile|start chrome|system\(|FigureCanvasTkAgg|history" python\gcs_viz
rg -n "build_.*figure|build_.*on_figure|viewer_bridge|EngineBridge" python\gcs_viz
```

Lightweight validation:

```bat
python -m compileall -q python\gcs_viz
set PYTHONPATH=%CD%\python
python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
scripts\start_gui.cmd
```
