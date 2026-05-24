# Experience Forging Note: P4.3 Graph/Chart Backend Decision

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p4-3-graph-chart-backend-decision`
- Time range: P4.3 dependency-governance decision
- Source artifacts:
  - `docs/architecture/84-p4-3-graph-chart-backend-decision.md`
  - `docs/agentic/tasks/2026-05-24-p4-3-graph-chart-backend-decision.md`
  - `docs/completed-tasks/2026-05-24-p4-3-graph-chart-backend-decision/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figure 71 already has semantic spec, tokenized HTML compositor, browser smoke, figure QA, and token lint. |
| Decisions | P4.3 defers graph/chart backends for P4.4 and approves no new dependency. |
| Preferences | Prefer repo-native rebuild before adding renderer packages or Figma MCP. |
| Hypotheses | P4.4 can expose whether richer graph/chart backends are actually necessary. |
| Open questions | P6 showcase may later require a real graph or chart compiler. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Make non-adoption an explicit dependency decision. | A roadmap step asks whether to add a powerful external backend. | Record a `ThirdPartyDecision` even when the answer is "defer". | Do not let "no package yet" remain an implicit default. | `84-p4-3-graph-chart-backend-decision.md` records provider order and future metadata requirements. | Applies to dependency choices, not ordinary implementation details. |
| Ask whether the current figure actually has the problem a backend solves. | A graph/chart backend is attractive but not obviously necessary. | Match package capability to the current figure's semantic need before adoption. | Do not add layout engines for figures that only need editorial panel flow. | Figure 71 is still an execution-map narrative, not a graph-layout or data-chart figure. | Revisit when showcase panels need quantitative plots or nontrivial graph layout. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "Top-tier figures require adding graph/chart packages now." | P4.2 and P5.1 already provide repo-native browser export and token discipline. | A future figure spec that cannot be expressed with the current compositor. |
| "No dependency decision is needed when not adding a package." | Future agents need to know whether omission was deliberate or accidental. | Not applicable; P4.3 now records the deliberate decision. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Future dependency-adjacent roadmap steps should capture an explicit
non-adoption decision when the work chooses repo-native tooling.

## Follow-Up

- Use this decision as the P4.4 dependency boundary.
- Revisit graph/chart backends only after P4.4 and the P5 layout gates.
