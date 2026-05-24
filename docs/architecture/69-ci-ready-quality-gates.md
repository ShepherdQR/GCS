# CI-Ready Quality Gates

Status: P6.3 showcase HTML figure gate integrated.

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
6. Python agentic toolkit unittest
7. Python showcase-scene renderer unittest
8. Python showcase fixture evidence metadata check
9. Python showcase fixture evidence unittest
10. Python showcase HTML compositor freshness check
11. Python showcase HTML compositor unittest
12. Python browser-export unittest
13. Python token lint and token-lint unittest
14. Python text-overflow check and unittest
15. Python overlap/contrast check and unittest
16. Python screenshot-baseline check and unittest
17. Python scene-schema algebra unittest
18. Python history-replay unittest
19. `cmake --preset clang-ninja`
20. `cmake --build --preset clang-ninja`
21. full CTest contract suite
22. explicit `ContractToolsContract` CTest selection for fixture corpus coverage
23. explicit public-evidence-chain CTest selection for rank, diagnostics,
    runtime, viewer, corpus, showcase, and replay-boundary evidence introduced
    in Steps 31 through 46
24. CLI smoke on `fixtures/scene/basic/g1.txt`
25. CLI smoke on
    `fixtures/scene/showcase/integrated_feature_showcase.gcs.json`

The command exits nonzero on the first failed gate by default and prints a
stable summary. `--continue-on-failure` runs the remaining gates before
returning failure. CTest gates use `--no-tests=error` so a broken selection is
treated as a failed quality gate.

The public evidence chain gate is intentionally redundant with full CTest. The
full suite remains the broad correctness boundary, while
`ctest.public_evidence_chain` is a named, affordable sentinel for the evidence
paths that must remain visible across modules:

- numeric max-absolute residual and free/frozen rank evidence;
- diagnostics promotion of numeric residual/rank evidence and duplicate
  redundancy subjects;
- kernel and IO validation for scene-facing solve intent;
- C++ loading of Python-authored `gcs-0.3` behavior scenes;
- runtime rank and post-local diagnostic projections;
- viewer overlay projections for rank, residual, conflict, redundancy, and
  gluing obstruction evidence;
- reusable contract-tool fixtures for boundary-frozen, tolerance-edge, and
  separator-chain scenarios;
- integrated showcase evidence for solve-intent boundary propagation,
  JSON behavior round-trip, boundary-frozen rank projection, viewer residual
  projection, positive CLI smoke, and negative scene behavior rejection;
- runtime replay boundary evidence proving command transaction traces project
  as report evidence, not JSON scene construction history actions.

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
- public evidence-chain coverage is named as an explicit gate and selects the
  Step 31 through Step 46 rank, diagnostics, runtime, viewer, corpus,
  showcase, and replay-boundary sentinel tests;
- scene-generation tests are part of the default gate;
- showcase-scene renderer tests are part of the default gate;
- showcase fixture evidence metadata checks are part of the default gate;
- showcase HTML compositor freshness checks are part of the default gate;
- token, text-overflow, overlap/contrast, and screenshot-baseline visual
  integrity checks are part of the default gate;
- Python scene-schema algebra tests are part of the default gate;
- Python history-replay tests are part of the default gate;
- the agentic toolkit gate sequence is unit-tested as a Python tools contract;
- representative basic and showcase CLI fixtures are part of the default gate;
- the implementation roadmap records the latest quality-gate extension step;
- runtime replay-boundary tests remain in the public evidence-chain sentinel.
