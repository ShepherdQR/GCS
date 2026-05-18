# GCS

GCS is a geometric constraint solving project. The solver core is written in C++ and the visual interface is launched through a batch entry point.

## Entry Points

- Visual interface: `GCS/start_tui.bat`
- C++ solver main program: `GCS/app/main.cpp`
- Visual Studio solution: `GCS.sln`
- Visual Studio project: `GCS/GCS.vcxproj`
- Model files: `GCS/scene/`
- Architecture: `architecture/architecture.md`
- Commercial GCS references: `architecture/reference/`

## Run

Build the C++ solver with Visual Studio first, then start the visual interface:

```bat
cd GCS
start_tui.bat
```

Build outputs are organized under `build/`, and the visual layer looks for the solver there first:

- `build/bin/<Platform>/<Configuration>/`: executables
- `build/obj/<Project>/<Platform>/<Configuration>/`: Visual Studio intermediate files
- `build/obj/tests/<Platform>/<Configuration>/`: manually built test object files

The C++ modules use a flat layout. For example, `GCS/cds/cds.h` and `GCS/cds/cds.cpp` live directly inside the `cds` module directory.

Text graph models, including test fixtures, live under `GCS/scene/`.

If Python dependencies are missing, install them with:

```bat
python -m pip install -r GCS/requirements.txt
```

## Repository Hygiene

The repository keeps source code, project files, documentation, tests, and reusable scene data. Local IDE state, compiler outputs, Python caches, temporary TUI scenes, and generated visualization files are ignored by `.gitignore`.
