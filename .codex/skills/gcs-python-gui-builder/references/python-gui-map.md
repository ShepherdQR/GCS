# Python GUI Map

## Current Layout

- `GCS/gcs_viz/platform_gui.py`: tkinter main window, controls, status log, embedded figure, actions.
- `GCS/gcs_viz/visualizer.py`: 3D, graph, and three-view rendering helpers.
- `GCS/gcs_viz/screens/dialogs_tk.py`: tkinter dialogs, including history replay UI.
- `GCS/gcs_viz/algebra.py`: Python data model, text/JSON read/write, behavior, history.
- `GCS/gcs_viz/engine_bridge.py`: bridge to the C++ executable.
- `GCS/gcs_viz/color_scheme.py`: shared colors.
- `GCS/gcs_viz/platform.py`: legacy textual interface.
- `GCS/start_tui.bat`: current launch entry point.

## UI Direction From Old Plans

Adopt the useful part of the removed `.trae` plans: GCS needs a local GUI with embedded matplotlib, not a browser or web server. Routine feedback should appear in the application status/log area. Constraint edits should refresh the canvas and make it clear when solving is needed or has run.

## Common Checks

Search before changing UI behavior:

```bat
rg -n "messagebox|os\.startfile|start chrome|system\(|FigureCanvasTkAgg|history" GCS\gcs_viz GCS
```
