import json
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

NAME = "cedar-ci"
PROJECT_DIR = Path(__file__).resolve().parents[1]
FIXTURE = PROJECT_DIR / "fixtures" / "cedar-ci.txt"


def run() -> str:
    evidence = FIXTURE.read_text(encoding="utf-8").strip()
    payload = {
        "model": "qwen3.5:4b",
        "stream": False,
        "think": False,
        "options": {"temperature": 0, "num_predict": 64},
        "messages": [
            {
                "role": "user",
                "content": f"Summarize in one sentence using only these facts: {evidence}",
            }
        ],
    }
    request = Request(
        "http://127.0.0.1:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=180) as response:
        result = json.load(response)

    summary = result["message"]["content"].strip()
    if not summary or result.get("done_reason") == "length":
        raise RuntimeError("Ollama returned an empty or truncated summary.")

    return (
        "# Cedar CI Brief\n\n"
        f"{summary}\n\n"
        "## Source evidence (synthetic)\n\n"
        f"{evidence}\n"
    )


if __name__ == "__main__":
    report = run()
    output_dir = PROJECT_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    output_path = output_dir / f"{NAME}-{timestamp}.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"Report saved: {output_path}")
    print(report)
