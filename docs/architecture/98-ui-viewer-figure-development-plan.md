# UI, Viewer, And Scientific Figure Development Plan

Status: active
Date: 2026-05-26

## Purpose

This plan turns the current UI/viewer/scientific-figure integration line into
the next development sequence. It starts from the current baseline:

- VE-001: Figure 72 integrated showcase review artifacts;
- VE-002: D5 viewer canvas evidence capture;
- Phase 8 and Phase 9 viewer projection refinements;
- Phase 10 TkAgg canvas visual QA;
- D5 Solver Evidence Workbench first package.

The goal is to move the line from **strong, integration in progress** toward
**strong and integrated** without updating the narrative map prematurely.

## Governing Conventions

- **GCS Evidence-First Interface Grammar**: UI state must come from reports,
  snapshots, histories, or explicit projections.
- **GCS Scientific Figure Pipeline**: figures are generated from semantic specs
  and source evidence, not hand-edited final pixels.
- **GCS Visual Integrity Gate**: promoted visual artifacts need reproducible
  checks, review outputs, and baseline policy.
- **GCS Quiet Technical Atelier**: density, calm hierarchy, and repeated-use
  legibility matter more than decorative novelty.

## Boundary

The viewer may make solver evidence inspectable. It must not compute durable
rank, residual, gluing, obstruction, conflict, redundancy, or repair truth.
Those meanings must arrive as structured reports or command drafts owned by
solver, diagnostics, decomposition planning, or session runtime.

This plan intentionally does not change `docs/architecture/95-gcs-narrative-map.md`.
The narrative map should be refreshed only after the next proof point is
implemented and validated.

## Development Thesis

The next maturity jump is not "more UI." It is one traceable evidence loop:

```text
structured solver or replay report
  -> viewer_bridge projection
  -> workbench state
  -> visual QA artifact
  -> figure or demo package
  -> reviewer-visible limitation and next action
```

Each milestone below should close one part of that loop while preserving module
ownership.

## Milestone Roadmap

| Milestone | Target | Main output | Promotion gate |
| --- | --- | --- | --- |
| UVF-01 | Harden VE-002 capture as a repeatable viewer QA entry point. | Full-window capture policy or explicit canvas-only policy, environment note, Art Director viewer review. | `capture_viewer_evidence.py`, screenshot baseline, UI QA, review note all agree. |
| UVF-02 | Define structured report-to-viewer projection. | A viewer projection contract for solve status, constraint states, residual/rank summaries, and report provenance. | No-Tk projection tests cover report inputs without GUI-side solver inference. |
| UVF-03 | Build evidence-backed Constraint Manager projection. | Constraint rows with ID, type, entities, state, evidence source, and command-draft affordances. | Rows trace to structured reports or explicit unknown state. |
| UVF-04 | Surface Constraint Manager in the local workbench. | GUI table/filter surface linked to canvas focus and non-mutating repair drafts. | User can select a violated or unknown constraint and see affected geometry plus evidence source. |
| UVF-05 | Add local-to-global evidence projection. | Context-cover, boundary, gluing, overlap, and obstruction projection contract. | Projection consumes planner/diagnostic reports and keeps unsupported data labeled. |
| UVF-06 | Produce the next scientific figure from the same evidence chain. | Figure 74 or equivalent report-to-viewer-to-figure artifact. | Figure spec, source report, browser/review artifact, QA, and manifest entry exist. |
| UVF-07 | Upgrade D5 into D6 external reviewer story. | One end-to-end demo package from scene to report to viewer to figure. | Reviewer can run or inspect the chain without reconstructing architecture history. |
| UVF-08 | Reassess narrative level. | Narrative map update only after UVF-03 or UVF-06 lands. | Evidence supports "strong and integrated" wording without hand-waving. |

## Immediate Work Queue

### UVF-01: Viewer Visual Evidence Hardening

Purpose:

- Turn VE-002 from a first capture into a maintained visual QA surface.

Deliverables:

- document whether the stable baseline is canvas-only or full-window;
- add a dependency/runtime note for the Python environment that can run
  TkAgg, Matplotlib, NetworkX, NumPy, and Pillow;
- add an Art Director review note for the VE-002 PNG;
- keep `assets/screenshot-baselines.json` as the exact-hash gate.

Acceptance:

- `python tools\ui_qa\capture_viewer_evidence.py` regenerates the artifact;
- `python tools\ui_qa\gcs_screenshot_baseline.py` passes;
- the review note separates defects from preferences.

### UVF-02: Structured Report Projection Contract

Purpose:

- Stop treating diagnostic overlay state as text parsing or metadata-only
  fallback when structured report evidence exists.

Deliverables:

- a report projection shape in `python/gcs_viz/viewer_bridge.py`;
- source fields for report ID, state version, constraint state, residual/rank
  summary, and provenance;
- fixture inputs under tests or docs that represent accepted, warning, and
  error reports;
- no-Tk tests for normalization and unknown-state behavior.

Acceptance:

- viewer projection can distinguish `satisfied`, `violated`, `unknown`,
  `unsupported`, and `not_reported`;
- every projected state has a source report or a named fallback reason;
- GUI code consumes the projection and does not parse solver meaning itself.

### UVF-03: Constraint Manager Projection

Purpose:

- Make constraints navigable as solver evidence, not just as editable scene
  objects.

Deliverables:

- read-only constraint-manager projection with stable IDs;
- columns for type, attached geometry, value, state, evidence source, and
  selection focus;
- filters for type and state;
- command-draft placeholders for future repair actions.

Acceptance:

- selecting a row highlights affected geometry and constraints;
- row state is evidence-backed or explicitly unknown;
- command drafts remain non-mutating until session runtime accepts them.

### UVF-04: Workbench Surface

Purpose:

- Move the local GUI closer to the Solver Evidence Workbench target while
  preserving the current Tkinter and Matplotlib stack.

Deliverables:

- constraint manager tab or panel in `platform_gui.py`;
- summary rail that shows selected constraint evidence;
- visual QA capture updated with a constraint-manager scenario.

Acceptance:

- no new browser/server dependency;
- narrow-width behavior remains stable;
- viewer canvas and table selection stay synchronized through projection
  helpers.

### UVF-05: Local-To-Global Evidence Projection

Purpose:

- Prepare Phase 12 without inventing planner truth in the viewer.

Deliverables:

- projection contract for context covers, overlaps, boundary projections,
  gluing status, and obstruction paths;
- unsupported-data report when planner/diagnostic input is incomplete;
- renderer hints only for supplied projection state.

Acceptance:

- the viewer can show which local context solved or failed only when the report
  says so;
- boundary and gluing evidence remains traceable to diagnostics/planner
  reports.

### UVF-06: Figure 74 Evidence Chain

Purpose:

- Add a scientific figure that proves UI/viewer/figure integration from one
  shared evidence source rather than parallel hand-written summaries.

Deliverables:

- figure brief and semantic spec;
- source report or fixture evidence;
- browser-composed review artifact;
- visual QA and screenshot baseline;
- visual evidence manifest entry.

Acceptance:

- the figure references the same projection vocabulary as the viewer;
- labels and state colors match `GCS Warm Evidence Tokens`;
- the five-second claim is visible and the three-minute evidence path is
  inspectable.

### UVF-07: D6 External Reviewer Story

Purpose:

- Turn D5 evidence into an external reviewer walkthrough.

Deliverables:

- demo package with scene, command path, viewer path, figure path, expected
  outputs, known limitations, and follow-up;
- one generated or captured artifact per step;
- brief reviewer script that does not require reading all architecture docs.

Acceptance:

- a reviewer can start from `docs/product/demos/` and inspect the full chain;
- D1/D2 gaps are either filled or explicitly marked as lower-level demos.

## Quality Gates

Use focused gates first:

```bat
python -B -m unittest tests.tools.test_capture_viewer_evidence tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_gcs_screenshot_baseline
python tools\ui_qa\capture_viewer_evidence.py
python tools\ui_qa\gcs_ui_qa.py
python tools\ui_qa\gcs_screenshot_baseline.py
```

Add broader gates when a milestone touches source reports, figure specs, or
runtime commands:

```bat
python tools\architecture_visualization\showcase_fixture_evidence.py
python tools\architecture_visualization\showcase_scene_html_compositor.py --check
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Promotion Rules

Promote the line to **strong and integrated** only when at least one
structured report can be traced through:

1. source scene or report;
2. viewer projection;
3. workbench state;
4. visual QA artifact;
5. scientific figure or demo package.

Promote it toward **very strong** only after both are true:

- constraint-manager or local-to-global inspector evidence is implemented;
- one scientific figure and one product demo consume the same projection or
  report source.

## Explicit Deferrals

- Do not add a new GUI stack.
- Do not reopen Figma MCP without a concrete external collaboration or
  editable-layout gap.
- Do not update the narrative map from this plan alone.
- Do not let UI tables compute solver diagnostics.
- Do not treat a canvas-only screenshot as full-window GUI evidence without
  labeling the limitation.
