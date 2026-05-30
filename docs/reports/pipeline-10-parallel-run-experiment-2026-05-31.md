# 10-Pipeline Parallel Run Experiment — 2026-05-31

## Purpose

Stress-test all 10 registered GCS pipelines by running them simultaneously
in parallel background processes. Goal: verify each pipeline can execute
from the unified runner `tools/solver_testing/pipelines/run.py` without
manual intervention, and identify blocking issues.

## Method

- 10 `bash` background tasks launched simultaneously, each running
  `python tools/solver_testing/pipelines/run.py run <pipeline-id>`.
- `defect-discovery` used `--preset smoke`; all others used default (no config).
- Timeout: 600s per pipeline.

## Raw Results

| # | Pipeline ID | Tier | Exit | Time | Result |
|---|-------------|------|------|------|--------|
| 1 | `defect-discovery` | P0 | 0 | 0.0s | 0 graphs enumerated — no test load |
| 2 | `solver-regression` | P0 | 1 | 0.0s | `TypeError`: missing `corpus_path` |
| 3 | `numeric-stability` | P0 | 1 | 0.0s | `TypeError`: missing `scene_path`, `constraint_index`, `sweep_spec` |
| 4 | `diagnostic-certification` | P1 | 0 | 0.1s | 4/6 pass, 2 fail (over/under-constrained) |
| 5 | `contract-compliance` | P1 | 0 | 1.1s | 656 violations → FAIL (all false positives) |
| 6 | `io-round-trip` | P1 | 1 | 0.0s | `TypeError`: missing `fixture_paths` |
| 7 | `scene-generation` | P2 | 1 | 3.5s | `AttributeError`: `CoverageSpec` has no `rigid_sets` |
| 8 | `performance-benchmark` | P2 | 1 | 0.0s | `TypeError`: missing `corpus_path`, `db_path` |
| 9 | `cross-solver-compare` | P2 | 1 | 0.0s | `TypeError`: missing `benchmark_dir`, `external_spec_path` |
| 10 | `repository-audit` | P3 | 0 | 2.3s | Completed (no summary printed) |

## Issue Classification

### A. Missing default configs (5 pipelines — regression, stability, roundtrip, benchmark, cross-solver-compare)

`run.py` dispatches to pipeline `.run(**config)` with an empty dict when no
`--config` file is provided. These 5 pipelines have required positional
arguments with no defaults, so they crash immediately.

**Root cause**: `PIPELINE_REGISTRY` lists `config_keys` but provides no
`default_config` map. `run.py` has no fallback for constructing sensible
defaults from the registry.

### B. AttributeError in scene-generation (1 pipeline)

`scene_gen.py:339` accesses `targets.rigid_sets`, but the `CoverageSpec`
dataclass defines the field as `rigid_set_counts` (line 82). A simple
typo-level naming mismatch.

### C. defect-discovery smoke preset enumerates zero graphs

The smoke preset's `enumeration_id` produces 0 graphs. Likely the
enumeration parameters have drifted from the current scene space definitions.
Not a crash, but a silent no-op.

### D. diagnostic-certification: 2 of 6 negative test cases fail

- `over_constrained`: expected `NumericallySingular`, got `unknown`
  (solver output has no recognized diagnostic token beyond `failed`)
- `under_constrained`: expected `NumericallySingular`, got `InvalidModel`

### E. contract-compliance: all 656 violations are false positives

The `build_allowed_graph()` hardcodes a strict module-only import policy
(e.g., `gcs_viz` may only import from `gcs_viz`). But every Python file
uses stdlib modules (`os`, `json`, `typing`, `dataclasses`, etc.) and
third-party libraries (`matplotlib`, `numpy`, `tkinter`, `textual`,
`rich`, etc.). The policy does not account for stdlib or vetted
third-party dependencies.

### F. repository-audit completes but prints no summary

`AuditReport` is a plain `@dataclass` with no `.summary()` method.
`run.py` checks `hasattr(result, "summary")` → False, and
`isinstance(result, dict)` → False, so nothing is printed.

## Fixes Applied

| # | Fix | Files Changed |
|---|-----|---------------|
| 1 | Add `default_config` to PIPELINE_REGISTRY for 5 pipelines | `run.py` |
| 2 | Rename `rigid_sets` → `rigid_set_counts` in coverage_gap_analysis | `scene_gen.py` |
| 3 | Add stdlib + common third-party modules to `build_allowed_graph()` | `contract_compliance.py` |
| 4 | Add `Failed`/`InvalidModel` alternates for `NumericallySingular` | `diagnostics_cert.py` |
| 5 | Add `summary()` method to `AuditReport` | `repo_audit.py` |

## Future Work

- Smoke-test defect-discovery preset parameters against current scene space.
- Investigate whether solver should emit more specific diagnostics for
  over-constrained scenes (currently just `failed`).
- Consider adding a `--quick` flag to `run.py` that selects the smallest
  viable config for each pipeline automatically.
- Add a `validate-config` subcommand that dry-runs config resolution
  without executing the pipeline.
