# SVG Editing Workflow

Research snapshot: 2026-05-24.

This workflow keeps Figure 1 reproducible while making the visual surface
editable in a real SVG editor. The goal is to let architecture evidence stay
generated from GCS fixtures, while color, typography, spacing, and selected
geometry can be adjusted without editing Python drawing code.

## Source Hierarchy

Figure 1 has four layers, ordered from most durable to most editorial:

| Layer | File | Owner | Purpose |
| --- | --- | --- | --- |
| Structural source | `docs/architecture/70-visualization/gcs-architecture-atlas.md` | architecture steward | Module boundaries, runtime flow, local-to-global semantics. |
| Fixture evidence | `fixtures/scene/saved/triangle_003_graph.json` | contract / scene tools | Stable example used to compute geometry, residuals, and rank evidence. |
| Design controls | `tools/architecture_visualization/figure1.theme.json` and `tools/architecture_visualization/figure1.layout.json` | human designer and Codex | Palette, fonts, radii, panel positions, and key box geometry. |
| Editorial artifact | `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.svg` | generator | The committed SVG shown in docs and README. |
| Review artifacts | `docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.inkscape.svg`, `figure1-gcs-local-to-global-V1.svg`, `figure1-gcs-local-to-global-V2.svg` | architecture steward | Tracked comparison snapshots, not the canonical rebuild target. |

The Python renderer is not the design surface. It is the deterministic bridge
between fixture evidence, architecture vocabulary, design controls, and SVG.

## Tool Choice

Use Inkscape as the primary local editor for the committed SVG. Inkscape edits
SVG natively, preserves normal SVG structure, and has command-line support for
query/export workflows. Figma can still be used for moodboards or exploratory
composition, but it should not become the canonical source for this figure
because SVG import/export can alter text, markers, IDs, and custom metadata.

## Round-Trip Contract

The generated SVG contains `id` and `data-layout-key` attributes on the
elements that are intended to round-trip through Inkscape. The first supported
round-trip covers:

- top-level panel group positions;
- panel background and plot rectangles;
- geometry evidence card geometry;
- residual/rank chart and rank card geometry;
- topos columns, gluing report box, and contract dictionary pills;
- pipeline and legend panel sizing through layout tokens.

Text content remains generated from architecture vocabulary and fixture
evidence. If a label changes meaning, update the renderer or architecture doc,
not only the SVG.

## Standard Workflow

1. Rebuild from source:

   ```powershell
   $env:PYTHONDONTWRITEBYTECODE='1'
   python tools\architecture_visualization\render_gcs_figure1.py --fixture fixtures\scene\saved\triangle_003_graph.json --out-dir docs\architecture\70-visualization\assets
   ```

2. Open the generated SVG in Inkscape:

   ```powershell
   inkscape docs\architecture\70-visualization\assets\figure1-gcs-local-to-global.svg
   ```

3. Move or resize elements that have stable IDs. Avoid ungrouping the panel
   groups unless the layout key is preserved.

4. Save the edited copy as a scratch file, for example:

   ```text
   docs/architecture/70-visualization/assets/figure1-gcs-local-to-global.inkscape.svg
   ```

5. Sync supported geometry back into layout tokens:

   ```powershell
   python tools\architecture_visualization\sync_inkscape_layout.py --svg docs\architecture\70-visualization\assets\figure1-gcs-local-to-global.inkscape.svg --layout tools\architecture_visualization\figure1.layout.json
   ```

6. Rebuild the official SVG from tokens:

   ```powershell
   python tools\architecture_visualization\render_gcs_figure1.py --fixture fixtures\scene\saved\triangle_003_graph.json --out-dir docs\architecture\70-visualization\assets
   ```

7. Review the official SVG, not the scratch file. Commit the JSON controls,
   renderer changes if any, and regenerated official assets.

## Editing Rules

- Prefer changing `figure1.theme.json` for color, typography, stroke, and radius.
- Prefer changing `figure1.layout.json` for position, size, and spacing.
- Use Inkscape for visual discovery, then sync back to JSON before committing.
- Keep generated evidence tied to the fixture. Do not manually edit residuals,
  ranks, IDs, or constraint counts inside the SVG.
- Keep architecture semantics in the atlas and renderer. Do not create an
  attractive diagram that contradicts dependency direction or runtime contracts.
- Do not commit new scratch `*.inkscape.svg` files unless a future design
  review explicitly needs them as source evidence. The existing tracked
  Inkscape and V1/V2 SVG files are review artifacts, not canonical outputs.

## Acceptance Checklist

- The official SVG rebuilds from the fixture without manual edits.
- The official SVG uses the warm editorial theme.
- Text sits inside its containing rounded rectangles at desktop and README scale.
- Panel labels `a` through `f` remain visible and ordered.
- The topos panel still maps mathematical language to concrete GCS contracts.
- The rank card distinguishes full variables, free columns, frozen columns, and
  nullity.
- The SVG opens in a browser and Inkscape without missing markers or fonts.

## Future Extensions

- Add a visual diff step that renders the SVG to PNG before and after token
  changes.
- Extend the sync script to read text coordinates if manual label positioning
  becomes frequent.
- Add theme variants only when they encode a real documentation need; avoid
  parallel aesthetic forks of the same architecture truth.
