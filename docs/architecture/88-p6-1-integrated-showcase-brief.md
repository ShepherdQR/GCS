# P6.1 Integrated Showcase Brief

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Brief Status

Accepted for P6.2 implementation.

This brief defines the integrated feature constraint graph showcase before any
new fixture or figure work. The goal is to make the showcase prove solver
credibility through one public scene, not through decorative storytelling.

## Five-Second Claim

GCS can carry one inspectable constraint scene from public JSON solve intent
through decomposition, numeric rank/residual evidence, gluing diagnostics,
viewer projection, CLI smoke, and negative rejection evidence.

## Audience

- Project maintainers deciding whether the solver architecture is coherent.
- Reviewers who need to see local-to-global evidence on one scene.
- Future demo or paper readers who need a vivid but faithful visual summary.
- The P6.4 Figma MCP decision, which should judge external tooling against a
  real repo-native showcase artifact.

## Source Evidence

| Source | Role |
| --- | --- |
| `fixtures/scene/showcase/integrated_feature_showcase.gcs.json` | Positive public JSON scene and solve intent. |
| `fixtures/scene/showcase/integrated_feature_showcase.metadata.json` | Expected public evidence counts and gate names. |
| `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.gcs.json` | Negative missing-fixed-ID behavior variant. |
| `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json` | Expected rejection code and missing ID evidence. |
| `tools/architecture_visualization/render_showcase_scene.py` | Existing deterministic Figure 72 renderer and report generator. |
| `docs/architecture/70-visualization/showcase-scene-report.md` | Current generated public-evidence summary. |
| `tools/agentic_design/agentic_toolkit.py run-quality-gates` | Default public evidence and visual-integrity gate chain. |

## Evidence Vocabulary

| Evidence role | Canonical token | Visual meaning |
| --- | --- | --- |
| Public scene/domain truth | `evidence.domain` | Geometry, entity identity, immutable scene facts. |
| Structural graph | `evidence.graph` | Incidence and component structure. |
| Planner boundary | `evidence.planner` | Cover, fixed boundary, SolveDAG, gluing. |
| Numeric proof | `evidence.numeric` | Rank, residual, local solve, convergence. |
| Diagnostics/public gate | `evidence.diagnostic` | Post-local diagnostics, contract tests, CLI smoke. |
| Rejection variant | `evidence.failure` | Missing fixed entity and typed report code. |
| IO/viewer boundary | `evidence.boundary` | Public scene IO and read-only viewer projection. |
| Accepted state | `state.ok` | Accepted with warnings, quality gate pass. |
| Warning state | `state.warning` | AcceptedWithWarnings and residual review context. |
| Error state | `state.error` | Negative variant rejection. |

## Required Panels

| Panel | Claim | Required evidence |
| --- | --- | --- |
| Scene Contract | Public JSON carries durable solve intent. | schema `gcs-0.3`, 6 geometries, 4 constraints, fixed geometry `[0]` |
| Constraint Graph | The scene is two connected local components, not isolated micro-fixtures. | components `(0,1,2)` and `(3,4,5)`, constraint IDs 0-3 |
| Boundary Plan | Fixed boundary propagates into decomposition and numeric tasks. | planner subproblems `2`, fixed boundary variable evidence |
| Numeric Evidence | Local solves expose rank and residual evidence. | numeric reports `2`, residual max `0.000000`, rank summaries |
| Gluing And Diagnostics | Local sections become a committed accepted state through diagnostics. | gluing accepted, post-local diagnostics warnings, commit accepted |
| Negative Variant | Invalid solve intent fails with a named stable report code. | `kernel.solve_intent_missing_fixed_entity`, missing ID `[999]` |
| Gate Chain | The scene is public evidence, not a private demo. | CTest showcase sentinels, CLI showcase smoke, renderer tests |

## Production Direction

P6.2 should promote or enrich fixture evidence before changing the final visual.
It should make the public scene and metadata sufficient for a renderer or HTML
compositor to consume without reverse-engineering expectations from C++ tests.

P6.3 should then produce a showcase figure that:

- starts from the public scene and metadata;
- exposes the evidence vocabulary above;
- uses `GCS Warm Evidence Tokens`;
- passes P5 token, text, overlap/contrast, and screenshot baseline gates where
  applicable;
- records an art-direction review result before P6.4.

The existing Figure 72 SVG is a useful deterministic atlas artifact. P6.3
should treat it as source evidence and either upgrade it through a tokenized
layout-aware pipeline or explicitly justify why the existing renderer remains
sufficient for this showcase.

## Art Director Review Questions

- Can the five-second claim be read without knowing the implementation history?
- Is the constraint scene visually central, with evidence around it rather than
  decoration around text?
- Are rank, residual, gluing, diagnostics, and rejection evidence visible or
  reachable?
- Does color encode the evidence vocabulary instead of generic categories?
- Does the figure feel like **GCS Quiet Technical Atelier**: warm, precise,
  calm, and inspectable?
- Does the artifact reveal whether Figma MCP would add collaboration value, or
  does the repo-native pipeline already carry the necessary review surface?

## Acceptance For P6.1

P6.1 is accepted when:

- the main claim, audience, source evidence, vocabulary, panels, and review
  questions are recorded;
- P6.2 knows what fixture evidence to promote;
- P6.3 knows what figure panels must communicate;
- P6.4 has explicit decision criteria tied to the showcase artifact.
