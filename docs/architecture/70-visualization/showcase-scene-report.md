# Integrated Showcase Scene Report

Source scene: `fixtures/scene/showcase/integrated_feature_showcase.gcs.json`

Metadata: `fixtures/scene/showcase/integrated_feature_showcase.metadata.json`

Generated figure: `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.svg`

## Public Evidence

| Evidence | Value |
| --- | --- |
| Schema | `gcs-0.3` |
| Rigid sets | `6` |
| Geometries | `6` |
| Constraints | `4` |
| Fixed geometry IDs | `[0]` |
| Planner subproblems | `2` |
| Numeric reports | `2` |
| Solve status | `AcceptedWithWarnings` |

## Negative Variant

| Evidence | Value |
| --- | --- |
| Metadata | `fixtures/scene/showcase/integrated_feature_showcase_missing_fixed.metadata.json` |
| Expected report code | `kernel.solve_intent_missing_fixed_entity` |
| Missing fixed geometry IDs | `[999]` |

## Regeneration

```bat
python tools\architecture_visualization\render_showcase_scene.py
```
