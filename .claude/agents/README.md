# GCS Claude Code Agents Index

Institutional agent role definitions for recurring project memory, review,
timeline, and governance practices. These are Claude Code-compatible agent
files converted from `docs/agentic/institutional-agents/`.

## Maturity Levels

| Level | Meaning |
|-------|---------|
| Candidate | Trigger conditions and expected output are written |
| Seed | Prompt, template, eval, and at least one concrete example |
| Practiced | Several examples across sessions or repeated reuse |
| Promoted | Trusted as part of normal workflow for its boundary |
| Institutional | Standing project capability with ongoing maintenance |

## Active Agents

| ID | Agent | Maturity | Purpose |
|----|-------|----------|---------|
| I001 | [bladesmith-quench-forge](bladesmith-quench-forge.md) | Practiced | Extract reusable lessons from exploratory work |
| I002 | [tailor-stitch-timeline](tailor-stitch-timeline.md) | Practiced | Maintain multi-session timelines |
| I003 | [atelier-steward-calibrate-review](atelier-steward-calibrate-review.md) | Seed | Review UI against design conventions |
| I004 | [art-director-frame-judge](art-director-frame-judge.md) | Seed | Independent visual judgment |

## Candidate Agents

| Agent | Purpose | Evidence needed before seed |
|-------|---------|---------------------------|
| [governance-sentinel](governance-sentinel.md) | Permission and audit governance | Prompt, review template, refusal eval |
| [demo-producer](demo-producer.md) | Product demo creation | Demo-package template, command-transcript standard |
| [benchmark-scout](benchmark-scout.md) | External solver comparison | Comparison criteria, source-citation standard |
| [release-shepherd](release-shepherd.md) | Release readiness | Release checklist, distribution non-goals |
| [night-watch](night-watch.md) | Nightly patrol and diagnostics | Real nightly run with findings |
| [acceptance-officer](acceptance-officer.md) | Independent evidence review | Prompt, gate template, refusal eval |
| [collation-officer](collation-officer.md) | Cross-read docs/code/tests | Prompt, consistency report template |
| [bookkeeper](bookkeeper.md) | Token/cost/value tracking | Budget ledger template |
| [gardener](gardener.md) | Small maintenance and debt | Maintenance record template |

## Promotion Rule

Do not promote a role because the name is appealing. Promote when the role has:
1. A recurring trigger
2. A bounded decision surface
3. A prompt and output template
4. At least one negative or refusal eval
5. Enough real examples to show that future sessions behave better with the
   role than without it

## Review Cadence

Review the agent registry when:
- A new institutional agent is added
- A seed agent gains a second or third real example
- A promoted role creates a project rule or skill update
- An eval fails or a role overclaims authority
- The agentic organization map changes

See `docs/agentic/institutional-agent-registry-and-scorecard.md` for the
authoritative registry and detailed score dimensions.
