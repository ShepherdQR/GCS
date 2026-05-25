# Scene Counterexamples

This directory stores expected-failure scenes that capture real solver boundaries. They are not green fixtures. Each entry includes metadata with the current expected status, solver obstruction, provenance, and replay-history evidence.

When a solver improvement makes a counterexample pass, update its metadata and promote it into the appropriate positive regression or milestone library.

| Fixture | Class | Current status | Accepted | Geometry / constraints |
| --- | --- | --- | --- | ---: |
| `mixed_geometry_20g40c_singular_20260524` | `singular_regression_counterexample` | `NumericallySingular` | `False` | 20 / 40 |
