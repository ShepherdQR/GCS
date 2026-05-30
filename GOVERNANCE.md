# Governance

GCS is a community-governed open-source project. This document defines roles,
decision processes, and how governance evolves.

## Roles

### Maintainer

Maintainers have merge authority and make architecture decisions. They are
responsible for:
- Reviewing and merging PRs that touch solver semantics, IO schema, or
  architecture.
- Keeping the narrative map and architecture docs current.
- Enforcing the Code of Conduct.
- Nominating new maintainers.

Current maintainers:
- ShepherdQR

### Reviewer

Reviewers are domain specialists who review PRs in their area of expertise.
They are trusted to:
- Approve or request changes on PRs within their domain.
- Triage issues.
- Provide technical guidance to contributors.

Reviewers are recognized after 5+ high-quality PRs in a domain.

### Contributor

Anyone with a merged PR. Contributors are listed in the repository's
contributors list (GitHub automatically tracks this).

### Reader

Anyone who builds, runs, or inspects GCS. Readers can file issues and
participate in discussions.

## Decision Process

### Lazy Consensus (default)

For documentation fixes, fixture additions, demo notes, and other non-structural
changes: if no maintainer or reviewer objects within 5 business days, the
contributor may merge.

### Explicit Approval

Required for:
- Solver semantics changes (status codes, report fields, diagnostic taxonomy)
- IO schema changes (JSON or text format, migration policy)
- Architecture doc changes (narrative map, target contracts, module boundaries)
- Dependency changes (new third-party libraries, build system changes)
- Governance changes (this document)

Explicit approval requires at least one maintainer approval.

### Maintainer Nomination

A contributor may be nominated as a maintainer by an existing maintainer after:
- Sustained contribution over 6+ months.
- Demonstrated understanding of the architecture and narrative map.
- Demonstrated good judgment in code review and issue triage.

Nominations are decided by consensus among existing maintainers.

## Code of Conduct

All participants must follow the [Code of Conduct](CODE_OF_CONDUCT.md).
Maintainers are responsible for enforcement.

## Governance Evolution

This governance document should be reviewed every 6 months. Review questions:
- Is the contributor ladder working? Are people advancing?
- Are response times acceptable for issues and PRs?
- Are deferred contribution categories still correctly scoped?
- Should any domain gain or lose a reviewer?
- Is the maintainer list adequate for the project's size?

Governance changes require explicit approval from all current maintainers.

## Attribution

This governance model is adapted from the [Minimum Viable Governance](https://github.com/github/MVG)
framework, scaled for the project's current size.
