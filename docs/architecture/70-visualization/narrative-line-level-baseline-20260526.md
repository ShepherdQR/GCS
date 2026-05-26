# Narrative Line Level Baseline

Status: baseline
Date: 2026-05-26
Figure: `figure95-narrative-line-level-baseline-20260526`

## Purpose

This baseline visualizes the `Level` column from
`docs/architecture/95-gcs-narrative-map.md` as of 2026-05-26 after the
researcher-audience narrative batch. It is meant to make the project imbalance
visible at a glance: internal solver, architecture, quality, and
agentic-operation narratives are strong, while external legibility still needs
automated demo summaries, replay packaging, benchmark execution, and public
researcher routing.

## Artifacts

- Source spec:
  `tools/architecture_visualization/specs/figure95-narrative-line-level-baseline.yaml`
- SVG baseline:
  `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.svg`
- PNG review render:
  `docs/architecture/70-visualization/assets/figure95-narrative-line-level-baseline-20260526.review.png`

## Score Mapping

| Text level | Numeric baseline score |
| --- | ---: |
| Very strong | 5.0 |
| Strong | 4.0 |
| Strong but split | 3.5 |
| Developing | 3.0 |
| Initial and strengthening | 2.5 |
| Partial | 2.0 |
| Weak | 1.0 |

The numeric scores are visualization aids only. The source of truth remains the
textual narrative-map levels and the next strengthening tasks listed there.

## Baseline Reading

- Strongest lines: module contracts and agentic-SE operating layer.
- Broadly strong lines: solver thesis, roadmap, fixture corpus, replay
  evidence, quality gates, and Git/PR governance.
- Middle lines: UI/viewer/scientific figures and institutional-agent learning.
- Strengthened weak-axis lines: product behavior evidence, release readiness,
  external comparison, and researcher audience strategy now have seed artifacts.
- Remaining weak-axis work: automate D2 summaries, package D3 replay evidence,
  freeze benchmark candidates, and route public docs around researchers.

## Refresh Rule

Refresh this baseline when any of these close:

- D2 classification script;
- D3 replay evidence package;
- B1 benchmark expected-output files;
- R1 researcher-preview release note;
- public README expansion;
- governance eval promotion from prompt-level to validator candidate.
