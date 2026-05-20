# Python GUI Map

## Current Layout

- `python/gcs_viz/platform_gui.py`: tkinter main window, controls, status log,
  embedded figure, actions.
- `python/gcs_viz/visualizer.py`: 3D, graph, and three-view rendering helpers.
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

## Common Checks

Search before changing UI behavior:

```bat
rg -n "messagebox|os\.startfile|start chrome|system\(|FigureCanvasTkAgg|history" python\gcs_viz
```
