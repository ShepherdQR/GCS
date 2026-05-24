# Integrated Showcase Scene Fixtures

This directory contains durable scene-facing showcase fixtures promoted from
the Step 41 C++ contract-tool model.

| Fixture | Purpose | Expected result |
| --- | --- | --- |
| `integrated_feature_showcase.gcs.json` | Positive public demo scene with fixed-boundary solve intent. | Loads and solves through the CLI with accepted warnings. |
| `integrated_feature_showcase_missing_fixed.gcs.json` | Negative behavior-intent variant with a missing fixed geometry ID. | Loader rejects the scene with `kernel.solve_intent_missing_fixed_entity`. |

The JSON `behavior` object is the source of truth for scene-facing solve
intent. Companion metadata records provenance and expected evidence, but does
not carry solver behavior by itself.
