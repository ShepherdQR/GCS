# GCS Release Readiness Checklist

Status: seed
Date: 2026-05-26
Primary audience: solver and geometric-constraint researchers

## Purpose

This checklist defines what "release ready" means for a research-facing GCS
snapshot. GCS is not yet a polished CAD product. A release should be judged by
whether a researcher can build, run, inspect, reproduce, and cite evidence.

## Current Decision

GCS is not yet release ready for broad public use. It is ready for curated
researcher review when the D1 and D2 evidence packages are kept current and the
known limitations are explicit.

## Release Modes

| Mode | Audience | Meaning | Current status |
| --- | --- | --- | --- |
| R0 internal checkpoint | Maintainers and local agents | Commit-level state with task cards, archives, and validations. | Active |
| R1 researcher preview | Solver researchers | Can run CLI demos, inspect fixtures, and read comparison plan. | Seed |
| R2 reproducible research snapshot | Researchers and reviewers | Frozen fixtures, versioned outputs, benchmark candidate set, and cited comparison criteria. | Later |
| R3 public tool release | Tool builders and users | Packaging, support boundaries, install path, and compatibility promises. | Later |

## Minimum R1 Gate

| Gate | Required evidence | Current state |
| --- | --- | --- |
| Build path | One documented local build path or pre-existing build assumption. | Partial; D1/D2 use `out/build/clang-ninja/GCS.exe`. |
| D1 CLI smoke | Command, expected status, and replay artifact. | Present in `docs/product/demos/d1-cli-smoke/`. |
| D2 diagnostics | Multi-case classification transcript. | Present in `docs/product/demos/d2-diagnostic-classification/`. |
| Fixture corpus map | Corpus levels and promotion rules. | Present in `docs/architecture/96-fixture-corpus-maturity-ladder.md`. |
| Benchmark plan | External comparison targets and candidate rules. | Present in `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md`. |
| Known limitations | Unsupported or partial behavior stated in demo docs. | Present for D1/D2. |
| Agentic closure | Task card, archive, validation evidence, scoped commit. | Required for each non-trivial release task. |

## Package Smoke Path

For an R1 preview, a researcher should be able to run:

```bat
git status -sb
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-inventory
python tools\agentic_design\agentic_toolkit.py validate-skills
python tools\agentic_design\agentic_toolkit.py check-dependencies
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
out\build\clang-ninja\GCS.exe fixtures\scene\verification\lgs\over_constrained.txt
out\build\clang-ninja\GCS.exe fixtures\scene\counterexamples\mixed_geometry_20g40c_singular_20260524.gcs.json
```

Expected interpretation:

- docs and dependency validators pass;
- `g1.txt` exits 0 and is accepted with warnings;
- over-constrained and singular cases exit nonzero as expected and preserve
  obstruction evidence.

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
- the D1/D2 command evidence;
- the benchmark selection criteria.

They should not cite:

- broad solver performance;
- benchmark superiority;
- production CAD readiness;
- GUI maturity;
- undocumented scene classes.

## Next Upgrade

To reach R2:

1. add a reproducible build transcript;
2. add a D2 classification script with JSON output;
3. freeze a small benchmark-candidate set;
4. record expected status and report fields for each candidate;
5. produce a versioned release note that includes skipped and unsupported
   checks.
