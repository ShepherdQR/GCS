# IO Interface Test Specification

## Module Under Test

`gcs::io::readGraph`, `gcs::io::dumpGraph`, `gcs::io::printSummary`

## Interface Contract

- `readGraph` correctly parses all sections of the file format
- `readGraph` handles missing/invalid files gracefully
- `dumpGraph` produces output that can be re-read (round-trip)
- `printSummary` produces console output without crashing

## Test Cases

| Test ID | Test Name | Interface | Arrange | Act | Assert |
|---------|-----------|-----------|---------|-----|--------|
| IO01 | `test_io_read_valid_file` | `readGraph` | Write valid test file to disk | readGraph(m, path) | Manager has correct RS/Geom/Constr counts and values |
| IO02 | `test_io_read_missing_file` | `readGraph` | Use non-existent path | readGraph(m, "nonexistent.txt") | Manager remains empty, no crash |
| IO03 | `test_io_read_rigidsets` | `readGraph` | File with 3 rigid sets | readGraph(m, path) | m.rigidSets.size()==3, ids match |
| IO04 | `test_io_read_geometry_types` | `readGraph` | File with Point, Line, Plane | readGraph(m, path) | Each geometry has correct GeometryType |
| IO05 | `test_io_read_geometry_params` | `readGraph` | File with non-zero params | readGraph(m, path) | g.v[0..5] match file values |
| IO06 | `test_io_read_constraint_types` | `readGraph` | File with all 5 constraint types | readGraph(m, path) | Each constraint has correct ConstraintType |
| IO07 | `test_io_read_constraint_values` | `readGraph` | File with constraint values | readGraph(m, path) | c.value matches file values |
| IO08 | `test_io_read_constraint_geometry_ids` | `readGraph` | File with multi-geometry constraints | readGraph(m, path) | c.geometryIds match file |
| IO09 | `test_io_dump_round_trip` | `readGraph` + `dumpGraph` | Read file → dump → read dump | Compare 2 Managers | Same topology, params, values |
| IO10 | `test_io_dump_empty_path` | `dumpGraph` | Pass empty string | dumpGraph(m, "") | Returns immediately, no file created |
| IO11 | `test_io_print_summary` | `printSummary` | Populate Manager | printSummary(m) | No crash (output to stdout) |

## Scene Fixtures

- `GCS/test/io/basic_5g_2c.txt` — 3 RS, 5 Geom, 2 Constr
- `GCS/test/io/malformed.txt` — Truncated file for error handling test
