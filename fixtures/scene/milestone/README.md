# Milestone Scene Fixtures

This directory stores generated public `gcs-0.3` scenes that mark current GCS
solver and catalog capability boundaries. These are durable fixtures, not
scratch exploration output. Each entry has companion metadata with generator
provenance, topology evidence, replay-history evidence, digests, and current
solver status.

Not every milestone scene is a green CLI smoke. A milestone may be accepted,
accepted with warnings, or intentionally retained as a documented current
solver boundary. Use the manifest and metadata as the source of truth for the
current expected status.

Scratch candidates remain under `.codex_scene_generation_store/` and should not
be promoted here unless a scene-generation task records why the fixture has
long-term verification or demonstration value.

| Fixture | Class | Current status | Accepted | Geometry / constraints |
| --- | --- | --- | --- | ---: |
| `milestone_20g40c_20260524` | current-solver milestone | `AcceptedWithWarnings` | `True` | 20 / 40 |
| `all_types_10g18c_20260524` | catalog-coverage milestone | `Failed` | `False` | 10 / 18 |
