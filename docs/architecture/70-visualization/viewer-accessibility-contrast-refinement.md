# Viewer Accessibility And Contrast Refinement

Status: complete
Date: 2026-05-26

Governing conventions:

- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Visual Integrity Gate**

## Result

Viewer state colors are now split by use:

- `STATE_COLORS` remains the graphic accent palette for focus rings,
  constraint overlays, halos, and plotted evidence.
- `STATE_TEXT_COLORS` is the small-text palette for status labels, logs, solve
  summaries, DOF state, and replay rail state.

This keeps warning, success, error, pending, and replay state text readable on
the warm viewer surfaces without changing the graphic evidence palette.

## Graph Node Labels

The graph renderer now chooses each geometry node label color from
`text_node_light` or `text_node_dark` by contrast against the node's rigid-set
fill. This avoids a single one-size text color failing on mid-tone rigid-set
palette entries.

## Legacy Inspector Path

The old stacked left-panel builder remains named as legacy-unused and outside
the active GUI builder set. The active inspector path is still
`_build_inspector_panel` plus `_build_right_panel`; UI QA continues to inspect
active command labels only in those builders.

## Acceptance Evidence

- Small state text has contrast-aware tokens.
- Dynamic graph-node label contrast is checked by UI QA.
- The renderer still consumes supplied projection/focus state only; it does not
  infer solver truth.
