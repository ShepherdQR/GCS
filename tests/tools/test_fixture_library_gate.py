import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = REPO_ROOT / "tools" / "scene_generation" / "fixture_library_gate.py"


def load_gate():
    spec = importlib.util.spec_from_file_location("fixture_library_gate_under_test", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_fake_solver(path: Path, wrong_status: str = "") -> list[str]:
    path.write_text(
        "\n".join(
            [
                "import sys",
                "from pathlib import Path",
                "scene = Path(sys.argv[1]).name",
                "outcomes = {",
                "  'milestone_20g40c_20260524.gcs.json': ('AcceptedWithWarnings', 'true', 0, ''),",
                "  'all_types_10g18c_20260524.gcs.json': ('Failed', 'false', 2, 'runtime.numeric_failure'),",
                "  'mixed_geometry_20g40c_singular_20260524.gcs.json': ('NumericallySingular', 'false', 2, 'runtime.post_local_diagnostics_blocked'),",
                "}",
                "status, accepted, exit_code, obstruction = outcomes[scene]",
                f"if scene == 'milestone_20g40c_20260524.gcs.json' and {wrong_status!r}:",
                f"    status = {wrong_status!r}",
                "print('GCS C++23 canonical kernel solver skeleton')",
                "print(f'Input: {sys.argv[1]}')",
                "print(f'Status: {status}')",
                "print(f'Accepted: {accepted}')",
                "if obstruction:",
                "    print(f'  runtime.obstruction_report: {obstruction}')",
                "    print(f'Obstruction: {obstruction} - expected fixture obstruction', file=sys.stderr)",
                "raise SystemExit(exit_code)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return [sys.executable, str(path)]


def copy_fixture_library(root: Path) -> None:
    target = root / "fixtures" / "scene"
    target.mkdir(parents=True)
    shutil.copytree(REPO_ROOT / "fixtures" / "scene" / "milestone", target / "milestone")
    shutil.copytree(REPO_ROOT / "fixtures" / "scene" / "counterexamples", target / "counterexamples")


def mutate_json(path: Path, mutator) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class FixtureLibraryGateTests(unittest.TestCase):
    def test_current_fixture_library_passes_with_expected_cli_outcomes(self):
        gate = load_gate()
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_solver = write_fake_solver(Path(temp_dir) / "fake_solver.py")

            result = gate.run_checks(solver_command=fake_solver)

        self.assertEqual([], result.errors)
        self.assertEqual(result.fixtures_checked, 3)

    def test_digest_mismatch_fails(self):
        gate = load_gate()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            copy_fixture_library(root)
            fake_solver = write_fake_solver(root / "fake_solver.py")
            model = root / "fixtures" / "scene" / "milestone" / "all_types_10g18c_20260524.gcs.json"
            mutate_json(model, lambda data: data.__setitem__("state_version", 99))

            result = gate.run_checks(
                milestone_manifest=root / "fixtures" / "scene" / "milestone" / "manifest.json",
                counterexample_manifest=root / "fixtures" / "scene" / "counterexamples" / "manifest.json",
                repo_root=root,
                solver_command=fake_solver,
            )

        self.assertTrue(any("canonical digest is" in error for error in result.errors))

    def test_cli_status_mismatch_fails(self):
        gate = load_gate()
        with tempfile.TemporaryDirectory() as temp_dir:
            fake_solver = write_fake_solver(Path(temp_dir) / "fake_solver.py", wrong_status="Solved")

            result = gate.run_checks(solver_command=fake_solver)

        self.assertTrue(any("CLI status 'Solved', expected 'AcceptedWithWarnings'" in error for error in result.errors))


if __name__ == "__main__":
    unittest.main()
