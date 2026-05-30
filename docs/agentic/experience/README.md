# Agentic SE Experience Library

Persist promoted agentic software-engineering lessons here. Each experience is
a folder, not a loose note, so the lesson can carry its explanation, candidate
skills, agent role cards, templates, prompts, eval ideas, and later evidence.

## Folder Contract

Use this shape for every promoted experience:

```text
docs/agentic/experience/
  NNN-short-experience-slug/
    README.md
    skills/
      <candidate-skill>/SKILL.md
    agents/
      <agent-role>.md
    templates/
      <artifact-template>.md
```

The folder `README.md` should answer:

- what recurring practice was learned;
- what problem or risk it controls;
- what theory, invariant, or operating model generalizes it;
- what artifacts make the lesson executable;
- what evidence or future gate would validate it.

Use `../experience-record-template.md` as the minimum record shape, then add
supporting material when the experience is ready to become reusable practice.
Promote lessons only after evidence shows they are recurring, high severity, or
important enough to define project operating discipline.

Do not store raw chat logs. Preserve distilled decisions, process evidence,
templates, and agent-facing instructions.

## Index

| ID | Experience | Status |
| --- | --- | --- |
| E001 | [Task-scoped session closure](001-task-scoped-session-closure/README.md) | active skill |
| E002 | [Phase-step summary-update-commit-continue](002-phase-step-summary-update-commit-continue/README.md) | promoted |
| E003 | [Git session branch governance](003-git-session-branch-governance/README.md) | candidate agent/skill |
| E004 | [AI governance queue control](004-ai-governance-queue-control/README.md) | candidate experience |
| E005 | [Repository audit value loop](005-repository-audit-value-loop/README.md) | candidate experience |
| E006 | [Parallel agent pipeline implementation](006-parallel-agent-pipeline-implementation/README.md) | candidate experience |
