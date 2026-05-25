# Enterprise Agentic PR Workflows

Date: 2026-05-25

## Question

How do mature coding-agent systems turn autonomous work into reviewable
software governance artifacts?

## Pattern

The leading workflow is branch-first and PR-centered:

1. A human gives scoped intent.
2. The agent runs in an isolated local, cloud, CI, or worktree environment.
3. The agent records actions, changes, tests, and failures.
4. The output becomes a branch, diff, PR, or review comment.
5. Humans inspect, request changes, approve, or discard.

Codex cloud, Copilot cloud agent, Claude Code GitHub Actions, and Jules all
fit this shape. They differ in product surface, but not in the core governance
contract.

## Enterprise Lessons

### The agent should inherit normal engineering flow

OpenAI Codex works against repositories and can create pull requests. GitHub
Copilot cloud agent places research, planning, edits, branch creation, commits,
pushes, and optional PR creation inside GitHub. Jules gives task summaries and
branch/PR publishing after async work. The common lesson is that an agent
should not create a parallel shadow engineering process. It should make normal
PR review more explicit.

### The PR should explain intent, not only show a diff

GitHub PR guidance asks authors to tell reviewers what feedback they need and
how to review multi-file changes. Agentic PRs need this even more because a
generated diff may be plausible locally while missing project intent. The PR
description should state:

- task intent;
- class of change;
- review order;
- tests and checks;
- residual risk;
- generated-vs-human-authored portions;
- whether this is exploratory, repair, or release-ready.

### Background agents should be interruptible and discardable

Vendor products expose background operation, but keep the final integration as
a review action. GCS should mirror that: a background job may produce findings
or a branch, but a human decides whether it becomes a durable task, PR, or
fixture.

## GCS Implications

GCS already has task cards and completed-task archives. A PR should connect
those records to the review surface:

- every non-trivial PR links to a task card or explains the low-risk exception;
- every high-risk PR links to evidence and affected contracts;
- every PR states whether it changes solver truth, agentic process, tests,
  fixtures, UI/viewer behavior, IO schema, or docs only;
- every PR records skipped checks as risk, not as pass.

## Recommended PR Classes

| Class | Meaning | Required review posture |
| --- | --- | --- |
| `architecture` | Durable rule or module-boundary change | Architecture steward review plus docs validation |
| `solver-contract` | C++ public contract, reports, state, diagnostics, IO | Module steward review plus build/CTest evidence |
| `quality-gate` | Test, fixture, CI, or validation behavior | Quality steward review and focused test evidence |
| `agentic-process` | Task cards, archives, skills, automations, lifecycle rules | Agentic artifact gates and closure review |
| `exploratory` | Research or discovery branch that may not merge | Draft PR, explicit non-merge goal, bounded outputs |
| `repair` | Fix proposed after review/diagnostic finding | Finding link, minimal diff, revalidation |
| `docs-only` | Non-semantic documentation update | Docs validation or explicit skip reason |

## Failure Modes To Watch

- A PR is large because the agent chased adjacent cleanup.
- A PR changes project policy without a task card or roadmap update.
- A generated PR contains no evidence of verification.
- A PR treats AI review as approval.
- A PR changes fixtures or generated data without provenance.
- A PR adds instructions that contradict module skills or architecture docs.

## GCS Decision

Adopt a PR audit protocol rather than a separate agent-only workflow. The PR is
the integration object; task cards and archives are the durable memory; quality
gates are the executable evidence.
