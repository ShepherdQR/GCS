# P6.4 Figma MCP Decision

Snapshot date: 2026-05-24.

Governing conventions:

- **GCS Scientific Figure Pipeline**
- **GCS Visual Integrity Gate**
- **GCS Art Director Review**
- **GCS Warm Evidence Tokens**

Governance owner:

- `gcs-third-party-governance-steward`

External sources checked:

- Figma developer docs: <https://developers.figma.com/docs/figma-mcp-server/>
- Figma help center remote/desktop comparison:
  <https://help.figma.com/hc/en-us/articles/35281385065751-Figma-MCP-collection-Compare-Figma-s-remote-and-desktop-MCP-servers>
- Figma desktop setup docs:
  <https://developers.figma.com/docs/figma-mcp-server/local-server-installation/>

## Decision

`ThirdPartyDecision`: defer installing or configuring Figma MCP for this
repository now.

Approve only a future, explicitly scoped pilot if P6/P7 work reveals a concrete
collaboration, editable-layout, or external review gap that the repo-native
HTML pipeline cannot cover.

No Figma MCP server, plugin, connector, package, generated Figma file, token, or
workspace configuration is approved by P6.4.

## Why

The repo-native path is now strong enough to be the default:

- Figure 72 has a semantic brief, enriched fixture evidence, tokenized HTML
  production artifact, freshness gate, text budgets, layout boxes, and contrast
  markers.
- Default quality gates cover token lint, showcase fixture evidence, showcase
  HTML freshness, text overflow, overlap/contrast, screenshot baseline, CTest
  public evidence, and CLI showcase smoke.
- The remaining Figure 72 gap is a review/export choice: browser PNG/PDF
  baseline versus external Figma review surface. It is not yet a blocker.

Figma's official docs position MCP as useful for design context, writing native
Figma content, code generation from selected frames, variables/components, and
Figma-to-code workflows. Those are valuable when a design file is the source of
truth. In GCS today, the source of truth is repo evidence: scene JSON, metadata,
theme tokens, HTML compositors, and executable gates.

## ThirdPartyRequest Assessment

| Field | P6.4 answer |
| --- | --- |
| Name | Figma MCP server, official remote or desktop variant. |
| Version | Service-managed; no pinned package or local vendored version selected. |
| Upstream URL | `developers.figma.com/docs/figma-mcp-server/` |
| License | Service/tool governed by Figma terms; no repo license artifact accepted. |
| Scope | Optional visual review/design collaboration workflow only; not solver/runtime/build/test code. |
| Provider order | Repo-native HTML/P5 gates first; optional official remote Figma MCP pilot second; official desktop MCP third if selection-based local workflow is required; no unofficial/community MCP without separate security review. |
| Build options | None. |
| Exposed targets | None. |
| Update procedure | Not needed until a pilot is accepted; future pilot must record client, access model, data boundary, and export artifacts. |

## Provider Order

1. **Repo-native production path**:
   `figure72.yaml` -> enriched showcase metadata -> HTML compositor -> P5
   visual-integrity gates -> optional browser export/baseline.
2. **Official remote Figma MCP pilot** if the project needs shared browser-based
   Figma review or write-to-canvas evaluation.
3. **Official desktop Figma MCP pilot** only when selection-based desktop
   context is specifically required.
4. **Unofficial MCP servers** are rejected until a separate security and
   dependency review records package, license, permissions, and data flow.

## CMake And Runtime Impact

Current decision impact:

- no CMake target changes;
- no production solver dependency changes;
- no test-only dependency changes;
- no global include or library path changes;
- no binary artifacts added;
- no ABI/runtime compatibility impact;
- no MCP client configuration committed.

Figma MCP must remain outside solver/runtime targets. If used later, it should
be a local design-review workflow, not a build prerequisite.

## Offline Behavior

P6.4 preserves offline default behavior.

Default configure, build, tests, visual-integrity gates, and showcase figure
checks must continue without network, Figma login, Figma desktop app, or remote
MCP access.

The official remote server is hosted by Figma and therefore not an offline
dependency. The official desktop flow requires the Figma desktop app and a local
MCP endpoint. Neither belongs in default quality gates.

## Required Tests And Audit Gates For A Future Pilot

Before any future Figma MCP pilot is accepted, add a short pilot request with:

- target artifact and reason the repo-native HTML path is insufficient;
- official remote or desktop provider choice;
- Figma account/seat/access assumptions;
- data boundary: which scene, image, or design data may leave the repo;
- write policy: whether tools may write native Figma content or download assets;
- artifact handoff: Figma file URL or exported review artifact;
- comparison against `figure72-gcs-integrated-showcase-scene.html`;
- rollback plan and proof that default quality gates stay offline.

Minimum validation:

```bat
python tools\agentic_design\agentic_toolkit.py run-quality-gates
```

The pilot must not replace repo-native evidence checks.

## Downstream Plan

Immediate next aesthetic work should be repo-native:

1. add a browser-rendered Figure 72 PNG/PDF review artifact if external review
   is needed;
2. add a screenshot-baseline entry for that review artifact if it becomes
   stable;
3. run `GCS Art Director Review` on Figure 72 HTML or browser review output;
4. revisit Figma MCP only if that review exposes a collaboration/editable-layout
   need that cannot be addressed by the HTML pipeline.

## Decision Acceptance

P6.4 is accepted because:

- Figma MCP was judged after P5 visual QA and P6 showcase evidence existed;
- the decision records provider order, scope, license/version boundary, offline
  behavior, CMake/runtime impact, and future audit gates;
- no dependency or MCP configuration is added prematurely;
- the next repo-native review path is explicit.
