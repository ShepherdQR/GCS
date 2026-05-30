# Maintenance Record Template

Maintenance cycle: `<YYYY-MM-DD-maintenance-N>`
Gardener: `gardener`
Date: `<YYYY-MM-DD>`

## Source of Issues

- [ ] Repository audit report
- [ ] Collation-officer consistency report
- [ ] Session notes
- [ ] Stale link check
- [ ] Manual observation
- [ ] Other: `<description>`

## Items Found

| # | Category | Path | Before state | Source |
| --- | --- | --- | --- | --- |
| 1 | dead-link / stale-path / typo / formatting / index / cleanup / minor-debt | | | |
| 2 | | | | |

## Triage

### Gardener-Scope (Fixed)

| # | Path | Before | After | Verification |
| --- | --- | --- | --- | --- |
| 1 | | | | build-check / compile-check / diff-review / manual |
| 2 | | | | |

### Escalated (Not Fixed)

| # | Path | Issue | Escalation rationale | Recommended path |
| --- | --- | --- | --- | --- |
| 1 | | | Touches module contract / changes behavior / exceeds safe scope / ambiguous impact | Task card for `<steward>` |
| 2 | | | | |

## Affected Files

```
<list of all changed files>
```

## Verification

| Check | Result | Notes |
| --- | --- | --- |
| `git diff --stat` scope | as expected / wider than expected | |
| Build check | passed / skipped (reason) | |
| Compile check | passed / skipped (reason) | |
| Manual diff review | no behavior change / anomaly found | |

## Escalation Criteria Applied

For each escalated item, the following criterion was triggered:

| Criterion | Description |
| --- | --- |
| Solver semantics | Change would alter mathematical meaning or solver output |
| Module contract | Change touches a public API, header, or documented interface |
| Fixture behavior | Change would alter test fixture input or expected output |
| Stable ID | Change would alter a contractually stable identifier |
| Quality gate | Change would modify a test assertion or gate threshold |
| Cross-module | Change spans module boundaries and cannot be reviewed as a unit |
| Behavior change | Change could alter user-visible output, build artifact, or test result |
| Ambiguous impact | Cannot determine with confidence that the change is safe |

## Summary

| Category | Count |
| --- | ---: |
| Items found | |
| Fixed (gardener-scope) | |
| Escalated (task-scope) | |
| Affected files | |
