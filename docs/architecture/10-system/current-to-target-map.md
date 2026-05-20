# Current To Target Map

The current repository is small and intentionally flat. The next rewrite should
use it as a set of historical prototypes, not as the final architecture.

## Existing Or Staging Modules

| Current path | Current role | Target home |
| --- | --- | --- |
| `src/gcs/kernel` | Entity structs, enums, manager, behavior intent. | `kernel`, later split from runtime concerns. |
| `src/gcs/io_adapters` | Text/JSON scene loading and summaries. | `io_adapters`. |
| `src/gcs/incidence_graph` | Connected-component decomposition prototype. | `incidence_graph`, later separated from planning policy. |
| `src/gcs/diagnostics` | DOF/status/residual diagnostics prototype. | `diagnostics`. |
| `src/gcs/numeric_engine` | Numeric leaf solving prototype. | `numeric_engine`. |
| `src/gcs/session_runtime` | Demo orchestration facade. | `session_runtime`. |
| `apps/gcs_cli` | Command-line executable entry point. | Thin shell over `session_runtime`. |
| `python/gcs_viz` | Local Python visualization. | Viewer application consuming `viewer_bridge` outputs. |
| `fixtures/scene` | Examples and fixture scenes, including `verification/`. | Versioned scenario corpus. |
| removed legacy C++ test tree | Old handwritten C++ unit tests. | To be replaced by contract-driven verification suites. |

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

The current layout is intentionally closer to the target architecture than the
old flat project. If prototype names remain inside source files, prefer moving
them toward the directory responsibility rather than adding compatibility
folders.
