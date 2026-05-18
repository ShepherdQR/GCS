# GCS

GCS is a geometric constraint solving project. The solver core is written in C++ and the visual interface is launched through a batch entry point.

## Entry Points

- Visual interface: `GCS/start_tui.bat`
- C++ solver main program: `GCS/app/src/main.cpp`
- Visual Studio solution: `GCS.sln`
- Visual Studio project: `GCS/GCS.vcxproj`

## Run

Build the C++ solver with Visual Studio first, then start the visual interface:

```bat
cd GCS
start_tui.bat
```

The visual layer looks for the compiled solver at the usual Visual Studio output paths, such as `x64/Debug/GCS.exe`.

If Python dependencies are missing, install them with:

```bat
python -m pip install -r GCS/requirements.txt
```

## Repository Hygiene

The repository keeps source code, project files, documentation, tests, and reusable scene data. Local IDE state, compiler outputs, Python caches, temporary TUI scenes, and generated visualization files are ignored by `.gitignore`.
