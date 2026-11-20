"""Verify scheduled execution when pythonw provides no standard error stream."""

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


class WindowlessRunnerChecks(unittest.TestCase):
    def run_probe(self, fail_first: bool):
        with tempfile.TemporaryDirectory() as directory:
            probe = textwrap.dedent("""
                import logging
                import sys
                from pathlib import Path
                from types import SimpleNamespace
                import scheduler

                root = Path(sys.argv[1])
                scheduler.AGENTS_DIR = root / "agents"
                scheduler.OUTPUTS_DIR = root / "outputs"
                scheduler.AGENTS_DIR.mkdir()
                (scheduler.AGENTS_DIR / "worker.py").write_text("")
                fail_first = sys.argv[2] == "True"
                if fail_first:
                    (scheduler.AGENTS_DIR / "aaa_failure.py").write_text("")

                def load_worker(name):
                    if name.endswith("aaa_failure"):
                        raise RuntimeError("Controlled import failure")
                    return SimpleNamespace(NAME="windowless", run=lambda: "Saved report")

                scheduler.importlib.import_module = load_worker
                sys.stderr = None
                result = scheduler.main()
                assert result == int(fail_first)
                assert len(logging.getLogger().handlers) == 1
                assert logging.getLogger().handlers[0].stream is not None
                logging.shutdown()
                reports = list(scheduler.OUTPUTS_DIR.glob("windowless-*.md"))
                assert len(reports) == 1
                assert reports[0].read_text() == "Saved report"
                log = (scheduler.OUTPUTS_DIR / "runner.log").read_text()
                assert "Worker starting: worker.py" in log
                assert f"exit_code={result}" in log
                if fail_first:
                    assert "Controlled import failure" in log
            """)
            result = subprocess.run(
                [sys.executable, "-c", probe, directory, str(fail_first)],
                cwd=Path(__file__).resolve().parents[1],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_windowless_success_logs_and_saves_report(self):
        self.run_probe(False)

    def test_windowless_failure_keeps_running_and_returns_one(self):
        self.run_probe(True)


if __name__ == "__main__":
    unittest.main()
