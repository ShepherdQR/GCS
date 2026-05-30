# Cache-Hit Diagnosis First-Pass Diagnostic - 2026-05-30

## Summary
The first-pass telemetry diagnosis supports a mixed hypothesis: high cache hit is not purely waste, but short process/ops sessions show enough cold-load and low-output signal to justify a Lite lane pilot.

## Thresholds
| Signal | Threshold |
|---|---:|
| High cache, legacy | >= 95% |
| Low token leverage ratio | < 2% |
| High token leverage ratio | >= 5% |
| Short high-overhead session | estimated cold-load overhead >= 50% of input |
| DeepSeek cache write estimate | 39,000 tokens/session |

## Diagnostic Buckets
| Bucket | Sessions | Input | Output | Cache read | Legacy hit | TLR | Avg BEI | Dominant task types |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| high_cache_high_tlr | 15 | 3,199,724 | 1,085,151 | 320,744,064 | 99.01% | 33.91% | 0.455 | unclassified:8, process:5, feature:2 |
| mixed_or_mid | 3 | 351,118 | 34,842 | 3,155,200 | 89.99% | 9.92% | 0.412 | feature:2, unclassified:1 |
| short_high_overhead | 10 | 513,498 | 19,906 | 2,181,504 | 80.95% | 3.88% | 0.270 | unclassified:7, feature:2, research:1 |
| zero_cache_low_tlr | 10 | 315,779 | 578 | 0 | 0.00% | 0.18% | 0.189 | ops:8, research:2 |

## Tool Redundancy Proxies
| Tool | Calls | Failures | Failure rate |
|---|---:|---:|---:|
| Bash | 513 | 55 | 10.72% |
| Read | 327 | 7 | 2.14% |
| Edit | 212 | 20 | 9.43% |
| Write | 125 | 6 | 4.80% |
| TaskUpdate | 101 | 0 | 0.00% |
| Glob | 75 | 2 | 2.67% |
| Grep | 57 | 2 | 3.51% |
| TaskCreate | 51 | 0 | 0.00% |
| Agent | 32 | 0 | 0.00% |
| WebSearch | 26 | 0 | 0.00% |
| mcp__ccd_session__mark_chapter | 13 | 0 | 0.00% |
| WebFetch | 5 | 0 | 0.00% |

Repeated-read proxy:
- Sessions with repeated reads of the same file: 10
- Highest repeated-read session: `2792b768-485a-4f69-a848-fd8a705dbed3` with 39 repeated read calls and max 16 reads of the same file.

Repeated-command proxy:
- Sessions with repeated identical Bash commands: 9
- Highest repeated-command session: `2792b768-485a-4f69-a848-fd8a705dbed3` with 22 repeated command calls.

## Task-Class Readout
| Task type | Sessions | Legacy hit | TLR | High-overhead count | Low-TLR count | Avg input/session |
|---|---:|---:|---:|---:|---:|---:|
| feature | 6 | 98.30% | 24.79% | 2 | 0 | 99540 |
| ops | 8 | 0.00% | 0.10% | 5 | 8 | 25214 |
| process | 5 | 98.90% | 27.86% | 0 | 0 | 267978 |
| research | 3 | 44.42% | 1.24% | 3 | 2 | 52435 |
| unclassified | 16 | 98.80% | 29.61% | 7 | 1 | 130248 |

## Interpretation
- High-cache/high-TLR sessions are evidence that cached institutional context can be productive. Do not remove the Full lane globally.
- Zero-cache/low-TLR and short high-overhead sessions are evidence that some process/ops work may be paying cold-load cost without enough output. These are the best Lite-lane candidates.
- Repeated read/command proxies provide a measurable redundancy signal for the A/B pilot, but they are only proxies; a reviewer still needs to score audit usefulness.
- The next step is the paired Full/Lite pilot described in the research plan, with USD cost excluded until cost storage is normalized.
