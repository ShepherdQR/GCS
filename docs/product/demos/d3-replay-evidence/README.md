# D3 Replay Evidence Demo

Status: active
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Claim

GCS can preserve a solver run as inspectable replay evidence: a researcher can
see whether the run was accepted, which report codes appeared, which stages
mutated durable state, and whether the transaction committed or rolled back.

## Scene

```text
fixtures/scene/basic/g1.txt
```

This is the same small scene used by D1. D3 focuses on the saved evidence
artifact rather than the console transcript.

## Command

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json
```

## Artifact

- `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.report.json`
- `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json`

## Fields To Inspect

| Field | Research meaning |
| --- | --- |
| `schema` | Replay evidence report version. |
| `accepted` and `status` | Top-level runtime outcome. |
| `base_version` and `final_version` | Whether durable state advanced. |
| `committed` and `rolled_back` | Transaction boundary. |
| `report_codes` | Compact evidence trace. |
| `stages` | Ordered command validation, planning, solving, diagnostics, gluing, and commit stages. |
| `durable_mutation` | Which stage changed state. |

## Expected Current Interpretation

- `accepted` is `true`.
- `status` is `AcceptedWithWarnings`.
- `committed` is `true`.
- `rolled_back` is `false`.
- `report_codes` includes `gluing.accepted` and `runtime.commit`.
- Warning-level post-local diagnostics are expected in the current
  implementation.

## Checker

```bat
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
```

Latest result:

```text
[OK] replay evidence check: 17/17 checks passed -> docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json
```

The checker verifies required fields, accepted-with-warnings status, commit
semantics, report-code presence, stage order, and the durable mutation stage.

## Research Boundary

This demo proves that replay evidence can be saved and inspected for a small
accepted scene. It does not yet prove schema stability across releases or
complete replay reconstruction in the viewer.

## Next Upgrade

Wire the checker into an R2 reproducible research gate and refresh the replay
artifact when schema or report-code semantics change.
