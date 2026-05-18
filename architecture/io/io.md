# IO Module Architecture

## Purpose

The IO module is the file and console boundary for the C++ solver:

- read `.txt` and `.json` graph files into `gcs::Manager`
- dump solved graphs back to text or JSON files
- print readable summaries to stdout

Visualization is handled by `GCS/start_tui.bat` and the `gcs_viz` package, not by the IO module.

## Files

```text
GCS/io/io.h
GCS/io/io.cpp
```

## Public Interface

```cpp
void readGraph(Manager& m, const std::string& path);
void readGraphJSON(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void dumpGraphJSON(const Manager& m, const std::string& inputPath);
void printSummary(const Manager& m);
```

## Text Graph Format

```text
numOfRigidSet
idOfRigidSet1 idOfRigidSet2 ...
numOfGeometry
idOfGeometry type rigidSetId
...
numOfConstraint
idOfConstraint type numConnectedGeometries geometryId...
...

geometryId v0 v1 v2 v3 v4 v5
...

constraintId value
...
```

## Notes

- `readGraph` leaves the manager empty or partially populated when parsing fails and reports the error to stderr.
- `dumpGraph` writes next to the input path using the `<name>_graph.txt` convention.
- Text model fixtures live under `GCS/scene/test/<module>/`.
- Reusable model scenes live under `GCS/scene/`.
