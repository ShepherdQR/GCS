# Governance Prompt Evals

Status: seed
Date: 2026-05-26

This directory stores prompt-level governance evals before they become
validator candidates. Each eval describes a scenario, expected refusal or
escalation behavior, passing response, and failing response.

Current seeds:

- `e-gov-001-refuse-unrelated-dirty-file-staging.md`
- `e-gov-002-refuse-audit-approval-overclaim.md`
- `e-gov-008-refuse-agent-promotion-overclaim.md`

Promotion rule:

- Stay at prompt-eval level until at least two real task archives exercise the
  behavior or one severe near miss justifies a validator candidate.
