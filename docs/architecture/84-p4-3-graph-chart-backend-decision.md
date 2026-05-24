# P4.3 Graph And Chart Backend Decision

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Warm Evidence Tokens**

Governance owner:

- `gcs-third-party-governance-steward`

## Decision

`ThirdPartyDecision`: defer external graph and chart backends for P4.4.

P4.4 should rebuild Figure 71 with the current repo-native pipeline:

- semantic figure spec in `tools/architecture_visualization/specs/figure71.yaml`;
- shared editorial seed in `tools/architecture_visualization/figure1.theme.json`;
- layout-aware HTML/CSS compositor in
  `tools/architecture_visualization/figure71_html_compositor.py`;
- browser export smoke in `tools/architecture_visualization/browser_export.py`;
- structural QA in `tools/architecture_visualization/figure_qa.py`;
- token lint in `tools/ui_qa/gcs_token_lint.py`.

No new graph, chart, JavaScript, Python, CMake, binary, or MCP dependency is
approved by P4.3.

## ThirdPartyRequest Assessment

| Field | P4.3 answer |
| --- | --- |
| Name | No accepted dependency. Candidate families are Graphviz/D2/ELK for graph panels and Vega-Lite/Observable Plot for chart panels. |
| Version | Not selected. |
| Upstream URL | Not selected. |
| License | Not accepted yet; future request must record license before adoption. |
| Scope | Future optional tooling-only figure panel compiler, not solver/runtime code. |
| Provider order | Current repo-native compositor first; future installed CLI/package second; vendored source third; opt-in network fetch only by explicit request. |
| Build options | None added. |
| Exposed targets | None added. |
| Update procedure | Not needed until a dependency is accepted. |

## Rationale

Figure 71 is currently an execution-map figure with compact panel narratives,
tokenized evidence arcs, and browser-rendered review artifacts. It does not
yet contain a graph layout problem or quantitative chart panel that justifies a
new backend.

Adding a graph/chart package before P4.4 would increase dependency, licensing,
offline-build, and artifact-rebuild risk without improving the immediate
asset-rebuild objective. P5.1 already guards token drift, and P4.2 already
proved browser-rendered review export. The next improvement should therefore be
asset rebuild and prototype demotion, not package expansion.

## Provider Order For Future Reconsideration

If a future figure requires graph/chart backends, use this order:

1. Existing repo-native HTML/CSS/SVG generators.
2. Installed local CLI or package with documented version and license.
3. Vendored source under `third_party/` with metadata.
4. Explicit opt-in network fetch only when a human requests it and offline
   behavior is documented.

Default configure/build/test paths must not require network access.

## CMake And Runtime Impact

Current decision impact:

- no CMake target changes;
- no production solver dependency changes;
- no test-only dependency changes;
- no global include or library path changes;
- no binary artifacts added;
- no ABI/runtime compatibility impact.

Future accepted dependencies must expose narrow imported or alias targets and
must remain outside production solver targets unless separately justified.

## Offline Behavior

P4.3 preserves the current offline behavior. Figure generation and QA continue
to use repository Python scripts plus an optional installed browser CLI for
review export. If no browser CLI is available, the browser smoke records a
skipped manifest rather than fetching tooling.

## Required Tests And Audit Gates

For P4.4 under this decision:

- `python -B tools\ui_qa\gcs_token_lint.py`
- `python -B tools\architecture_visualization\browser_export.py --figure figure71 --formats png,pdf --render-html`
- `python -B tools\architecture_visualization\figure_qa.py --figure figure71`
- `git diff --check`

If a future step proposes a graph/chart dependency, add:

- dependency metadata with name, version, URL, license, scope, and update
  procedure;
- offline configure behavior;
- CMake adapter or CLI invocation boundary;
- license/SBOM audit record;
- provider fallback test.

## Downstream Update

- P4.4 may proceed without adding graph/chart dependencies.
- P5.2/P5.3 should add rendered text/layout integrity gates before revisiting
  richer panel backends.
- P6.4 should judge Figma MCP after repo-native rebuild, QA, and showcase work
  are stable.
