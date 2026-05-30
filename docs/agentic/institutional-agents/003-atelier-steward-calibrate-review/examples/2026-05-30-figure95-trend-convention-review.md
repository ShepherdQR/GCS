# Atelier Steward Convention Fit Report: Figure 95 Narrative Line Level Trend

Date: 2026-05-30

Role: `Atelier Steward: Calibrate-Review`

Status: conditional-fit

Role maturity effect: seed-example-only

## Source Scope

- Request: Review the GCS Narrative Line Level Trend figure at `figure95-narrative-line-level-trend-20260526.svg` against GCS design-system conventions.
- Artifact under review:
  - `docs/architecture/70-visualization/assets/figure95-narrative-line-level-trend-20260526.svg`
- Source evidence:
  - `tools/architecture_visualization/specs/figure95-narrative-line-level-trend-20260526.yaml` (semantic spec)
  - `docs/architecture/70-visualization/narrative-line-level-trend-20260526.md` (trend report)
  - `docs/architecture/70-visualization/narrative-line-level-baseline-20260526.md` (baseline report)
  - `docs/architecture/75-ui-design-system-conventions.md` (governing conventions)
  - `docs/architecture/79-ui-token-taxonomy.md` (canonical token table)
  - `docs/architecture/76-ui-design-system-execution-plan.md` (execution plan)
- Files intentionally out of scope:
  - `docs/architecture/95-gcs-narrative-map.md` (source data, not visual)
  - `tools/ui_qa/gcs_token_lint.py` (generated assets are excluded from lint scope)

## Governing Conventions

| Convention | Applies? | Evidence |
| --- | --- | --- |
| GCS Quiet Technical Atelier | yes | The figure is a maturity-trend visualization in the architecture atlas; it must present evidence calmly and without decorative excess. |
| GCS Warm Evidence Tokens | yes | Every color in the SVG should trace to a canonical token or be explained as intentional drift. |
| GCS Evidence-First Interface Grammar | yes | Typographic hierarchy, label economy, and evidence-first layout rules apply. |
| GCS Scientific Figure Pipeline | yes | The figure is a dense architecture figure with a semantic spec and an SVG export; the pipeline requires spec-driven production with QA artifacts. |
| GCS Visual Integrity Gate | partially | Token discipline and structural checks apply, but generated SVG assets are explicitly excluded from the default token-lint scope per the P5.1 gate rule. |
| GCS Art Director Review | no | This is a steward convention-fit review, not an independent visual-taste judgment. Art Director review is downstream. |

## Evidence Read

| Evidence | Observation | Confidence |
| --- | --- | --- |
| SVG source (lines 1-105) | 23 distinct color hex values across backgrounds, rules, text, lines, circles, badges, and reading box. | high |
| SVG source typography | Font stack "Segoe UI, Arial, sans-serif" on all text elements; sizes 38px (title), 18px (subtitle/phase labels), 19px (narrative labels), 16px (data/annotations/reading body), 17px (reading title), 15px (axis ticks). All weights either 700 or default. | high |
| SVG source accessibility | `<title>`, `<desc>`, `role="img"`, `aria-labelledby` all present on line 1. | high |
| Semantic spec YAML | Schema `gcs.narrative_line_level_trend.v1` with source docs, level scale, two snapshot score tables, trend reading, and export path. No `canonical_token` fields. | high |
| Canonical token taxonomy | 23 surface, text, rule, evidence, state, geometry, constraint, rigid-set, figure, and viewer tokens defined with canonical hex values. | high |
| Trend report markdown | Links to the spec and SVG, contains a trend reading table and next strengthening targets. No QA artifact reference. | medium |

## Fit Findings

| Priority | Convention | Finding | Required action |
| --- | --- | --- | --- |
| P1 | GCS Warm Evidence Tokens | All 8 text colors in the SVG shift to cool blue-grey territory (#243036, #5d6468, #4d575c, #6a6f73, #253138, #465056, #263238, #566065) rather than using warm canonical text tokens (#181715, #5F5B53, #8B867A). This is systematic drift against the warm-evidence thesis. | Re-tint all text fills to canonical warm neutrals: `text.primary` (#181715) for title and data labels, `text.secondary` (#5F5B53) for subtitle and narrative labels, `text.muted` (#8B867A) for axis ticks and annotations. |
| P1 | GCS Warm Evidence Tokens | The six accent colors for narrative lines (#2d9bb3 teal, #d98c2b orange, #789d3e green, #8f6aa8 purple, #4f79c7 blue, #b56f53 brown) do not match any canonical evidence, state, geometry, or rigid-set token. The muted variants (#d9ecf0, #f3d7ab, #d7e4c6, #e6d9ee, #dce7ff, #ead6cd) are reasonable as lighter companions but likewise have no canonical equivalents. | Define narrative-line color tokens or map each line to an existing evidence-family token. The muted variants should be derived systematically (e.g., evidence.domain.fill / evidence.domain.stroke patterns) rather than chosen ad hoc. |
| P2 | GCS Quiet Technical Atelier | The cool text palette weakens the "quiet technical atelier" warmth. An evidence-first layout is preserved (narrative labels left, data points right, reading box bottom), but the reading box fill (#eef3ed) and border (#c6d1c4) are green-tinted surfaces with no canonical surface or rule token match. | Re-tint reading box fill toward `surface.panel.subtle` (#EFEDE6) or `evidence.planner.fill` (#E3F0E4) if the green tint is intentional. Re-tint the border toward `rule.soft` (#ECE7DD). |
| P2 | GCS Scientific Figure Pipeline | The semantic spec (figure95-narrative-line-level-trend-20260526.yaml) is present and carries structured data, but the SVG is hand-coded with hardcoded coordinates (not generated from the spec by a compositor). No QA review artifact (no `.review.png`, `.review.pdf`, `.qa.json`) references this trend figure specifically. | Either add a compositor that generates the SVG from the spec, or explicitly label this figure as a spec-informed hand-drawn figure with the pipeline shortfall documented. Run `figure_qa.py` or its equivalent and attach a QA artifact. |
| P3 | GCS Evidence-First Interface Grammar | Narrative line labels use font-size 19px, which matches no canonical size in the hierarchy (canonical sizes are 38/18/17/16/15). The 19px is close to 18px (subtitle) but is a one-off drift. | Use 18px (subtitle) or 16px (data label) consistently. |
| P3 | GCS Warm Evidence Tokens | Surface and rule colors show mild drift from canonical tokens: background #f7f5ef vs `surface.paper` (#F7F4EC); panel #fffdf7 vs `surface.panel` (#FFFEFA); border #cfc7b7 vs `rule.default` (#D8D1C4) or `rule.strong` (#C9BDAA); grid #e5ddcf vs `rule.soft` (#ECE7DD). Each is within two deltas of a canonical match but collectively they add to a slightly-cooler-than-canonical feel. | Align surface and rule hex values to canonical tokens, or add explicit aliases in the figure spec if the drift is intentional. |
| P3 | GCS Scientific Figure Pipeline | The spec does not include `canonical_token` fields on its elements, unlike the Figure 71/72 YAML specs which carry per-element `canonical_token` mappings. Without canonical token references in the spec, token-lint automation cannot verify the SVG against the taxonomy. | Add `canonical_token` fields to the YAML spec for each color-bearing element (background, panel, rules, text levels, narrative line colors). |

## Boundary Check

- Solver/runtime truth remains outside UI/viewer artifacts: yes. The figure visualizes narrative maturity scores, not solver state.
- Generated artifacts are rebuildable from repo sources: partial. The semantic spec exists and contains the source data, but there is no compositor script to regenerate the SVG from the spec. The SVG must be hand-edited when scores change.
- Dense text uses layout-aware composition rather than coordinate-only labels: no. All text is placed via hardcoded x/y coordinates (e.g., `x="86" y="244"`), which is coordinate-only drawing. The figure has 6 narrative labels and 12 data point labels, enough to benefit from layout-aware composition.

## Token Drift Detail

### Text colors: systematic cool-shift

| Element | SVG hex | Nearest canonical | Delta |
| --- | --- | --- | --- |
| Title (line 6) | #243036 | text.primary #181715 | Blue-shifted, lighter |
| Subtitle (line 7) | #5d6468 | text.secondary #5F5B53 | Blue-shifted |
| Phase labels (lines 11-12) | #4d575c | text.secondary #5F5B53 | Blue-shifted |
| Axis ticks (line 14) | #6a6f73 | text.muted #8B867A | Much cooler, darker |
| Narrative labels (line 32) | #253138 | text.primary #181715 | Blue-shifted |
| Data labels (line 76) | #253138 | text.primary #181715 | Blue-shifted |
| Annotation text (lines 96-99) | #566065 | text.muted #8B867A | Much cooler |
| Reading box title (line 103) | #263238 | text.primary #181715 | Blue-shifted |
| Reading box body (line 104) | #465056 | text.secondary #5F5B53 | Blue-shifted |

### Accent colors: no canonical matches

| Element | SVG hex | Closest canonical | Notes |
| --- | --- | --- | --- |
| Teal line/circles | #2d9bb3 | none | No teal in canonical evidence, state, or rigid-set tokens |
| Orange line/circles | #d98c2b | state.warning #B88746 | Warmer and brighter than canonical warning |
| Green line/circles/badge | #789d3e | state.ok #4B8A64 | Much brighter and yellower than canonical ok |
| Purple line/circles | #8f6aa8 | none | No purple in canonical tokens at this saturation |
| Blue line/circles | #4f79c7 | none | No blue in canonical tokens at this saturation |
| Brown line/circles | #b56f53 | rigidSet.palette.05 #C66E4E | Close but not exact; brown is not an evidence token |

## Decision

Conditional fit.

Rationale: Figure 95 has a semantic spec, accessible metadata, and a clear evidence-first layout with good typographic hierarchy. These are genuine strengths. However, three issues prevent a "fit" verdict:

1. **Systematic text color drift.** Every text element uses a cool blue-grey palette instead of the canonical warm-neutral text tokens. This is the most important finding because it touches every visible label in the figure and weakens the Quiet Technical Atelier warmth.

2. **Accent colors lack canonical grounding.** The six narrative-line colors are reasonable as a muted categorical set, but none trace to a defined evidence, state, or rigid-set token. The muted/strong pairs (e.g., #d9ecf0 / #2d9bb3) are a thoughtful pattern, but the specific hex values are not derived from the token taxonomy.

3. **Hand-coded SVG without compositor.** The pipeline expects spec-to-SVG generation for dense figures. This figure has a spec but a hand-placed SVG with hardcoded coordinates. When scores change, the SVG must be manually edited, which risks label misalignment.

The figure is well-mannered and serves its purpose. It is not a violation of the design system, but it does not demonstrate full compliance with the token vocabulary or the production pipeline.

## Commit Boundary

- Recommended commit scope: this review report only, as an example artifact for the Atelier Steward role.
- Files that should not be included: the SVG figure, the YAML spec, the trend report markdown, or any token taxonomy documents.
- Follow-up owner: the figure producer should address the P1 text-color and accent-color findings in a separate figure-refresh task. The figure should be regenerated with canonical tokens before the next narrative-map refresh.

## Role Status

This report counts as one seed example for I003. It does not upgrade the role to practiced by itself. The report applies the convention-fit template to a concrete GCS visual artifact (SVG figure with accompanying YAML spec) and ties every finding to a named convention and specific line numbers or hex codes.
