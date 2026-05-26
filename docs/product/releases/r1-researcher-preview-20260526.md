# R1 Researcher Preview 2026-05-26

Status: active
Date: 2026-05-26
Audience: solver and geometric-constraint researchers

## Decision

This snapshot is suitable as an R1 researcher preview in the local checkout:
researchers can inspect the thesis, run the command-line evidence path, review
D2 diagnostic classifications, inspect D3 replay evidence, and read B1
expected outputs.

It is not a public tool release.

## Evidence Route

| Step | Artifact |
| --- | --- |
| Read the thesis | `docs/architecture/95-gcs-narrative-map.md` |
| Run D1 smoke | `docs/product/demos/d1-cli-smoke/` |
| Run D2 diagnostics | `tools/product_demo/diagnostic_classification.py` |
| Inspect D2 evidence | `docs/product/demos/d2-diagnostic-classification/artifacts/d2-diagnostic-summary.json` |
| Inspect D3 replay | `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.report.json` |
| Check D3 replay | `tools/product_demo/replay_evidence_check.py` and `docs/product/demos/d3-replay-evidence/artifacts/g1-replay-evidence.check.json` |
| Inspect D5 static workbench | `docs/product/demos/d5-solver-evidence-workbench/` |
| Inspect B1 expected outputs | `docs/architecture/benchmarks/b1-diagnostic-classification/expected/` |
| Run package smoke | `tools/product_demo/r1_package_smoke.py` |

## Smoke Command

```bat
python tools\product_demo\r1_package_smoke.py --output docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json
```

Current artifact:

- `docs/product/releases/artifacts/r1-researcher-preview-smoke-20260526.json`

The smoke path checks docs validation, inventory validation, skill validation,
dependency boundaries, D1 CLI smoke, D2 JSON classification, and D3 replay
artifact shape. The dedicated D3 replay checker performs the stronger
schema-aware check.

## Supported In R1

- Local Windows checkout used by this repository.
- Existing C++ CLI build at `out/build/clang-ninja/GCS.exe`.
- D1, D2, and D3 researcher evidence packages.
- B1 internal expected-output files.
- Markdown release note and JSON smoke artifact.

## Not Supported In R1

- Installer or package manager workflow.
- Public binary download.
- Broad OS/compiler compatibility.
- GUI-first workflow.
- Performance benchmark claims.
- CAD feature parity.
- External solver superiority claims.

## Known Limitations

- `AcceptedWithWarnings` remains expected for several accepted cases because
  post-local diagnostics are still warning-level in the current implementation.
- Under-constrained behavior is inferred from rank/nullity evidence rather
  than a dedicated top-level status.
- Over-constrained and inconsistent examples may surface as numeric failure
  until the diagnostic taxonomy is split more finely.
- B1 expected outputs are internal regression evidence, not external
  benchmark results.

## Next Release Target

The next release target is R2 reproducible research snapshot. R2 needs:

1. reproducible build transcript;
2. frozen B2 research microbenchmark candidates;
3. expected-output files for B2-01 and B2-02;
4. first optional external baseline adapter decision;
5. versioned migration policy for expected outputs.
