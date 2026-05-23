# Generated GCS Model Library

This directory contains durable public `gcs-0.3` scene models promoted from the scene-space explorer. Each model has a matching metadata package under `metadata/` with provenance, validation gates, topology policy, and digests.

Source batch: `generated_complex_constraints_20260524`.
Source scratch store: `.codex_scene_generation_store`.

| Fixture | Geometries | Constraints | Rigid sets | Topology | Gates |
| --- | ---: | ---: | ---: | --- | --- |
| [codex_complex10_20260524_run00_c0000.gcs.json](codex_complex10_20260524_run00_c0000.gcs.json) | 14 | 32 | 4 | ear_decomposition, v=14, extra=7, layout=circular | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run01_c0000.gcs.json](codex_complex10_20260524_run01_c0000.gcs.json) | 14 | 31 | 4 | ear_decomposition, v=14, extra=6, layout=circular | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run02_c0000.gcs.json](codex_complex10_20260524_run02_c0000.gcs.json) | 14 | 32 | 5 | ear_decomposition, v=14, extra=7, layout=circular | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run03_c0000.gcs.json](codex_complex10_20260524_run03_c0000.gcs.json) | 14 | 33 | 4 | ear_decomposition, v=14, extra=8, layout=grid | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run04_c0000.gcs.json](codex_complex10_20260524_run04_c0000.gcs.json) | 14 | 21 | 5 | cycle_plus_chords, v=14, extra=7, layout=circular | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run05_c0000.gcs.json](codex_complex10_20260524_run05_c0000.gcs.json) | 14 | 33 | 4 | ear_decomposition, v=14, extra=8, layout=grid | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run06_c0000.gcs.json](codex_complex10_20260524_run06_c0000.gcs.json) | 14 | 20 | 5 | cycle_plus_chords, v=14, extra=6, layout=random | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run07_c0000.gcs.json](codex_complex10_20260524_run07_c0000.gcs.json) | 10 | 18 | 4 | cycle_plus_chords, v=10, extra=8, layout=random | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run08_c0000.gcs.json](codex_complex10_20260524_run08_c0000.gcs.json) | 10 | 18 | 5 | cycle_plus_chords, v=10, extra=8, layout=circular | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |
| [codex_complex10_20260524_run09_c0000.gcs.json](codex_complex10_20260524_run09_c0000.gcs.json) | 14 | 20 | 5 | cycle_plus_chords, v=14, extra=6, layout=grid | local_schema_validation=passed; geometry_primal_projection=passed; geometry_primal_biconnectivity=passed; canonical_serialization=passed |

Update policy: add future generated models through `promote_candidate`, keep the public `.gcs.json`, refresh `manifest.json`, and store the promotion package as `metadata/<fixture_id>.metadata.json`.
