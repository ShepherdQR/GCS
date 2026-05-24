# Experience Forging Note: P6.2 Showcase Fixture Evidence

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p6-2-showcase-fixture-evidence`
- Time range: P6.2 fixture evidence promotion
- Source artifacts:
  - `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
  - `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json`
  - `tools/architecture_visualization/showcase_fixture_evidence.py`
  - `tests/tools/test_showcase_fixture_evidence.py`
  - `docs/architecture/89-p6-2-showcase-fixture-evidence.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | The showcase fixture now names rank/residual, gluing, diagnostics, replay-boundary, panel, token, and rejection expectations. |
| Decisions | Metadata is an evidence contract; CTest and CLI remain runtime truth. |
| Preferences | Figure tooling should consume explicit evidence metadata rather than retyping CLI facts. |
| Hypotheses | P6.3 will be simpler if the renderer reads an enriched evidence bundle. |
| Open questions | Whether the current SVG renderer should be upgraded to a layout-aware HTML compositor. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Promote fixture evidence before figure production. | A showcase brief names panels and evidence roles. | Add metadata fields and a checker before changing the renderer. | Do not duplicate solver behavior in metadata. | `showcase_fixture_evidence.py` checks scene/metadata consistency. | Ends where runtime execution is required. |
| Include negative evidence as a first-class fixture contract. | The showcase has a missing-fixed negative variant. | Check the required panel, token, report code, and missing ID. | Do not let the final figure hide rejection behavior. | Forced report-code mismatch fails in tests. | Applies when solver credibility is the visual subject. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Metadata can replace CLI/CTest runtime gates." | Metadata is descriptive; runtime gates prove behavior. | Continue running public evidence chain and CLI smoke. |
| "P6.3 should hard-code evidence facts in the renderer." | The metadata is now the intended source for showcase facts. | Renderer update that consumes enriched metadata. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Before producing a high-stakes figure, promote fixture evidence into an
executable metadata contract and add forced failure tests.

## Follow-Up

- P6.3 should consume the enriched metadata directly.
- P6.4 should treat the metadata checker as part of the repo-native alternative
  to external design-surface workflows.
