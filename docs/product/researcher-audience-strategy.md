# Researcher Audience Strategy

Status: active
Date: 2026-05-26

## Decision

The primary audience for the next GCS narrative phase is:

```text
solver and geometric-constraint researchers
```

Secondary audiences remain CAD or geometry-tool developers, agentic-SE
practitioners, and local visualization users. They should not drive the next
release narrative until the researcher-facing evidence path is stronger.

## Why Researchers First

Researchers are the right primary audience because GCS's strongest current
assets are not product polish. They are:

- local-to-global solver semantics;
- diagnostic reports and obstruction vocabulary;
- rank, residual, and nullity evidence;
- fixture, milestone, and counterexample corpora;
- explicit task, validation, and archive governance.

A researcher can value partial but honest evidence. A general CAD user would
reasonably expect robust modeling breadth, packaging, and GUI polish that GCS
does not yet claim.

## Researcher Jobs

| Researcher job | GCS answer |
| --- | --- |
| Inspect how a scene is represented. | Stable fixture paths and architecture vocabulary. |
| Compare success and failure cases. | D1/D2 demo packages and counterexample metadata. |
| Study diagnostic evidence. | Rank, residual, obstruction, rollback, and commit reports. |
| Propose a new benchmark candidate. | Benchmark selection criteria and fixture maturity ladder. |
| Reproduce a claim. | Command transcripts and archived evidence. |
| Understand project evolution. | Narrative map, Figure 95, completed-task archives. |

## Message Hierarchy

Use this order in researcher-facing docs:

1. GCS is an evidence-rich geometric constraint solving research workbench.
2. Its differentiator is explicit diagnostic and local-to-global evidence, not
   breadth of CAD features.
3. Current demos are command-line and fixture-centered.
4. Counterexamples are first-class research assets.
5. Benchmarks will be promoted only when fixture status, expected reports, and
   unsupported cases are explicit.

## Non-Positioning

Avoid these claims:

- "GCS is a production CAD system."
- "GCS outperforms commercial solvers."
- "GCS is release ready for general users."
- "The GUI is the primary product."
- "A single successful fixture proves solver correctness."

## Adoption Path

| Step | Researcher action | GCS artifact |
| --- | --- | --- |
| 1 | Read the project thesis. | `docs/architecture/95-gcs-narrative-map.md` |
| 2 | Run a smoke command. | `docs/product/demos/d1-cli-smoke/` |
| 3 | Run diagnostic examples. | `docs/product/demos/d2-diagnostic-classification/` |
| 4 | Inspect fixture maturity. | `docs/architecture/96-fixture-corpus-maturity-ladder.md` |
| 5 | Compare with solver baselines. | `docs/architecture/97-external-solver-comparison-and-benchmark-plan.md` |
| 6 | Propose a benchmark candidate. | `docs/architecture/98-benchmark-candidate-selection-criteria.md` |

## Documentation Consequences

- Product docs should foreground evidence, fixtures, and reproducibility.
- Demo docs should include command transcripts before screenshots.
- Release docs should say "researcher preview" before "public release."
- External comparison should avoid marketing language and state non-goals.
- README expansion should point researchers to D1/D2 before UI screenshots.

## Next Decision

After the D2 classification script and first benchmark candidates exist, decide
whether the public README should present GCS as:

- a research workbench first;
- a solver architecture reference implementation;
- an agentic-SE case study around a real solver;
- or a staged combination with researcher workbench as the front door.
