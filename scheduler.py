import importlib
import logging
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
AGENTS_DIR = PROJECT_DIR / "agents"
OUTPUTS_DIR = PROJECT_DIR / "outputs"


def main() -> int:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(OUTPUTS_DIR / "runner.log", encoding="utf-8"),
        ],
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
            worker = importlib.import_module(f"agents.{path.stem}")
            report = worker.run()
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
            output_path = OUTPUTS_DIR / f"{worker.NAME}-{timestamp}.md"
            output_path.write_text(report, encoding="utf-8")
            logging.info("Report saved: %s", output_path)
        except Exception:
            logging.exception("Worker failed: %s", path.name)
            failed = True

    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
