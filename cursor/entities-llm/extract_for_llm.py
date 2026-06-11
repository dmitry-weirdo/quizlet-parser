"""Extract unique card answers + sample questions from quizlet-modules."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
MODULES = ROOT.parents[1] / "quizlet-modules"
OUT = ROOT / "entities_queue.json"
MAX_SAMPLES = 3


def parse_modules() -> tuple[dict[str, dict], int]:
    """Return answer -> {answer, frequency, sample_questions}, total card count."""
    data: dict[str, dict] = {}
    questions_seen: dict[str, set[str]] = defaultdict(set)
    total = 0

    for path in sorted(MODULES.glob("*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            answer, question = line.split("\t", 1)
            answer = re.sub(r"\s+", " ", answer.strip())
            question = re.sub(r"\s+", " ", question.strip())
            if not answer:
                continue
            total += 1
            if answer not in data:
                data[answer] = {
                    "answer": answer,
                    "frequency": 0,
                    "sample_questions": [],
                }
            data[answer]["frequency"] += 1
            if question and len(questions_seen[answer]) < MAX_SAMPLES:
                if question not in questions_seen[answer]:
                    questions_seen[answer].add(question)
                    data[answer]["sample_questions"].append(question)

    return data, total


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    data, total = parse_modules()
    queue = sorted(data.values(), key=lambda x: (-x["frequency"], x["answer"].lower()))
    payload = {
        "total_cards": total,
        "unique_answers": len(queue),
        "entities": queue,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"cards: {total}, unique: {len(queue)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
