# UI Aesthetic Phase 1: Theme Foundation

## Goal

Unify the existing Tkinter GUI and Matplotlib renderers under one warm,
professional theme while keeping the current layout and behavior intact.

This phase deliberately avoids an inspector rewrite, icon system, or advanced
interaction states. It is a foundation pass.

## Target Feeling

The app should read as a precise desktop modeling tool:

- warm ivory canvas;
- quiet panel chrome;
- low-saturation categorical colors;
- thin borders;
- restrained labels;
- clear status color without alarmist neon.

## Theme Tokens

Core surface tokens:

- `bg_window`: app background;
- `bg_panel`: left and toolbar panels;
- `bg_canvas`: Matplotlib figure background;
- `bg_table`: table body;
- `border`: separators and frame borders;
- `text_primary`, `text_secondary`, `text_muted`.

Semantic tokens:

- `accent`: primary active/replay/action color;
- `info`;
- `success`;
- `warning`;
- `error`;
- `grid`;
- `axis`;
- `constraint_default`.

The rigid-set palette should be categorical but muted. The constraint palette
should be softer than the current pure RGB/CMY palette.

## Tkinter Scope

Apply theme through ttk styles in `platform_gui.py`:

- root background;
- base `TFrame`, `TLabelframe`, `TLabel`;
- `TButton`, `TRadiobutton`, `Horizontal.TScale`;
- `Treeview` and headings;
- status and log labels.

Keep layout, widget hierarchy, command handlers, and dialog behavior unchanged.

## Matplotlib Scope

Apply the theme in `visualizer.py` through helper functions:

- figure face color;
- axes face color;
- title and label colors;
- tick colors;
- grid color and alpha;
- softened legend frame;
- summary text color.

Keep renderer inputs and outputs unchanged. Renderer functions should still draw
on the provided `Figure` and avoid Tk dependencies.

## Non-Goals

- no switch away from Tkinter;
- no browser or web frontend;
- no new dependencies;
- no screenshot asset generation;
- no layout rewrite;
- no changes to solver semantics or scene IO.

## Acceptance Checks

- `python -m compileall -q python\gcs_viz`;
- focused `git diff --check` on touched files;
- manual GUI check when a local display and required Python packages are
  available.
