"""Load and classify style pairs from quizlet-modules."""
from __future__ import annotations

import re
from pathlib import Path

from knowledge.paths import QUIZLET_MODULES


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


def has_placeholder(question: str) -> bool:
    return bool(
        re.search(
            r"\b(ОН|ОНА|ОНИ|НЁМ|НЕЙ|НИХ|ЭТО|ЭТИ|ТАК|ТАМ|СТОЛЬКО)\b",
            question,
            re.I,
        )
    )


def load_style_pairs(modules_dir: Path | None = None) -> list[dict]:
    base = modules_dir or QUIZLET_MODULES
    pairs: list[dict] = []
    for path in sorted(base.glob("*.txt")):
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
                    "has_placeholder": has_placeholder(question),
                    "source_file": path.name,
                }
            )
    return pairs
