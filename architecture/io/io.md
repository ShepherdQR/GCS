# IO Module Architecture

## Module Name

**IO** — Input/Output

## Module Purpose

The IO module is responsible for all file and external communication for the GCS system:

1. **Reading**: Parse constraint graph files (`.txt`) into Manager data structures
2. **Writing**: Serialize Manager data structures into graph visualization files
3. **Display**: Launch external visualization tools (web browser with Three.js viewer)
4. **Reporting**: Print human-readable summaries to the console

The IO module acts as the **boundary layer** between the external world (files, browser, console) and the internal GCS system (Core data model).

## Module Interface

### Header File

```
include/gcs/io.h
```

### Primary Interface

```cpp
void readGraph(Manager& m, const std::string& path);
void dumpGraph(const Manager& m, const std::string& inputPath);
void displayGraph(const std::string& graphFile);
void printSummary(const Manager& m);
```

### Future Extensions (Phase 2+)

```cpp
class IGraphReader {
public:
    virtual ~IGraphReader() = default;
    virtual bool read(Manager& m, const std::string& path) = 0;
};

class IGraphWriter {
public:
    virtual ~IGraphWriter() = default;
    virtual bool write(const Manager& m, const std::string& path) = 0;
};

class TxtGraphReader : public IGraphReader { /* current readGraph */ };
class TxtGraphWriter : public IGraphWriter { /* current dumpGraph */ };

class GraphIO {
public:
    void setReader(std::unique_ptr<IGraphReader> reader);
    void setWriter(std::unique_ptr<IGraphWriter> writer);
    bool read(Manager& m, const std::string& path);
    bool write(const Manager& m, const std::string& path);
private:
    std::unique_ptr<IGraphReader> reader_;
    std::unique_ptr<IGraphWriter> writer_;
};
```

### Usage Example

```cpp
Manager m;
readGraph(m, "g1.txt");
printSummary(m);
dumpGraph(m, "g1.txt");
```

## Module Implementation

### File Format (Current)

The input file format is a text-based, line-oriented format:

```
Section 1: Topology
────────────────────
numOfRigidSet
id1 id2 id3 ...
numOfGeometry
id1 type1 rigidSetId1
id2 type2 rigidSetId2
...
numOfConstraint
id1 type1 numConn1 geomId1 geomId2 ...
id2 type2 numConn2 geomId3 geomId4 ...
...

Section 2: Parameters
─────────────────────
geomId1 v[0] v[1] v[2] v[3] v[4] v[5]
geomId2 v[0] v[1] v[2] v[3] v[4] v[5]
...

Section 3: Constraint Values
─────────────────────────────
constraintId1 value1
constraintId2 value2
...
```

### readGraph Implementation

```
1. Open input file
2. Read topology section:
   a. Read number of rigid sets → create RigidSet objects
   b. Read number of geometries → create Geometry objects with type cast from int
   c. Read number of constraints → create Constraint objects with type cast from int
3. Read parameter section:
   a. For each geometry: read id + 6 doubles → set v[0..5]
4. Read constraint value section:
   a. For each constraint: read id + value → set constraint.value
5. Close file
```

### dumpGraph Implementation

```
1. If inputPath is empty, return immediately
2. Extract base filename from inputPath (strip directory and extension)
3. Create output file: ../x64/Debug/<base>_graph.txt
4. Write topology section (rigid sets, geometries, constraints)
5. Write parameter section (geometry values)
6. Write constraint value section
7. Close output file
8. Call displayGraph() to open browser viewer
```

### displayGraph Implementation

```
1. Construct URL: http://localhost:8000/display.html?file=<graphFile>
2. Launch browser:
   - Windows: start chrome "<url>"
   - macOS: open "<url>"
   - Linux: xdg-open "<url>"
```

### printSummary Implementation

```
1. Print rigid sets with their geometry IDs
2. Print geometries with type names, rigid set IDs, and parameter values
3. Print constraints with type names, connected geometry IDs, and values
```

### Error Handling

| Error | Handling |
|-------|---------|
| File not found | Print error to stderr, return without crashing |
| Parse error (invalid format) | Print error to stderr with line info, return |
| Missing geometry ID in parameters | Print error, return |
| Missing constraint ID in parameters | Print error, return |
| Output file creation failure | Print error to stderr, return |

## Module Test

### Unit Tests

| Test | Description |
|------|-------------|
| `test_read_valid_file` | Read g1.txt → verify Manager contents |
| `test_read_missing_file` | Read non-existent file → error message, empty Manager |
| `test_read_empty_rigidsets` | File with 0 rigid sets → empty rigidSets vector |
| `test_read_geometry_types` | Verify Point, Line, Plane types parsed correctly |
| `test_read_constraint_types` | Verify all 5 constraint types parsed correctly |
| `test_read_parameters` | Verify geometry parameters read correctly |
| `test_read_constraint_values` | Verify constraint values read correctly |
| `test_dump_graph` | Dump Manager → verify output file contents |
| `test_dump_empty_path` | dumpGraph with empty path → no output file |
| `test_print_summary` | printSummary → verify console output format |

### Integration Tests

| Test | Description |
|------|-------------|
| `test_round_trip` | Read → Dump → Read again → verify Managers are equal |
| `test_g1_full_pipeline` | Read g1.txt → dump → verify output matches expected |

### Test Fixtures

- `fixtures/g1.txt` — Standard sample file (3 rigid sets, 5 geometries, 2 constraints)
- `fixtures/empty.txt` — File with 0 rigid sets, 0 geometries, 0 constraints
- `fixtures/large.txt` — Generated file with 1000 geometries
- `fixtures/expected_g1_graph.txt` — Expected output for round-trip test

## Module Performance

### Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| readGraph | O(G + C) | Linear in number of geometries and constraints |
| dumpGraph | O(G + C) | Linear in number of geometries and constraints |
| printSummary | O(G + C) | Linear in number of geometries and constraints |
| displayGraph | O(1) | Just launches a browser process |

### Performance Targets

| File Size | Geometries | Read Time | Write Time |
|-----------|-----------|-----------|-----------|
| Small | 100 | < 1ms | < 1ms |
| Medium | 10,000 | < 10ms | < 10ms |
| Large | 1,000,000 | < 1s | < 1s |

### I/O Bottlenecks

- File I/O is the bottleneck — not CPU processing
- For very large files, consider streaming parser instead of loading entire file
- Current implementation uses `ifstream >>` which is adequate for medium-sized files

## Module Scalability

### File Size Scalability

- Current implementation loads entire file into memory — limited by available RAM
- For files > 100MB, consider streaming parser
- Output file size is proportional to graph size

### Format Scalability

- Current format is simple text — easy to parse but verbose
- Future: consider binary format for large graphs
- Future: consider JSON/XML for interoperability

### Platform Scalability

- `displayGraph` has platform-specific browser launch commands (Windows/macOS/Linux)
- File path handling uses both `/` and `\` separators (cross-platform)
- No platform-specific file I/O — uses standard C++ streams

## Module Maintainability

### Code Organization

```
include/gcs/io.h    ← Function declarations
src/io.cpp          ← All IO implementation
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Free functions (not class) | Simple, no state needed for current functionality |
| `using namespace std` in .cpp | Implementation file only; headers use qualified names |
| `static_cast<int>(type)` for output | Backward compatibility with existing file format |
| Hardcoded output path | Matches existing project structure; should be configurable in future |

### Maintainability Practices

- Error messages are descriptive and include context (file name, ID)
- Parse errors return early without crashing
- Output format matches input format for round-trip compatibility
- Console output uses consistent formatting

### Known Technical Debt

| Issue | Priority | Fix |
|-------|----------|-----|
| Hardcoded output path `../x64/Debug/` | Medium | Make output directory configurable |
| No error codes or exceptions | Low | Return error codes or throw exceptions |
| `using namespace std` in .cpp | Low | Acceptable in implementation files only |
| No streaming for large files | Low | Add streaming parser if needed |

## Module Extensibility

### Adding a New File Format

1. Create new `IGraphReader` / `IGraphWriter` subclass (e.g., `JsonGraphReader`)
2. Register with `GraphIO` (Phase 2)
3. No changes to Core or other modules

### Extension Points

| Extension | Mechanism |
|-----------|-----------|
| New input format | Implement IGraphReader |
| New output format | Implement IGraphWriter |
| Custom visualization | Replace displayGraph with different launcher |
| Progress reporting | Add callback interface for large file reads |
| Binary format | Implement IGraphReader/Writer with binary serialization |

### Future Format Support

| Format | Use Case |
|--------|----------|
| JSON | Web API interoperability |
| Binary | Large graph performance |
| STEP/IGES | CAD system integration |
| SVG | 2D diagram output |

## Module Reusability

### Reuse Scenarios

| Scenario | How IO Supports It |
|----------|-------------------|
| Different file formats | IGraphReader/IGraphWriter interface (Phase 2) |
| Embedded in application | readGraph/dumpGraph can be called from any code |
| Batch processing | Call readGraph in a loop for multiple files |
| Testing | Test fixtures can be read/written easily |
| CI/CD integration | Console output can be captured and parsed |

### Reusability Principles

- IO depends only on Core — no dependency on DCM, LGS, or CDS
- readGraph populates a Manager without side effects
- dumpGraph reads from Manager without modifying it
- printSummary uses only const Manager reference
- displayGraph is the only function with external side effects (browser launch)
