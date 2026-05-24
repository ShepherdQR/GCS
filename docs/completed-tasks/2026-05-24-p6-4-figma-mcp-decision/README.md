---
task_id: 2026-05-24-p6-4-figma-mcp-decision
status: complete
session_goal: "Judge whether Figma MCP should be installed or configured after P5/P6 repo-native visual work."
archive_target: docs/completed-tasks/2026-05-24-p6-4-figma-mcp-decision/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-4-figma-mcp-decision-forging-note.md
---

# P6.4 Figma MCP Decision

## Task Objective

Decide whether to install or configure Figma MCP now that GCS has repo-native
visual-integrity gates and a Figure 72 HTML showcase artifact.

## Scope And Non-Goals

In scope:

- check official Figma MCP documentation;
- record a third-party governance decision;
- define provider order, scope, offline behavior, and future audit gates;
- update roadmap and archive the decision.

Out of scope:

- installing Figma MCP;
- configuring MCP clients;
- creating a Figma file;
- adding unofficial Figma MCP packages.

## Interaction Summary

P6.4 was intentionally delayed until after P5 gates and P6 showcase evidence.
After Figure 72 became a repo-native HTML production artifact, the decision
could compare Figma MCP against a concrete alternative rather than tool
enthusiasm.

## Work Completed

- Added `docs/architecture/91-p6-4-figma-mcp-decision.md`.
- Recorded `ThirdPartyDecision`: defer install/configuration now; allow only a
  future explicit pilot if a collaboration/editable-layout gap appears.
- Recorded provider order, license/version boundary, offline behavior,
  CMake/runtime impact, and future audit gates.
- Updated roadmap docs to mark P6.4 complete.
- Added this completed-task archive and a Bladesmith process note.

## Files And Artifacts

- `docs/architecture/91-p6-4-figma-mcp-decision.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/agentic/tasks/2026-05-24-p6-4-figma-mcp-decision.md`
- `docs/completed-tasks/2026-05-24-p6-4-figma-mcp-decision/README.md`

## Evidence

```text
Official Figma docs checked:
- https://developers.figma.com/docs/figma-mcp-server/
- https://help.figma.com/hc/en-us/articles/35281385065751-Figma-MCP-collection-Compare-Figma-s-remote-and-desktop-MCP-servers
- https://developers.figma.com/docs/figma-mcp-server/local-server-installation/

python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p6-4-figma-mcp-decision.md
Passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p6-4-figma-mcp-decision\README.md
Passed.

python tools\agentic_design\agentic_toolkit.py validate-docs
Passed.

git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
Passed with only existing CRLF conversion warnings.
```

## Decisions

- Decision: do not install or configure Figma MCP now. Rationale: Figure 72
  already has a repo-native HTML production path and default visual-integrity
  gates.
- Decision: allow a future official remote Figma MCP pilot only if a concrete
  collaboration, editable-layout, or review gap appears. Rationale: official
  docs position remote MCP as the broadest current feature path, but GCS does
  not yet need a Figma file as source of truth.
- Decision: reject unofficial/community Figma MCP packages for now. Rationale:
  they need separate license, permissions, security, and data-flow review.

## Skipped Checks And Risks

- Full build and CTest were skipped because this was documentation-only
  third-party governance following a full P6.3 quality-gate pass.
- Figma MCP capability and access terms may change; future pilots must recheck
  official docs.
- Figure 72 still lacks a browser PNG/PDF baseline.

## Follow-Up

- Prefer a repo-native Figure 72 browser review PNG/PDF and screenshot baseline
  before reopening Figma MCP.
- Revisit Figma MCP only with a specific pilot request and data-boundary plan.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-24-p6-4-figma-mcp-decision/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-4-figma-mcp-decision-forging-note.md`
- Skill, eval, fixture, or tool update needed: none now; a future pilot should
  create a separate third-party request.
