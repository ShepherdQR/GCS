# Institutional Agent Registry And Scorecard

Status: active
Date: 2026-05-26

## Purpose

This scorecard records the current maturity of GCS institutional agents. It is
a governance artifact, not a naming catalog: a role advances only when it has
clear boundaries, reusable prompts, templates, examples, and refusal or review
evals.

## Maturity Levels

| Level | Meaning | Promotion evidence |
| --- | --- | --- |
| Candidate | A useful repeated role has been named. | Trigger conditions and expected output are written. |
| Seed | The role has a prompt, template, eval, and at least one concrete example. | One real use case, explicit guardrails, and a stable home. |
| Practiced | The role has several examples across sessions or repeated reuse by one workflow. | Evidence that reuse reduces ambiguity or recurrence. |
| Promoted | The role is trusted as part of normal workflow for its boundary. | Multiple examples, refusal behavior, and index discoverability. |
| Institutional | The role is a standing project capability with ongoing maintenance. | Ownership, operating standard, evals, and review cadence. |

## Current Registry

| ID | Agent | Current maturity | Evidence package | Score | Next action |
| --- | --- | --- | --- | ---: | --- |
| I001 | Bladesmith: Quench-Forge | Promoted | Prompt, template, refusal eval, and 20+ examples under `001-bladesmith-quench-forge/`. Promotion note: `promotion-20260527.md`. | 10/10 | Keep periodic stale-rule review; separate repeated pressure from one-off preference. |
| I002 | Tailor: Stitch-Timeline | Practiced, promoted seed | Prompt, template, refusal eval, and 4 timeline examples under `002-tailor-stitch-timeline/`. | 8/10 | Add separate architecture, agentic-SE, and fixture timeline examples when those threads diverge. |
| I003 | Atelier Steward: Calibrate-Review | Seed | Prompt, template, refusal eval, and one Figure 72 convention-fit example under `003-atelier-steward-calibrate-review/`. | 6/10 | Collect two more UI or figure reviews before promotion. |
| I004 | Art Director: Frame-Judge | Seed | Prompt, template, refusal eval, and one Figure 72 visual-review example under `004-art-director-frame-judge/`. | 6/10 | Require rendered-artifact evidence for every new example; avoid approval without visual input. |
| I005 | Acceptance Officer: Evidence-Gate | Seed | Prompt (`005-acceptance-officer/README.md`), gate template (`templates/acceptance-report-template.md`), refusal eval (`evals/refuse-evidence-free-acceptance.md`). | 5/10 | Collect two real acceptance reviews on completed tasks before promotion. |

## Score Dimensions

| Dimension | Weight | What good looks like |
| --- | ---: | --- |
| Contract clarity | 2 | Mission, trigger rhythm, inputs, outputs, and guardrails are explicit. |
| Prompt usability | 1 | A scoped invocation prompt exists and is easy to reuse. |
| Template usability | 1 | Output shape is durable enough for later sessions. |
| Eval or refusal coverage | 2 | The role has at least one negative eval or refusal case. |
| Example evidence | 2 | Real examples show the role operating under pressure. |
| Boundary discipline | 1 | The role knows what it must not decide. |
| Index discoverability | 1 | The role is findable from the institutional-agent directory and related docs. |

Scores are directional. They are intended to guide promotion decisions, not to
rank the roles by importance.

## Role Notes

### I001 Bladesmith

The Bladesmith is the strongest role by evidence volume. It captures reusable
lessons from completed tasks, visual pipeline work, gate policy, replay
evidence, and cleanup sessions. Its main governance risk is over-promotion:
because it has many examples, it must still separate repeated pressure from
one-off preference.

Next useful eval:

- refuse turning a single successful shortcut into a project rule without a
  second example or explicit provisional label.

### I002 Tailor

The Tailor has enough examples to be trusted for stitching multi-session state.
It is especially important when commits, task archives, and roadmap docs are
spread across sessions. Its main risk is invented causality: timeline entries
must not explain motives that are not present in evidence.

Next useful eval:

- refuse to merge two adjacent events into one causal story when the archives
  do not support that connection.

### I003 Atelier Steward

The Atelier Steward is useful but still early. It protects named design-system
conventions and should stay seed-level until more UI or figure artifacts are
reviewed against the same convention language.

Next useful eval:

- reject a UI change that claims convention compliance but does not name the
  governing convention or step.

### I004 Art Director

The Art Director is a complementary visual reviewer. It judges hierarchy,
taste, readability, and evidence clarity after an artifact exists. Its refusal
behavior is more important than its approval behavior: it must not approve a
visual claim without seeing the rendered surface.

Next useful eval:

- refuse final approval when only source text or a figure description is
  provided.

### I005 Acceptance Officer

The Acceptance Officer is the independent evidence gate. It inspects completed
work against its own claims and refuses evidence-free completion. Its seed
package (prompt, gate template, refusal eval) was created 2026-05-28. It has
not yet been exercised on a real task — the first real acceptance review is
the next milestone.

Next useful eval:

- refuse acceptance when git diff includes files outside the task card's
  affected paths (scope mismatch).

## Candidate Backlog

| Candidate | Trigger | Evidence needed before seed |
| --- | --- | --- |
| Governance Sentinel | Permission, PR audit, or automation claims are changing. | One prompt, one review template, and refusal eval for unauthorized approval or merge. |
| Git Session Steward | Git branch, worktree, push, or session-ownership operations. | Pre-mutation checklist template, refusal eval for pushing master with unrelated ahead commits, and one real push-safety intervention. |
| Demo Producer | A product demo package is created or refreshed. | Demo-package template, command-transcript standard, and one demo archive. |
| Benchmark Scout | External solver comparison or benchmark candidates are proposed. | Comparison criteria, source-citation standard, and one rejected weak benchmark example. |
| Release Shepherd | Release readiness or packaging docs become active. | Release checklist, distribution non-goals, and evidence gate mapping. |
| Night-Watch | Nightly diagnostics, repository health checks, or scheduled patrol. | Real nightly run with findings, dated run directory, and one refusal eval for unauthorized commit/push. |
| Acceptance Officer | A non-trivial task claims completion and is ready for archive. | One prompt, gate template, and refusal eval for evidence-free acceptance. |
| Collation Officer | Documentation and implementation may have diverged; consistency audit needed. | One prompt, consistency report template, and one real cross-read with specific citations. |
| Bookkeeper | Cost-benefit questions arise or session efficiency needs analysis. | Budget ledger template, one real cost-vs-value report, and directional cost estimates. |
| Gardener | Small frictions accumulate; stale references need batch cleanup. | Maintenance record template, one real batch with before/after verification, and escalation criteria. |

## Promotion Rule

Do not promote a role because the name is appealing. Promote when the role has:

1. a recurring trigger;
2. a bounded decision surface;
3. a prompt and output template;
4. at least one negative or refusal eval;
5. enough real examples to show that future sessions will behave better with
   the role than without it.

## Review Cadence

Review this scorecard when:

- a new institutional agent is added;
- a seed agent gains a second or third real example;
- a promoted role creates a project rule or skill update;
- an eval fails or a role overclaims authority;
- the agentic organization map changes.
