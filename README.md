# GCS

GCS is a geometric constraint solving workspace. The repository is now arranged
around the target architecture vocabulary and a C++23 modules build.

## Repository Layout

| Path | Purpose |
| --- | --- |
| `src/gcs/kernel` | Domain model, stable IDs, behavior intent, and type helpers. |
| `src/gcs/incidence_graph` | Current connected-component decomposition prototype. |
| `src/gcs/diagnostics` | Current DOF/status/residual diagnostics prototype. |
| `src/gcs/numeric_engine` | Current numeric solving prototype. |
| `src/gcs/io_adapters` | Text and JSON scene import/export. |
| `src/gcs/session_runtime` | Temporary orchestration facade over the current solver modules. |
| `apps/gcs_cli` | Thin command-line executable entry point. |
| `python/gcs_viz` | Local Python visualization application. |
| `fixtures/scene` | Reproducible text and JSON scene inputs. |
| `scripts` | Repository automation and launch scripts. |
| `docs/architecture` | Durable architecture source of truth. |
| `docs/research` | Background research notes and exploratory material. |

The current C++ implementation still contains prototype logic from the old
`core/dcm/lgs/cds/io/app` modules, but the physical layout now names the target
responsibilities. Future solver work should make the code match these
boundaries instead of reintroducing legacy project structure.

## Build

Use the Clang + Ninja CMake preset:

```bat
scripts\build_clang_ninja.cmd
```

The executable is generated at:

```text
out/build/clang-ninja/GCS.exe
```

The CLI defaults to `fixtures/scene/basic/g1.txt` when no scene path is passed:

```bat
out\build\clang-ninja\GCS.exe fixtures\scene\basic\g1.txt
```

## Python Viewer

Install Python dependencies when needed:

```bat
python -m pip install -r python\requirements.txt
```

Launch the local viewer:

```bat
scripts\start_gui.cmd
```

Set `GCS_EXE` if you want the viewer to call a solver executable outside the
default CMake preset output path.

## Testing

Run the full local quality gate before pushing solver or architecture changes:

```bat
scripts\run_quality_gates.cmd
```

The gate wraps agentic design validation, dependency checks, Python scene tool
tests, CMake build, CTest contract suites, fixture-corpus checks, and a
representative CLI smoke run.

New tests should be designed around the target contracts in
`docs/architecture/30-contracts` and the verification scenes in
`fixtures/scene/verification`.
