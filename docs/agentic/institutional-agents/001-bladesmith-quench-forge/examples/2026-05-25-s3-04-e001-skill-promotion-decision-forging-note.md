# Experience Forging Note: S3-04 E001 Skill Promotion Decision

Date: 2026-05-25

Role: `Bladesmith: Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-25-s3-04-e001-skill-promotion-decision`
- Time range: 2026-05-25
- Source artifacts:
  - `.codex/skills/task-scoped-session-closer/SKILL.md`
  - `docs/agentic/experience/001-task-scoped-session-closure/promotion/2026-05-25-s3-04-skill-promotion-decision.md`
  - `docs/agentic/agile-pdca-roadmap.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | E001 has positive closure samples, a negative eval, a low-risk boundary, and S2-01 opt-in gate policy. |
| Decisions | Promote E001 into an active project skill while keeping default gate enforcement deferred. |
| Preferences | Promote recurring operating discipline as skills only after it has evidence and boundaries. |
| Hypotheses | A narrow skill description will reduce over-triggering on tiny work. |
| Open questions | Whether S2-05 should later make any E001 checks default. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Promote a process skill only after both positive and negative evidence exist. | A candidate process skill has repeated successful use. | Check for real closures, a failure eval, and an escape hatch before activation. | Do not install a skill from one good anecdote. | E001 S3-04 decision record | Applies to process skills, not module steward skills already required by architecture. |
| A skill can be active without becoming a default gate. | A practice is useful for agents but not ready as CI enforcement. | Promote the workflow skill and leave gate enforcement to a later phase. | Do not confuse human/agent operating guidance with automated blocking policy. | S2-01 opt-in policy plus S3-04 decision | S2-05 owns default gate promotion. |
| Skill descriptions must encode refusal boundaries. | A project skill could over-trigger. | Put low-risk exclusions in the description and entry rule. | Do not rely on memory of prior roadmap discussions. | Active skill frontmatter and Entry Rule | Future skill revisions may tighten triggers. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| Promoting E001 means all tasks need archives. | S1-04 explicitly permits chat-only and commit-note-only small work. | Evidence that small-task archives improve resumption. |
| Active skill promotion means default CI enforcement. | S2-01 designed opt-in gates and S2-05 owns default promotion. | Two clean opt-in task cycles and legacy policy. |

## Recommended Promotion

Choose one:

- update a skill.

Rationale: The task promoted E001 into `.codex/skills/task-scoped-session-closer`.

## Follow-Up

- Reassess institutional-agent candidates in S4-05 using the updated skill
  landscape.
- Implement S2-02 before relying on opt-in task-card gates.
