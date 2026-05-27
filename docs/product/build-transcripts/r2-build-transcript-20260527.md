# R2 Reproducible Build Transcript

Date: 2026-05-27
Status: active
Release: R2

## Purpose

This transcript records a clean build of GCS from source in a documented
environment. It is the R2 evidence that a reviewer can reproduce the build
and run the contract test suite.

## Build Environment

| Component | Version | Path |
| --- | --- | --- |
| OS | Windows 11 Pro 10.0.26200 | — |
| Compiler | Clang 20.1.7 | `C:/Softwares/LLVM/LLVM_20_1_7/bin/clang++.exe` |
| CMake | 4.3.2 | `C:/Softwares/Cmake/cmake_4_3_2/bin/cmake.exe` |
| Ninja | 1.13.2 | `C:/Softwares/ninja/ninja_1_13_2/ninja.exe` |
| GTest | 1.17.0 | `C:/Softwares/GTest/GTest_1_17_0/install/clang-ninja-debug` |
| Windows SDK | 10.0.26100.0 | `C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64/` |
| C++ Standard | C++23 (`-std=c++23`) | Extensions OFF |
| Linker | LLD (LLVM) | `-fuse-ld=lld` |

## Build Command

```bat
scripts\build_clang_ninja.cmd
```

Equivalent manual invocation:

```bash
cmake --preset clang-ninja
cmake --build --preset clang-ninja
```

## Configure Output

```
-- The CXX compiler identification is Clang 20.1.7 with GNU-like command-line
-- Detecting CXX compiler ABI info - done
-- Check for working CXX compiler: C:/Softwares/LLVM/LLVM_20_1_7/bin/clang++.exe - skipped
-- Detecting CXX compile features - done
-- Configuring done (4.8s)
-- Generating done (0.1s)
-- Build files have been written to: out/build/clang-ninja
```

## Build Output

**Total:** 98/98 steps completed. 0 errors, 0 warnings.

### Compilation Units (42 objects)

| Module | Source | Type |
| --- | --- | --- |
| kernel | `src/gcs/kernel/kernel.cppm` | Module interface |
| kernel | `src/gcs/kernel/kernel.cpp` | Module implementation |
| tools | `src/gcs/tools/contract_tools.cppm` | Module interface |
| tools | `src/gcs/tools/contract_tools.cpp` | Module implementation |
| io_adapters | `src/gcs/io_adapters/io_adapters.cppm` | Module interface |
| io_adapters | `src/gcs/io_adapters/io_adapters.cpp` | Module implementation |
| constraint_catalog | `src/gcs/constraint_catalog/constraint_catalog.cppm` | Module interface |
| constraint_catalog | `src/gcs/constraint_catalog/constraint_catalog.cpp` | Module implementation |
| incidence_graph | `src/gcs/incidence_graph/incidence_graph.cppm` | Module interface |
| incidence_graph | `src/gcs/incidence_graph/incidence_graph.cpp` | Module implementation |
| decomposition_planner | `src/gcs/decomposition_planner/decomposition_planner.cppm` | Module interface |
| decomposition_planner | `src/gcs/decomposition_planner/decomposition_planner.cpp` | Module implementation |
| numeric_engine | `src/gcs/numeric_engine/numeric_engine.cppm` | Module interface |
| numeric_engine | `src/gcs/numeric_engine/numeric_engine.cpp` | Module implementation |
| diagnostics | `src/gcs/diagnostics/diagnostics.cppm` | Module interface |
| diagnostics | `src/gcs/diagnostics/diagnostics.cpp` | Module implementation |
| session_runtime | `src/gcs/session_runtime/session_runtime.cppm` | Module interface |
| session_runtime | `src/gcs/session_runtime/session_runtime.cpp` | Module implementation |
| viewer_bridge | `src/gcs/viewer_bridge/viewer_bridge.cppm` | Module interface |
| viewer_bridge | `src/gcs/viewer_bridge/viewer_bridge.cpp` | Module implementation |
| gcs_cli | `apps/gcs_cli/main.cpp` | Application |

### Contract Test Units (12 objects, 1 per module + cross-module)

| Test executable | Module under test |
| --- | --- |
| `gcs_kernel_contract_tests.exe` | kernel |
| `gcs_constraint_catalog_contract_tests.exe` | constraint_catalog |
| `gcs_incidence_graph_contract_tests.exe` | incidence_graph |
| `gcs_decomposition_planner_contract_tests.exe` | decomposition_planner |
| `gcs_numeric_engine_contract_tests.exe` | numeric_engine |
| `gcs_diagnostics_contract_tests.exe` | diagnostics |
| `gcs_session_runtime_contract_tests.exe` | session_runtime |
| `gcs_io_adapters_contract_tests.exe` | io_adapters |
| `gcs_viewer_bridge_contract_tests.exe` | viewer_bridge |
| `gcs_contract_tools_contract_tests.exe` | contract_tools |
| `gcs_module_dependency_contract_tests.exe` | module_dependency |
| `gcs_cross_module_quality_contract_tests.exe` | cross_module_quality |
| `gcs_pipeline_contract_tests.exe` | pipeline (end-to-end) |

### Link Output

| Target | Type |
| --- | --- |
| `gcs_solver.lib` | Static library |
| `GCS.exe` | CLI executable |
| 13 contract test executables | Test executables |

## Contract Test Results

```
Test project out/build/clang-ninja
115/115 tests passed
0 tests failed

Label Time Summary:
contract    =   1.56 sec*proc (115 tests)

Total Test time (real) =   1.72 sec
```

### Test Distribution by Module

| Module | Tests | Result |
| --- | ---: | --- |
| Kernel | 9 | PASS |
| Constraint Catalog | 8 | PASS |
| Incidence Graph | 6 | PASS |
| Decomposition Planner | 10 | PASS |
| Numeric Engine | 15 | PASS |
| Diagnostics | 9 | PASS |
| Session Runtime | 10 | PASS |
| IO Adapters | 13 | PASS |
| Viewer Bridge | 13 | PASS |
| Contract Tools | 12 | PASS |
| Module Dependency | 2 | PASS |
| Cross-Module Quality | 5 | PASS |
| Pipeline (end-to-end) | 3 | PASS |

## Reproducibility Notes

- The build uses C++23 modules (`.cppm` files). Module scanning order is
  deterministic given the same compiler version.
- The Ninja generator produces a deterministic build graph from the CMake
  configuration.
- No network access is required during build (GTest is pre-installed).
- The build produces no warnings with `-Wall -Wextra` under Clang 20.1.7.

## Known Variance

- Timestamps in build output vary per invocation.
- Object file paths are absolute and machine-specific.
- GTest installation path is machine-specific; CMakePresets.json can be
  adjusted for other environments.

## R2 Smoke Check

```bat
# Build
scripts\build_clang_ninja.cmd

# Contract tests
ctest --test-dir out\build\clang-ninja --output-on-failure

# CLI smoke
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt

# Replay checker
python tools\product_demo\replay_evidence_check.py --input docs\product\demos\d3-replay-evidence\artifacts\g1-replay-evidence.report.json --output NUL
```

Expected: build succeeds, 115/115 tests pass, CLI reports `AcceptedWithWarnings`,
replay checker reports `17/17 checks passed`.
