import importlib.util
import sys
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
            r"RejectsShowcaseSceneWithMissingFixedEntity",
            r"RejectsSolveIntentMissingReferences",
            r"ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence",
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
        self.assertNotIn("ctest.contracts", gate_ids)
        self.assertNotIn("ctest.public_evidence_chain", gate_ids)
        self.assertNotIn("cli.basic_scene", gate_ids)
        self.assertNotIn("cli.showcase_scene", gate_ids)
        self.assertIn("agentic.check-dependencies", gate_ids)
        self.assertIn("cmake.build", gate_ids)


if __name__ == "__main__":
    unittest.main()
