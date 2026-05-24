# UI Aesthetic Roadmap

## Thesis

The GCS viewer should feel like a quiet technical atelier: warm, precise,
mathematical, and calm under repeated use. It should not look like a neon debug
panel, a web marketing page, or a generic AI dashboard.

The visual system must serve solver work first:

- geometry and constraints remain inspectable;
- color carries semantic weight instead of decoration;
- dense model data stays scannable;
- replay and solve feedback feel deliberate rather than noisy;
- Tkinter and Matplotlib share one visual language.

## Style Principles

- Use warm technical neutrals instead of cool blue-gray chrome.
- Use muted categorical colors for rigid sets; avoid saturated rainbow colors.
- Reserve strong accent color for active focus, replay, and important actions.
- Prefer line style, opacity, and shape for constraint type; use color for
  state and focus.
- Keep surfaces flat with thin borders. Avoid heavy shadows and glossy effects.
- Keep UI controls dense but quiet. Make the model canvas the visual center.
- Replace emoji-led command labels with stable text or future line icons.

## Phase 1: Theme Foundation

Persist the shared palette and apply it to the existing Tkinter and Matplotlib
surfaces without changing layout or interaction ownership.

Deliverables:

- warm neutral and semantic color tokens in `python/gcs_viz/color_scheme.py`;
- muted rigid-set and constraint palettes;
- ttk root, panels, labels, buttons, treeviews, status, and log colors using
  the shared theme;
- Matplotlib canvas, axes, grid, labels, legend, and summary text using the
  same theme;
- no GUI layout rewrite.

Acceptance:

- `python -m compileall -q python\gcs_viz` passes when pycache is writable;
- `python -B -m py_compile` passes for touched Python files;
- rendered views are visibly warmer, lower saturation, and less default
  Matplotlib-like.

## Phase 2: Viewport Semantics

Make the visualization more expressive without increasing visual noise.

Detailed design: `docs/architecture/72-ui-aesthetic-phase-2-viewport-semantics.md`.

Deliverables:

- geometry type encoded by marker/shape and size;
- constraint type encoded primarily by line style;
- selected, replay-current, violated, and solved states defined as visual
  states;
- graph view node/edge styling aligned with 3D and three-view renderers;
- legend reduced to semantic swatches and line samples.

Acceptance:

- normal state is calm;
- active or invalid objects are immediately visible;
- labels do not dominate the model by default.

## Phase 3: Inspector Layout

Reshape the left column from stacked debug panels into a model inspector.

Detailed design: `docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md`.

Deliverables:

- top model summary section with model name, RS/G/C counts, DOF, and status;
- tabs or segmented control for Rigid Sets, Geometries, and Constraints;
- local table toolbars for add/edit/delete actions;
- separate primary actions for Solve, Replay, Save, and Load.

Acceptance:

- repeated editing requires less scrolling;
- the main command path is visually distinct from object tables;
- narrow-window behavior remains stable.

## Phase 4: Replay And Solve Polish

Make temporal workflows feel intentional.

Detailed design: `docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md`.

Deliverables:

- replay rail near the viewport with step, action, and speed controls;
- current replay action highlight in the renderer;
- solve report summary surface with satisfied/violated counts;
- status messages with consistent tone and color.

Acceptance:

- replay is understandable without a separate dialog;
- solve feedback is readable without scanning terminal-style logs.

## Phase 5: Design QA And Accessibility

Codify visual quality gates.

Detailed design: `docs/architecture/72-ui-aesthetic-phase-5-design-qa-accessibility.md`.

Deliverables:

- screenshot-based visual review checklist for core states;
- color contrast notes for text and status colors;
- fixture scene set for UI QA;
- documented do/don't rules for future GUI work.

Acceptance:

- future UI changes can be reviewed against stable aesthetic rules;
- visual polish survives feature additions.

## Phase 6 And Beyond

The complete forward plan is now maintained in
`docs/architecture/77-ui-design-development-plan-report.md`.

Next planned phases:

- Phase 6: Interaction Semantics;
- Phase 7: Solve Diagnostics Overlay;
- Phase 8: Accessibility And Contrast Refinement;
- Phase 9: Replay Rail Refinement;
- Phase 10: Manual Visual QA Pass.
