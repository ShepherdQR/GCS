# Token Lint Gate

Snapshot date: 2026-05-24.

This note records the P5.1 `GCS Visual Integrity Gate` landing for token
discipline across the Python viewer, architecture figure renderers, and
semantic figure specs.

Governing conventions:

- **GCS Warm Evidence Tokens**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**

## Rule

Raw `#RRGGBB` values are allowed only in approved token sources:

- `python/gcs_viz/color_scheme.py`
- `tools/architecture_visualization/figure1.theme.json`

Renderer, viewer, and QA code must consume named tokens or theme keys. Figure
specs must use known canonical token names from
`docs/architecture/79-ui-token-taxonomy.md`.

## Tool

`tools/ui_qa/gcs_token_lint.py` checks three things:

- raw hex values outside approved token-source files;
- string literal references to unknown `GCS_TOKENS`, `GCS_THEME`,
  `STATE_COLORS`, or renderer `COLORS` keys;
- unknown `canonical_token` values in JSON/YAML figure specs.

The tool uses only the Python standard library and is part of the default
agentic quality-gate sequence through:

```text
python.gcs_token_lint
python.gcs_token_lint_tests
```

## Current Scope

Default scanned paths:

- `python/gcs_viz`
- `tools/architecture_visualization`
- `tools/ui_qa`

Default scope intentionally excludes generated assets and long-form docs,
because those may contain exported colors or explanatory examples. Generated
asset quality remains a later P4.4/P5.2/P5.3 concern.

## Acceptance Evidence

- Current repo token lint passes.
- A forced raw-hex fixture fails.
- A forced unknown `GCS_TOKENS` fixture fails.
- A forced unknown figure-spec `canonical_token` fixture fails.
- The default quality-gate command list includes the token lint and its tests.

## Future Gates

P5.1 does not prove visual quality by itself. It is the guardrail that prevents
token drift before later gates add rendered text overflow, overlap, contrast,
and screenshot baseline checks.
