# 14c — Open-Source Roadmap

Status: draft
Date: 2026-05-30
Parent: `docs/narrative-lines/14-business-open-source-strategy/development-plan.md`
Sibling: `commercialization-path.md`

## Purpose

This document is the open-source annex to narrative line 14 (business/open-source
strategy). It defines the phased path from the current internal researcher-preview
repository to a public, community-capable open-source project. It does not assume
commercialization — a pure open-source trajectory is viable and independent of
the sibling commercialization path.

## Guiding Principles

1. **Evidence before visibility.** Do not go public before the researcher preview
   is externally validated. A public repo with zero external reviews is not
   open-source — it is an unverified deposit.
2. **Researcher-first, always.** The primary audience is solver and
   geometric-constraint researchers. Community infrastructure should serve
   technical depth, not marketing breadth.
3. **Progressive disclosure.** Open-source maturity is not a flag — it is a
   sequence of gates. Each gate unlocks more surface area.
4. **Low-process, high-evidence.** Do not add governance ceremony. Add
   verifiable artifacts (build transcripts, expected outputs, replay checks).
5. **Respect the contribution boundary.** The project knows what it is and what
   it is not. The contribution doc should protect contributors from wasting time
   on deferred topics.

## Current State (May 2026)

| Asset | Status |
|-------|--------|
| Repository visibility | Internal / researcher-access only |
| License file | Missing |
| CONTRIBUTING.md | Missing |
| CODE_OF_CONDUCT.md | Missing |
| Issue templates | Missing |
| PR template | Missing |
| CHANGELOG | Missing |
| GOVERNANCE.md | Missing |
| Contribution boundary doc | Present (`docs/product/researcher-contribution-boundary.md`) |
| 20-minute contributor path | Present (`docs/product/20-minute-contributor-path.md`) |
| R1 researcher preview | Present (local preview only) |
| R2 build transcript | Present (single-machine) |
| D1/D2/D3 demo packages | Present |
| B1 expected outputs | Present |
| Task card + archive pipeline | Active and validated |
| External reviews archived | Zero |
| External contributions archived | Zero |

## License Recommendation

### Recommended: Apache 2.0

| Criterion | Assessment |
|-----------|------------|
| Patent grant | Explicit patent grant clause — important for a solver with novel algorithms |
| Permissiveness | Permissive — maximizes adoption by researchers and potential industrial users |
| Compatibility | Compatible with GPL v3 (one-way), BSD, MIT — does not fragment the ecosystem |
| Contributor protection | Clear contributor license terms without copyleft enforcement burden |
| Commercial friendliness | No copyleft virality — commercial users can embed without source disclosure |

### Why not GPL/AGPL?

- GPL would block embedding by proprietary CAD tools, which limits the solver's
  reach. The project's goal is to be the *reference implementation* for
  evidence-rich geometric constraint solving — permissive licensing maximizes
  that reach.
- AGPL adds SaaS protection but GCS is a local solver, not a network service.
  The clause adds complexity with no practical benefit.
- If dual licensing is pursued later (see `commercialization-path.md`), Apache
  2.0 is compatible with a proprietary dual-license fork without CLA
  complications.

### Why not MIT?

- MIT lacks a patent grant. For a solver that may include novel decomposition,
  diagnostic, or numeric techniques, the patent grant in Apache 2.0 is worth
  the slightly longer license text.

### Decision gate

The license decision should be finalized as part of Phase 2 (public launch).
Document the final choice at `docs/product/license-decision.md`.

## Phased Open-Source Plan

### Phase 0: Foundation (current — internal only)

Keep the repo researcher-access. Complete the R2 gates and prepare the public
surface.

Checklist:

- [x] Researcher contribution boundary doc
- [x] 20-minute contributor path
- [x] R1 researcher preview package
- [x] D1, D2, D3 demo packages
- [x] R2 build transcript (single machine)
- [x] B1 expected output files
- [ ] R2 build transcript verified on a second machine
- [x] B2 expected-output files for B2-01 and B2-02
- [ ] First external review archived (P2.1 in weakness plan)

### Phase 1: Pre-Public Preparation (estimated 4-8 weeks from now)

Complete all repository infrastructure before making the repo public. None of
these depend on external people.

#### 1.1 Repository Metadata

```text
/LICENSE              — Apache 2.0
/CONTRIBUTING.md      — Contribution workflow, CLA if applicable, DCO if used
/CODE_OF_CONDUCT.md   — Adopt Contributor Covenant v2.1 (standard, low-friction)
/SECURITY.md          — How to report security issues (private channel, response SLA)
/CHANGELOG.md         — Keep a curated changelog following Keep a Changelog format
/GOVERNANCE.md         — Project governance: maintainer roles, decision process, merge policy
```

Contents of key files:

**CONTRIBUTING.md** should include:
- Link to `docs/product/researcher-contribution-boundary.md` (welcome vs. defer)
- Link to `docs/product/20-minute-contributor-path.md` (onboarding)
- Task card requirement for non-trivial changes
- PR checklist: task card linked, scope verified, validation evidence included
- How to run validators: `python tools/agentic_design/agentic_toolkit.py validate-docs`
- How to propose a fixture or benchmark candidate

**GOVERNANCE.md** should define:
- **Maintainer** role: merge authority, architecture decision authority
- **Contributor** role: anyone with a merged PR
- **Reviewer** role: domain specialists (typically module stewards)
- Decision process: lazy consensus for small changes, explicit approval for
  architecture/solver/schema changes
- Maintainer nomination: demonstrated sustained contribution + existing
  maintainer approval
- Current maintainer list (initially: project creator)

**SECURITY.md** should include:
- How to privately report security issues (email or encrypted channel)
- Response SLA: acknowledge within 5 business days
- Scope: solver crash, memory safety, undefined behavior, diagnostic
  misclassification that could lead to incorrect solver claims
- Out of scope: unsupported scene classes, benchmark disagreements, feature
  requests

#### 1.2 Issue Templates

```text
.github/ISSUE_TEMPLATE/01-bug-report.md
.github/ISSUE_TEMPLATE/02-fixture-proposal.md
.github/ISSUE_TEMPLATE/03-benchmark-candidate.md
.github/ISSUE_TEMPLATE/04-documentation-improvement.md
.github/ISSUE_TEMPLATE/config.yml                 — disable blank issues, point to templates
```

Each template should include the relevant checklist from the contribution
boundary doc. Bug reports should ask for: fixture path, command, expected
status, actual status, report fields.

#### 1.3 PR Template

```text
.github/pull_request_template.md
```

Template body:

```markdown
### Task Card
- [ ] Task card exists at `docs/agentic/tasks/<slug>.md`
- [ ] Task card validates: `python tools/agentic_design/agentic_toolkit.py validate-task-card docs/agentic/tasks/<slug>.md`

### Scope
- [ ] Staged files match the task card scope
- [ ] No unrelated dirty files staged
- [ ] `git diff --cached --name-only` reviewed

### Validation
- [ ] `python tools/agentic_design/agentic_toolkit.py validate-docs` passes
- [ ] Relevant tests pass (list test suite and result)
- [ ] New fixtures include metadata and expected status

### Evidence
- [ ] Demo or command transcript attached (if user-facing)
- [ ] Expected output files updated (if output format changed)

### Related
- Closes #<issue>
- Ref: `docs/architecture/<relevant>.md`
```

#### 1.4 README Expansion

The current README should be expanded with:
- One-line thesis at the top
- Build badge (when CI is public)
- License badge
- Quick-start: build, run D1 smoke, run validators
- Link to `docs/architecture/95-gcs-narrative-map.md` (project thesis)
- Link to `docs/product/20-minute-contributor-path.md` (new contributors)
- Link to `docs/product/researcher-contribution-boundary.md` (what to contribute)
- "R1 Researcher Preview" section with demo ladder links
- Citation section (how to cite GCS in a paper)

#### 1.5 Pre-Public Review

Before flipping visibility:
1. Have one internal reviewer follow the 20-minute contributor path from a
   fresh clone on a machine that has never built GCS.
2. Record every friction point.
3. Fix the top 3 frictions before launch.

### Phase 2: Public Launch (estimated 8-12 weeks from now)

Precondition: at least one real external review archived (P2.1 weakness plan).

#### 2.1 Repository Visibility

Make the repository public. The exact platform depends on current hosting:
- If on GitHub: Settings → Change repository visibility → Public
- If self-hosted: configure public read access

#### 2.2 Launch Announcement

Minimal, evidence-first announcement:

- **Primary channel**: relevant research mailing lists, solver/geometry forums,
  or personal researcher networks.
- **Format**: a short post pointing to the thesis, the D1/D2/D3 demos, and the
  contribution boundary.
- **Tone**: "GCS is an evidence-rich geometric constraint solving research
  workbench. It is not a production CAD system. Researchers are invited to
  inspect, reproduce, and critique the evidence."
- **No**: Product Hunt, Hacker News "Show HN", or general tech press. The
  audience is researchers, not developers at large.

#### 2.3 First Public Release Tag

Tag the first public release:

```bash
git tag -a v0.1.0 -m "GCS v0.1.0 — R2 Researcher Snapshot"
```

The tag should correspond to an R2 reproducible research snapshot. Include a
GitHub Release with:
- Release notes linking to the R2 build transcript
- Known limitations (from the release readiness checklist)
- Supported platforms (initially: Windows, clang-ninja build)
- Unsupported claims (from the researcher audience strategy)

#### 2.4 Community Response Infrastructure

Be ready to respond to:
- **Issues**: acknowledge within 3 business days, classify as bug/fixture
  proposal/benchmark candidate/documentation/out-of-scope
- **PRs**: first-response within 5 business days, clear acceptance/rejection
  with reference to contribution boundary
- **Discussions**: if GitHub Discussions is enabled, seed with one topic per
  unresolved architecture question (e.g., "How should rigid-set DOF diagnostics
  work in 3D?")

### Phase 3: Community Building (estimated 3-6 months after launch)

#### 3.1 Contributor Ladder

Define explicit pathways from first-time contributor to maintainer:

| Level | Requirements | Privileges |
|-------|-------------|------------|
| **Reader** | None | Read, build, run, file issues |
| **First-time contributor** | One merged PR (any size) | Listed in CONTRIBUTORS |
| **Repeat contributor** | 3+ merged PRs | Triage permissions on issues |
| **Reviewer** | Domain expertise demonstrated over 5+ PRs | PR review authority in domain |
| **Maintainer** | Sustained contribution + existing maintainer nomination | Merge authority, architecture decisions |

The first external contributor who lands a real PR is a narrative milestone.
Archive it in the line-14 evidence artifact.

#### 3.2 Good First Issues

Seed the issue tracker with 5-10 "good first issue" items:

- Clarify a doc link or index reference
- Add a D1/D2 demo note without changing solver behavior
- Classify an existing fixture under the corpus maturity ladder
- Add a negative test case for a documented limitation
- Improve a command transcript in a demo README

Each should include: the file to touch, the expected outcome, and which
validator to run to confirm success.

#### 3.3 Research Community Engagement

- **Conference adjacencies**: When a relevant paper or talk references geometric
  constraint solving, open an issue linking to the paper and noting how GCS
  approaches the same problem.
- **Reproducibility**: If a paper claims a constraint solving result, try to
  encode it as a GCS fixture and publish the fixture with a note on what
  matches and what does not.
- **Citation tracking**: Maintain a `CITATION.cff` file in the repo root.
  Record every paper, talk, or blog post that references GCS.

#### 3.4 CI/CD Visibility

When the repo is public, CI results should be visible:
- Build status badge in README
- Test suite status badge in README
- Link to CI dashboard for full logs
- Per-PR CI runs with results posted as PR checks

### Phase 4: Mature Open-Source (estimated 12+ months after launch)

#### 4.1 Community Governance

- If the project attracts 3+ regular external contributors, expand the
  maintainer list to include at least one external maintainer.
- Hold a public governance review every 6 months: are contribution barriers
  appropriate? Is the maintainer response time acceptable? Are deferred
  contribution categories still correctly scoped?

#### 4.2 Ecosystem Integration

- Package for a package manager (vcpkg for C++, pip for Python visualization)
- Provide a CMake `find_package` target for downstream embedding
- Maintain a list of downstream projects that use or embed GCS

#### 4.3 Release Cadence

| Release type | Cadence | Example version |
|-------------|---------|-----------------|
| Snapshot | On every merged PR (default branch) | `main` |
| Researcher snapshot (R2) | Quarterly, with frozen fixtures and build transcript | `v0.2.0` |
| Public tool release (R3) | Annually, with packaging and support boundaries | `v1.0.0` |

Versioning follows [Semantic Versioning](https://semver.org):
- **Major**: solver report format change, API break, schema migration
- **Minor**: new diagnostic, new constraint type, new fixture class
- **Patch**: bug fix, doc clarification, test improvement

#### 4.4 Sustainability

For a pure open-source project (no commercial sibling), sustainability means:

- **Institutional memory**: The maintainer knowledge is in the architecture
  docs, the narrative map, and the task archives — not in a single person's
  head. This is GCS's strongest sustainability asset.
- **Bus factor**: Actively work to increase the number of people who can
  build, run, and understand the solver independently.
- **Grant readiness**: If the project reaches research significance, it should
  be positioned for academic grants (NSF, EU Horizon, etc.). This requires:
  published papers citing GCS, a clear research contribution statement, and
  a community of users beyond the original authors.

## Anti-Patterns to Avoid

1. **Going public before the first external review.**
   A public repo with no external validation is a ghost town, not a community.
   Wait for P2.1.

2. **GitHub-star-driven development.**
   Stars measure visibility, not quality. Do not optimize issues, features, or
   announcements for star count. The metric is: can a researcher reproduce and
   critique the evidence?

3. **Process inflation.**
   Do not add a CODEOWNERS file, branch protection rules, required reviews, or
   CI gate policies that exceed what the actual contributor volume justifies.
   Two maintainers and one external contributor do not need the governance
   machinery of a 100-person project.

4. **Over-polishing before feedback.**
   The response to "no external reviewer yet" is not another internal demo
   package. It is finding a reviewer. The fallback (internal structured
   walkthrough) is acceptable once — not repeatedly.

5. **Treating the contribution boundary as permanent.**
   The deferred list (CAD feature parity, performance leaderboard, GUI-first
   workflow) should be reviewed every 6 months. What is deferred today may be
   ready tomorrow.

6. **Hiding limitations.**
   The README, release notes, and demo docs must be explicit about unsupported
   behavior. A researcher who discovers an unstated limitation loses trust.
   A researcher who reads a stated limitation gains respect for the project's
   honesty.

## Alignment With Release Modes

| Phase | Release mode | Repository state |
|-------|-------------|------------------|
| Phase 0 | R0 internal checkpoint | Private / researcher-access |
| Phase 1 | R1 researcher preview (local) | Private / researcher-access |
| Phase 2 | R2 reproducible research snapshot | **Public** |
| Phase 3 | R2+ with community | Public |
| Phase 4 | R3 public tool release | Public, packaged |

## Alignment With Narrative Lines

| Related line | Open-source impact |
|-------------|-------------------|
| 11 (Product/user) | Open-source community becomes a primary user channel alongside researchers |
| 12 (Release/packaging) | R3 packaging is gated on open-source community size and demand |
| 13 (Benchmark/comparison) | Public benchmarks invite external comparison and critique — this is a feature, not a risk |
| 06 (Agentic-SE) | The agentic governance model is itself an open-source contribution — other projects can adopt the task card / archive / evidence pipeline |
| 09 (Institutional agents) | Public visibility creates more agent interaction data, accelerating agent learning and promotion |
| 04 (Fixture corpus) | External fixture contributions diversify the corpus beyond what internal generation can produce |

## Dependency Graph

```text
Phase 0 (current)           — all internal
    |
    v
Phase 1 (repo infra)        — independent, start any time
    |
    v
P2.1 (first external review) — depends on external person
    |
    v
Phase 2 (public launch)     — gates on P2.1
    |
    v
Phase 3 (community building) — depends on Phase 2
    |
    v
Phase 4 (mature open-source) — depends on Phase 3
```

Phase 1 can (and should) start immediately — none of it depends on external
people. The public launch (Phase 2) gates on the first external review.

## Update Rule

Update this document when:
- Phase 1 repository infrastructure is created.
- A license decision is finalized.
- The first external review (P2.1) is archived.
- The repository visibility changes to public.
- The first external PR is merged.
- A release tag is created.
- The contributor ladder adds a new level or a new person advances.
- The governance model changes.
- The narrative map baseline is refreshed and line 14's level changes.
