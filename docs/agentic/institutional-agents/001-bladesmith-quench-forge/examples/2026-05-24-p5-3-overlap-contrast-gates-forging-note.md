# Experience Forging Note: P5.3 Overlap And Contrast Gates

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p5-3-overlap-contrast-gates`
- Time range: P5.3 overlap/contrast gate implementation
- Source artifacts:
  - `tools/ui_qa/gcs_overlap_contrast.py`
  - `tests/tools/test_gcs_overlap_contrast.py`
  - `tools/architecture_visualization/figure71_html_compositor.py`
  - `docs/architecture/70-visualization/overlap-contrast-gate.md`
  - `docs/completed-tasks/2026-05-24-p5-3-overlap-contrast-gates/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figure 71 HTML now carries six panel boxes and 21 contrast targets. |
| Decisions | Use declared design-grid boxes and contrast markers before screenshot baselines. |
| Preferences | Missing visual-integrity instrumentation should fail. |
| Hypotheses | Source-level overlap/contrast markers will make P5.4 pixel baselines easier to interpret. |
| Open questions | Which exact screenshot backend should produce stable baseline pixels. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Make layout contracts explicit before pixel baselines. | A figure uses CSS grid and needs overlap checks. | Emit deterministic design-grid boxes for critical panels. | Do not claim browser-pixel overlap proof from source boxes. | Forced overlap fixture fails in `tests/tools/test_gcs_overlap_contrast.py`. | Ends where exact rendered rectangles are required. |
| Put contrast thresholds in the artifact metadata. | A visual role has a different contrast expectation than body text. | Store foreground, background, and minimum ratio per target. | Do not hard-code one threshold for every semantic visual role. | Token chips use explicit threshold metadata. | Applies to generated HTML with known color tokens. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Source-level boxes prove no visual overlap." | They prove the declared grid contract, not browser-rendered pixels. | P5.4 screenshot/pixel baseline. |
| "All contrast targets should use 4.5." | Some evidence chips are semantic markers rather than body text. | Role-specific accessibility policy after screenshot review. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Generated figures should emit QA metadata for key regions and text contrast
targets before pixel-level comparison is introduced.

## Follow-Up

- Reuse overlap/contrast labels in P5.4 screenshot reports.
- Consider role-specific contrast policy if later reviews need stricter chip
  treatment.
