import importlib
import logging
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = PROJECT_DIR / "agents"
OUTPUTS_DIR = PROJECT_DIR / "outputs"


def main() -> int:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    handlers = [logging.FileHandler(OUTPUTS_DIR / "runner.log", encoding="utf-8")]
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
    )

    workers = sorted(
        path for path in AGENTS_DIR.glob("*.py") if not path.name.startswith("_")
    )
    if not workers:
        logging.error("No workers found in %s", AGENTS_DIR)
        return 1

    failed = False
    for path in workers:
        try:
            logging.info("Worker starting: %s", path.name)
            worker = importlib.import_module(f"agents.{path.stem}")
            report = worker.run()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
            output_path = OUTPUTS_DIR / f"{worker.NAME}-{timestamp}.md"
            output_path.write_text(report, encoding="utf-8")
            logging.info("Report saved: %s", output_path)
        except Exception:
            logging.exception("Worker failed: %s", path.name)
            failed = True

    exit_code = int(failed)
    logging.info("Runner completed: workers=%s exit_code=%s", len(workers), exit_code)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
