# Third-Party Dependency Policy

## Purpose

Third-party code is part of architecture because it affects build
reproducibility, licensing, binary compatibility, and solver portability. GCS
should keep its mathematical core small and explicit, while still allowing
well-scoped external libraries for tests, numerics, parsing, and tooling.

## Repository Layout

Use this layout when dependencies are vendored:

```text
third_party/
  README.md
  <library>/
    upstream source or submodule
cmake/
  third_party/
    optional dependency adapter modules
```

`third_party/<library>` should contain either a pinned upstream source tree or
a git submodule. Do not scatter copied headers or source files across solver
modules.

## Dependency Preference Order

Use dependencies in this order:

1. CMake package already installed on the developer or CI machine.
2. Vendored source under `third_party/`.
3. Explicit opt-in `FetchContent`.
4. Prebuilt binary artifacts such as DLLs, only when source builds are
   impractical and the artifact contract is documented.

Normal configure/build commands must not perform network access unless an
explicit option says so.

## Source Vs Binary Rule

Prefer source dependencies over committed binaries.

Source dependencies are easier to:

- build with the same compiler and runtime as GCS;
- audit and patch;
- use across Debug and Release builds;
- use with C++23 modules and current CMake policies;
- reproduce on CI.

Prebuilt DLLs or libraries may be used only when all of these are documented:

- upstream version and license;
- compiler, runtime, architecture, and build type;
- expected directory layout;
- how the DLL reaches the executable at test/runtime;
- how the artifact is updated or regenerated.

## CMake Contract

Every third-party dependency must be hidden behind a small CMake contract:

- expose imported or alias targets, not raw include/link variables;
- keep dependency options prefixed with `GCS_`;
- keep test-only dependencies out of production targets;
- use `EXCLUDE_FROM_ALL` for vendored test dependencies when possible;
- preserve C++23 module scanning for GCS targets.

Project modules should link only to targets such as `GTest::gtest_main`,
`gcs_solver`, or future `GCS::<name>` aliases. Solver code must not depend on a
third-party include path leaking globally.

## GoogleTest Policy

GoogleTest is a test-only dependency.

Preferred integration:

1. `find_package(GTest CONFIG QUIET)` or `find_package(GTest QUIET)`.
2. If `third_party/googletest` exists, use
   `add_subdirectory(third_party/googletest EXCLUDE_FROM_ALL)`.
3. If still unavailable and `GCS_FETCH_GTEST=ON`, fetch a pinned upstream
   release with CMake `FetchContent`.
4. If still unavailable, skip C++ tests with a clear CMake status message.

Do not commit GoogleTest DLLs as the default path. A DLL-based setup is allowed
only as a documented local or CI artifact strategy, because it couples tests to
compiler, CRT, architecture, build type, and PATH/copy behavior.

Do not copy only a few GoogleTest files into the repository. If vendored,
vendor the pinned upstream source tree or use a submodule so licensing,
CMake targets, and internal file relationships remain intact.

## Versioning And Review

Every new vendored dependency needs:

- name, upstream URL, version/tag/commit;
- license summary;
- reason for inclusion;
- whether it is production, test-only, tooling-only, or optional;
- update procedure;
- CMake target names exposed to GCS.

For small dependencies, prefer documenting them in `third_party/README.md`.
For larger dependencies, add `third_party/<library>/GCS_THIRD_PARTY.md` with
the same metadata.

## Current Policy Decision

For the initial C++23 solver skeleton, GoogleTest should stay test-only and
minimal:

- use installed GTest when present;
- optionally use `third_party/googletest` if we decide to vendor it;
- optionally use `GCS_FETCH_GTEST=ON` for developer convenience;
- skip tests gracefully when no GTest provider is available.

This keeps the production solver free of third-party dependencies while making
contract tests easy to enable.
