# PR Audit And Review Quality

Date: 2026-05-25

## Question

What should AI-assisted PR review do, and what should it never be allowed to
decide?

## Pattern

AI review is strongest as a first-pass or second-pass filter over serious
issues, missed evidence, policy drift, and review routing. It is weak as a
final authority because it can miss contextual issues, over-comment on low
value concerns, and fail to understand project intent.

## Evidence From Products

Codex code review is positioned as a high-signal review pass focused on serious
issues. It follows repository guidance and can be asked to fix a P1 issue in
the same PR context when permitted.

GitHub Copilot code review explicitly leaves a comment review, not an approval
or request-changes review. It does not count toward required approvals and does
not block merging. This is a healthy default for GCS: automated review can
inform reviewers without replacing them.

Claude Code Review uses repository guidance files and queues review requests
when another review is running. This supports a queueing model for GCS nightly
diagnostics: do not run overlapping PR audits against the same branch.

## Evidence From Research

SWE-PRBench reports that frontier AI reviewers detected only a minority of
human-flagged issues in its benchmark. Large-scale PR studies report that
agentic PR failure correlates with broad diffs, many touched files, CI failure,
unwanted features, duplicate work, and misalignment with reviewer intent.

The practical conclusion is that AI review should be treated as a triage and
focus mechanism. It should not be treated as an oracle.

## GCS Review Quality Model

GCS PR audit should score review readiness across five dimensions:

| Dimension | Audit question | Example evidence |
| --- | --- | --- |
| Intent fit | Does the diff match the task request and non-goals? | Task card, PR summary, changed-file list |
| Boundary fit | Does ownership remain inside the right module/process layer? | Architecture map, module skill, dependency check |
| Evidence fit | Were the right tests or validators run for the risk? | Quality-gate output, focused tests |
| Risk fit | Are skipped checks, generated artifacts, and repair limits named? | Evidence bundle, skipped-check section |
| Review fit | Does the PR tell humans what to inspect first? | Review focus and file order |

## PR Audit Output Contract

An audit should emit:

- `decision`: `ready_for_human_review`, `needs_author_revision`,
  `needs_human_gate`, `exploratory_only`, or `blocked`;
- `risk_tier`: `low`, `medium`, `high`;
- `pr_class`;
- `affected_contracts`;
- `findings` with severity and file/path references;
- `missing_evidence`;
- `recommended_reviewers` by steward or module;
- `forbidden_action_check`;
- `next_action`.

## Severity

| Severity | Meaning |
| --- | --- |
| P0 | Must stop: unsafe merge, destructive action, policy contradiction, missing high-risk gate |
| P1 | Must address before merge: likely bug, contract drift, missing required evidence |
| P2 | Should address: unclear docs, weak evidence, over-broad diff, missing review focus |
| P3 | Optional: polish, naming, minor clarity |

Automated PR comments should prefer P0/P1 and keep P2/P3 in the summary unless
the PR is explicitly a documentation or process cleanup.

## GCS-Specific Review Subjects

- Stable IDs and state-version provenance.
- Typed reports and report codes.
- Module dependency direction.
- Distinction between solver truth, IO adaptation, viewer projection, and
  agentic process.
- Generated fixture provenance and promotion gates.
- Runtime transaction atomicity and replay evidence.
- Negative cases and obstruction evidence.
- Skipped checks and sandbox/network assumptions.

## GCS Decision

PR audit should be a non-approving evidence review. It can block its own
recommendation, but it cannot approve or merge. The human reviewer remains the
authority for intent, risk acceptance, and merge.
