# Repository Audit Pipeline — Development Plan

**Status**: proposed (partial tooling exists)
**Priority**: P3
**Owner**: gcs-repository-audit-steward

## Purpose

Automated repository health checks: file classification, directory structure
validation, stale file detection, snapshot collection, trend analysis.

## What's Partially Implemented

- `tools/agentic_design/agentic_toolkit.py validate-docs` — doc validation
- `tools/scene_generation/fixture_library_gate.py` — fixture quality gate

## Toolchain Needed

### `tools/solver_testing/pipelines/repo_audit.py`

```
RepoAuditor
├── classify_files(root, rules) → FileClassification
│   ├── source: .cpp, .h, .hpp
│   ├── python: .py
│   ├── docs: .md in docs/
│   ├── fixtures: .txt, .json in fixtures/
│   ├── config: CMakeLists.txt, .json configs
│   ├── unknown: everything else
│   └── large_files: >1MB
├── check_directory_conventions(root) → list[Violation]
│   ├── orphaned_files outside expected dirs
│   ├── empty_directories
│   └── nested_.git_dirs
├── detect_stale_artifacts(root, max_age_days) → list[StaleFile]
│   └── files not modified in N days, flag for archival
├── collect_snapshot(root) → RepoSnapshot
│   ├── file_count by category
│   ├── total_lines by category
│   └── largest files
├── compare_snapshots(before, after) → SnapshotDiff
└── generate_audit_report(results) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/repo_audit.py \
  --root . \
  --stale-threshold 90 \
  --snapshot \
  --output audit_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `repo_audit.py` — file classifier | 100行 |
| 2 | Directory convention checker | 100行 |
| 3 | Stale file detector + snapshot | 100行 |
| 4 | CLI + report | 50行 |

**Total**: ~350 lines
