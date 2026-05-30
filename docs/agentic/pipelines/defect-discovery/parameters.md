# Defect Discovery Pipeline — Parameters

## Enumeration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enumeration_id` | string | required | Unique ID for this enumeration run |
| `num_geometries` | int | `5` | Number of geometric entities |
| `num_constraints` | int | `5` | Number of constraints |
| `num_rigid_sets` | int | `2` | Number of rigid body sets |
| `geometry_types` | list[string] | `["Point","Line","Plane"]` | Allowed geometry types |
| `constraint_types` | list[string] | `["Coincident","Parallel","Perpendicular","Distance","Angle"]` | Allowed constraint types |
| `require_biconnected` | bool | `true` | Require geometry-primal biconnectivity (set false for connectivity-only) |
| `max_graphs` | int | `10000` | Maximum graphs to enumerate |
| `max_seconds` | float | `0.0` | Time budget (0 = unlimited) |
| `seed` | int | `0` | Random seed for determinism |

## Mutation Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategies` | list[string] | all 8 | Mutation strategies to apply |
| `seed` | int | `0` | Random seed |

### Available Mutation Strategies

| Strategy | Applies To | Operation |
|----------|-----------|-----------|
| `zero_to_nonzero` | All | 0 → random(0.1, 10) |
| `positive_to_negative` | Distance | +v → −v |
| `small_to_large` | All | v → v×100 |
| `large_to_small` | All | v → v/100 |
| `angle_out_of_range` | Angle | v → v±π |
| `epsilon_perturb` | All | v → v×(1±1e-3) |
| `extreme_value` | All | v → ±1e6 |
| `zero_value` | All | v → 0 |

## Solver Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `solver_command` | list[string] | auto-detect | Solver executable path |
| `timeout_seconds` | float | `30.0` | Per-solve timeout |

## Pipeline Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_graphs` | int | `10` | Max graphs to pipeline-test (subset of enumerated) |
| `strategies` | string | `"positive_to_negative,zero_to_nonzero,angle_out_of_range"` | Comma-separated strategy names |

## Defect Classification Taxonomy

| Error Type | Severity | Auto-Fix? |
|-----------|----------|-----------|
| `negative_distance` | wrong_result | Yes — abs() |
| `invalid_angle_range` | wrong_result | Yes — wrap to [0,π] |
| `invalid_parameter_value` | wrong_result | Yes — clamp |
| `degenerate_geometry` | wrong_result | Yes — perturb |
| `gluing_boundary_mismatch` | wrong_result | No — developer |
| `numerically_singular` | wrong_result | No — developer |
| `solver_crash` | crash | No — developer |
| `solver_timeout` | crash | No — developer |
| `solver_failed` | wrong_result | No — developer |
| `diagnostics_lost` | diagnostic_only | No — informational |
| `diagnostics_appeared` | diagnostic_only | No — informational |

## Parameter Presets

### Quick Smoke (`--preset smoke`)
```json
{"max_graphs": 5, "strategies": "positive_to_negative,epsilon_perturb", "timeout_seconds": 5}
```

### Standard Run (`--preset standard`)
```json
{"max_graphs": 20, "strategies": "positive_to_negative,zero_to_nonzero,epsilon_perturb,extreme_value", "timeout_seconds": 10}
```

### Full Sweep (`--preset full`)
```json
{"max_graphs": 200, "strategies": "all", "timeout_seconds": 30}
```
