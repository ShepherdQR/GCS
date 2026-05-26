import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLKIT_PATH = REPO_ROOT / "tools" / "agentic_design" / "agentic_toolkit.py"


def load_toolkit():
    spec = importlib.util.spec_from_file_location("agentic_toolkit_under_test", TOOLKIT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def default_args(**overrides):
    args = {
        "preset": "clang-ninja",
        "build_dir": "out/build/clang-ninja",
        "skip_agentic": False,
        "skip_python_tools": False,
        "skip_build": False,
        "skip_ctest": False,
        "skip_cli": False,
        "include_task_cards": [],
        "include_completed_reports": [],
        "include_fixture_library": False,
        "include_repository_audit": False,
    }
    args.update(overrides)
    return SimpleNamespace(**args)


def task_card_text(**overrides):
    values = {
        "task_id": "2026-05-25-valid-agentic-gate",
        "status": "complete",
        "request": "Validate one active task card through opt-in quality gates.",
        "scope": "tool",
        "risk": "medium",
        "human_gate_required": "false",
        "human_gate_reason": "",
    }
    values.update(overrides)
    return f"""---
task_id: {values["task_id"]}
status: {values["status"]}
request: "{values["request"]}"
scope: {values["scope"]}
risk: {values["risk"]}
owning_agent: gcs-quality-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - tools/agentic_design/agentic_toolkit.py
required_evidence:
  - python -m unittest tests.tools.test_agentic_toolkit
human_gate_required: {values["human_gate_required"]}
human_gate_reason: "{values["human_gate_reason"]}"
---

# {values["task_id"]}

## Scope

Validate only explicitly selected active task cards.

## Non-Goals

- Do not validate all historical task cards.

## Context To Read

- `docs/agentic/quality-gate-opt-in-policy.md`

## Acceptance Gates

- Included task cards pass or fail with named evidence.

## Verification Plan

```bat
python -m unittest tests.tools.test_agentic_toolkit
```

## Evidence Bundle

- Unit test evidence is recorded by the caller.

## Residual Risks

- Default enforcement remains deferred.
"""


def completed_report_text(task_id="2026-05-25-valid-completed-report-gate"):
    archive_target = f"docs/completed-tasks/{task_id}/"
    return f"""---
task_id: {task_id}
status: complete
session_goal: "Validate one active completed-task report through opt-in quality gates."
archive_target: {archive_target}
experience_links:
  - none
---

# {task_id}

## Task Objective

Validate completed-task include behavior for new reports without selecting the legacy archive tree.

## Scope And Non-Goals

In scope:

- Validate the named report.

Out of scope:

- Do not migrate historical archives.

## Interaction Summary

The test constructs a focused report fixture and validates it through the include helper.

## Work Completed

- Added structural validation coverage for opt-in completed reports.

## Files And Artifacts

- `tools/agentic_design/agentic_toolkit.py`: include gate implementation surface.

## Evidence

```text
python -m unittest tests.tools.test_agentic_toolkit
Passed for the focused include report fixture.
```

## Decisions

- Keep completed-report validation path-scoped until legacy policy exists.

## Skipped Checks And Risks

- Full build is not relevant for this structural report fixture.

## Follow-Up

- Decide later whether closure scoring becomes an optional gate.

## Archive Handoff

- Archive path: `{archive_target}`
- Related experience:
  - none
- Skill, eval, fixture, or tool update needed: none for this fixture.
"""


class AgenticToolkitTests(unittest.TestCase):
    def test_quality_gate_sequence_names_public_evidence_chain(self):
        toolkit = load_toolkit()
        build_dir = Path("out/build/clang-ninja")
        commands = toolkit.build_quality_gate_commands(
            default_args(),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )

        gate_ids = [gate.gate_id for gate in commands]
        self.assertEqual(
            gate_ids,
            [
                "agentic.validate-docs",
                "agentic.validate-inventory",
                "agentic.validate-skills",
                "agentic.check-dependencies",
                "python.scene_generation_explorer",
                "python.agentic_toolkit",
                "python.showcase_scene_renderer",
                "python.showcase_fixture_evidence",
                "python.showcase_fixture_evidence_tests",
                "python.showcase_scene_html_compositor",
                "python.showcase_scene_html_compositor_tests",
                "python.browser_export",
                "python.gcs_token_lint",
                "python.gcs_token_lint_tests",
                "python.gcs_text_overflow",
                "python.gcs_text_overflow_tests",
                "python.gcs_overlap_contrast",
                "python.gcs_overlap_contrast_tests",
                "python.gcs_screenshot_baseline",
                "python.gcs_screenshot_baseline_tests",
                "python.gcs_viz_algebra",
                "python.gcs_viz_history_replay",
                "cmake.configure",
                "cmake.build",
                "ctest.contracts",
                "ctest.fixture_corpus",
                "ctest.public_evidence_chain",
                "cli.basic_scene",
                "cli.showcase_scene",
                "cli.replay_evidence_basic_scene",
                "cli.replay_evidence_report_artifact",
            ],
        )

        evidence_gate = next(gate for gate in commands if gate.gate_id == "ctest.public_evidence_chain")
        self.assertIn("-R", evidence_gate.command)
        pattern = evidence_gate.command[evidence_gate.command.index("-R") + 1]
        for fragment in [
            r"NumericEngineContract\.",
            r"DiagnosticsContract\.",
            r"DecompositionPlannerContract\.",
            r"IoAdaptersContract\.",
            r"KernelContract\.",
            r"SessionRuntimeContract\.",
            r"ViewerBridgeContract\.",
            r"ShowcaseJsonSceneCarriesSolveIntentBehavior",
            r"LoadsPythonAuthoredJsonBehaviorScene",
            r"RejectsShowcaseSceneWithMissingFixedEntity",
            r"RejectsSolveIntentMissingReferences",
            r"ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory",
            r"ReplayEvidenceExportIsDeterministicReportEvidence",
            r"ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence",
            r"RuntimeHistoryFrameProjectsAsReportEvidenceOnly",
            r"ReplayEvidenceSummaryPreservesRuntimeReportBoundary",
            r"ReplayEvidenceReportArtifactIsDeterministicAndSceneHistoryFree",
            r"ContractToolsContract\.",
            r"IntegratedShowcaseFixtureCarriesPublicEvidenceContract",
        ]:
            self.assertIn(fragment, pattern)

    def test_quality_gate_skips_are_composable(self):
        toolkit = load_toolkit()
        build_dir = Path("out/build/clang-ninja")
        commands = toolkit.build_quality_gate_commands(
            default_args(skip_python_tools=True, skip_ctest=True, skip_cli=True),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )

        gate_ids = [gate.gate_id for gate in commands]
        self.assertNotIn("python.scene_generation_explorer", gate_ids)
        self.assertNotIn("python.agentic_toolkit", gate_ids)
        self.assertNotIn("python.showcase_scene_renderer", gate_ids)
        self.assertNotIn("python.showcase_fixture_evidence", gate_ids)
        self.assertNotIn("python.showcase_fixture_evidence_tests", gate_ids)
        self.assertNotIn("python.showcase_scene_html_compositor", gate_ids)
        self.assertNotIn("python.showcase_scene_html_compositor_tests", gate_ids)
        self.assertNotIn("python.browser_export", gate_ids)
        self.assertNotIn("python.gcs_token_lint", gate_ids)
        self.assertNotIn("python.gcs_token_lint_tests", gate_ids)
        self.assertNotIn("python.gcs_text_overflow", gate_ids)
        self.assertNotIn("python.gcs_text_overflow_tests", gate_ids)
        self.assertNotIn("python.gcs_overlap_contrast", gate_ids)
        self.assertNotIn("python.gcs_overlap_contrast_tests", gate_ids)
        self.assertNotIn("python.gcs_screenshot_baseline", gate_ids)
        self.assertNotIn("python.gcs_screenshot_baseline_tests", gate_ids)
        self.assertNotIn("python.gcs_viz_algebra", gate_ids)
        self.assertNotIn("python.gcs_viz_history_replay", gate_ids)
        self.assertNotIn("ctest.contracts", gate_ids)
        self.assertNotIn("ctest.public_evidence_chain", gate_ids)
        self.assertNotIn("cli.basic_scene", gate_ids)
        self.assertNotIn("cli.showcase_scene", gate_ids)
        self.assertNotIn("cli.replay_evidence_basic_scene", gate_ids)
        self.assertNotIn("cli.replay_evidence_report_artifact", gate_ids)
        self.assertIn("agentic.check-dependencies", gate_ids)
        self.assertIn("cmake.build", gate_ids)

    def test_quality_gate_artifact_includes_are_explicit(self):
        toolkit = load_toolkit()
        build_dir = Path("out/build/clang-ninja")

        default_commands = toolkit.build_quality_gate_commands(
            default_args(),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )
        default_gate_ids = [gate.gate_id for gate in default_commands]
        self.assertNotIn("agentic.task-cards", default_gate_ids)
        self.assertNotIn("agentic.completed-task-reports", default_gate_ids)

        commands = toolkit.build_quality_gate_commands(
            default_args(
                include_task_cards=["docs/agentic/tasks/current.md"],
                include_completed_reports=["docs/completed-tasks/current"],
            ),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )

        gate_by_id = {gate.gate_id: gate.command for gate in commands}
        self.assertIn("agentic.task-cards", gate_by_id)
        self.assertIn("validate-task-card-includes", gate_by_id["agentic.task-cards"])
        self.assertIn("docs/agentic/tasks/current.md", gate_by_id["agentic.task-cards"])
        self.assertIn("agentic.completed-task-reports", gate_by_id)
        self.assertIn("validate-completed-report-includes", gate_by_id["agentic.completed-task-reports"])
        self.assertIn("docs/completed-tasks/current", gate_by_id["agentic.completed-task-reports"])

    def test_fixture_library_gate_is_focused_opt_in(self):
        toolkit = load_toolkit()
        build_dir = Path("out/build/clang-ninja")

        default_gate_ids = [
            gate.gate_id
            for gate in toolkit.build_quality_gate_commands(
                default_args(),
                Path("tools/agentic_design/agentic_toolkit.py"),
                "python",
                build_dir,
                build_dir / "GCS.exe",
            )
        ]
        self.assertNotIn("python.fixture_library_gate", default_gate_ids)

        commands = toolkit.build_quality_gate_commands(
            default_args(include_fixture_library=True),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )

        gate_ids = [gate.gate_id for gate in commands]
        self.assertIn("python.fixture_library_gate", gate_ids)
        fixture_gate = next(gate for gate in commands if gate.gate_id == "python.fixture_library_gate")
        command_parts = [str(part).replace("\\", "/") for part in fixture_gate.command]
        self.assertTrue(any(part.endswith("tools/scene_generation/fixture_library_gate.py") for part in command_parts))
        self.assertIn("--gcs-exe", fixture_gate.command)

    def test_repository_audit_gate_is_focused_opt_in(self):
        toolkit = load_toolkit()
        build_dir = Path("out/build/clang-ninja")

        default_gate_ids = [
            gate.gate_id
            for gate in toolkit.build_quality_gate_commands(
                default_args(),
                Path("tools/agentic_design/agentic_toolkit.py"),
                "python",
                build_dir,
                build_dir / "GCS.exe",
            )
        ]
        self.assertNotIn("python.repository_audit_check", default_gate_ids)

        commands = toolkit.build_quality_gate_commands(
            default_args(include_repository_audit=True),
            Path("tools/agentic_design/agentic_toolkit.py"),
            "python",
            build_dir,
            build_dir / "GCS.exe",
        )

        gate = next(item for item in commands if item.gate_id == "python.repository_audit_check")
        command_parts = [str(part).replace("\\", "/") for part in gate.command]
        self.assertTrue(any(part.endswith("tools/repository_audit/repository_audit.py") for part in command_parts))
        self.assertEqual(gate.command[-1], "check")

    def test_pr_audit_classifies_agentic_tooling_diff(self):
        toolkit = load_toolkit()

        audit = toolkit.build_pr_audit(
            base="origin/master",
            head="HEAD",
            changed_paths=[
                "tools/agentic_design/agentic_toolkit.py",
                "tests/tools/test_agentic_toolkit.py",
                "docs/agentic/tasks/2026-05-25-agentic-governance-execution.md",
                "docs/agentic/schemas/pr-audit.schema.json",
            ],
            evidence_passed=[
                "python -m unittest tests.tools.test_agentic_toolkit",
                "validate-docs",
                "validate-task-card for changed task cards",
            ],
        )

        self.assertEqual(audit["schema_version"], "gcs.pr-audit.v1")
        self.assertEqual(audit["pr_class"], "quality-gate")
        self.assertEqual(audit["risk_tier"], "medium")
        self.assertEqual(audit["decision"], "ready_for_human_review")
        self.assertEqual(audit["task_card"], "docs/agentic/tasks/2026-05-25-agentic-governance-execution.md")
        self.assertEqual(audit["evidence"]["skipped"], [])
        self.assertIn("Agentic toolkit command surface", audit["affected_contracts"])
        self.assertEqual(audit["forbidden_action_check"]["merge"], "not_performed")

        results = toolkit.validate_pr_audit_record(audit)
        self.assertEqual([(item.ok, item.message) for item in results], [(True, "pr-audit: pr-audit passed")])

    def test_pr_audit_flags_fixture_promotion_gate(self):
        toolkit = load_toolkit()

        audit = toolkit.build_pr_audit(
            base="origin/master",
            head="HEAD",
            changed_paths=["fixtures/scene/generated/new-scene.gcs.json"],
            task_card="docs/agentic/tasks/2026-05-25-fixture-promotion.md",
        )

        self.assertEqual(audit["pr_class"], "scene-exploration")
        self.assertEqual(audit["risk_tier"], "high")
        self.assertEqual(audit["decision"], "needs_author_revision")
        self.assertTrue(any(finding["severity"] == "P1" for finding in audit["findings"]))
        self.assertTrue(any(item["check"] == "focused contract tests or explicit skip risk" for item in audit["evidence"]["skipped"]))

    def test_pr_audit_validator_rejects_ready_with_skipped_evidence(self):
        toolkit = load_toolkit()
        audit = toolkit.build_pr_audit(
            base="origin/master",
            head="HEAD",
            changed_paths=["tools/agentic_design/agentic_toolkit.py"],
            task_card="docs/agentic/tasks/2026-05-25-agentic-governance-execution.md",
        )
        audit["decision"] = "ready_for_human_review"
        audit["next_action"] = "human_review"

        results = toolkit.validate_pr_audit_record(audit)

        self.assertTrue(any(not item.ok and "ready audit cannot include skipped evidence" in item.message for item in results))

    def test_pr_audit_validator_rejects_forbidden_actions(self):
        toolkit = load_toolkit()
        audit = toolkit.build_pr_audit(
            base="origin/master",
            head="HEAD",
            changed_paths=["docs/research/example.md"],
        )
        audit["forbidden_action_check"]["force_push"] = "performed"

        results = toolkit.validate_pr_audit_record(audit)

        self.assertTrue(any(not item.ok and "unattended force_push is forbidden" in item.message for item in results))

    def test_pr_audit_validator_rejects_high_risk_ready(self):
        toolkit = load_toolkit()
        audit = toolkit.build_pr_audit(
            base="origin/master",
            head="HEAD",
            changed_paths=["src/gcs/kernel/kernel.cppm"],
            task_card="docs/agentic/tasks/2026-05-25-agentic-governance-execution.md",
            evidence_passed=["focused contract tests or explicit skip risk"],
        )
        audit["decision"] = "ready_for_human_review"

        results = toolkit.validate_pr_audit_record(audit)

        self.assertTrue(any(not item.ok and "high-risk audit cannot be ready" in item.message for item in results))

    def test_nightly_index_summarizes_findings_json(self):
        toolkit = load_toolkit()
        with tempfile.TemporaryDirectory() as temp_dir:
            runs = Path(temp_dir)
            run = runs / "2026-05-25"
            run.mkdir()
            (run / "findings.json").write_text(
                json.dumps({
                    "status": "findings",
                    "findings": [
                        {"severity": "P1", "category": "quality_gate"},
                        {"severity": "P2", "category": "pr_audit"},
                    ],
                    "skipped_checks": [{"check": "ctest"}],
                }),
                encoding="utf-8",
            )

            markdown = toolkit.nightly_index_markdown(runs, generated_at="2026-05-25T02:30:00+08:00")

        self.assertIn("| [2026-05-25](2026-05-25/README.md) | findings | 2 | 0 | 1 | 1 | 0 | 1 |", markdown)
        self.assertIn("| `quality_gate` | 1 |", markdown)
        self.assertIn("First-two-run calibration is still open", markdown)

    def test_task_card_include_pathspecs_validate_active_records(self):
        toolkit = load_toolkit()
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            root = Path(temp_dir)
            cards = root / "cards"
            cards.mkdir()
            valid = cards / "valid.md"
            valid.write_text(task_card_text(), encoding="utf-8")
            missing_request = cards / "missing-request.md"
            missing_request.write_text(
                task_card_text().replace('request: "Validate one active task card through opt-in quality gates."\n', ""),
                encoding="utf-8",
            )
            high_risk = cards / "high-risk.md"
            high_risk.write_text(task_card_text(risk="high"), encoding="utf-8")
            placeholder = cards / "placeholder.md"
            placeholder.write_text(
                task_card_text().replace("Unit test evidence is recorded by the caller.", "Record commands run."),
                encoding="utf-8",
            )

            results = toolkit.validate_task_card_includes([str(cards)])

        messages = [item.message for item in results]
        self.assertTrue(any(item.ok and "valid.md passed" in item.message for item in results))
        self.assertTrue(any("missing frontmatter field request" in message for message in messages))
        self.assertTrue(any("high-risk tasks require human_gate_required: true" in message for message in messages))
        self.assertTrue(any("placeholder text remains: Record commands run" in message for message in messages))

    def test_task_card_include_unmatched_pathspec_fails(self):
        toolkit = load_toolkit()

        results = toolkit.validate_task_card_includes(["docs/agentic/tasks/no-such-card-*.md"])

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].ok)
        self.assertIn("unmatched include pathspec", results[0].message)

    def test_completed_report_include_pathspecs_validate_new_reports(self):
        toolkit = load_toolkit()
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            root = Path(temp_dir)
            valid_dir = root / "2026-05-25-valid-completed-report-gate"
            valid_dir.mkdir()
            valid_report = valid_dir / "README.md"
            valid_report.write_text(completed_report_text(), encoding="utf-8")
            invalid_dir = root / "2026-05-25-invalid-completed-report-gate"
            invalid_dir.mkdir()
            invalid_report = invalid_dir / "README.md"
            invalid_report.write_text(
                completed_report_text("2026-05-25-invalid-completed-report-gate").replace(
                    "## Decisions\n\n- Keep completed-report validation path-scoped until legacy policy exists.\n\n",
                    "",
                ),
                encoding="utf-8",
            )

            results = toolkit.validate_completed_report_includes([str(root)], require_index=True)

        messages = [item.message for item in results]
        self.assertTrue(any(item.ok and "valid-completed-report-gate/README.md passed" in item.message for item in results))
        self.assertTrue(any("missing or empty section ## Decisions" in message for message in messages))

    def test_completed_report_include_unmatched_pathspec_fails(self):
        toolkit = load_toolkit()

        results = toolkit.validate_completed_report_includes(["docs/completed-tasks/no-such-report-*"])

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].ok)
        self.assertIn("unmatched include pathspec", results[0].message)

    def test_phase_step_plan_template_contains_e002_frontmatter(self):
        toolkit = load_toolkit()
        args = SimpleNamespace(
            slug="demo",
            objective="Create an executable E002 test plan.",
            task_id="",
            title="",
            status="draft",
            owner="gcs-architecture-steward",
            phase="phase-1",
            step="step-1",
            date="2026-05-24",
        )

        text = toolkit.phase_step_plan_template(args)

        self.assertIn("record_type: e002_phase_step_plan", text)
        self.assertIn("task_id: 2026-05-24-demo", text)
        self.assertIn("### Next Step Declaration", text)

    def test_phase_step_validator_accepts_filled_plan(self):
        toolkit = load_toolkit()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "phase-step.md"
            path.write_text(FILLED_PHASE_STEP_PLAN, encoding="utf-8")

            results = toolkit.validate_phase_step_record_file(path)

        self.assertEqual([(item.ok, item.message) for item in results], [(True, f"phase-step-record: {path} passed")])

    def test_phase_step_validator_rejects_placeholders(self):
        toolkit = load_toolkit()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "phase-step.md"
            path.write_text(FILLED_PHASE_STEP_PLAN.replace("Step goal: Build", "Step goal: TBD"), encoding="utf-8")

            results = toolkit.validate_phase_step_record_file(path)

        self.assertTrue(any(not item.ok and "placeholder text remains: TBD" in item.message for item in results))

    def test_show_next_step_extracts_declaration(self):
        toolkit = load_toolkit()

        next_step = toolkit.extract_next_step_declaration(FILLED_PHASE_STEP_PLAN)

        self.assertIn("Next step id: step-2", next_step)
        self.assertIn("First action: Open the current status record.", next_step)


FILLED_PHASE_STEP_PLAN = """---
record_type: e002_phase_step_plan
task_id: 2026-05-24-demo
status: in_progress
current_phase: phase-1
current_step: step-1
owner: "gcs-architecture-steward"
updated: 2026-05-24
---

# Filled Phase-Step Plan

## Task Objective

- Objective: Build an executable E002 plan record.
- Scope: Agentic lifecycle documentation and tooling only.
- Non-goals: Solver runtime behavior remains unchanged.
- Acceptance evidence: Validator accepts this filled record.
- E001 closure target: Completed-task report when the overall task closes.

## Phase Roadmap

| Phase | Goal | Initial Steps | Completion Test | Status | Downstream Update Rule |
| --- | --- | --- | --- | --- | --- |
| phase-1 | Formalize tooling. | step-1, step-2 | Commands and tests exist. | open | Replan phase-2 after summary. |

## Current Phase

- Phase id: phase-1
- Phase goal: Formalize tooling.
- Phase status: open
- Starting branch: master
- Dirty worktree notes: Unrelated files are ignored.
- Expected artifacts: Toolkit command and tests.
- Phase completion test: Unit tests pass.
- Downstream replanning rule: Replan after the phase summary.

## Step Record

### Step Declaration

- Step id: step-1
- Step status: summarized
- Step goal: Build the first validator.
- Target artifact: tools/agentic_design/agentic_toolkit.py
- First action: Add structural checks.
- Out of scope: Semantic grading.
- Expected verification: Python unit test.

### Execution Evidence

- Files changed: tools/agentic_design/agentic_toolkit.py
- Commands run: python -m unittest tests.tools.test_agentic_toolkit
- Tool observations: The validator returned OK.
- Verification result: Passed.
- Skipped checks: Full C++ build is not relevant.

### Step Summary

- What changed: E002 records have structural validation.
- What was learned: Required headings are enough for first tooling.
- What remains uncertain: Semantic quality still needs review.
- Skipped checks: Full build skipped because docs tooling changed.
- Risks: Validator remains intentionally shallow.

### Current Phase Update

- Remaining steps before update: Add next-step extraction.
- Changes to remaining steps: Keep next-step extraction as planned.
- Newly added steps: Add a unit test.
- Deferred steps: CI gate promotion is deferred.
- Superseded steps: None.
- Reason for update: Structural validator scope is clear.
- Updated next step: step-2.

### Commit Boundary

- Branch checked: master.
- Staged files inspected: Yes.
- Commit scope: E002 tooling files.
- Commit hash: not-yet-committed.
- No-commit reason: The test record is in memory.
- Commit message: research: tool E002 continuation records.

### Next Step Declaration

- Next step id: step-2
- Target artifact: tests/tools/test_agentic_toolkit.py
- Purpose: Cover resume extraction.
- First action: Open the current status record.
- Blockers or gates: None.

## Phase Summary

- Phase result: The phase remains open.
- Evidence: Unit test plan is available.
- What changed in downstream plans: Gate promotion remains phase 5.
- Deferred work: Empirical validation.
- Promotion target considered: Toolkit command only.
- Next phase: phase-2.
- Downstream phase updates: No change.

## Resume Pointer

- Current phase: phase-1
- Current step: step-2
- Next action: Open the current status record.
- Required context: Read E002 formal model first.
- Last commit: not-yet-committed.
"""


if __name__ == "__main__":
    unittest.main()
