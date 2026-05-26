# GCS Repository Audit

Generated: `2026-05-26T13:01:12.905721+00:00`
Repository: `C:/Codes/Trae/s002_GCS/GCS`
Revision: `7555ff8844af348a2fbbda149bf26f8d6c8f28ce`
Branch: `<unknown>`
Dirty worktree: `no`
Schema: `gcs-repository-audit-0.1`
Tool: `0.1`

## Executive Summary

- Counted 825 tracked files, 798 text files, 27 binary files, and 149,448 physical text lines.
- Found 0 errors and 0 warnings under the current repository-audit policy.
- Agentic surface: 20 project-local skills, 20 skill agent configs, 4 institutional agents, 49 task cards, and 62 completed-task archives.

## Counting Contract

| Field | Value |
| --- | --- |
| tracked_files_only | yes |
| include_untracked | no |
| include_build_output | no |
| excluded_roots | out, outputs, var, .git |
| text_extensions | .cmd, .cmake, .cpp, .cppm, .gitignore, .json, .jsonl, .md, .ps1, .py, .txt, .yaml, .yml |

## Totals

| Metric | Count |
| --- | --- |
| files | 825 |
| text_files | 798 |
| binary_files | 27 |
| physical_lines | 149,448 |
| bytes | 9,499,655 |

## Agentic Governance Surface

| Surface | Count |
| --- | --- |
| project_local_skills | 20 |
| skill_agent_configs | 20 |
| institutional_agents | 4 |
| task_cards | 49 |
| completed_task_archives | 62 |
| pr_audits | 3 |

## Artifact Class Breakdown

| Key | Files | Text | Binary | Lines |
| --- | --- | --- | --- | --- |
| generated_store | 161 | 161 | 0 | 33,416 |
| research_doc | 81 | 81 | 0 | 21,151 |
| architecture_doc | 86 | 83 | 3 | 17,579 |
| agentic_process_doc | 166 | 166 | 0 | 17,400 |
| tooling | 53 | 53 | 0 | 15,033 |
| fixture | 75 | 75 | 0 | 14,444 |
| completed_task_archive | 64 | 64 | 0 | 9,489 |
| solver_source | 20 | 20 | 0 | 9,134 |
| viewer_python | 13 | 13 | 0 | 3,967 |
| contract_test | 13 | 13 | 0 | 2,654 |
| tool_test | 15 | 15 | 0 | 2,626 |
| codex_skill | 45 | 45 | 0 | 1,653 |
| repo_root_config | 5 | 5 | 0 | 467 |
| product_doc | 2 | 2 | 0 | 173 |
| project_report | 1 | 1 | 0 | 159 |
| application_shell | 1 | 1 | 0 | 103 |
| visual_asset | 24 | 0 | 24 | 0 |

## Lifecycle Layer Breakdown

| Key | Files | Text | Binary | Lines |
| --- | --- | --- | --- | --- |
| generated_evidence | 161 | 161 | 0 | 33,416 |
| research | 81 | 81 | 0 | 21,151 |
| architecture | 86 | 83 | 3 | 17,579 |
| process | 166 | 166 | 0 | 17,400 |
| support | 53 | 53 | 0 | 15,033 |
| evidence | 75 | 75 | 0 | 14,444 |
| product | 36 | 36 | 0 | 13,377 |
| archive | 64 | 64 | 0 | 9,489 |
| test | 28 | 28 | 0 | 5,280 |
| skill | 45 | 45 | 0 | 1,653 |
| configuration | 5 | 5 | 0 | 467 |
| report | 1 | 1 | 0 | 159 |
| asset | 24 | 0 | 24 | 0 |

## Top-Level Breakdown

| Key | Files | Text | Binary | Lines |
| --- | --- | --- | --- | --- |
| docs | 424 | 397 | 27 | 65,951 |
| .codex_scene_generation_store | 161 | 161 | 0 | 33,416 |
| tools | 48 | 48 | 0 | 14,945 |
| fixtures | 75 | 75 | 0 | 14,444 |
| src | 20 | 20 | 0 | 9,134 |
| tests | 28 | 28 | 0 | 5,280 |
| python | 14 | 14 | 0 | 3,972 |
| .codex | 45 | 45 | 0 | 1,653 |
| CMakeLists.txt | 1 | 1 | 0 | 251 |
| apps | 1 | 1 | 0 | 103 |
| README.md | 1 | 1 | 0 | 90 |
| scripts | 5 | 5 | 0 | 88 |
| .gitignore | 1 | 1 | 0 | 87 |
| CMakePresets.json | 1 | 1 | 0 | 34 |

## GCS Module Coverage

| Module | Source Files | Interfaces | Implementations | Source Lines | Contract Tests | Contract Lines | Skill Files |
| --- | --- | --- | --- | --- | --- | --- | --- |
| constraint_catalog | 2 | 1 | 1 | 991 | 1 | 228 | 2 |
| contract_tools | 2 | 1 | 1 | 825 | 1 | 260 | 2 |
| decomposition_planner | 2 | 1 | 1 | 687 | 1 | 187 | 2 |
| diagnostics | 2 | 1 | 1 | 838 | 1 | 261 | 2 |
| incidence_graph | 2 | 1 | 1 | 482 | 1 | 107 | 2 |
| io_adapters | 2 | 1 | 1 | 1,468 | 1 | 204 | 2 |
| kernel | 2 | 1 | 1 | 991 | 1 | 169 | 2 |
| numeric_engine | 2 | 1 | 1 | 1,115 | 1 | 255 | 2 |
| session_runtime | 2 | 1 | 1 | 860 | 1 | 276 | 2 |
| viewer_bridge | 2 | 1 | 1 | 877 | 1 | 467 | 2 |

## Largest Text Files

| Path | Class | Lines |
| --- | --- | --- |
| tools/agentic_design/agentic_toolkit.py | tooling | 2,737 |
| docs/architecture/66-implementation-execution-roadmap.md | architecture_doc | 1,911 |
| fixtures/scene/milestone/milestone_20g40c_20260524.gcs.json | fixture | 1,827 |
| fixtures/scene/counterexamples/mixed_geometry_20g40c_singular_20260524.gcs.json | fixture | 1,808 |
| docs/architecture/68-forward-execution-plan-2026-05-24.md | architecture_doc | 1,415 |
| src/gcs/io_adapters/io_adapters.cpp | solver_source | 1,339 |
| tools/scene_generation/tools.py | tooling | 1,092 |
| python/gcs_viz/platform_gui.py | viewer_python | 1,088 |
| docs/architecture/63-target-contract-interface-implementation-test-design.md | architecture_doc | 980 |
| src/gcs/numeric_engine/numeric_engine.cpp | solver_source | 941 |

## Largest Binary Files

| Path | Class | Bytes |
| --- | --- | --- |
| docs/research/20260523/assets/top-ai-architecture-figures/03-alphafold2-architecture-results.png | visual_asset | 906,600 |
| docs/research/20260523/assets/top-ai-architecture-figures/04-alphafold3-inference-architecture.png | visual_asset | 888,640 |
| docs/research/20260523/assets/top-ai-architecture-figures/08-gnome-discovery-flywheel.png | visual_asset | 411,772 |
| docs/research/20260523/assets/top-ai-architecture-figures/09-gencast-weather-diffusion.png | visual_asset | 387,041 |
| docs/research/papers/LGS/ershov.pdf | visual_asset | 326,047 |
| docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.png | visual_asset | 281,703 |
| docs/architecture/70-visualization/assets/figure71-gcs-step-1-40-evidence-map.review.pdf | visual_asset | 191,329 |
| docs/research/20260523/assets/top-ai-architecture-figures/02-alphastar-architecture-overview.jpg | visual_asset | 185,875 |
| docs/research/20260523/assets/top-ai-architecture-figures/01-alphago-training-pipeline.jpg | visual_asset | 180,907 |
| docs/research/20260523/assets/top-ai-architecture-figures/05-alphatensor-search-learn.png | visual_asset | 127,537 |

## Findings

No repository-audit findings under the current policy.

## Reproduction

```bat
python tools\repository_audit\repository_audit.py report --snapshot docs\reports\repository-audit\2026-05-26\snapshot.json --output docs\reports\repository-audit\2026-05-26\README.md
```
