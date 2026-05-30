# Contract Compliance Pipeline — Development Plan

**Status**: proposed
**Priority**: P1
**Owner**: gcs-kernel-contract-steward

## Purpose

Verify that module boundaries and interface contracts are upheld across the
codebase. Check that module A does not import module B when the architecture
spec forbids it, that stable IDs are immutable, that snapshot semantics hold.

## Toolchain Needed

### `tools/solver_testing/pipelines/contract_compliance.py`

```
ContractChecker
├── module_dependency_audit() → list[Violation]
│   ├── parse Python imports, C++ includes
│   ├── compare against allowed dependency graph
│   └── flag cross-boundary violations
├── stable_id_audit() → list[Violation]
│   ├── check that IDs are never reassigned
│   └── check that IDs survive round-trips
├── snapshot_immutability_check() → list[Violation]
│   └── verify ModelSnapshot fields are read-only post-construction
├── tolerance_consistency_check() → list[Violation]
│   └── verify all modules use the same tolerance values
└── generate_compliance_report(violations) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/contract_compliance.py \
  --modules src/gcs \
  --contracts docs/architecture/30-contracts/ \
  --output compliance_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `contract_compliance.py` — dependency graph checker | 150行 |
| 2 | Stable ID audit (Python-side checks) | 100行 |
| 3 | Tolerance consistency | 50行 |
| 4 | CLI + report aggregation | 50行 |

**Total**: ~350 lines
