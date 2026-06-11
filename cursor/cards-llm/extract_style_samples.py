"""Sample diverse Q/A pairs from quizlet-modules for LLM style reference."""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT / "quizlet-modules"
OUT = Path(__file__).parent / "style_samples.json"
TARGET = 50


def classify_answer(answer: str) -> str:
    a = answer.strip()
    if re.fullmatch(r"\d{4}", a):
        return "year"
    if re.fullmatch(r"\d+", a):
        return "number"
    if re.search(r"[a-zA-Z]{3,}", a) and not re.search(r"[а-яА-ЯёЁ]", a):
        return "latin"
    if any(w in a.lower() for w in ("фильм", "картин", "роман", "рассказ", "пьес", "балет")):
        return "work"
    if len(a.split()) >= 3 and a[0].isupper():
        return "person"
    if "?" in a or len(a.split()) >= 5:
        return "definition"
    return "term"


def load_pairs() -> list[dict]:
    pairs: list[dict] = []
    for path in sorted(MODULES.glob("*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if "\t" not in line:
                continue
            answer, question = line.split("\t", 1)
            answer = re.sub(r"\s+", " ", answer.strip())
            question = re.sub(r"\s+", " ", question.strip())
            if not answer or not question:
                continue
            pairs.append(
                {
                    "answer": answer,
                    "question": question,
                    "category": classify_answer(answer),
                    "has_placeholder": bool(
                        re.search(
                            r"\b(ОН|ОНА|ОНИ|НЁМ|НЕЙ|НИХ|ЭТО|ЭТИ|ТАК|ТАМ|СТОЛЬКО)\b",
                            question,
                            re.I,
                        )
                    ),
                }
            )
    return pairs


def sample_pairs(pairs: list[dict], n: int) -> list[dict]:
    by_cat: dict[str, list[dict]] = {}
    for p in pairs:
        by_cat.setdefault(p["category"], []).append(p)

    picked: list[dict] = []
    seen_answers: set[str] = set()

    # Prefer placeholder-style questions (ЧГК pattern)
    placeholder = [p for p in pairs if p["has_placeholder"]]
    random.shuffle(placeholder)
    for p in placeholder:
        if len(picked) >= n // 2:
            break
        if p["answer"] in seen_answers:
            continue
        picked.append(p)
        seen_answers.add(p["answer"])

    # One per category
    for cat in sorted(by_cat):
        pool = [p for p in by_cat[cat] if p["answer"] not in seen_answers]
        if not pool:
            continue
        p = random.choice(pool)
        picked.append(p)
        seen_answers.add(p["answer"])

    random.shuffle(pairs)
    for p in pairs:
        if len(picked) >= n:
            break
        if p["answer"] in seen_answers:
            continue
        picked.append(p)
        seen_answers.add(p["answer"])

    return picked[:n]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    random.seed(43)
    pairs = load_pairs()
    samples = sample_pairs(pairs, TARGET)
    payload = {
        "source": "quizlet-modules",
        "total_pairs_in_modules": len(pairs),
        "sample_count": len(samples),
        "samples": samples,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"pairs: {len(pairs)}, samples: {len(samples)} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
