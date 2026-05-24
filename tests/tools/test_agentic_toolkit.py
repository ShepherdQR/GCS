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
    }
    args.update(overrides)
    return SimpleNamespace(**args)


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
                "python.gcs_viz_algebra",
                "python.gcs_viz_history_replay",
                "cmake.configure",
                "cmake.build",
                "ctest.contracts",
                "ctest.fixture_corpus",
                "ctest.public_evidence_chain",
                "cli.basic_scene",
                "cli.showcase_scene",
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
            r"ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence",
            r"RuntimeHistoryFrameProjectsAsReportEvidenceOnly",
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
        self.assertNotIn("python.gcs_viz_algebra", gate_ids)
        self.assertNotIn("python.gcs_viz_history_replay", gate_ids)
        self.assertNotIn("ctest.contracts", gate_ids)
        self.assertNotIn("ctest.public_evidence_chain", gate_ids)
        self.assertNotIn("cli.basic_scene", gate_ids)
        self.assertNotIn("cli.showcase_scene", gate_ids)
        self.assertIn("agentic.check-dependencies", gate_ids)
        self.assertIn("cmake.build", gate_ids)

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
