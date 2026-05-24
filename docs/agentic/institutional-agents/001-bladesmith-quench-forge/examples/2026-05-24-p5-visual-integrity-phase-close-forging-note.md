# Experience Forging Note: P5 Visual Integrity Phase Close

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p5-visual-integrity-phase-close`
- Time range: P5 phase-close planning
- Source artifacts:
  - `docs/architecture/87-p5-visual-integrity-phase-close.md`
  - `docs/architecture/76-ui-design-system-execution-plan.md`
  - `docs/architecture/82-ui-design-next-work-plan.md`
  - `docs/completed-tasks/2026-05-24-p5-visual-integrity-phase-close/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | P5 now has default gates for tokens, text overflow, overlap, contrast, and screenshot baselines. |
| Decisions | Keep taste judgment reviewer-only until P6 produces more examples. |
| Preferences | Phase close should separate executable checks from art-direction judgment. |
| Hypotheses | P6 showcase work will reveal whether external design-surface tooling is worth adding. |
| Open questions | Whether Figma MCP adds enough value after the repo-native showcase exists. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Close a visual QA phase by naming gate ownership. | A phase adds several checks with different levels of determinism. | Split default quality gates from reviewer-only gates. | Do not pretend taste checks are deterministic too early. | `87-p5-visual-integrity-phase-close.md` records both lists. | Applies at phase boundaries. |
| Move from infrastructure to showcase once gates are stable. | The same figure has passed token, text, overlap, contrast, and screenshot gates. | Start the integrated showcase instead of adding more checks around one artifact. | Keep residual risks visible. | P6.1 is the next step in `82-ui-design-next-work-plan.md`. | Ends when a new artifact family exposes new failure modes. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Every aesthetic judgment should become an automated gate." | Some judgments are editorial and need artifact context. | More showcase artifacts and repeated review patterns. |
| "Figma MCP is now obviously necessary." | P5 strengthened repo-native QA but did not yet test showcase collaboration needs. | P6.3 showcase output and P6.4 governance decision. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

At every phase close, record which checks are executable defaults and which
remain named human-review gates.

## Follow-Up

- Use the same default/reviewer-only split when P6 closes.
- Feed the P6.4 Figma MCP decision with actual showcase evidence, not tool
  enthusiasm.
