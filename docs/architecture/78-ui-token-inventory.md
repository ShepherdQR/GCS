# UI Token Inventory

Snapshot date: 2026-05-24.

This inventory completes P2.1 of the UI design system execution plan. It maps
the current GCS color, state, and figure-theme sources before P2.2 defines the
canonical `GCS Warm Evidence Tokens` vocabulary.

Governing conventions:

- **GCS Quiet Technical Atelier**
- **GCS Warm Evidence Tokens**
- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**

## Scope

This pass inventories the surfaces that currently carry visual meaning:

- Python viewer theme and semantic palettes;
- Matplotlib canvas, axes, markers, line styles, and legends;
- Tkinter/ttk panels, tables, command controls, and status surfaces;
- architecture figure themes and renderer fallback dictionaries;
- HTML figure compositor theme use;
- terminal/Rich styles that still expose older visual choices.

No runtime behavior changes are made in this step.

## Current Sources

| Source | Role | Token state | Notes |
| --- | --- | --- | --- |
| `tools/architecture_visualization/figure1.theme.json` | Figure/editorial theme baseline. | Structured JSON theme. | Defines `claude-warm-editorial`, warm paper surfaces, semantic module colors, typography, radii, and stroke widths. |
| `tools/architecture_visualization/render_gcs_figure1.py` | Figure 1 SVG renderer. | Duplicated fallback dictionary plus direct token use. | Repeats many `figure1.theme.json` colors so the renderer can run without the JSON file. Includes at least one local one-off fill color that should become a named token. |
| `tools/architecture_visualization/render_gcs_figure71.py` | Figure 71 prototype SVG renderer. | Duplicated fallback dictionary plus dense direct token use. | Useful as historical prototype, but not the target dense-figure paradigm. |
| `tools/architecture_visualization/figure71_html_compositor.py` | Figure 71 HTML/CSS compositor. | Uses theme data with a fallback dictionary. | This is closer to the desired layout-aware pipeline, but fallback tokens still need naming alignment. |
| `python/gcs_viz/color_scheme.py` | Python viewer color source. | Central Python constants. | Defines muted rigid-set swatches, constraint colors, and `GCS_THEME` UI roles such as background, text, accent, info, success, warning, and error. |
| `python/gcs_viz/visualizer.py` | Matplotlib scene, graph, and evidence rendering. | Consumes `GCS_THEME`, rigid-set colors, constraint colors, marker styles, and line styles. | Matplotlib panes, grids, labels, legends, selected objects, graph view, and replay/focus states already depend on shared Python theme values. |
| `python/gcs_viz/platform_gui.py` | Tkinter/ttk application chrome. | Consumes `GCS_THEME`. | Applies warm surfaces and text colors to root, frames, treeviews, command controls, status surfaces, and log views. |
| `python/gcs_viz/platform.py` | CLI/Rich terminal surface. | Mixed theme strings and older hard-coded terminal style. | Still includes a dark terminal style (`white on #16213e`) that is outside the warm atelier language and should be migrated or explicitly scoped. |

## Current Token Families

### Figure/editorial

`figure1.theme.json` currently defines these practical families:

- surface and paper: `paper`, `panel`, `surface`, `plot`, `white`;
- text: `ink`, `muted`, `quiet`;
- rules: `rule`, `rule_soft`;
- semantic evidence: `domain`, `graph`, `planner`, `numeric`,
  `diagnostic`, `failure`, `boundary`;
- strokes for semantic evidence: `*_stroke`;
- geometry and constraint accents: `point`, `constraint`;
- state and focus: `ok`, `accent`;
- auxiliary figure color: `cool_domain`.

The theme also stores typography, border radii, stroke widths, panel metrics,
and shadow opacity. These should remain part of the token discussion even when
P2.2 focuses first on colors and state semantics.

### Python viewer

`python/gcs_viz/color_scheme.py` currently defines:

- muted categorical rigid-set colors in `RIGID_SET_COLORS`;
- constraint type colors in `CONSTRAINT_COLORS`;
- UI roles in `GCS_THEME`, including `bg_window`, `bg_primary`, `bg_panel`,
  `bg_panel_alt`, `bg_canvas`, `bg_table`, `bg_table_selected`,
  `text_primary`, `text_secondary`, `text_muted`, `text_on_accent`, `accent`,
  `accent_active`, `info`, `success`, `warning`, `error`, `border`,
  `border_strong`, `grid`, `axis`, and `constraint_default`.

The Python viewer is already warm and restrained, but its names are UI-role
oriented while the figure theme names are evidence-semantics oriented.

### Matplotlib semantics

`python/gcs_viz/visualizer.py` layers visual semantics on top of the Python
theme:

- geometry markers in `GEOMETRY_MARKERS`;
- constraint line styles in `CONSTRAINT_LINE_STYLES`;
- graph-view line styles in `CONSTRAINT_GRAPH_LINE_STYLES`;
- selected geometry focus rings using `GCS_THEME["accent"]`;
- graph and 3D axis colors from `bg_canvas`, `grid`, `axis`, and text tokens;
- legend and summary surfaces using `bg_panel`, `border`, and text tokens.

This confirms that P2.2 must include non-color token categories for marker,
line, state, and evidence roles, not only hex names.

### Tkinter/ttk semantics

`python/gcs_viz/platform_gui.py` uses the Python theme for:

- application backgrounds and panels;
- object tables and selection;
- command and action controls;
- status and log surfaces;
- text hierarchy and border tone.

The code already has one central theme import, so P2.3 should be able to mirror
canonical tokens into this file without changing interaction logic.

## Gaps And Risks

1. Figure and viewer surfaces use compatible taste but different naming axes:
   evidence-domain names in figures, UI-role names in Python.
2. Renderer fallback dictionaries duplicate `figure1.theme.json`, increasing
   the chance of quiet drift.
3. The figure theme uses lowercase hex values while the Python viewer uses
   uppercase hex values. This is harmless visually but noisy in review and
   generated diffs.
4. Rigid-set and constraint palettes exist only as Python viewer constants.
   They need explicit design-system names before being reused in figures or
   reports.
5. Terminal/Rich styles still contain an older dark style that does not match
   `GCS Quiet Technical Atelier`.
6. At least one renderer one-off color should become a named token or be
   removed when the renderer is demoted.
7. P2.3 should avoid changing solver, runtime, IO, or viewer-state ownership.
   Token mirroring is a presentation-layer change only.

## P2.2 Inputs

P2.2 should define a canonical token table before code changes. The table
should cover at least:

- `surface.*`: paper, panel, canvas, table, selected table row;
- `text.*`: primary, secondary, muted, text on accent;
- `rule.*`: default, soft, strong, grid, axis;
- `evidence.*`: domain, graph, planner, numeric, diagnostic, failure,
  boundary;
- `evidence.*.stroke`: stroke variants for the evidence families;
- `state.*`: focus, focus active, ok, info, warning, error, replay current,
  violated, solved, pending;
- `geometry.*`: point, line, circle, distance, angle, incidence marker roles;
- `constraint.*`: default, type palette, line style roles;
- `rigidSet.palette.*`: muted categorical swatches;
- `figure.*`: shadow, radius, stroke width, panel padding, typography roles;
- `viewer.*`: Matplotlib marker and line-style aliases where color alone is
  insufficient.

## Recommended Direction

Use `figure1.theme.json` as the editorial seed, but do not make raw figure token
names the only canonical vocabulary. P2.2 should create a cross-surface mapping
where evidence semantics and UI roles both point to the same stable token
values.

After P2.2, P2.3 can update `python/gcs_viz/color_scheme.py` as the Python
mirror of those names. P2.4 can then align the HTML/CSS figure compositor and
document how future figure renderers consume the same tokens.
