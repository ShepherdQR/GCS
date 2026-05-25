# S3-04 E001 Skill Promotion Decision

Date: 2026-05-25

Decision: promote E001 into the active project skill
`.codex/skills/task-scoped-session-closer`.

## Evidence Considered

Positive closure samples:

- C001 four-phase Agentic SE roadmap bootstrap scored 38/40.
- Step 47 runtime replay evidence export scored 37/40.
- Step 50 replay evidence workflow review scored 38/40.
- S2-01 opt-in gate policy scored 36/40.

Negative and boundary evidence:

- S3-02 added a negative eval for false completion and archive pollution.
- S1-04 defined the low-risk chat-only boundary.
- S2-01 designed opt-in quality-gate behavior so E001 does not become default
  archive enforcement too early.

## Decision Rationale

Promote now because the pattern is recurring, has multiple real task samples,
has a negative eval, and has a low-risk escape hatch. The active skill should
make the practice easier to invoke for future non-trivial tasks.

Do not promote E001 into a default quality gate yet. The skill is an operating
workflow; S2-02 through S2-05 still own executable opt-in gates, legacy archive
policy, and possible default enforcement.

## Skill Boundary

The active skill applies to:

- non-trivial, multi-step, or medium/high-risk GCS work;
- tasks involving commits, pushes, repository cleanup, quality gates, fixtures,
  architecture docs, or institutional-agent artifacts;
- tasks that need completed-task archives and future resumption.

The active skill does not apply to:

- tiny chat-only status answers;
- typo/link/index-only edits that can be captured by a commit note;
- raw transcript archiving;
- forced validation of all legacy completed-task records.

## Follow-Up

- S2-02 should implement task-card include tests for opt-in gates.
- S4-05 should reassess institutional agents now that E001 has an active
  closure skill and Bladesmith/Tailor have multiple real examples.
- E001 should stay out of default quality gates until S2-05.
