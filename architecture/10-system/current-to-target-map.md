# Current To Target Map

The current repository is small and intentionally flat. The next rewrite should
use it as a set of historical prototypes, not as the final architecture.

## Existing Modules

| Current name | Current role | Target home |
| --- | --- | --- |
| `core` | Entity structs, enums, manager, behavior intent. | `kernel` and `session_runtime`. |
| `io` | Text/JSON scene loading and summaries. | `io_adapters`. |
| `dcm` | Connected-component decomposition. | `incidence_graph` and `decomposition_planner`. |
| `lgs` | DOF/status/residual diagnostics. | `diagnostics`. |
| `cds` | Numeric leaf solving. | `numeric_engine`. |
| `app` | Demo orchestration facade. | `session_runtime` or thin executable shell. |
| `gcs_viz` | Local Python visualization. | `viewer_bridge` plus an external viewer app. |
| `scene` | Examples and test fixtures. | `fixtures` or `scenario_corpus`. |
| `test` | Hand-written C++ test executables. | `verification` suites. |

## Rename Intent

The target names are more precise:

- `kernel` is mathematical and durable; it is not a generic dumping ground.
- `incidence_graph` names the actual structure behind decomposition.
- `decomposition_planner` separates graph facts from solving decisions.
- `diagnostics` names explanation and certification, not "local solver".
- `numeric_engine` names a replaceable backend, not a product-specific acronym.
- `session_runtime` owns user command semantics, undo, and transactions.

## Migration Policy

During the rewrite:

1. define contracts first;
2. build the new `kernel`;
3. port fixtures into a versioned scenario corpus;
4. add graph and diagnostic layers before the numeric engine;
5. keep the current numeric solver only as a baseline backend;
6. add the viewer as a consumer of reports, not as owner of state.

The rewrite should avoid preserving old names just because they exist. Keep a
name only when it describes the new responsibility exactly.
