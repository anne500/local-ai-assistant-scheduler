"""Create a source-backed brief from a pinned public GitHub Actions run."""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4

from agents._ollama import summarize

PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPOSITORY = "anne500/home-assistant-bri-demo"


def fetch_json(url: str) -> dict:
    request = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "local-ai-assistant-scheduler",
    })
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def collect_evidence(repository: str, run_id: int) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Repository must use owner/name format.")
    if run_id <= 0:
        raise ValueError("Run ID must be positive.")
    base = f"https://api.github.com/repos/{repository}/actions/runs/{run_id}"
    raw_run = fetch_json(base)
    if raw_run["id"] != run_id:
        raise ValueError("GitHub returned a different run ID.")
    if raw_run["repository"]["full_name"].lower() != repository.lower():
        raise ValueError("GitHub returned a different repository.")
    run = {key: raw_run.get(key) for key in (
        "id", "name", "status", "conclusion", "run_attempt", "head_sha",
        "head_branch", "event", "created_at", "run_started_at", "updated_at", "html_url",
    )}
    attempt = run["run_attempt"]
    if not isinstance(attempt, int) or attempt <= 0:
        raise ValueError("Run attempt must be a positive integer.")
    jobs = []
    page = 1
    while True:
        payload = fetch_json(f"{base}/attempts/{attempt}/jobs?per_page=100&page={page}")
        batch = payload["jobs"]
        for job in batch:
            if job["run_id"] != run_id or job.get("run_attempt", attempt) != attempt:
                raise ValueError("Job metadata belongs to a different run or attempt.")
            jobs.append({
                "id": job["id"], "name": job["name"],
                "status": job["status"], "conclusion": job.get("conclusion"),
                "started_at": job.get("started_at"), "completed_at": job.get("completed_at"),
                "html_url": job.get("html_url"),
                "steps": [{key: step.get(key) for key in (
                    "number", "name", "status", "conclusion",
                )} for step in job.get("steps", [])],
            })
        if len(jobs) >= payload["total_count"] or not batch:
            break
        page += 1
    final_run = fetch_json(base)
    if any(final_run.get(key) != raw_run.get(key) for key in ("run_attempt", "status", "updated_at")):
        raise RuntimeError("The run changed during retrieval. Repeat the request for a consistent snapshot.")
    gaps = ["Build logs were not retrieved; root cause is unavailable from this snapshot."]
    if not jobs:
        gaps.append("No job metadata was returned.")
    for job in jobs:
        if not job["steps"]:
            gaps.append(f"Job {job['id']} has no step metadata.")
    if len(jobs) < payload["total_count"]:
        gaps.append("The jobs response ended before all advertised jobs were returned.")
    return {
        "repository": repository, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "run": run, "jobs": jobs, "evidence_gaps": gaps,
        "root_cause": "Unavailable: diagnostic logs were not retrieved.",
        "sources": [base, f"{base}/attempts/{attempt}/jobs"],
    }


def render_report(evidence: dict, summary: str | None = None) -> str:
    run = evidence["run"]
    lines = [
        "# GitHub CI Evidence Brief", "",
        f"Repository: {evidence['repository']}", "",
        f"Run ID: {run['id']} | Attempt: {run['run_attempt']}", "",
        f"Workflow: {run['name']}", "",
        f"Status: {run['status']} | Conclusion: {run['conclusion']}", "",
        f"Run created at: {run['created_at']}", "",
        f"Retrieved at (UTC): {evidence['retrieved_at_utc']}", "",
        f"Source: {run['html_url']}", "",
        "## Available job evidence", "",
    ]
    for job in evidence["jobs"]:
        lines.append(f"- Job {job['id']}: {job['name']}; {job['status']}; {job['conclusion']}.")
        for step in job["steps"]:
            lines.append(f"  - Step {step['number']}: {step['name']}; {step['conclusion']}.")
    lines += ["", "## Evidence gaps", ""]
    lines.extend(f"- {gap}" for gap in evidence["evidence_gaps"])
    lines += ["", f"Root cause: {evidence['root_cause']}", ""]
    if summary is not None:
        lines += ["## Model summary for review", "", summary, ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPOSITORY)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--metadata-only", action="store_true", help="Save retrieved metadata without calling Ollama.")
    args = parser.parse_args()
    try:
        evidence = collect_evidence(args.repo, args.run_id)
        output_dir = PROJECT_DIR / "outputs"
        output_dir.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S_%f")
        stem = f"github-ci-{args.run_id}-{stamp}-{uuid4().hex[:8]}"
        evidence_path = output_dir / f"{stem}.json"
        evidence_bytes = (json.dumps(evidence, indent=2) + "\n").encode("utf-8")
        with evidence_path.open("xb") as output:
            output.write(evidence_bytes)
        report = render_report(evidence)
        model_failed = False
        if not args.metadata_only:
            try:
                summary = summarize(
                    "Write one short sentence stating the supplied workflow name, run ID, "
                    "status and conclusion. Attribute it to GitHub metadata. "
                    "Use only supplied facts. Root cause is unavailable; do not infer "
                    "a cause, repair, release decision or current repository health.",
                    evidence,
                )
                report = render_report(evidence, summary)
            except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError, KeyError) as error:
                report += f"\n## Model status\n\nSummary unavailable: {type(error).__name__}. Evidence was retained.\n"
                model_failed = True
        digest = hashlib.sha256(evidence_bytes).hexdigest()
        report += f"\n## Saved evidence\n\nFile: {evidence_path.name}\n\nSHA-256: {digest}\n"
        report_path = output_dir / f"{stem}.md"
        with report_path.open("x", encoding="utf-8") as output:
            output.write(report)
        print(f"Evidence saved: {evidence_path}")
        print(f"Report saved: {report_path}")
        print(report)
        return int(model_failed)
    except (HTTPError, URLError, TimeoutError, ValueError, KeyError, OSError, RuntimeError) as error:
        print(f"CI extension failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
