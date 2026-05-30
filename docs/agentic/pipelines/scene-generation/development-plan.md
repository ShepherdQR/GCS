# Scene Generation Pipeline — Development Plan

**Status**: proposed (partially implemented)
**Priority**: P2
**Owner**: gcs-scene-generation-engineer

## Purpose

Generate scene fixtures with configurable coverage goals (geometry types,
constraint types, rigid set configurations, topology patterns). Produce
machine-readable coverage reports and promote qualified candidates into
the shared fixture corpus.

## What's Partially Implemented

- `tools/scene_generation/tools.py explore_scene_space` — sampling-based explorer
- `tools/scene_generation/tools.py enumerate_scene_space` — exhaustive enumerator
- `tools/scene_generation/tools.py promote_candidate` — fixture promotion

## Toolchain Needed

### `tools/solver_testing/pipelines/scene_gen.py`

Orchestrates the existing tools into a coverage-driven pipeline:

```
SceneGenPipeline
├── define_coverage_targets(spec) → CoverageSpec
│   ├── geometry_type_coverage: each type ≥ N fixtures
│   ├── constraint_type_coverage: each type ≥ N fixtures
│   ├── rigid_set_coverage: 2RS, 3RS, 4RS ≥ N each
│   └── topology_coverage: cycle, tree, complete ≥ N each
├── run_exploration(spec, budget) → ExplorationResult
├── run_enumeration(spec, budget) → EnumerationResult
├── promote_qualified(accepted, gates) → list[PromotionResult]
├── coverage_gap_analysis(current, targets) → list[Gap]
└── generate_coverage_report(results) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/scene_gen.py \
  --coverage targets.json \
  --budget max_candidates=500 \
  --promote \
  --output coverage_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `scene_gen.py` — coverage target spec parser | 100行 |
| 2 | Orchestration over explore + enumerate | 100行 |
| 3 | Coverage gap analysis | 100行 |
| 4 | CLI + multi-strategy runner | 100行 |

**Total**: ~400 lines
