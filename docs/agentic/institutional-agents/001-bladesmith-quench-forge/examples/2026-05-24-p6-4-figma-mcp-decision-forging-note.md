# Experience Forging Note: P6.4 Figma MCP Decision

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p6-4-figma-mcp-decision`
- Time range: P6.4 third-party governance decision
- Source artifacts:
  - `docs/architecture/91-p6-4-figma-mcp-decision.md`
  - `docs/architecture/90-p6-3-showcase-figure-pipeline.md`
  - official Figma MCP documentation
  - `docs/completed-tasks/2026-05-24-p6-4-figma-mcp-decision/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figma offers official remote and desktop MCP paths, while GCS now has a repo-native Figure 72 HTML path. |
| Decisions | Defer install/configuration; allow only a future explicit pilot. |
| Preferences | External design tools should answer a concrete collaboration or editable-layout gap. |
| Hypotheses | A browser review PNG/PDF baseline may solve the next review need without Figma. |
| Open questions | Whether future external reviewers require a native Figma file. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Judge external design tooling against a working repo-native artifact. | Figma MCP becomes tempting after visual QA improves. | Compare it with Figure 72 HTML, not with an imagined future pipeline. | Do not install before a concrete gap is named. | `91-p6-4-figma-mcp-decision.md` records provider order and pilot gates. | Applies to optional design-surface tools. |
| Keep MCP out of default build and QA paths. | A tool depends on external service/app/client state. | Preserve offline default quality gates and make MCP pilot-only. | Do not make Figma login or desktop app a repo prerequisite. | Offline behavior section in the decision doc. | Ends if the project formally adopts Figma as source of truth. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Official MCP exists, so install it." | Capability is not the same as project need. | A named collaboration, editable-layout, or review gap. |
| "Repo-native HTML means Figma is never useful." | External reviewers or designers may later need native Figma canvas workflows. | A scoped pilot request with data-boundary plan. |

## Recommended Promotion

Choose one:

- update a governance checklist.

Rationale:

Optional MCP/design-surface tools should have a `ThirdPartyDecision` with
provider order, offline behavior, and pilot gates before installation.

## Follow-Up

- Prefer Figure 72 browser review artifacts before reopening Figma MCP.
- If a pilot is needed, use official remote Figma MCP first unless a desktop
  selection workflow is explicitly required.
