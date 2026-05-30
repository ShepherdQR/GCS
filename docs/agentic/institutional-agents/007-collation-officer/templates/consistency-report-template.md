# Consistency Report Template

Report ID: `<COL-YYYYMMDD-NNN>`
Prepared by: `collation-officer`
Date: `<YYYY-MM-DD>`
Scope: `<description of the audit scope — e.g., "post-refactor module contract audit", "pre-release skill description audit">`

## Artifact Pairs Checked

| Pair ID | Artifact A | Artifact B | Relationship | Target contract (if any) |
| --- | --- | --- | --- | --- |
| P1 | `docs/architecture/...` | `src/gcs/...` | doc vs. implementation | `docs/architecture/30-contracts/...` |
| P2 | `.claude/skills/...` | `tools/...` | skill description vs. invoked tool | |

## Sources NOT Checked

| Source | Reason not checked | Residual risk |
| --- | --- | --- |
| | | |

## Findings

### Finding F1: `<short title>`

| Field | Detail |
| --- | --- |
| Pair | P1 |
| Artifact A claim | (quote or paraphrase with citation: file, line, section) |
| Artifact B claim | (quote or paraphrase with citation: file, line, section) |
| Discrepancy | (description of the mismatch) |
| Classification | `doc_stale` / `code_ahead` / `both_wrong` / `ambiguous` |
| Severity | `cosmetic` / `misleading` / `breaking` |
| Confidence | `high` / `medium` / `low` |
| Recommended fix | (which artifact to change, and what the change should be) |
| Escalation | (if ambiguous, note who should decide) |

### Finding F2: `<short title>`

...

## Summary

| Classification | Count |
| --- | ---: |
| doc_stale | |
| code_ahead | |
| both_wrong | |
| ambiguous | |
| **Total discrepancies** | |

| Severity | Count |
| --- | ---: |
| cosmetic | |
| misleading | |
| breaking | |

## Unresolved / Escalated

| Finding | Escalated to | Reason |
| --- | --- | --- |
| | | |

## Recommendations

1.
2.
3.

## Confidence Statement

Overall audit confidence: `high` / `medium` / `low`

Factors affecting confidence:
- (e.g., "All target contracts were available and unambiguous")
- (e.g., "Two pairs could not be fully checked because the canonical reference is in flux")
