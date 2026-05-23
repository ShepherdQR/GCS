# CI-Ready Quality Gates

Status: Step 18 implementation contract.

## Purpose

Step 18 promotes the existing contract, dependency, fixture, scene, and CLI
checks into one deterministic quality-gate entry point. The gate is designed
for local pre-push use and for CI jobs that provision the repository's CMake
preset toolchain.

The quality gate is still a support workflow. It does not become a runtime
dependency of the C++ solver core.

## Entry Points

Preferred command:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

Windows wrappers:

```bat
scripts\run_quality_gates.cmd
powershell -ExecutionPolicy Bypass -File scripts\run_quality_gates.ps1
```

## Gate Sequence

The default gate runs:

1. `validate-docs`
2. `validate-inventory`
3. `validate-skills`
4. `check-dependencies`
5. Python scene auto explorer unittest
6. `cmake --preset clang-ninja`
7. `cmake --build --preset clang-ninja`
8. full CTest contract suite
9. explicit `ContractToolsContract` CTest selection for fixture corpus coverage
10. CLI smoke on `fixtures/scene/basic/g1.txt`

The command exits nonzero on the first failed gate by default and prints a
stable summary. `--continue-on-failure` runs the remaining gates before
returning failure. CTest gates use `--no-tests=error` so a broken selection is
treated as a failed quality gate.

## CI Parameters

Supported flags:

- `--preset <name>`: CMake configure/build preset, default `clang-ninja`.
- `--build-dir <path>`: CTest and CLI build directory, default
  `out/build/clang-ninja`.
- `--skip-agentic`: skip docs, inventory, skills, and dependency checks.
- `--skip-python-tools`: skip Python scene-generation tool tests.
- `--skip-build`: skip CMake configure/build.
- `--skip-ctest`: skip CTest gates.
- `--skip-cli`: skip representative CLI smoke.
- `--continue-on-failure`: collect all failures before returning.

CI jobs should prefer the default command. Narrow skips are intended for
debugging or staged jobs, not for final merge gates.

## Acceptance Contract

A change is Step 18 complete when:

- the quality gate command is documented and runnable from repository root;
- agentic design checks are part of the default gate;
- CMake build and CTest are part of the default gate;
- fixture corpus coverage is named as an explicit gate and actually selects
  the contract-tools fixture tests;
- scene-generation tests are part of the default gate;
- a representative CLI fixture is part of the default gate;
- the implementation roadmap records Step 18 as complete.
