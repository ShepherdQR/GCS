# R2 Reproducible Build Transcript — 2026-05-30

Status: baseline
Date: 2026-05-30
Previous: none (first R2 transcript)

## Purpose

Record the build environment, configuration, and verification steps that
produce a working GCS.exe. This transcript supports the R2 release-readiness
claim that a researcher with the same toolchain can reproduce the solver
binary and run the contract test suite.

## Reproducibility Caveat

This transcript records **behavioral reproducibility**: same OS, same
toolchain, same source tree → same solver behavior (same 128 CTest
results, same GCS.exe output on g1.txt). Full byte-for-byte binary
reproducibility is not claimed. Differences in build path, timestamps,
or compiler minor versions may produce different binaries that behave
identically.

## Environment

| Item | Value |
|------|-------|
| OS | Microsoft Windows 10.0.26200.8457 |
| Architecture | x86_64-pc-windows-msvc |
| Compiler | clang version 22.1.5 (LLVM 20.1.7) |
| CMake | 4.3.2 |
| Build system | Ninja 1.13.2 |
| Source tree | `C:/Codes/AI/GCS_A` |
| Git commit | [`6ab0b8a`](https://github.com/ShepherdQR/GCS_A/commit/6ab0b8a) |

## Build Configuration

Preset: `clang-ninja` (from `CMakePresets.json`)

```
cmake --preset clang-ninja
```

Key CMake variables (from preset):
- `CMAKE_CXX_COMPILER`: clang++
- `CMAKE_CXX_STANDARD`: 23
- `CMAKE_BUILD_TYPE`: (preset default)

Configure output:
```
-- Configuring done (0.3s)
-- Generating done (0.1s)
-- Build files have been written to: C:/Codes/AI/GCS_A/out/build/clang-ninja
```

## Build

```
cmake --build --preset clang-ninja
```

Result: 64 build steps, all targets compiled successfully. No warnings or
errors. Incremental rebuild reports `ninja: no work to do`.

Targets produced:
- `GCS.exe` — CLI solver application
- 14 contract test executables (gcs_*_contract_tests.exe)

## Verification

### CTest Contract Suite

```
ctest --output-on-failure
```

Result: **128/128 tests passed, 0 failures.** (Total time: 1.61s)

Test coverage by module:

| Module | Tests | Status |
|--------|------:|--------|
| Kernel | 9 | All pass |
| Constraint Catalog | 8 | All pass |
| Incidence Graph | 11 | All pass |
| Decomposition Planner | 18 | All pass |
| Numeric Engine | 15 | All pass |
| Diagnostics | 9 | All pass |
| Session Runtime | 10 | All pass |
| IO Adapters | 13 | All pass |
| Viewer Bridge | 13 | All pass |
| Contract Tools | 12 | All pass |
| Module Dependencies | 2 | All pass |
| Cross-Module Quality | 5 | All pass |
| Pipeline | 3 | All pass |

### GCS.exe Self-Test

```
GCS.exe fixtures/scene/basic/g1.txt
```

Result: `Status: AcceptedWithWarnings`. 3 local solves converged, gluing
accepted, runtime committed verified state. Output consistent with
expected solver behavior for a 5-entity, 2-constraint scene with 3
rigid sets.

## R2 Readiness Notes

- Build is clean with no warnings or errors.
- Contract test suite (128 tests) passes with 0 failures.
- GCS.exe produces deterministic output on the g1 baseline fixture.
- Python tools (`validate-docs`, `validate-skills`, `check_staged_scope`,
  `check_completion_evidence`) all pass independently.
- This transcript should be refreshed after any compiler upgrade, new
  module addition, or solver pipeline change that expands the test suite.

## Refresh Rule

Generate a new transcript when:
- Compiler or CMake version changes.
- The CTest suite grows by 10+ tests.
- A new release candidate is cut.
- At minimum, quarterly.
