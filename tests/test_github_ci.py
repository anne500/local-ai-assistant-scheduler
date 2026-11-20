"""Deterministic checks for CI source identity and missing-evidence boundaries."""

import unittest
import tempfile
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
from extensions.github_ci import collect_evidence, render_report, main


RUN = {
    "id": 21890541227, "repository": {"full_name": "anne500/home-assistant-bri-demo"},
    "name": "Validate with hassfest", "status": "completed", "conclusion": "failure",
    "run_attempt": 1, "created_at": "2026-02-11T02:33:54Z", "updated_at": "2026-02-11T02:34:13Z",
    "html_url": "https://github.com/anne500/home-assistant-bri-demo/actions/runs/21890541227",
}
JOBS = {"total_count": 1, "jobs": [{
    "id": 63195208285, "run_id": RUN["id"], "run_attempt": 1,
    "name": "validate", "status": "completed", "conclusion": "failure", "steps": [],
}]}


class CIEvidenceChecks(unittest.TestCase):
    @patch("builtins.print")
    @patch("extensions.github_ci.summarize")
    @patch("extensions.github_ci.collect_evidence")
    def test_metadata_mode_skips_model_and_saves_evidence(self, collect, summarize, output):
        collect.return_value = {
            "repository": "anne500/home-assistant-bri-demo", "retrieved_at_utc": "2026-11-20T00:00:00Z",
            "run": RUN, "jobs": [], "evidence_gaps": ["Logs unavailable"], "root_cause": "Unavailable",
        }
        with tempfile.TemporaryDirectory() as directory:
            with patch("extensions.github_ci.PROJECT_DIR", Path(directory)), patch("sys.argv", ["github_ci", "--run-id", str(RUN["id"]), "--metadata-only"]):
                self.assertEqual(main(), 0)
            self.assertEqual(len(list(Path(directory).glob("outputs/*.json"))), 1)
            self.assertEqual(len(list(Path(directory).glob("outputs/*.md"))), 1)
            summarize.assert_not_called()

    @patch("builtins.print")
    @patch("extensions.github_ci.summarize", side_effect=RuntimeError("Model failed"))
    @patch("extensions.github_ci.collect_evidence")
    def test_model_failure_retains_evidence_and_reports_failure(self, collect, summarize, output):
        collect.return_value = {
            "repository": "anne500/home-assistant-bri-demo", "retrieved_at_utc": "2026-11-20T00:00:00Z",
            "run": RUN, "jobs": [], "evidence_gaps": ["Logs unavailable"], "root_cause": "Unavailable",
        }
        with tempfile.TemporaryDirectory() as directory:
            with patch("extensions.github_ci.PROJECT_DIR", Path(directory)), patch("sys.argv", ["github_ci", "--run-id", str(RUN["id"])]):
                self.assertEqual(main(), 1)
            self.assertEqual(len(list(Path(directory).glob("outputs/*.json"))), 1)
            report = next(Path(directory).glob("outputs/*.md")).read_text()
            self.assertIn("Summary unavailable: RuntimeError", report)
            self.assertIn("SHA-256:", report)

    @patch("extensions.github_ci.fetch_json", side_effect=[RUN, JOBS, RUN])
    def test_missing_steps_and_logs_are_explicit(self, fetch):
        evidence = collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])
        report = render_report(evidence)
        self.assertIn("Job 63195208285 has no step metadata.", report)
        self.assertIn("Root cause: Unavailable", report)
        self.assertIn("2026-02-11T02:33:54Z", report)
        self.assertIn(str(RUN["id"]), report)
        self.assertIn("/attempts/1/jobs", fetch.call_args_list[1].args[0])

    @patch("extensions.github_ci.fetch_json")
    def test_invalid_repository_fails_before_fetch(self, fetch):
        with self.assertRaises(ValueError):
            collect_evidence("../elsewhere", 1)
        fetch.assert_not_called()

    @patch("extensions.github_ci.fetch_json", return_value={**RUN, "id": 1})
    def test_run_mismatch_fails(self, fetch):
        with self.assertRaises(ValueError):
            collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])

    @patch("extensions.github_ci.fetch_json", return_value={**RUN, "repository": {"full_name": "other/repo"}})
    def test_repository_mismatch_fails(self, fetch):
        with self.assertRaises(ValueError):
            collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])

    @patch("extensions.github_ci.fetch_json", side_effect=[RUN, {"total_count": 0, "jobs": []}, RUN])
    def test_empty_jobs_record_gap(self, fetch):
        evidence = collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])
        self.assertIn("No job metadata was returned.", evidence["evidence_gaps"])

    @patch("extensions.github_ci.fetch_json")
    def test_pagination_retains_all_jobs(self, fetch):
        second = deepcopy(JOBS["jobs"][0])
        second["id"] = 2
        fetch.side_effect = [RUN, {"total_count": 2, "jobs": JOBS["jobs"]}, {"total_count": 2, "jobs": [second]}, RUN]
        evidence = collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])
        self.assertEqual(len(evidence["jobs"]), 2)
        self.assertIn("page=2", fetch.call_args_list[2].args[0])

    @patch("extensions.github_ci.fetch_json", side_effect=[RUN, JOBS, {**RUN, "run_attempt": 2}])
    def test_concurrent_rerun_rejected(self, fetch):
        with self.assertRaises(RuntimeError):
            collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])

    @patch("extensions.github_ci.fetch_json")
    def test_job_identity_mismatch_rejected(self, fetch):
        wrong = deepcopy(JOBS)
        wrong["jobs"][0]["run_id"] = 99
        fetch.side_effect = [RUN, wrong]
        with self.assertRaises(ValueError):
            collect_evidence("anne500/home-assistant-bri-demo", RUN["id"])


if __name__ == "__main__":
    unittest.main()
