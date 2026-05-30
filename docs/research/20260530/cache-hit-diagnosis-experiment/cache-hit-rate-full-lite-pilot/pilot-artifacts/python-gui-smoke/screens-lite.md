# Python GUI Smoke Lite

- Run label: `CACHE_HIT_EXPERIMENT_RUN python-gui-smoke-1-lite python-gui-smoke-1 Lite`
- Controller task card: `docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`
- Scope: compact screen/module smoke for `python/gcs_viz`
- Result: **fail**, because `platform_gui` cannot import in this environment without `matplotlib`

## Minimal Inventory

Command:

```powershell
Get-ChildItem -Path python\gcs_viz -File | Select-Object Name,Length | Format-Table -AutoSize
```

Observed top-level modules:

```text
algebra.py        13952
color_scheme.py    7686
engine_bridge.py   4560
event_store.py     3551
platform.py       20938
platform_gui.py   51855
viewer_bridge.py  17325
visualizer.py     29750
__init__.py          36
__main__.py         293
```

Command:

```powershell
Get-ChildItem -Path python\gcs_viz\screens -Force | Select-Object Name,Mode,Length | Format-Table -AutoSize
```

Observed screen/dialog modules:

```text
dialogs.py       6372
dialogs_tk.py   12915
__init__.py         0
```

Command:

```powershell
rg -n "class .*Tk|class .*Dialog|def main|Tk\(|Notebook|Toplevel|FigureCanvasTkAgg" python\gcs_viz\platform_gui.py python\gcs_viz\screens\dialogs_tk.py python\gcs_viz\viewer_bridge.py python\gcs_viz\visualizer.py
```

Observed GUI entry/screen evidence:

```text
python\gcs_viz\screens\dialogs_tk.py:12:class AddRigidSetDialog(tk.Toplevel):
python\gcs_viz\screens\dialogs_tk.py:67:class AddGeometryDialog(tk.Toplevel):
python\gcs_viz\screens\dialogs_tk.py:141:class AddConstraintDialog(tk.Toplevel):
python\gcs_viz\screens\dialogs_tk.py:221:class DeleteConfirmDialog(tk.Toplevel):
python\gcs_viz\screens\dialogs_tk.py:266:class EditConstraintDialog(tk.Toplevel):
python\gcs_viz\platform_gui.py:57:        self.root = tk.Tk()
python\gcs_viz\platform_gui.py:125:        self.object_notebook = ttk.Notebook(browser_frame)
python\gcs_viz\platform_gui.py:334:        self.canvas_widget = FigureCanvasTkAgg(self.fig, master=parent)
python\gcs_viz\platform_gui.py:1091:def main():
```

## Check Evidence

Command:

```powershell
python -m compileall -q python\gcs_viz
```

Result: pass; command exited `0` with no output.

Command:

```powershell
$env:PYTHONPATH=(Get-Location).Path + '\python'; python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
```

Result: fail.

```text
ModuleNotFoundError: No module named 'matplotlib'
```

Command:

```powershell
Get-Content -Path python\requirements.txt
```

Dependency evidence:

```text
matplotlib
networkx
numpy
rich
textual
```

## Smoke Assessment

- Compile health: pass.
- Import/startup health: fail before GUI construction because `matplotlib` is unavailable in the active Python environment.
- Obvious missing screens/modules: no missing source file was detected for the expected Lite-lane GUI shape; observed modules include `platform_gui.py`, `visualizer.py`, `viewer_bridge.py`, `engine_bridge.py`, and `screens/dialogs_tk.py`.
- Obvious runtime gap: active interpreter lacks required GUI dependency `matplotlib`.

## Next Action

Install or select the Python environment with `python\requirements.txt`, then rerun:

```powershell
python -m compileall -q python\gcs_viz
$env:PYTHONPATH=(Get-Location).Path + '\python'; python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
```
