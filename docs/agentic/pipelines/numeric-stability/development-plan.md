# Numeric Stability Pipeline — Development Plan

**Status**: proposed
**Priority**: P0
**Owner**: gcs-cpp-solver-maintainer

## Purpose

Systematically test solver behavior under extreme numerical conditions:
very small/large constraint values, near-degenerate geometries, ill-conditioned
configurations. Measure condition numbers, rank stability, residual growth.

## Toolchain Needed

### `tools/solver_testing/pipelines/stability.py`

```
StabilityTester
├── generate_value_sweep(constraint, range_spec) → list[float]
│   ├── logspace: 1e-12 → 1e12 in N steps
│   ├── near_zero: 0 ± ε, ε×2, ε×4...
│   └── boundaries: at schema limits
├── generate_geometry_perturbations(geometry, magnitude) → list[vec6]
│   ├── zero_direction: Line/Plane direction → 0
│   ├── coincident_points: two Points → same position
│   └── parallel_lines: two Lines → same direction
├── stability_solve(scene, value_sweep) → list[StabilityPoint]
│   └── per value: {value, status, rank, condition, residual_norm}
├── analyze_stability(points) → StabilityReport
│   ├── condition_trend: does condition number blow up?
│   ├── rank_drops: does rank estimate suddenly drop?
│   └── failure_boundary: at what value does solve fail?
└── generate_report(report) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/stability.py \
  --scene fixtures/scene/basic/g1.txt \
  --sweep logspace --range 1e-12,1e12 --steps 20 \
  --output stability_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `stability.py` — value sweep + multi-solve | 200行 |
| 2 | Geometry perturbation generators | 150行 |
| 3 | Stability analysis (trend detection) | 100行 |
| 4 | CLI + report output | 50行 |

**Total**: ~500 lines
