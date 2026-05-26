import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
REPOSITORY_AUDIT_ROOT = REPO_ROOT / "tools" / "repository_audit"
sys.path.insert(0, str(REPOSITORY_AUDIT_ROOT))

from gcs_repository_audit.classify import ARTIFACT_LAYERS, classify_path, normalize_path
from gcs_repository_audit.collect import collect_snapshot, write_snapshot
from gcs_repository_audit.diff import compare_snapshots, render_archive_delta, render_markdown_diff, write_diff
from gcs_repository_audit.models import GitInfo
from gcs_repository_audit.registry import (
    accepted_snapshots,
    load_registry_entries,
    render_markdown_index,
    write_accepted_trend,
)
from gcs_repository_audit.report import render_markdown_report
from gcs_repository_audit.trend import build_trend, render_markdown_trend


class RepositoryAuditTests(unittest.TestCase):
    def test_classifier_covers_architecture_artifact_classes(self):
        examples = {
            "solver_source": "src/gcs/kernel/kernel.cppm",
            "application_shell": "apps/gcs_cli/main.cpp",
            "viewer_python": "python/gcs_viz/visualizer.py",
            "tooling": "tools/repository_audit/repository_audit.py",
            "contract_test": "tests/contracts/kernel/kernel_contract_tests.cpp",
            "tool_test": "tests/tools/test_repository_audit.py",
            "fixture": "fixtures/scene/basic/g1.txt",
            "architecture_doc": "docs/architecture/README.md",
            "product_doc": "docs/product/gcs-product-user-brief.md",
            "research_doc": "docs/research/topic.md",
            "project_report": "docs/reports/repository-audit/2026-05-26/README.md",
            "agentic_process_doc": "docs/agentic/README.md",
            "completed_task_archive": "docs/completed-tasks/demo/README.md",
            "codex_skill": ".codex/skills/gcs-kernel-contract-steward/SKILL.md",
            "generated_store": ".codex_scene_generation_store/demo/scene.json",
            "visual_asset": "docs/architecture/70-visualization/assets/figure.svg",
            "repo_root_config": "README.md",
            "unknown": "misc/unclassified.bin",
        }

        self.assertEqual(set(examples), set(ARTIFACT_LAYERS))
        for artifact_class, path in examples.items():
            self.assertEqual(classify_path(path), artifact_class)
        self.assertEqual(classify_path("docs/current-model.md"), "architecture_doc")
        self.assertEqual(classify_path("python/requirements.txt"), "repo_root_config")

    def test_normalize_path_preserves_non_ascii_and_windows_separators(self):
        self.assertEqual(normalize_path(r".\docs\research\几何\约束.md"), "docs/research/几何/约束.md")

    def test_collect_snapshot_joins_module_inventory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            inventory = root / "tools" / "agentic_design" / "module_inventory.json"
            inventory.parent.mkdir(parents=True)
            inventory.write_text(
                json.dumps({
                    "modules": [
                        {
                            "id": "kernel",
                            "source_dir": "src/gcs/kernel",
                            "contract_test": "tests/contracts/kernel/kernel_contract_tests.cpp",
                            "skill": ".codex/skills/gcs-kernel-contract-steward",
                        }
                    ]
                }),
                encoding="utf-8",
            )
            files = {
                "src/gcs/kernel/kernel.cppm": "export module gcs.kernel;\n",
                "src/gcs/kernel/kernel.cpp": "module gcs.kernel;\n",
                "tests/contracts/kernel/kernel_contract_tests.cpp": "#include <gtest/gtest.h>\n",
                ".codex/skills/gcs-kernel-contract-steward/SKILL.md": "---\nname: gcs-kernel-contract-steward\n---\n",
                "docs/research/几何/约束.md": "# 非 ASCII path\n",
            }
            for relative, content in files.items():
                path = root / Path(*relative.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            snapshot = collect_snapshot(
                root,
                tracked_paths=[
                    "src/gcs/kernel/kernel.cppm",
                    "src/gcs/kernel/kernel.cpp",
                    "tests/contracts/kernel/kernel_contract_tests.cpp",
                    ".codex/skills/gcs-kernel-contract-steward/SKILL.md",
                    r"docs\research\几何\约束.md",
                ],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc", branch="test", dirty=False),
            )

        self.assertEqual(snapshot.schema_version, "gcs-repository-audit-0.1")
        self.assertEqual(snapshot.totals["files"], 5)
        self.assertTrue(any(metric.path == "docs/research/几何/约束.md" for metric in snapshot.files))
        kernel = next(metric for metric in snapshot.modules if metric.module_id == "kernel")
        self.assertEqual(kernel.source_files, 2)
        self.assertEqual(kernel.interface_files, 1)
        self.assertEqual(kernel.implementation_files, 1)
        self.assertEqual(kernel.contract_test_files, 1)
        self.assertEqual(kernel.skill_files, 1)
        self.assertEqual(snapshot.findings, [])

    def test_policy_reports_tracked_build_output_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            output = root / "out" / "build" / "artifact.txt"
            output.parent.mkdir(parents=True)
            output.write_text("generated\n", encoding="utf-8")

            snapshot = collect_snapshot(
                root,
                tracked_paths=["out/build/artifact.txt"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc", branch="test", dirty=False),
            )

        self.assertTrue(any(finding.id == "tracked-build-output" and finding.severity == "error" for finding in snapshot.findings))

    def test_write_snapshot_outputs_stable_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc", branch="test", dirty=False),
            )
            output = root / "snapshot.json"

            write_snapshot(snapshot, output)

            data = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], "gcs-repository-audit-0.1")
        self.assertEqual(data["totals"]["files"], 1)
        self.assertEqual(data["files"][0]["artifact_class"], "repo_root_config")

    def test_render_markdown_report_summarizes_agentic_surface(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            files = {
                ".codex/skills/gcs-kernel-contract-steward/SKILL.md": "---\nname: gcs-kernel-contract-steward\n---\n",
                ".codex/skills/gcs-kernel-contract-steward/agents/openai.yaml": "model: test\n",
                "docs/agentic/institutional-agents/001-demo-role/README.md": "# Demo\n",
                "docs/agentic/tasks/2026-05-26-demo.md": "---\ntask_id: demo\n---\n",
                "docs/completed-tasks/2026-05-26-demo/README.md": "# Demo\n",
                "docs/agentic/pr-audits/2026-05-26-demo.json": "{}\n",
                "docs/reports/repository-audit/2026-05-26/README.md": "# Report\n",
            }
            for relative, content in files.items():
                path = root / Path(*relative.split("/"))
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            snapshot = collect_snapshot(
                root,
                tracked_paths=list(files),
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc", branch="test", dirty=False),
            )

        report = render_markdown_report(snapshot, command="repository_audit.py report --output README.md")

        self.assertIn("## Agentic Governance Surface", report)
        self.assertIn("| project_local_skills | 1 |", report)
        self.assertIn("| skill_agent_configs | 1 |", report)
        self.assertIn("| institutional_agents | 1 |", report)
        self.assertIn("| project_report |", report)

    def test_compare_snapshots_reports_file_and_group_deltas(self):
        with tempfile.TemporaryDirectory() as base_dir, tempfile.TemporaryDirectory() as head_dir:
            base_root = Path(base_dir)
            head_root = Path(head_dir)
            base_files = {
                "README.md": "# Demo\n",
                "docs/architecture/old.md": "# Old\n",
            }
            head_files = {
                "README.md": "# Demo\n\nMore detail.\n",
                "docs/architecture/new.md": "# New\nMore\n",
            }
            for root, files in [(base_root, base_files), (head_root, head_files)]:
                for relative, content in files.items():
                    path = root / Path(*relative.split("/"))
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")

            base_snapshot = collect_snapshot(
                base_root,
                tracked_paths=list(base_files),
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="base", branch="test", dirty=False),
            )
            head_snapshot = collect_snapshot(
                head_root,
                tracked_paths=list(head_files),
                generated_at="2026-05-26T00:00:01+00:00",
                git_info=GitInfo(head="head", branch="test", dirty=False),
            )

        diff = compare_snapshots(base_snapshot, head_snapshot, generated_at="2026-05-26T00:00:02+00:00")
        data = diff.to_dict()
        files = {item["path"]: item for item in data["files"]}

        self.assertEqual(data["schema_version"], "gcs-repository-audit-diff-0.1")
        self.assertEqual(data["summary"]["changed_files"], 3)
        self.assertEqual(data["summary"]["added_files"], 1)
        self.assertEqual(data["summary"]["removed_files"], 1)
        self.assertEqual(data["summary"]["modified_files"], 1)
        self.assertEqual(files["docs/architecture/new.md"]["change_type"], "added")
        self.assertEqual(files["docs/architecture/old.md"]["change_type"], "removed")
        self.assertEqual(files["README.md"]["change_type"], "modified")
        self.assertEqual(data["totals"]["physical_lines"]["delta"], 3)
        architecture_delta = next(
            group
            for group in data["groups"]["by_artifact_class"]
            if group["key"] == "architecture_doc"
        )
        self.assertEqual(architecture_delta["delta_files"], 0)
        self.assertEqual(architecture_delta["delta_physical_lines"], 1)

    def test_write_diff_outputs_stable_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            base_path = root / "README.md"
            base_path.write_text("# Demo\n", encoding="utf-8")
            base_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="base", branch="test", dirty=False),
            )
            base_path.write_text("# Demo\n\nExpanded.\n", encoding="utf-8")
            head_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:01+00:00",
                git_info=GitInfo(head="head", branch="test", dirty=False),
            )
            output = root / "diff.json"

            write_diff(compare_snapshots(base_snapshot, head_snapshot), output)

            data = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(data["schema_version"], "gcs-repository-audit-diff-0.1")
        self.assertEqual(data["summary"]["modified_files"], 1)
        self.assertEqual(data["files"][0]["path"], "README.md")

    def test_render_markdown_diff_summarizes_deltas(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            base_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="base", branch="test", dirty=False),
            )
            readme.write_text("# Demo\n\nExpanded.\n", encoding="utf-8")
            head_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:01+00:00",
                git_info=GitInfo(head="head", branch="test", dirty=False),
            )

        report = render_markdown_diff(compare_snapshots(base_snapshot, head_snapshot))

        self.assertIn("# GCS Repository Audit Diff", report)
        self.assertIn("## Total Deltas", report)
        self.assertIn("| physical_lines | 1 | 3 | +2 |", report)
        self.assertIn("| modified | README.md | repo_root_config | +2 |", report)

    def test_render_archive_delta_summarizes_task_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            base_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="base", branch="test", dirty=False),
            )
            report_path = root / "docs" / "reports" / "repository-audit" / "delta.md"
            report_path.parent.mkdir(parents=True)
            report_path.write_text("# Delta\nMore\n", encoding="utf-8")
            head_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md", "docs/reports/repository-audit/delta.md"],
                generated_at="2026-05-26T00:00:01+00:00",
                git_info=GitInfo(head="head", branch="test", dirty=False),
            )

        report = render_archive_delta(compare_snapshots(base_snapshot, head_snapshot), command="archive-delta")

        self.assertIn("## Repository Audit Delta", report)
        self.assertIn("| changed_files | 1 |", report)
        self.assertIn("| delta_physical_lines | +2 |", report)
        self.assertIn("| project_report | +1 | +2 |", report)
        self.assertIn("archive-delta", report)

    def test_render_markdown_trend_summarizes_snapshot_series(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            base_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="base123456789", branch="test", dirty=False),
            )
            report_path = root / "docs" / "reports" / "repository-audit" / "demo.md"
            report_path.parent.mkdir(parents=True)
            report_path.write_text("# Report\nEvidence\n", encoding="utf-8")
            head_snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md", "docs/reports/repository-audit/demo.md"],
                generated_at="2026-05-26T00:00:01+00:00",
                git_info=GitInfo(head="head123456789", branch="test", dirty=False),
            )

        trend = build_trend([base_snapshot, head_snapshot], generated_at="2026-05-26T00:00:02+00:00")
        report = render_markdown_trend(trend)

        self.assertEqual(trend["schema_version"], "gcs-repository-audit-trend-0.1")
        self.assertIn("# GCS Repository Audit Trend", report)
        self.assertIn("Source: `snapshot-series`", report)
        self.assertIn("| files | 1 | 2 | +1 |", report)
        self.assertIn("| project_report | +1 | +2 |", report)

    def test_registry_index_renders_accepted_snapshot_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc123456789", branch=None, dirty=False),
            )

            reports_root = root / "docs" / "reports" / "repository-audit"
            accepted_dir = reports_root / "2026-05-26"
            accepted_dir.mkdir(parents=True)
            write_snapshot(snapshot, accepted_dir / "snapshot.json")
            (accepted_dir / "README.md").write_text("# Accepted Report\n", encoding="utf-8")
            (accepted_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "gcs-repository-audit-manifest-0.1",
                        "snapshot_id": "2026-05-26",
                        "acceptance_state": "accepted",
                        "accepted_at": "2026-05-26T00:00:01+00:00",
                        "accepted_by": "test",
                        "acceptance_scope": "milestone",
                        "revision": "abc123456789",
                        "snapshot_path": "snapshot.json",
                        "report_path": "README.md",
                        "description": "First accepted snapshot.",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            entries = load_registry_entries(reports_root)
            report = render_markdown_index(
                reports_root,
                entries,
                output=reports_root / "README.md",
                generated_at="2026-05-26T00:00:02+00:00",
            )

        self.assertEqual(len(entries), 1)
        self.assertIn("# GCS Repository Audit Index", report)
        self.assertIn("Accepted snapshots: `1`", report)
        self.assertIn("| 2026-05-26 | 2026-05-26T00:00:01+00:00 | abc123456789 | 1 | 1 | 0 |", report)
        self.assertIn("[snapshot](2026-05-26/snapshot.json)", report)

    def test_accepted_trend_allows_single_baseline_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            readme = root / "README.md"
            readme.write_text("# Demo\n", encoding="utf-8")
            snapshot = collect_snapshot(
                root,
                tracked_paths=["README.md"],
                generated_at="2026-05-26T00:00:00+00:00",
                git_info=GitInfo(head="abc123456789", branch=None, dirty=False),
            )

            reports_root = root / "docs" / "reports" / "repository-audit"
            accepted_dir = reports_root / "2026-05-26"
            accepted_dir.mkdir(parents=True)
            write_snapshot(snapshot, accepted_dir / "snapshot.json")
            (accepted_dir / "README.md").write_text("# Accepted Report\n", encoding="utf-8")
            (accepted_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "gcs-repository-audit-manifest-0.1",
                        "snapshot_id": "2026-05-26",
                        "acceptance_state": "accepted",
                        "accepted_at": "2026-05-26T00:00:01+00:00",
                        "revision": "abc123456789",
                        "snapshot_path": "snapshot.json",
                        "report_path": "README.md",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            output = reports_root / "trend.md"

            count = write_accepted_trend(reports_root, output, command="accepted-trend")
            loaded_snapshot_count = len(accepted_snapshots(reports_root))

            report = output.read_text(encoding="utf-8")

        self.assertEqual(count, 1)
        self.assertEqual(loaded_snapshot_count, 1)
        self.assertIn("Source: `accepted-snapshot-registry`", report)
        self.assertIn("baseline-only trend", report)
        self.assertIn("| files | 1 | 1 | 0 |", report)


if __name__ == "__main__":
    unittest.main()
