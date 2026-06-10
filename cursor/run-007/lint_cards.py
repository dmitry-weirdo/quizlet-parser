"""Lint run-007 cards for common quizlet-rules violations."""
import json
import re
import sys
from pathlib import Path


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def answer_in_question(question: str, answer: str) -> bool:
    q = norm(question)
    a = norm(answer)
    if len(a) < 3:
        return False
    q_clean = re.sub(
        r"\b(это|эти|этим|этого|этой|этом|эту|эта|он|она|оно|его|её|им|ней|нем|них|"
        r"так|такой|такая|такое|такие|там)\b",
        "",
        q,
    )
    return a in q_clean


def lint_examples(examples: list) -> list[str]:
    issues = []
    for ex in examples:
        eid = ex["id"]
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
                issues.append(f"{prefix}: «произнесена ОН» — ОН должен быть подлежащим")
            if re.search(r"\bназывают\s+\w+\s+ЭТИМ\b", q) and "«" not in a and " " not in a.strip():
                issues.append(f"{prefix}: «называют … ЭТИМ» с обрезанным ответом (пример 4)")
            if re.search(r"\bзвали\s+ЭТИМ\b", q):
                issues.append(f"{prefix}: «звали ЭТИМ» — персона → ОН/ОНА (пример 1)")
            if answer_in_question(q, a):
                issues.append(f"{prefix}: ответ «{a}» встречается в вопросе")
    return issues


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    path = Path(__file__).parent / "parsing-examples-cursor.json"
    if not path.exists():
        print("parsing-examples-cursor.json not found — run build_output.py first", file=sys.stderr)
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
