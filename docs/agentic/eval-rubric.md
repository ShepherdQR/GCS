# Agentic Eval Rubric

This rubric scores agent work products. It complements CTest and build gates;
it does not replace them.

## Scores

| Score | Meaning |
| --- | --- |
| 0 | Fails the task or violates a guardrail. |
| 1 | Partially useful but missing important evidence or scope control. |
| 2 | Correct for the narrow task with adequate evidence. |
| 3 | Correct, well-scoped, verified, and improves future work. |

## Dimensions

| Dimension | What To Check |
| --- | --- |
| Scope control | Only requested files and owned boundaries changed. |
| Contract fit | Public contracts, report codes, stable IDs, and fixtures stay coherent. |
| Dependency direction | Lower modules do not import runtime, IO, viewer, UI, or agentic layers. |
| Evidence | Required commands ran or skipped checks are explained. |
| Negative coverage | New behavior has failure or obstruction coverage when relevant. |
| Reviewability | Diff, task card, and evidence can be inspected quickly. |
| Learning | Repeated failure patterns are captured as experience records. |

## Pass Rule

High-risk solver work needs score 2 or better in every dimension and score 3
in dependency direction and evidence. Low-risk documentation work may pass with
score 2 in the relevant dimensions.
