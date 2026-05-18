# GCS Test Architecture

## 1. Overview

This document defines the GCS module test system. The test system verifies that each module's public interface contract is fulfilled correctly. Tests are organized per module, with each module having its own test spec document, scene fixtures, and test executable.

## 2. Test Conventions

- **Test naming**: `test_<module>_<what>_<condition>_<expected>`
- **Test structure**: Arrange → Act → Assert
- **Assertion macro**: `GCS_ASSERT(condition, message)` — custom macro, no framework dependency
- **Test runner**: Each module has a `test_<module>.cpp` with a `main()` that runs all tests and reports pass/fail
- **Scene fixtures**: `.txt` graph files stored in `GCS/test/<module>/` directory
- **Test result**: Console output with `[PASS]` / `[FAIL]` per test, summary at end

## 3. Test Framework

A lightweight test framework defined in `GCS/test/test_framework.h`:

- `GCS_ASSERT(cond, msg)` — assert condition with message
- `GCS_ASSERT_EQ(a, b, msg)` — assert equality
- `GCS_ASSERT_NE(a, b, msg)` — assert inequality
- `GCS_ASSERT_GT(a, b, msg)` — assert greater than
- `GCS_ASSERT_LT(a, b, msg)` — assert less than
- `GCS_TEST_SUMMARY()` — print summary and return exit code

## 4. Scene Fixture Format

All scene fixtures follow the existing GCS graph file format:

```
Section 1: Topology
numOfRigidSet
id1 id2 id3 ...
numOfGeometry
id1 type1 rigidSetId1
id2 type2 rigidSetId2
...
numOfConstraint
id1 type1 numConn1 geomId1 geomId2 ...
...

Section 2: Parameters
geomId1 v[0] v[1] v[2] v[3] v[4] v[5]
...

Section 3: Constraint Values
constraintId1 value1
...
```

## 5. Test Module Map

| Module | Test Spec | Fixture Dir | Test File | Test IDs |
|--------|-----------|-------------|-----------|----------|
| Core | `core/test_core.md` | `GCS/test/core/` | `test_core.cpp` | C01-C17 |
| IO | `io/test_io.md` | `GCS/test/io/` | `test_io.cpp` | IO01-IO11 |
| DCM | `dcm/test_dcm.md` | `GCS/test/dcm/` | `test_dcm.cpp` | D01-D12 |
| LGS | `lgs/test_lgs.md` | `GCS/test/lgs/` | `test_lgs.cpp` | L01-L15 |
| CDS | `cds/test_cds.md` | `GCS/test/cds/` | `test_cds.cpp` | CD01-CD10 |
| App | `app/test_app.md` | `GCS/test/app/` | `test_app.cpp` | A01-A18 |

## 6. How to Run Tests

Each test module compiles as a standalone executable:

```bash
# Build all tests (from GCS/test/)
cl /EHsc /std:c++17 /I..\core\include /I..\io\include /I..\dcm\include /I..\lgs\include /I..\cds\include /I..\app\include /I. core\test_core.cpp ..\core\src\core.cpp /Fe:test_core.exe

# Run a specific test module
test_core.exe
test_io.exe
test_dcm.exe
test_lgs.exe
test_cds.exe
test_app.exe
```

## 7. Test Count Summary

| Module | Test Count |
|--------|-----------|
| Core | 17 |
| IO | 11 |
| DCM | 12 |
| LGS | 15 |
| CDS | 10 |
| App | 18 |
| **Total** | **83** |
