# P6.2 Showcase Fixture Evidence

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Evidence-First Interface Grammar**
- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Warm Evidence Tokens**

## Step Result

P6.2 promotes the integrated showcase fixture metadata into a renderer-consumable
evidence contract.

The positive fixture now records the P6.1 brief path, required panels,
canonical evidence tokens, expected rank/residual reports, gluing evidence,
diagnostics, replay-boundary gates, and public quality gates. The negative
fixture records the rejection panel and stable missing-fixed report code.

## Evidence Bundle

| Evidence | Positive fixture expectation |
| --- | --- |
| Public scene | `fixtures/scene/showcase/integrated_feature_showcase.gcs.json` |
| Brief | `docs/architecture/88-p6-1-integrated-showcase-brief.md` |
| Rigid sets/geometries/constraints | `6 / 6 / 4` |
| Fixed geometry IDs | `[0]` |
| Planner subproblems | `2` |
| Cover contexts | `3` |
| Local numeric reports | `2` |
| Rank reports | rank `2` for both local reports |
| Residual reports | `2`, max residual `0.0` |
| Gluing | `gluing.accepted` |
| Diagnostics | `2` post-local diagnostics warnings |
| Replay boundary | runtime trace remains report evidence, not scene construction history |
| CLI status | `AcceptedWithWarnings` |

Negative evidence:

| Evidence | Negative fixture expectation |
| --- | --- |
| Fixture | `integrated_feature_showcase_missing_fixed.gcs.json` |
| Required panel | `negative_variant` |
| Token | `evidence.failure` |
| Missing fixed IDs | `[999]` |
| Report code | `kernel.solve_intent_missing_fixed_entity` |

## Executable Gate

Run:

```bat
python -B tools\architecture_visualization\showcase_fixture_evidence.py
```

The checker validates:

- manifest entries point to existing model and metadata files;
- metadata points back to the manifest model path;
- the P6.1 brief exists;
- positive fixture scene counts match metadata;
- required panels and canonical tokens are present;
- rank/residual/gluing/diagnostic/replay expectations are present;
- negative fixture report code and missing fixed IDs are stable.

The checker and its tests are part of the default `run-quality-gates` sequence.

## Public Gate Coverage

P6.2 keeps the existing solver/report public gates as the authority for runtime
behavior:

- `ctest.public_evidence_chain`
- `cli.showcase_scene`
- `ViewerBridgeContract.ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence`
- `IoAdaptersContract.ShowcaseJsonSceneCarriesSolveIntentBehavior`
- `IoAdaptersContract.RejectsShowcaseSceneWithMissingFixedEntity`
- `SessionRuntimeContract.ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory`
- `ViewerBridgeContract.RuntimeHistoryFrameProjectsAsReportEvidenceOnly`

## Boundary

The fixture metadata is an evidence contract, not a second solver. It records
what the public scene is expected to demonstrate, while CTest and CLI gates
remain responsible for proving actual runtime behavior.

P6.3 should consume this enriched metadata when producing the showcase figure.
