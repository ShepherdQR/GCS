import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SESSION_EFFICIENCY_ROOT = REPO_ROOT / "tools" / "session_efficiency"
sys.path.insert(0, str(SESSION_EFFICIENCY_ROOT))

from gcs_session_efficiency import enrich_record, render_markdown_report, write_markdown_report


def base_record():
    return {
        "session_id": "demo-session",
        "task_id": "2026-05-26-demo",
        "task_class": "implementation",
        "token_telemetry": {
            "input_tokens": 8000,
            "output_tokens": 2000,
            "total_tokens": 10000,
            "source": "manual",
            "confidence": "estimated",
        },
        "durable_outputs": {
            "code_files": 2,
            "test_files": 1,
            "architecture_docs": 1,
            "task_cards": 1,
            "completed_archives": 1,
            "generated_reports": 1,
            "commits": 1,
        },
        "validation": {
            "checks_run": 4,
            "checks_passed": 4,
            "checks_failed": 0,
            "checks_skipped": 0,
            "closure_score": 38,
            "closure_score_max": 40,
        },
        "outcome_assessment": {
            "scope_completion": 1.0,
            "risk_reduction": 0.8,
            "reuse_score": 0.9,
            "rework_penalty": 0.0,
        },
    }


class SessionEfficiencyTests(unittest.TestCase):
    def test_known_token_record_computes_value_per_1k_tokens(self):
        enriched = enrich_record(base_record())

        metrics = enriched["derived_metrics"]

        self.assertEqual(metrics["token_cost_k"], 10.0)
        self.assertGreater(metrics["outcome_score"], 0.8)
        self.assertIsNotNone(metrics["value_per_1k_tokens"])
        self.assertEqual(metrics["value_per_1k_tokens"], metrics["net_efficiency"])

    def test_unknown_token_record_keeps_efficiency_denominators_empty(self):
        record = base_record()
        record["token_telemetry"] = {
            "source": "unknown",
            "confidence": "unknown",
        }

        enriched = enrich_record(record)
        report = render_markdown_report([record])

        self.assertIsNone(enriched["derived_metrics"]["token_cost_k"])
        self.assertIsNone(enriched["derived_metrics"]["value_per_1k_tokens"])
        self.assertIn("| 2026-05-26-demo | implementation | n/a | unknown |", report)

    def test_rework_penalty_lowers_net_efficiency(self):
        record = base_record()
        record["validation"]["checks_failed"] = 2
        record["outcome_assessment"]["rework_penalty"] = 0.4

        enriched = enrich_record(record)
        metrics = enriched["derived_metrics"]

        self.assertEqual(metrics["rework_penalty"], 0.4)
        self.assertLess(metrics["net_efficiency"], metrics["value_per_1k_tokens"])

    def test_write_markdown_report_outputs_table(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "session-efficiency.md"

            write_markdown_report([base_record()], output, command="session_efficiency.py report")

            report = output.read_text(encoding="utf-8")

        self.assertIn("# GCS Session Efficiency Report", report)
        self.assertIn("Token-known records: `1`", report)
        self.assertIn("session_efficiency.py report", report)


if __name__ == "__main__":
    unittest.main()
