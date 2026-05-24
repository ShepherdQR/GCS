# Experience Forging Note: P4 Scientific Figure Pipeline Phase Close

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p4-scientific-figure-pipeline-phase-close`
- Time range: P4 phase closure after P4.1-P4.4
- Source artifacts:
  - `docs/architecture/86-p4-scientific-figure-pipeline-phase-close.md`
  - `docs/architecture/76-ui-design-system-execution-plan.md`
  - `docs/architecture/82-ui-design-next-work-plan.md`
  - `docs/completed-tasks/2026-05-24-p4-scientific-figure-pipeline-phase-close/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | P4 completed schema, browser export, dependency decision, and Figure 71 rebuild. |
| Decisions | P4 is closed; P5 is active; P5.2 is next; Figma MCP remains deferred. |
| Preferences | Close a phase with explicit residual risks before starting the next gate family. |
| Hypotheses | The next high-leverage aesthetic work is measurable visual QA, not more pipeline scaffolding. |
| Open questions | Which screenshot backend should become stable enough for P5.4. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Phase close should name residual risk, not only completion. | A phase has all planned steps done. | Record what the phase proved and what it still cannot prove. | Do not let "Done" imply later gates are unnecessary. | P4 close names overflow, overlap, contrast, and screenshot risk for P5. | Applies to phase transitions, not tiny single-step fixes. |
| Make the next phase active in the persisted plan. | A phase closes and the roadmap continues. | Update the active phase and next step in the next-work plan. | Do not rely on conversational memory for continuation. | `82-ui-design-next-work-plan.md` now makes P5 active and P5.2 next. | Applies whenever the user asks for continuous execution. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "P4 close means visual quality is solved." | P4 solved production path; P5 must still solve visual integrity gates. | P5.2/P5.3/P5.4 results. |
| "Now install Figma MCP." | Repo-native QA and showcase evidence are not mature enough yet. | P6.4 governance decision after P6.3. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Every phase close should explicitly update the active phase, next step, stable
decisions, and residual risks.

## Follow-Up

- Use this phase-close shape for P5 after screenshot baselines land.
- Keep Figma MCP deferred until the planned P6.4 decision.
