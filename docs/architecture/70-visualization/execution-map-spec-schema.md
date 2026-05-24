# Execution Map Spec Schema

Snapshot date: 2026-05-24.

This note completes the documentation part of P4.1. It defines the first stable
schema contract for GCS execution-map figure specs.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Warm Evidence Tokens**
- **GCS Visual Integrity Gate**

## Schema

Current schema version:

`gcs.execution_map.v1`

Required top-level fields:

- `id`
- `schema_version`
- `title`
- `subtitle`
- `source_report` or `source_reports`
- `expected_step_range`
- `token_taxonomy`
- `theme`
- `exports`
- `quality`
- `arcs`

Required arc fields:

- `id`
- `title`
- `range`
- `token`
- `canonical_token`
- `claim`
- `panel_type`

## Token Rule

`token` may keep the short compatibility key used by older figure specs, such
as `domain`, `numeric`, or `diagnostic`.

`canonical_token` must use a dot-path evidence token from
`79-ui-token-taxonomy.md`, such as:

- `evidence.domain`
- `evidence.graph`
- `evidence.planner`
- `evidence.numeric`
- `evidence.diagnostic`
- `evidence.failure`
- `evidence.boundary`

Renderers must prefer `canonical_token` when it exists and keep `token` only as
a compatibility boundary.

## Current Landing

`tools/architecture_visualization/specs/figure71.yaml` now declares
`schema_version`, `expected_step_range`, `token_taxonomy`, and per-arc
`canonical_token` fields. `figure_qa.py` checks the schema version and
canonical token coverage.
