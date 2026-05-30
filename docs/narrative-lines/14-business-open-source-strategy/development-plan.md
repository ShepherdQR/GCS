# 14 — Business/Open-Source Strategy

Status: active
Date: 2026-05-30
Parent map: `docs/architecture/95-gcs-narrative-map.md`
Weakness plan: `docs/agentic/narrative-weakness-development-plan-20260530.md`

## Current Level

**Developing (3.0)**

## Current State

Primary audience, README route, contribution boundary, R1 preview route, and
first external researcher review packet are documented. The strategy exists
on paper.

## Main Gap

Public distribution and actual external contribution workflow are still
researcher-preview only. No real external contribution or review has landed.

## Weakness Root Cause

No real external contribution or review has landed.

## Evidence Artifact

Researcher audience strategy, contribution boundary, and first review packet.

## Promotion Gate

Archive a real researcher review or contribution.

## Next Move

Archive the first real external review or contribution.

## Recent Progress (2026-05-30)

- B2 expected-output files for B2-01 and B2-02 created.
- Phase 1 open-source infrastructure completed: LICENSE (Apache 2.0),
  CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md,
  GOVERNANCE.md, CITATION.cff, 4 issue templates, PR template, config.yml,
  and README expansion.
- Detailed roadmaps written: `open-source-roadmap.md` and
  `commercialization-path.md`.

## Development Plan

### Phase 1: Pre-Public Preparation (current)

1. [x] LICENSE (Apache 2.0)
2. [x] CONTRIBUTING.md
3. [x] CODE_OF_CONDUCT.md (Contributor Covenant v2.1)
4. [x] SECURITY.md
5. [x] CHANGELOG.md (Keep a Changelog format, [Unreleased])
6. [x] GOVERNANCE.md
7. [x] Issue templates (4 templates + config.yml)
8. [x] PR template (with task card, scope, validation, evidence checklist)
9. [x] README expansion (license, citation, contributing, security, project status)
10. [x] CITATION.cff
11. [ ] **Pre-public review**: have one internal reviewer follow the 20-minute
    contributor path from a fresh clone on a different machine that has never
    built GCS. Record every friction point in
    `docs/product/reviews/pre-public-friction-log.md`. Fix the top 3 frictions
    before launch.

### Phase 2: Seek External Feedback (next 4-8 weeks)

12. [ ] **Archive first external review** (P2.1 in weakness plan).
    Precondition: a real external person (researcher, colleague,
    open-source contributor) reviews the R1 researcher preview. Their feedback
    is recorded at `docs/product/reviews/`. A response note classifies feedback
    as accepted, deferred, or declined.

13. [ ] **Archive first external contribution** (P2.2 in weakness plan).
    When a real external person submits a PR, issue, or email patch: test the
    contribution boundary doc against the real case, record friction, review
    and merge or decline, archive the outcome.

### Fallback (if no external person appears within 8 weeks)

14. [ ] **Internal simulation**: have an internal contributor follow the
    20-minute contributor path from a fresh clone on a different machine.
    Record every friction point. Downgrade the review target to "internal
    structured walkthrough with a fresh reader" with explicit caveats.

### Phase 4: Public Distribution Decision (12+ weeks, gates on Phase 2)

15. [ ] **Make public distribution decision** (P4.1 in weakness plan).
    Precondition: at least one real external review (12) and one external
    contribution (13) exist. Decide: make repository public, keep
    researcher-access-only, or staged release model. If public: finalize
    license, expand README, add CONTRIBUTING.md and issue templates (already
    prepared in Phase 1).

### Long-term (12+ weeks)

16. [ ] If public: monitor external engagement (stars, issues, PRs, citations).
    Record first external citation or mention as an archive milestone.
17. [ ] If researcher-access-only: refresh the decision every 3 months based on
    accumulated external feedback.

## Dependencies

- Product/user (11): external review validates product story.
- Release/packaging (12): external contributors need reproducible build.
- All other lines: open-source readiness depends on overall project maturity.

## Related

- Arc 4: Product And Adoption
- `docs/product/researcher-audience-strategy.md`
- `docs/product/gcs-product-user-brief.md`
- `docs/agentic/narrative-weakness-development-plan-20260530.md` (P2.2, P4.1)
