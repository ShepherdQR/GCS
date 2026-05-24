# Viewer Inspector Layout Audit

Snapshot date: 2026-05-24.

This note completes the audit part of P3.3. It compares the current Tk
inspector against `72-ui-aesthetic-phase-3-inspector-layout.md`.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**

## Result

The active `platform_gui.py` inspector already satisfies the Phase 3 layout
contract:

- `Model Summary` is visible at the top and shows model name, RS/G/C counts,
  net DOF, and status.
- `Object Browser` uses `ttk.Notebook` tabs for Rigid Sets, Geometries, and
  Constraints.
- Object add/edit/remove controls are local to the active table.
- `Commands` separates Solve, Replay History, replay speed, Save, and Load
  from object editing.
- The left column is fixed at 320 px and the root minimum size is 960 x 600,
  preserving narrow-window behavior.

## P3.3 Change

The old `_build_left_panel` scroll-stack implementation was not called by the
active UI. It is now renamed `_build_left_panel_legacy_unused` and marked as a
legacy comparison path so future work does not accidentally revive the stacked
debug layout.

## Remaining Layout Work

P3.4 should focus on replay and solve evidence polish near the viewport, not on
another inspector rewrite.
