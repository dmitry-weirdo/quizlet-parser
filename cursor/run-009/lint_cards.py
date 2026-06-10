"""Lint run-009: quizlet-rules, per-pair cognates, entities present."""
import json
import re
import sys
from pathlib import Path


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def strip_placeholders(q: str) -> str:
    return re.sub(
        r"\b(это|эти|этим|этого|этой|этом|эту|эта|он|она|оно|его|её|им|ней|нем|них|"
        r"так|такой|такая|такое|такие|там|делал|сделал)\b",
        "",
        norm(q),
    )


def answer_tokens_in_question(question: str, answer: str) -> bool:
    q = strip_placeholders(question)
    a = norm(answer)
    if len(a) < 3:
        return False
    if a in q:
        return True
    for word in re.findall(r"[a-zA-Zа-яА-ЯёЁ]{4,}", a):
        if len(word) >= 4 and word in q:
            return True
    return False


def lint_examples(examples: list) -> list[str]:
    issues = []
    for ex in examples:
        eid = ex["id"]
        entities = ex.get("entities") or []
        if not entities:
            issues.append(f"{eid}: пустой entities")

        entity_norm = {norm(e) for e in entities}
        for i, card in enumerate(ex.get("cards", []), 1):
            q = card["question"]
            a = card.get("answer", "")
            prefix = f"{eid}[{i}]"

            if re.search(r"\bКто\b", q):
                issues.append(f"{prefix}: содержит «Кто»")
            if re.search(r"\bкак называется\b", q, re.I):
                issues.append(f"{prefix}: содержит «как называется»")
            if re.search(r"\bчто такое\b", q, re.I):
                issues.append(f"{prefix}: содержит «что такое»")
            if re.search(r"\bпроизнесен[аоы]?\s+ОН\b", q, re.I):
                issues.append(f"{prefix}: «произнесена ОН»")
            if re.search(r"\bзвали\s+ЭТИМ\b", q):
                issues.append(f"{prefix}: «звали ЭТИМ» — персона → ОН/ОНА")
            if re.search(r"\bназывают\s+ЭТИМ\s+эффектом\b", q, re.I):
                issues.append(f"{prefix}: «ЭТИМ эффектом» → ИМ (пример 10)")
            if answer_tokens_in_question(q, a):
                issues.append(f"{prefix}: ответ «{a}» (или его часть) в вопросе этой пары")

            an = norm(a)
            if (
                an
                and not re.match(r"^[\d.:,\-\s]+$", an)
                and not re.match(r"^[a-z .,'\-]+$", an)
                and an not in entity_norm
                and not any(an in en or en in an for en in entity_norm if len(en) > 3)
            ):
                issues.append(
                    f"{prefix}: ответ «{a}» не в entities (добавь entity или wiki в logic)"
                )
    return issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(__file__).parent / "parsing-examples-cursor.json"
    if not path.exists():
        print("Run build_output.py first", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text(encoding="utf-8"))
    issues = lint_examples(data["examples"])
    if issues:
        print(f"FAIL: {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    print("OK: no lint issues")


if __name__ == "__main__":
    main()
