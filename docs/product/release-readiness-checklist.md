# GCS Release Readiness Checklist

Status: seed
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This checklist defines what "release ready" means for a research-facing GCS
snapshot. GCS is not yet a polished CAD product. A release should be judged by
whether a researcher can build, run, inspect, reproduce, and cite evidence.

## Current Decision

GCS is not yet release ready for broad public use. It is ready for local R1
researcher preview when the D1, D2, D3, and package-smoke evidence artifacts
are kept current and the known limitations are explicit.

## Release Modes

| Mode | Audience | Meaning | Current status |
| --- | --- | --- | --- |
| R0 internal checkpoint | Maintainers and local agents | Commit-level state with task cards, archives, and validations. | Active |
| R1 researcher preview | Solver researchers | Can run CLI demos, inspect fixtures, inspect replay evidence, and read comparison plan. | Active local preview |
| R2 reproducible research snapshot | Researchers and reviewers | Frozen fixtures, versioned outputs, benchmark candidate set, reproducible build transcript, and cited comparison criteria. | Build transcript created; pending second-machine verification. |
| R3 public tool release | Tool builders and users | Packaging, support boundaries, install path, and compatibility promises. | Later |

## Minimum R1 Gate

| Gate | Required evidence | Current state |
| --- | --- | --- |
| Build path | One documented local build path or pre-existing build assumption. | Partial; D1/D2 use `out/build/clang-ninja/GCS.exe`. |
| D1 CLI smoke | Command, expected status, and replay artifact. | Present in `docs/product/demos/d1-cli-smoke/`. |
| D2 diagnostics | Multi-case classification transcript and JSON summary. | Present in `docs/product/demos/d2-diagnostic-classification/` and `tools/product_demo/diagnostic_classification.py`. |
| D3 replay evidence | Saved replay evidence artifact, field guide, and schema-aware checker. | Present in `docs/product/demos/d3-replay-evidence/` and `tools/product_demo/replay_evidence_check.py`. |
| Fixture corpus map | Corpus levels and promotion rules. | Present in `docs/architecture/96-fixture-corpus-maturity-ladder.md`. |
| Benchmark plan | External comparison targets and candidate rules. | Present in `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`. |
| B1 expected outputs | Internal expected-output files for diagnostic classification. | Present in `docs/architecture/benchmarks/b1-diagnostic-classification/`. |
| Known limitations | Unsupported or partial behavior stated in demo docs. | Present for D1/D2. |
| Package smoke | One command that writes R1 JSON evidence. | Present in `tools/product_demo/r1_package_smoke.py`. |
| Agentic closure | Task card, archive, validation evidence, scoped commit. | Required for each non-trivial release task. |

## Package Smoke Path

For an R1 preview, a researcher should be able to run:

```bat
git status -sb
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
python tools\product_demo\diagnostic_classification.py --output docs\product\demos\d2-diagnostic-classification\artifacts\d2-diagnostic-summary.json
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.check.json
python tools\product_demo\r1_package_smoke.py --output docs\product\releases\artifacts\r1-researcher-preview-smoke-20260526.json
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\over_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
```

Expected interpretation:

- docs and dependency validators pass;
- `g1.txt` exits 0 and is accepted with warnings;
- over-constrained and singular cases exit nonzero as expected and preserve
  obstruction evidence.
- D2, D3 checker, and R1 JSON evidence report all checks passed.

## Support Boundaries

Supported for R1:

- Windows local checkout used by the current project;
- PowerShell command transcripts;
- current C++ CLI build under `out/build/clang-ninja/GCS.exe`;
- documented fixtures and counterexamples;
- Markdown evidence packages.

Not supported for R1:

- package managers or installers;
- public binary downloads;
- stable GUI workflows;
- compatibility guarantees across compilers or operating systems;
- performance claims;
- complete CAD sketcher feature parity.

## Researcher Citation Boundary

An R1 researcher may cite:

- the architecture thesis;
- the fixture and counterexample taxonomy;
- the D1/D2/D3 command and artifact evidence;
- the benchmark selection criteria.

They should not cite:

- broad solver performance;
- benchmark superiority;
- production CAD readiness;
- GUI maturity;
- undocumented scene classes.

## Next Upgrade

To reach R2:

1. [x] add a reproducible build transcript (`docs/product/r2-build-transcript.md`);
2. [ ] wire the replay checker into a release gate;
3. [ ] freeze a small B2 benchmark-candidate set;
4. [ ] record expected status and report fields for each B2 candidate;
5. [ ] produce a versioned release note that includes skipped and unsupported
   checks.
6. [ ] verify build transcript on a second machine by a different researcher.
