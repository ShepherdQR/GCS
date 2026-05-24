---
task_id: 2026-05-24-p4-4-execution-map-rebuild
status: complete
session_goal: "Close P4.4 by rebuilding Figure 71 through the repo-native scientific figure pipeline and demoting the old SVG to historical prototype."
archive_target: docs/completed-tasks/2026-05-24-p4-4-execution-map-rebuild/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p4-4-execution-map-rebuild-forging-note.md
---

# P4.4 Execution-Map Rebuild

## Task Objective

Rebuild Figure 71 as a browser-rendered, tokenized, QA-checked artifact and
make the Step 1-40 report display that artifact instead of the older
coordinate-drawn SVG prototype.

## Scope And Non-Goals

In scope:

- refresh Figure 71 HTML and review artifacts;
- refresh browser manifest and Figure 71 QA evidence;
- add a fallback manifest refresh mode for already produced browser artifacts;
- add unit coverage for that fallback;
- update architecture docs and roadmap state.

Out of scope:

- adding graph/chart/Figma/MCP dependencies;
- redesigning Figure 71 content;
- deleting historical SVG assets;
- adding P5.2/P5.3 rendered layout gates.

## Interaction Summary

P4.3 decided not to add graph/chart dependencies for P4.4. The rebuild then
used the existing repo-native path. Direct browser CLI export refreshed review
artifacts but did not exit cleanly in this Windows desktop session, so P4.4
added `--reuse-existing-artifacts` to refresh manifest evidence from existing
PNG/PDF outputs while still checking HTML token presence.

## Work Completed

- Added `--reuse-existing-artifacts` to `browser_export.py`.
- Added `tests/tools/test_browser_export.py`.
- Added `python.browser_export` to the default quality-gate sequence.
- Refreshed Figure 71 browser export manifest and review PDF artifact.
- Re-ran Figure 71 QA successfully.
- Updated the Step 1-40 report to embed the review PNG and link HTML/PDF/QA
  artifacts.
- Added `docs/architecture/85-p4-4-execution-map-rebuild.md`.

## Files And Artifacts

- `tools/architecture_visualization/browser_export.py`
- `tests/tools/test_browser_export.py`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/tools/test_agentic_toolkit.py`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-browser-export.json`
- `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.pdf`
- `docs/architecture/71-step-1-40-execution-report.md`
- `docs/architecture/74-scientific-figure-production-paradigm.md`
- `docs/architecture/85-p4-4-execution-map-rebuild.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`

## Evidence

```text
python -B tools\ui_qa\gcs_token_lint.py
Passed.

python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html --reuse-existing-artifacts
Passed; manifest status exported with backend existing-artifacts.

python -B tools\architecture_visualization\figure_qa.py --figure figure71
Passed all schema, step coverage, HTML layout, token, browser manifest, and artifact checks.

python -m unittest tests.tools.test_browser_export
Ran 2 tests.
OK

python -m unittest tests.tools.test_agentic_toolkit
Ran 6 tests.
OK

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed, including the new python.browser_export gate.
```

## Decisions

- Decision: display the review PNG in the Step 1-40 report. Rationale: it is
  the browser-rendered artifact from the production pipeline.
- Decision: keep the old SVG as historical prototype. Rationale: it remains
  useful provenance for the pre-pipeline approach but should not be the display
  artifact.
- Decision: add a manifest refresh fallback rather than depending on clean
  browser-process shutdown. Rationale: this environment produced the files but
  did not return cleanly, and future constrained sessions need a truthful
  manifest path.

## Skipped Checks And Risks

- No requested P4.4 source or figure QA checks were skipped.
- Direct browser export timed out in this local session after writing artifacts;
  the fallback manifest mode records existing artifacts but is not a substitute
  for a clean browser export when the browser CLI behaves normally.
- P5.2/P5.3 remain necessary for stronger rendered text overflow, overlap, and
  contrast proof.

## Follow-Up

- Close P4 with a short phase summary.
- Start P5.2 text overflow gate after P4 close.
- Reassess Figma MCP only after the P5/P6 repo-native path is stable.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-24-p4-4-execution-map-rebuild/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p4-4-execution-map-rebuild-forging-note.md`
- Skill, eval, fixture, or tool update needed: P5.2 should add rendered text
  overflow fixtures and fail cases.
