# Experience Forging Note: P4.2 Browser Export Smoke

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p4-2-browser-export-smoke`
- Time range: P4.2 browser export implementation and validation
- Source artifacts:
  - `docs/agentic/tasks/2026-05-24-p4-2-browser-export-smoke.md`
  - `tools/architecture_visualization/browser_export.py`
  - `tools/architecture_visualization/figure_qa.py`
  - `docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-browser-export.json`
  - `docs/completed-tasks/2026-05-24-p4-2-browser-export-smoke/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Browser CLI export produced PNG/PDF artifacts after refreshing the HTML source. |
| Decisions | P4.2 stays dependency-light; token proof is required even if browser export is skipped. |
| Preferences | Prefer repo-native browser evidence before Figma MCP or new renderer dependencies. |
| Hypotheses | A later visual QA gate can compare browser screenshots once token lint and overflow checks exist. |
| Open questions | Whether SVG review export needs a real backend or should stay outside the browser smoke gate. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Refresh source HTML before export smoke. | A spec/compositor has changed since the last artifact build. | Run browser export with `--render-html` so token proof tests the current compositor. | Do not silently trust stale generated HTML. | The first smoke exported artifacts but failed token checks until HTML was regenerated. | Applies to generated figure artifacts, not hand-authored docs. |
| Make optional tooling produce a manifest, not silence. | Browser tooling may be absent or vary by workstation. | Record `exported`, `partial`, `skipped`, or `failed` status and keep token proof separate. | Missing token proof must fail even when browser availability is optional. | `figure_qa.py` now checks browser status and `html_tokens_passed`. | Does not replace full screenshot/contrast/overlap gates. |
| Keep export smoke narrower than asset rebuild. | A figure pipeline needs export confidence before final polish. | Produce review artifacts and QA evidence first, then schedule token lint and rebuild separately. | Do not mix broad editorial redesign into the smoke gate. | P4.2 closed with a thin tool and roadmap update, while P4.4 remains pending. | Applies when the next step has distinct risk or review criteria. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Install Figma MCP immediately for top-tier figures." | P4.2 showed repo-native browser export can already produce inspectable artifacts. | Reassess only after token lint, overflow, overlap, contrast, and screenshot gates mature. |
| "PNG/PDF export proves final visual quality." | Export only proves browser rendering and token presence; it does not prove text hierarchy, contrast, or overlap quality. | P5.2/P5.3/P5.4 visual integrity gates. |
| "SVG must be part of the browser smoke." | Chromium CLI does not provide reliable HTML-to-SVG export. | A governed backend or design-surface decision in a later step. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

The reusable practice is small and concrete: generated figure export checks
should refresh source artifacts, produce a manifest, and keep optional browser
availability separate from mandatory token proof.

## Follow-Up

- Add this smoke pattern to future figure QA checklist language when P5.1 adds
  token lint.
- Revisit SVG export only after the P4.3 dependency decision.
