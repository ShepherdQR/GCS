# P6.3 Showcase Figure Pipeline

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**

## Step Result

P6.3 adds a tokenized, layout-aware HTML production path for Figure 72.

The new compositor reads the public showcase scene, enriched P6.2 metadata, the
negative missing-fixed metadata, and the shared warm evidence theme. It outputs:

- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html`

The existing SVG renderer remains a deterministic legacy atlas artifact:

- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.svg`
- `docs/architecture/70-visualization/showcase-scene-report.md`

## Semantic Source

The source of truth for P6.3 is:

- brief: `docs/architecture/88-p6-1-integrated-showcase-brief.md`
- spec: `tools/architecture_visualization/specs/figure72.yaml`
- scene: `fixtures/scene/showcase/integrated_feature_showcase.gcs.json`
- metadata: `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`
- negative metadata:
  `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json`
- compositor: `tools/architecture_visualization/showcase_scene_html_compositor.py`

## Panels

The HTML figure implements the P6.1 panel contract:

| Panel | Evidence token | Source evidence |
| --- | --- | --- |
| Scene Contract | `evidence.domain` | public JSON counts and fixed IDs |
| Constraint Graph | `evidence.graph` | components and constraint/geometry mix |
| Boundary Plan | `evidence.planner` | fixed boundary, planner subproblems, cover contexts |
| Numeric Evidence | `evidence.numeric` | rank, free/frozen variables, residual max |
| Gluing Diagnostics | `evidence.diagnostic` | `gluing.accepted` and post-local diagnostics |
| Negative Variant | `evidence.failure` | missing fixed ID and typed report code |
| Gate Chain | `evidence.boundary` | fixture, viewer, replay, and CLI public gates |

## Visual Integrity

P6.3 extends the P5 source-level visual gates to Figure 72 HTML:

- `gcs_text_overflow.py` now scans Figure 71 and Figure 72 HTML.
- `gcs_overlap_contrast.py` now scans Figure 71 and Figure 72 HTML.
- Figure 72 emits text budgets, layout boxes, and contrast markers.
- The default quality gates run a compositor freshness check with `--check`.

Current local results:

```text
python -B tools\architecture_visualization\showcase_scene_html_compositor.py --check
Figure 72 showcase HTML is up to date.

python -B tools\ui_qa\gcs_text_overflow.py
GCS text overflow checks passed (170 budgets)

python -B tools\ui_qa\gcs_overlap_contrast.py
GCS overlap/contrast checks passed (13 boxes, 90 contrast targets)
```

## Art Direction Judgment

P6.3 is conditionally approved for the P6.4 Figma MCP decision:

- approved: evidence hierarchy is now explicit, source-driven, and layout-aware;
- approved: negative rejection evidence is visible as a first-class panel;
- approved: tokenized colors follow `GCS Warm Evidence Tokens`;
- residual: no browser-rendered Figure 72 PNG/PDF baseline has been promoted
  yet;
- residual: the legacy SVG still exists and should not be mistaken for the
  production path.

The key P6.4 question is now narrow: does Figma MCP add collaboration,
editable-layout, or review value beyond this repo-native HTML pipeline?

## Boundary

P6.3 does not install Figma, add a graph-layout package, or create a browser
screenshot baseline for Figure 72. It creates the production source artifact
needed to judge those choices.
