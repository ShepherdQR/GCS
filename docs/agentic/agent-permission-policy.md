# GCS Agent Permission Policy

Status: proposed v1.
Date: 2026-05-26.

## Purpose

This policy turns the AI governance boundary into an inspectable action model.
It applies to Codex-style agents, nightly diagnostics, PR audit tooling, repair
agents, and future scheduled work.

The rule is simple: an agent may produce evidence and proposals unattended, but
it must not silently take authority-bearing actions.

## Action Classes

| Class | Examples | Default |
| --- | --- | --- |
| `read` | inspect files, run `git diff`, read docs, list tasks | allowed |
| `local_write` | edit task cards, reports, docs, run artifacts, low-risk tests | allowed inside task scope |
| `test` | run unit tests, validators, quality gates | allowed; skipped checks must record risk |
| `git_write` | commit, merge, branch delete, force-push, remote branch delete | human-authorized only |
| `network` | fetch, push, browse, package download, external API call | human-authorized only |
| `dependency` | install, vendor, upgrade, or remove dependencies | human gate required |
| `fixture_promotion` | move generated or scratch scenes into durable fixtures | human gate required |
| `protected_semantics` | solver/runtime/IO/viewer semantic mutation | task card and human review required |
| `approval` | approve PR, merge PR, mark high-risk change ready without human gate | forbidden unattended |

## Unattended Allowed Actions

Agents may do these without additional approval when the task scope already
authorizes the work:

- classify a PR or diff;
- write `docs/agentic/nightly-runs/YYYY-MM-DD/` artifacts;
- generate advisory `pr-audit.json`;
- run repository validators and tests;
- propose repair steps;
- prepare a low-risk patch candidate in an isolated worktree;
- record skipped checks as risk.

## Human-Gated Actions

Agents need explicit human authorization before:

- committing or pushing;
- merging branches;
- deleting local or remote branches;
- changing dependency state;
- using network-dependent repair;
- promoting fixtures;
- changing protected solver/runtime/IO/viewer semantics;
- expanding a scheduled automation's write boundary.

## Forbidden Unattended Actions

Automated agents must not:

- approve PRs;
- merge PRs or protected branches;
- force-push;
- delete branches without explicit user request;
- promote fixtures without an explicit promotion gate;
- hide failed or skipped checks;
- count an automated audit as human approval.

## PR Audit Enforcement

`pr-audit.json` records forbidden-action posture in:

```json
{
  "forbidden_action_check": {
    "merge": "not_performed",
    "approve": "not_performed",
    "force_push": "not_performed",
    "branch_delete": "not_performed",
    "fixture_promotion": "not_performed"
  }
}
```

Use:

```bat
python tools\agentic_design\agentic_toolkit.py validate-pr-audit docs\agentic\pr-audits\<audit>.json
```

The validator rejects:

- missing required audit fields;
- ready decisions with failed or skipped evidence;
- ready decisions with P0/P1/P2 findings;
- medium or high risk audits without a task card;
- high-risk audits marked ready without a human gate;
- performed merge, approve, force-push, branch-delete actions;
- fixture promotion without an explicit gate.

## Relationship To Nightly Diagnostics

Nightly diagnostics may detect, classify, summarize, and recommend repair.
During calibration it should write only its dated run directory. Later, low-risk
patch candidates may be allowed, but merge, approval, force-push, branch
deletion, dependency changes, and fixture promotion remain human-gated.

## Promotion Path

This policy should remain proposed until:

1. `validate-pr-audit` passes on at least two real PR audit artifacts.
2. The first two nightly diagnostic runs are labeled for signal versus noise.
3. A reviewer confirms that the validator blocks real risk without blocking
   low-risk docs-only work.
