# Experience Forging Note: P6.1 Integrated Showcase Brief

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p6-1-integrated-showcase-brief`
- Time range: P6.1 showcase brief definition
- Source artifacts:
  - `docs/architecture/88-p6-1-integrated-showcase-brief.md`
  - `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
  - `docs/architecture/70-visualization/showcase-scene-report.md`
  - `docs/completed-tasks/2026-05-24-p6-1-integrated-showcase-brief/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | The existing showcase scene already has positive metadata, a negative variant, renderer tests, and CLI/public evidence gates. |
| Decisions | P6.1 stays brief-only so P6.2/P6.3 inherit a clear claim. |
| Preferences | Negative rejection evidence should be visible in the showcase, not hidden in tests. |
| Hypotheses | A claim-first brief will reduce manual figure rescue in P6.3. |
| Open questions | Whether existing fixture metadata is rich enough for a layout-aware showcase compositor. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Define the five-second claim before touching assets. | A showcase phase begins after visual QA gates are stable. | Write a brief that names audience, panels, vocabulary, and review questions. | Do not regenerate figures before the claim is clear. | `88-p6-1-integrated-showcase-brief.md` records the claim and panels. | Applies to showcase and paper/demo artifacts. |
| Make rejection evidence part of the story. | The fixture has both positive and negative behavior variants. | Require a negative-variant panel in the showcase brief. | Do not present only accepted happy-path output. | Missing fixed ID is named in source evidence and panels. | Applies when solver credibility is the subject. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "The existing Figure 72 SVG is automatically the final showcase." | It is useful source evidence, but P6.3 still has to judge the production pipeline. | Visual-integrity QA and art-direction review after P6.3. |
| "Figma MCP can be decided from abstract preference." | The decision should be grounded in a real showcase artifact and collaboration gap. | P6.3 output and P6.4 governance note. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

High-stakes visual work should start with a brief that names source evidence,
panel claims, and reviewer questions before implementation.

## Follow-Up

- P6.2 should promote fixture evidence in renderer-consumable form.
- P6.3 should treat the brief as the acceptance contract for the showcase
  figure.
