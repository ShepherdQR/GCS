# UI Aesthetic Phase 4: Replay And Solve Polish

## Goal

Make temporal workflows legible in the main window. Replay and solve should
feel like intentional application states, not log lines appended to a debug
surface.

This phase keeps history replay in `platform_gui.py`, renderer emphasis in
`visualizer.py`, and read-only dispatch in `viewer_bridge.py`.

## Replay State Contract

The GUI owns transient replay state:

- active/inactive;
- total history steps;
- current step index;
- current action label;
- current replay speed.

This state is displayed near the viewport in a replay rail. It is not persisted
to scene files.

## Replay Rail

The replay rail should sit near the top of the viewport and include:

- current step / total steps;
- current action;
- speed control;
- a small stop/cancel affordance.

The rail is visible during replay and quiet otherwise. During normal editing it
may collapse to a compact "Replay Ready" line or remain hidden.

## Focus Flow

Replay focus continues to use the optional renderer `focus` dictionary:

- `platform_gui.py` maps the active history entry to focused IDs;
- `viewer_bridge.render_graph_view` forwards focus;
- `visualizer.py` renders focus as accent halo/stroke.

Phase 4 may improve labels and rail text, but it must not move mutation logic
into renderer code.

## Solve Summary

After solve completes, the GUI stores a transient solve summary:

- status text;
- satisfied count;
- violated count;
- total checked constraints;
- whether an output graph was applied.

The summary appears near the viewport or status area as a concise report. The
raw C++ output remains outside the GUI unless a later diagnostics surface is
introduced.

## Message Tone

Status messages should use consistent language:

- "Solving..." when a solve is running;
- "Solved: N/N constraints satisfied" for clean results;
- "Solve warning: X violated" for violations;
- "Replay step i/n: Action" during replay;
- "Replay complete" at the end.

Avoid relying on symbolic glyphs or emoji for meaning.

## Non-Goals

- no re-running solver during replay;
- no durable solve-report schema;
- no timeline editor;
- no animation framework;
- no modal replay window.

## Acceptance Checks

- replay progress is understandable without reading the bottom log;
- changing replay speed during replay affects subsequent steps;
- replay cancel restores the current model view;
- solve results are readable as a compact summary;
- renderer focus still works in 3D, graph, and three-view modes;
- touched Python parses with `ast.parse`;
- focused `git diff --check` passes.
