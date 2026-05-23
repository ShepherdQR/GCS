# UI Aesthetic Phase 3: Inspector Layout

## Goal

Turn the left column into a model inspector that supports repeated editing
without feeling like a stack of debug controls.

This phase keeps the existing Tkinter application, dialogs, graph mutation
handlers, and renderer contracts. It changes layout and information hierarchy
only inside `platform_gui.py`.

## Layout Contract

The left panel is organized as three stable zones:

- model summary: model name, RS/G/C counts, DOF, and global status;
- object browser: Rigid Sets, Geometries, and Constraints grouped behind a
  compact notebook or segmented control;
- command zone: Solve, Replay, Save, and Load as separate primary actions.

The status bar remains at the bottom for operational feedback. The model
summary is not a log; it is a persistent readout of current model state.

## Model Summary

The model summary should be visible without scrolling. It owns:

- loaded model name;
- rigid-set, geometry, and constraint counts;
- net DOF;
- classification status.

The summary updates from `graph_summary(graph)` and the current model name. It
must not compute new solver semantics in the GUI.

## Object Browser

Rigid Sets, Geometries, and Constraints should be browsable without scrolling
past unrelated sections.

Rules:

- use a compact `ttk.Notebook` for the three object tables;
- keep one table active at a time;
- keep add/edit/delete controls local to the active object type;
- preserve existing dialog classes and command handlers;
- keep double-click-to-edit for constraints.

The object tables continue to be populated by `_refresh_tables`.

## Command Zone

Primary commands are separated from object editing:

- Solve;
- Replay History;
- Save;
- Load.

Replay speed can stay in this zone until Phase 4 moves temporal controls closer
to the viewport.

## Visual Rules

- keep density high enough for desktop work;
- avoid nested decorative cards;
- use existing theme tokens only;
- use text labels for commands until a stable icon system exists;
- preserve narrow-window behavior by using fixed left-column width and compact
  table heights.

## Non-Goals

- no new persistence schema;
- no new solver/report semantics;
- no browser UI;
- no renderer changes;
- no drag selection or hit testing.

## Acceptance Checks

- model name and summary are visible immediately after load/save;
- object editing requires less vertical scrolling than Phase 2;
- existing Add/Remove/Edit/Solve/Replay/Save/Load handlers still work;
- `_refresh_tables`, `_update_dof`, and `_update_status_info` remain the state
  refresh path;
- touched Python parses with `ast.parse`;
- focused `git diff --check` passes.
