---
task_id: 2026-05-26-ve002-viewer-visual-evidence
status: complete
session_goal: "Promoted VE-002 from future viewer evidence to a reproducible TkAgg viewer-canvas artifact for the D5 Solver Evidence Workbench, updated Phase 10/D5 documentation, and kept the narrative map unchanged."
archive_target: docs/completed-tasks/2026-05-26-ve002-viewer-visual-evidence/
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/
---

# 2026-05-26-ve002-viewer-visual-evidence

## Task Objective

Execute the next UI/viewer/scientific-figure follow-up plan after the initial
integration branch: add real viewer visual evidence for D5, validate it through
the visual integrity gate, and push the branch without making another narrative
map update.

## Scope And Non-Goals

In scope:

- VE-002 viewer visual evidence capture.
- Phase 10 viewer visual QA note.
- D5 Solver Evidence Workbench evidence update.
- Screenshot baseline update for the viewer review PNG.
- Focused tests and validation.
- Task card, completed-task archive, commit, and push.

Out of scope:

- `docs/architecture/95-gcs-narrative-map.md`.
- Solver runtime, numeric, IO, or report-code semantics.
- Full operating-system window screenshot capture.
- New GUI stack, web viewer, or Figma MCP.

## Interaction Summary

The user accepted the follow-up plan but explicitly said not to rush another
narrative map update. The work therefore stayed on the existing isolated branch
and focused on the proof point that was still missing: a concrete viewer visual
artifact connected to D5 and the shared visual evidence manifest.

## Work Completed

- Added `tools/ui_qa/capture_viewer_evidence.py`.
- Generated
  `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.review.png`.
- Generated
  `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.capture.json`.
- Added the VE-002 PNG to
  `docs/architecture/70-visualization/assets/screenshot-baselines.json`.
- Added `docs/architecture/70-visualization/viewer-phase-10-visual-qa.md`.
- Updated the visual evidence manifest, architecture atlas, Phase 10 report,
  integration plan, D5 demo package, demo index, and demo ladder.
- Added `tests/tools/test_capture_viewer_evidence.py`.
- Fixed a Summary-panel collision in
  `python/gcs_viz/visualizer.py` by separating diagnostic DOF text from the
  legend in three-view panels.

## Files And Artifacts

- `tools/ui_qa/capture_viewer_evidence.py`: reproducible VE-002 capture tool.
- `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.review.png`:
  four-state viewer review contact sheet.
- `docs/architecture/70-visualization/assets/ve002-d5-viewer-evidence-workbench.capture.json`:
  rail-state, focus, graph-summary, and capture-scope manifest.
- `docs/architecture/70-visualization/viewer-phase-10-visual-qa.md`:
  Phase 10 checklist and risk note.
- `docs/product/demos/d5-solver-evidence-workbench/`: D5 package now links
  Figure 72 and VE-002.

## Evidence

```text
tools\ui_qa\capture_viewer_evidence.py
PASS: generated VE-002 review PNG and capture JSON.

python -B -m compileall -q python\gcs_viz tools\ui_qa tests\tools\test_capture_viewer_evidence.py
PASS.

python -B -m unittest tests.tools.test_capture_viewer_evidence tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_gcs_screenshot_baseline
PASS: 24/24 tests.

python tools\ui_qa\gcs_screenshot_baseline.py
PASS: 3 baselines checked.

python tools\ui_qa\gcs_ui_qa.py
PASS with advisory graphic-accent contrast warnings; optional headless render skipped because base Python lacks matplotlib.

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ve002-viewer-visual-evidence.md
PASS.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ve002-viewer-visual-evidence\README.md
PASS.

python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ve002-viewer-visual-evidence\README.md --min-score 30
PASS: 36/40.

python tools\agentic_design\agentic_toolkit.py validate-docs
PASS.

git diff --check
PASS with LF-to-CRLF working-copy warnings only.
```

## Decisions

- Treat VE-002 as a viewer-canvas review artifact, not as a full-window
  screenshot, because OS-level screen grab was not reliable in this shell.
- Record rail state in JSON rather than forcing it into the canvas export.
- Keep `95-gcs-narrative-map.md` unchanged in this follow-up per user request.
- Fix the visible Summary-panel overlap immediately because the capture exposed
  a real Phase 10 visual defect.

## Skipped Checks And Risks

- Full-window screenshot capture was skipped; this remains a future visual QA
  improvement.
- The C++ engine was not available in this worktree, so the pass does not claim
  a live solve success.
- Structured report-to-viewer projection is still future work before Phase 11
  constraint-manager rows should become user-facing.

## Follow-Up

- Add full-window viewer screenshots if a reliable local capture backend is
  available.
- Start Phase 11 only after diagnostic report projections can provide
  evidence-backed constraint-manager rows.
- Keep D5 synchronized with both VE-001 Figure 72 and VE-002 viewer evidence.

## Session Learning

- Experience: candidate. This task reinforced that visual QA artifacts should
  be inspected before closure because the generated contact sheet revealed a
  real three-view layout collision.
- Skill: no promotion. Existing UI, viewer, figure, and closure skills covered
  the work.
- Agent: no promotion. The Art Director role can review future viewer
  artifacts, but this single pass does not justify a new institutional agent.

## Archive Handoff

- Task card:
  `docs/agentic/tasks/2026-05-26-ve002-viewer-visual-evidence.md`
- Archive path:
  `docs/completed-tasks/2026-05-26-ve002-viewer-visual-evidence/`
- Branch:
  `codex/2026-05-26-ui-viewer-figure-integration`
