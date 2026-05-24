# Experience Forging Note: P4.4 Execution-Map Rebuild

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p4-4-execution-map-rebuild`
- Time range: Figure 71 rebuild, manifest refresh, and prototype demotion
- Source artifacts:
  - `tools/architecture_visualization/browser_export.py`
  - `tests/tools/test_browser_export.py`
  - `docs/architecture/71-step-1-40-execution-report.md`
  - `docs/architecture/85-p4-4-execution-map-rebuild.md`
  - `docs/completed-tasks/2026-05-24-p4-4-execution-map-rebuild/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Direct browser CLI export refreshed PNG/PDF artifacts but did not return cleanly in this Windows session. |
| Decisions | Display the browser-rendered review PNG and keep the old SVG only as historical prototype. |
| Preferences | Prefer truthful manifest evidence over pretending a timed-out browser process was clean. |
| Hypotheses | Existing-artifact manifest refresh will help constrained local sessions without weakening normal browser export. |
| Open questions | Whether P5.4 screenshot baselines should use browser CLI, Browser plugin, or another stable capture path. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Separate artifact production from manifest refresh. | A browser process writes review files but does not exit cleanly. | Add a manifest mode that reuses existing artifacts and still proves HTML token presence. | Do not claim a clean browser run when the process timed out. | `--reuse-existing-artifacts` records backend `existing-artifacts` in the manifest. | Applies to generated review artifacts, not missing artifacts. |
| Demote prototypes by changing the display entry point. | A prototype and production artifact coexist. | Keep the prototype as provenance but embed the production review artifact in the user-facing doc. | Do not delete provenance just to hide the old path. | `71-step-1-40-execution-report.md` now embeds the review PNG and links the old SVG as historical prototype. | Applies when the prototype is not harmful and still explains lineage. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Existing-artifact manifest refresh replaces browser export." | It only refreshes evidence after artifacts already exist; it cannot create review images. | A normal browser export pass or future screenshot baseline gate. |
| "The old SVG should be deleted." | It is useful as provenance for why the pipeline changed. | A later cleanup policy for historical visual assets. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Figure rebuild steps should record whether artifacts were produced by a clean
export run or by an existing-artifact manifest refresh, and display docs should
point at the production artifact rather than the prototype.

## Follow-Up

- Consider adding the clean-export versus manifest-refresh distinction to the
  future visual QA checklist.
- Use P5.4 to decide the stable screenshot backend.
