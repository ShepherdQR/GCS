# IO Interface Test Specification

## Module Under Test

`gcs::io::readGraph`, `gcs::io::readGraphJSON`, `gcs::io::dumpGraph`, `gcs::io::dumpGraphJSON`, `gcs::io::printSummary`

## Interface Contract

- `readGraph` correctly parses the text scene format.
- JSON IO preserves structure, behavior intent, constraints, history, and parameters when present.
- Missing or invalid files are handled without crashing.
- `dumpGraph` produces text output that can be re-read.
- `printSummary` produces console output without crashing.

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| IO01 | `test_io_read_valid_file` | `readGraph` | Valid fixture | `readGraph(m, path)` | Manager has correct RS/Geom/Constr counts |
| IO02 | `test_io_read_missing_file` | `readGraph` | Missing path | `readGraph(m, path)` | Manager remains empty |
| IO03 | `test_io_read_rigidsets` | `readGraph` | File with 3 rigid sets | `readGraph(m, path)` | RS ids match |
| IO04 | `test_io_read_geometry_types` | `readGraph` | File with Point, Line, Plane | `readGraph(m, path)` | Geometry types match |
| IO05 | `test_io_read_geometry_params` | `readGraph` | File with non-zero params | `readGraph(m, path)` | Values match file |
| IO06 | `test_io_read_constraint_types` | `readGraph` | File with constraint types | `readGraph(m, path)` | Constraint types match |
| IO07 | `test_io_read_constraint_values` | `readGraph` | File with constraint values | `readGraph(m, path)` | Constraint values match |
| IO08 | `test_io_read_constraint_geometry_ids` | `readGraph` | File with multi-geometry constraints | `readGraph(m, path)` | Geometry IDs match |
| IO09 | `test_io_dump_round_trip` | `readGraph` + `dumpGraph` | Read file, dump, read dump | Compare managers | Same topology, params, values |
| IO10 | `test_io_dump_empty_path` | `dumpGraph` | Empty path | `dumpGraph(m, "")` | Returns immediately |
| IO11 | `test_io_print_summary` | `printSummary` | Populated Manager | `printSummary(m)` | No crash |

## Scene Fixtures

- `GCS/scene/test/io/basic_5g_2c.txt` - 3 RS, 5 Geom, 2 Constr
- `GCS/scene/test/io/malformed.txt` - Truncated file for error handling
