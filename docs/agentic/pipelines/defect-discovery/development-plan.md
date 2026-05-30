# Defect Discovery Pipeline — Development Plan

**Status**: active (v1 implemented)
**Priority**: P0

## What's Implemented

- `tools/scene_generation/gcs_scene_generation/enumerator.py` — exhaustive enumeration
- `tools/solver_testing/mutator.py` — 8 mutation strategies
- `tools/solver_testing/runner.py` — batch solver execution
- `tools/solver_testing/defect_store.py` — JSON defect library
- `tools/solver_testing/analyzer.py` — classification + auto-fix
- `tools/solver_testing/pipeline.py` — end-to-end orchestration

## Remaining Work

- [ ] Store solver stdout in defect records (currently only stderr)
- [ ] Add `--preset` flag (smoke/standard/full)
- [ ] Auto-detect solvable graphs before mutation (skip pre-filtered)
- [ ] Parallel solver execution for batch speedup
- [ ] Defect store migration path for scale (>10K defects)
- [ ] Integration with `nightly-immune` as a sub-check
