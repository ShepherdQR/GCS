# Figure Renderer Token Usage

Snapshot date: 2026-05-24.

This note completes the usage-note part of P2.4. It defines how HTML/CSS
figure renderers consume `GCS Warm Evidence Tokens` without losing compatibility
with the existing short keys in `figure1.theme.json`.

Governing conventions:

- **GCS Warm Evidence Tokens**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**

## Canonical Names

New figure specs and renderers should name tokens with the dot paths from
`docs/architecture/79-ui-token-taxonomy.md`.

Preferred examples:

- `surface.paper`
- `surface.canvas`
- `text.primary`
- `rule.default`
- `state.focus`
- `evidence.domain.fill`
- `evidence.numeric.stroke`
- `geometry.point.color`
- `constraint.emphasis.color`

Existing figure specs may keep short evidence names such as `domain`,
`numeric`, `planner`, `diagnostic`, `failure`, and `boundary`. Renderers should
translate those names to `evidence.*` before producing CSS or SVG.

## CSS Custom Properties

HTML renderers should expose canonical CSS custom properties with this pattern:

- `--gcs-surface-paper`
- `--gcs-surface-panel`
- `--gcs-surface-canvas`
- `--gcs-text-primary`
- `--gcs-text-secondary`
- `--gcs-rule-default`
- `--gcs-state-focus`
- `--gcs-evidence-domain-fill`
- `--gcs-evidence-domain-stroke`

Compatibility aliases such as `--paper`, `--panel`, `--ink`, and `--rule` may
remain inside older renderers, but they should point to the canonical
`--gcs-*` variables rather than raw hex values.

## Panel Tokens

Panel-level evidence color should be injected through canonical local variables:

- `--gcs-token-fill`
- `--gcs-token-stroke`

Older class rules may continue to read `--token-fill` and `--token-stroke` as
aliases during the transition.

## Renderer Rules

1. Load `figure1.theme.json` as the current editorial seed.
2. Add canonical aliases after reading the theme.
3. Use canonical token names in generated CSS and inline SVG attributes.
4. Keep short-key compatibility only at the renderer boundary.
5. Do not introduce one-off hex values in renderer code.
6. Run structural QA after rendering and browser screenshot QA before a figure
   is declared final.

## Current Landing

`tools/architecture_visualization/figure71_html_compositor.py` now canonicalizes
theme colors, emits `--gcs-*` CSS custom properties, keeps old CSS aliases, and
translates short evidence token names to canonical `evidence.*` names.
