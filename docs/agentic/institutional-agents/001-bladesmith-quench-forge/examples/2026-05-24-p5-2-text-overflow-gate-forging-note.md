# Experience Forging Note: P5.2 Text Overflow Gate

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p5-2-text-overflow-gate`
- Time range: P5.2 text-budget gate implementation
- Source artifacts:
  - `tools/ui_qa/gcs_text_overflow.py`
  - `tests/tools/test_gcs_text_overflow.py`
  - `tools/architecture_visualization/figure71_html_compositor.py`
  - `docs/architecture/70-visualization/text-overflow-gate.md`
  - `docs/completed-tasks/2026-05-24-p5-2-text-overflow-gate/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figure 71 HTML now carries 101 text-budget markers checked by the P5.2 gate. |
| Decisions | Use budget-based source checks before pixel-level screenshot baselines. |
| Preferences | Make missing instrumentation fail instead of silently passing visual QA. |
| Hypotheses | Explicit budgets will make later P5.3/P5.4 gates easier to localize. |
| Open questions | The exact screenshot backend for pixel-perfect overflow remains P5.4 work. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Add instrumentation before measuring layout globally. | A visual QA gate needs to inspect generated dense HTML. | Put explicit labels and budgets on the text containers that matter. | Do not let uninstrumented HTML pass as visually checked. | Missing-budget fixture fails in `tests/tools/test_gcs_text_overflow.py`. | Applies to generated artifacts where source can emit markers. |
| Start with forced fixtures before screenshot baselines. | Pixel tooling is not stable yet, but the rule is mechanically checkable. | Add source-level pass/fail tests now and reserve pixel checks for later. | Do not claim pixel-perfect proof from text budgets. | P5.2 archive names exact screenshot work as P5.4. | Ends where actual rendered geometry is required. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Text budget checks prove no rendered overflow." | They bound text growth but do not inspect pixels or font metrics. | P5.4 screenshot/pixel baseline. |
| "Every HTML element needs a budget." | Only meaningful figure text containers need budgets; structural wrappers do not. | A future QA failure showing an unbudgeted text role matters. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Generated figure HTML should expose labels and budgets for important text
containers before later visual QA tries to reason about pixels.

## Follow-Up

- Use the same marker style for P5.3 overlap targets if bounding metadata is
  added.
- Keep exact pixel overflow for P5.4.
