# UI Token Taxonomy

Snapshot date: 2026-05-24.

This document completes P2.2 of the UI design system execution plan. It defines
the canonical `GCS Warm Evidence Tokens` names that future GUI, figure, report,
and QA work should use.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**

## Naming Rule

Canonical token names use lowercase dot paths:

`family.role.variant.state`

Examples:

- `surface.paper`
- `text.primary`
- `rule.soft`
- `evidence.domain.fill`
- `state.focus.active`
- `constraint.type.distance.color`
- `viewer.geometry.point.marker`

The canonical name describes meaning, not the current implementation file. A
Python constant, JSON key, CSS variable, or Matplotlib style may alias the same
canonical token, but new design work should name the canonical token first.

## Source Policy

`tools/architecture_visualization/figure1.theme.json` remains the editorial
seed for warmth, evidence colors, typography, radii, and stroke widths.
`python/gcs_viz/color_scheme.py` remains the Python viewer mirror until P2.3
updates it.

When the two disagree by small warm-neutral drift, P2.2 names the canonical
target and records the current Python alias. P2.3 may then adopt the canonical
value or preserve a compatibility alias if a visual QA pass shows the viewer
needs the existing value.

## Core Surface Tokens

| Canonical token | Canonical value | Figure seed | Current Python alias | Meaning |
| --- | --- | --- | --- | --- |
| `surface.paper` | `#F7F4EC` | `paper` | `bg_window`, `bg_primary` (`#F7F3EA`) | Overall app/report/page ground. |
| `surface.panel` | `#FFFEFA` | `panel` | `bg_table` (`#FFFCF7`) | Primary readable panel or table surface. |
| `surface.panel.subtle` | `#EFEDE6` | `boundary` | `bg_panel` (`#EFE8DC`) | Quiet grouping surface. |
| `surface.panel.muted` | `#E8DFD0` | none | `bg_panel_alt` | Secondary control rail or status surface. |
| `surface.canvas` | `#FBFAF5` | `plot` | `bg_canvas` (`#FAF9F5`) | Matplotlib plot or visual model canvas. |
| `surface.table.selected` | `#EAD9CF` | none | `bg_table_selected` | Selected row, pressed quiet control, or local focus fill. |
| `surface.track` | `#EFEBE2` | `bar_track` | none | Progress, magnitude, or rail track. |

## Text Tokens

| Canonical token | Canonical value | Figure seed | Current Python alias | Meaning |
| --- | --- | --- | --- | --- |
| `text.primary` | `#181715` | `ink` | `text_primary` (`#141413`) | Primary labels, titles, and high-confidence facts. |
| `text.secondary` | `#5F5B53` | `muted` | `text_secondary` (`#635D53`) | Body labels and secondary table content. |
| `text.muted` | `#8B867A` | `quiet` | `text_muted`, `axis` (`#8A8178`) | Low-emphasis labels, axes, and inactive metadata. |
| `text.inverse` | `#FAF9F5` | none | `text_on_accent` | Text on accent or strong state fills. |

## Rule Tokens

| Canonical token | Canonical value | Figure seed | Current Python alias | Meaning |
| --- | --- | --- | --- | --- |
| `rule.default` | `#D8D1C4` | `rule` | `border` (`#DDD5C7`) | Default panel/table border. |
| `rule.soft` | `#ECE7DD` | `rule_soft` | `grid` (`#E6DED1`) | Internal dividers and quiet plot grid. |
| `rule.strong` | `#C9BDAA` | none | `border_strong` | Stronger control or table boundary. |
| `rule.axis` | `#8B867A` | `quiet` | `axis` (`#8A8178`) | Plot axes and tick text. |

## Evidence Tokens

These tokens carry architecture and solver evidence semantics. They should
remain stable across architecture figures, GUI overlays, reports, and
showcase visuals.

| Canonical token | Fill | Stroke | Figure seed | Meaning |
| --- | --- | --- | --- | --- |
| `evidence.domain` | `#E7EDF8` | `#435F8C` | `domain`, `domain_stroke` | Durable model truth, kernel contracts, geometry ownership. |
| `evidence.graph` | `#EFE7F3` | `#765D87` | `graph`, `graph_stroke` | Incidence, body graph, decomposition graph, structural evidence. |
| `evidence.planner` | `#E3F0E4` | `#477861` | `planner`, `planner_stroke` | Covers, boundaries, gluing, SolveDAG planning. |
| `evidence.numeric` | `#EDF2DF` | `#5E7D43` | `numeric`, `numeric_stroke` | Residuals, rank, local solve, numeric engine evidence. |
| `evidence.diagnostic` | `#F6E7CF` | `#A36B32` | `diagnostic`, `diagnostic_stroke` | Diagnostic decisions, conflict/redundancy reports, public gates. |
| `evidence.failure` | `#F3DDD7` | `#A94C43` | `failure`, `failure_stroke` | Rejection, obstruction, invalid command, failed quality gate. |
| `evidence.boundary` | `#EFEDE6` | `#777166` | `boundary`, `boundary_stroke` | IO/viewer/adapter boundary and read-only projection. |

When a surface needs individual fill and stroke tokens, append `.fill` or
`.stroke`, for example `evidence.numeric.fill` and `evidence.numeric.stroke`.

## State Tokens

| Canonical token | Canonical value | Current alias | Meaning |
| --- | --- | --- | --- |
| `state.focus` | `#C8643F` | figure `accent`; Python `accent` (`#D97757`) | Selected object, current evidence, active replay moment. |
| `state.focus.active` | `#B85F45` | Python `accent_active` | Pressed primary control or active focus edge. |
| `state.ok` | `#4B8A64` | figure `ok`; Python `success` (`#788C5D`) | Satisfied, accepted, solved, or quality-gate pass. |
| `state.info` | `#6A8FB5` | Python `info` | Informational status that is not solver evidence. |
| `state.warning` | `#B88746` | Python `warning`; rigid-set swatch | Under-constrained, pending risk, or attention without failure. |
| `state.error` | `#B8574E` | Python `error`; constraint type 0 | Invalid, over-constrained, failed, or rejected UI state. |
| `state.pending` | `#8B867A` | figure `quiet`; Python `text_muted` | Pending, inactive, not yet promoted. |
| `state.replay.current` | `#C8643F` | figure `accent`; Python `accent` | Current replay step or history frame. |
| `state.violation` | `#A94C43` | `evidence.failure.stroke` | Constraint violation or obstruction evidence. |

State must not rely on color alone. Use labels, line style, marker shape, icon,
or table status text when state is user-visible.

## Geometry And Constraint Tokens

| Canonical token | Value | Current source | Meaning |
| --- | --- | --- | --- |
| `geometry.point.color` | `#334C78` | figure `point` | Point glyph and point evidence accent. |
| `geometry.point.marker` | `o` | `GEOMETRY_MARKERS` | Matplotlib point marker. |
| `geometry.line.marker` | `D` | `GEOMETRY_MARKERS` | Matplotlib line geometry marker. |
| `geometry.plane.marker` | `s` | `GEOMETRY_MARKERS` | Matplotlib plane geometry marker. |
| `geometry.point.nodeSize` | `300` | `GEOMETRY_NODE_SIZES` | Graph-view point node size. |
| `geometry.line.nodeSize` | `390` | `GEOMETRY_NODE_SIZES` | Graph-view line node size. |
| `geometry.plane.nodeSize` | `480` | `GEOMETRY_NODE_SIZES` | Graph-view plane node size. |
| `constraint.default.color` | `#8B867A` | Python `constraint_default` (`#8A8178`) | Constraint fallback when type is unknown. |
| `constraint.emphasis.color` | `#B97834` | figure `constraint` | Figure-level emphasized constraint. |

## Constraint Type Tokens

| Canonical token | Color | Matplotlib style | Graph style | Current type id |
| --- | --- | --- | --- | --- |
| `constraint.type.coincident` | `#B8574E` | `dotted` | `dotted` | `0` |
| `constraint.type.parallel` | `#788C5D` | `dashed` | `dashed` | `1` |
| `constraint.type.perpendicular` | `#66738F` | `dashdot` | `dashdot` | `2` |
| `constraint.type.distance` | `#B88746` | `solid` | `solid` | `3` |
| `constraint.type.angle` | `#7C617B` | `(0, (3, 2))` | `dashed` | `4` |

Constraint meaning should be encoded primarily by line style and marker shape.
Color is secondary evidence and must remain muted.

## Rigid-Set Palette

Rigid sets use a muted categorical palette, not a rainbow. These names make the
existing Python swatches portable to figures and reports.

| Canonical token | Value |
| --- | --- |
| `rigidSet.palette.01` | `#587C7A` |
| `rigidSet.palette.02` | `#B88746` |
| `rigidSet.palette.03` | `#7C617B` |
| `rigidSet.palette.04` | `#788C5D` |
| `rigidSet.palette.05` | `#C66E4E` |
| `rigidSet.palette.06` | `#66738F` |
| `rigidSet.palette.07` | `#8A8178` |
| `rigidSet.palette.08` | `#9A7A5F` |
| `rigidSet.palette.09` | `#5F7D9A` |
| `rigidSet.palette.10` | `#A86E73` |
| `rigidSet.palette.11` | `#6F8B72` |
| `rigidSet.palette.12` | `#9B8A5F` |
| `rigidSet.palette.13` | `#6E6A86` |
| `rigidSet.palette.14` | `#A06F4F` |
| `rigidSet.palette.15` | `#557D8A` |

## Figure And Viewer Structure Tokens

| Canonical token | Value | Source | Meaning |
| --- | --- | --- | --- |
| `figure.font.sans` | `Anthropic Sans, Inter, Segoe UI, Arial, sans-serif` | `figure1.theme.json` | Figure and HTML compositor sans stack. |
| `figure.font.serif` | `Anthropic Serif, Georgia, Cambria, Times New Roman, serif` | `figure1.theme.json` | Figure editorial title stack. |
| `figure.radius.panel` | `8` | `figure1.theme.json` | Panel radius; maximum for ordinary cards/panels. |
| `figure.radius.card` | `6` | `figure1.theme.json` | Small evidence fact card radius. |
| `figure.radius.small` | `4` | `figure1.theme.json` | Small chip or glyph radius. |
| `figure.radius.pill` | `12` | `figure1.theme.json` | Compact status pill radius. |
| `figure.stroke.default` | `1.1` | `figure1.theme.json` | Default SVG/figure stroke width. |
| `figure.stroke.grid` | `1.0` | `figure1.theme.json` | Figure grid stroke width. |
| `figure.stroke.arrow` | `1.4` | `figure1.theme.json` | Flow/evidence arrow stroke width. |
| `figure.stroke.constraint` | `2.4` | `figure1.theme.json` | Emphasized constraint stroke width. |

## Alias Rules For P2.3

P2.3 should update `python/gcs_viz/color_scheme.py` by introducing a canonical
token layer and keeping backwards-compatible aliases:

- `GCS_TOKENS`: canonical dot-path names grouped by family;
- `RIGID_SET_COLORS`: generated from `rigidSet.palette.*`;
- `CONSTRAINT_COLORS`: generated from `constraint.type.*.color`;
- `GCS_THEME`: compatibility aliases for existing viewer code;
- optional `GEOMETRY_STYLE_TOKENS` and `CONSTRAINT_STYLE_TOKENS` if marker and
  line-style names move out of `visualizer.py`.

P2.3 must not move solver truth into the viewer. It is a presentation-layer
mirror only.

## Alias Rules For P2.4

P2.4 should align figure renderer and compositor token access:

- JSON theme keys may remain short for current renderers, but new specs should
  reference canonical token names.
- Renderer fallback dictionaries should either be generated from canonical
  tokens or clearly marked as compatibility fallbacks.
- CSS custom properties should use kebab-case equivalents, for example
  `--gcs-surface-paper` and `--gcs-evidence-domain-fill`.

## Acceptance Rule

A future UI or figure change passes P2 token review only when it names the
canonical token it uses or explains why a new token is needed.
