# R2 Reproducible Build Transcript

Status: active
Date: 2026-05-27
Release: R2 researcher preview (proposed)

## Purpose

This transcript records the exact environment, commands, and expected outputs
for a clean, reproducible build of GCS from source. It enables an external
researcher to verify that their build produces an equivalent artifact.

## Environment

| Component | Version / Value |
|---|---|
| Operating system | Windows 11 x64 (build 10.0.26200) |
| C++ compiler | Clang 22.1.5 (LLVM 20) |
| C++ standard library | MSVC STL (Visual Studio 2022 18.0) |
| Build system | CMake 4.3.2 |
| Build executor | Ninja 1.13.2 |
| C++ standard | C++23 |
| Python | 3.12+ |
| Git commit | `18a19fd77665fe754f482b7453caaa618dd8df7c` |

## Build Steps

### 1. Clone the repository

```bat
git clone <repo-url> gcs
cd gcs
```

Ensure the working tree is at the expected commit:

```bat
git rev-parse HEAD
:: Expected: 18a19fd77665fe754f482b7453caaa618dd8df7c
git status
:: Expected: nothing to commit, working tree clean
```

### 2. Configure

```bat
cmake --preset clang-ninja
```

Expected output:

```text
-- Configuring done (N.Ns)
-- Generating done (N.Ns)
-- Build files have been written to: .../out/build/clang-ninja
```

### 3. Build

```bat
cmake --build --preset clang-ninja
```

Expected: all 26 build steps complete without errors. The static library
`gcs_solver.lib` is produced first, then `GCS.exe` and 13 CTest executables.

### 4. Verify binary

```text
File: out/build/clang-ninja/GCS.exe
Size: ~1.15 MB (1,147,392 bytes in this transcript)
SHA-256: 879c86e7c3a32f2a2d1b590720598b9d434f8980f7fee3e5a99d061239fafa12
```

Note: The SHA-256 hash is expected to differ across compilers, STL versions,
and build configurations. The hash recorded here is a reference point for this
exact environment, not a universal fingerprint. A researcher using a different
Clang or MSVC version may produce a different binary.

### 5. Run contract tests

```bat
ctest --test-dir out/build/clang-ninja --output-on-failure
```

Expected: 115 tests pass, 0 fail.

```text
100% tests passed, 0 tests failed out of 115
```

### 6. Run quality gates

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

Expected: all default gates pass (docs validation, Python tool tests, build,
CTest, fixture checks, CLI smoke).

### 7. Smoke test

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

Expected output includes:

```text
Status: AcceptedWithWarnings
Accepted: true
runtime.commit: Runtime committed the verified proposed state.
```

### 8. Replay evidence check

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt --save-replay-evidence d3_replay.report.json
python tools\product_demo\replay_evidence_check.py --input d3_replay.report.json --output d3_check.json
```

Expected: `17/17 checks passed`.

## R2 Release Criteria

An R2 build is considered reproducible when:

1. [x] Build completes from clean checkout.
2. [x] All 115 CTest contract tests pass.
3. [x] Default quality gates pass.
4. [x] CLI smoke produces `AcceptedWithWarnings`.
5. [x] D3 replay evidence checker reports `17/17 checks passed`.
6. [ ] Build transcript is verified by a second researcher on different hardware. (pending external feedback)
7. [ ] Schema-aware replay checker is wired into release gate. (pending Task 1 follow-up in narrative map)
8. [ ] D5 workbench screenshot baselines pass on a second machine. (pending live GUI work)

## Known Non-Reproducibility Factors

- **SHA-256 hash**: Varies with compiler version, STL version, and optimization flags.
- **Build time**: Depends on machine speed; not part of the contract.
- **Python matplotlib backend**: Headless (Agg) is used in CI, but GUI tests require TkAgg.
- **Network access**: Not required for build. GTest is fetched via FetchContent on first configure but can be cached.

## Relationship To R1

R1 (2026-05-26) was a researcher preview with smoke automation and a
release-readiness checklist. R2 adds a reproducible build transcript, D3
replay checker integration, and explicit verification criteria.

## Next Steps After R2

- Wire replay evidence checker into the release gate.
- Have a second researcher verify this transcript.
- Define R3 criteria (packaging, installer, broader test matrix).
