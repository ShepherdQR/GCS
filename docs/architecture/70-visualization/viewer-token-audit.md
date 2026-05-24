# Viewer Token Audit

Snapshot date: 2026-05-24.

This note completes the audit part of P3.1. It records where Python viewer and
legacy textual surfaces consume `GCS Warm Evidence Tokens`.

Governing conventions:

- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Visual Integrity Gate**

## Audit Scope

Command:

```powershell
rg -n "#[0-9A-Fa-f]{6}|white on|style=|Style\(" python/gcs_viz
```

Reviewed surfaces:

- `python/gcs_viz/color_scheme.py`
- `python/gcs_viz/visualizer.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/platform.py`

## Findings

| Surface | Result | Action |
| --- | --- | --- |
| `color_scheme.py` | Contains canonical raw hex values by design. | Treat as the only allowed Python raw-hex source for P3. |
| `visualizer.py` | Uses imported token aliases for Matplotlib colors, markers, node sizes, and line styles. | No P3.1 change needed. |
| `platform_gui.py` | Uses `GCS_THEME` for Tkinter/ttk surfaces, status colors, log colors, and Matplotlib welcome colors. | No P3.1 change needed. |
| `platform.py` | Legacy textual status used Rich named colors and `white on #16213e`. | Updated DOF and status styles to use `GCS_THEME` aliases. |

## Remaining Rule

For P3 work, raw hex values in `python/gcs_viz` are allowed only in
`color_scheme.py`. Other viewer files should use `GCS_TOKENS`, `GCS_THEME`,
`RIGID_SET_COLORS`, `CONSTRAINT_COLORS`, or exported style aliases.

Future P5 token lint should encode this rule directly.
