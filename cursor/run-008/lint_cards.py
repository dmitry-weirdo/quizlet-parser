"""Lint run-008 cards for quizlet-rules violations."""
import json
import re
import sys
from pathlib import Path

# Common cognate pairs from quizlet-rules examples (question stem -> answer must not contain)
COGNATE_CHECKS = [
    (r"апельсин", r"апельсин"),
    (r"сделк", r"сделк"),
    (r"нейросет", r"нейро"),
    (r"тыща", r"тысяч"),
    (r"\bфильтр", r"фильтр"),
    (r"колокол", r"glocke|колокол"),
    (r"троллейбус", r"троллейбус"),
    (r"retrieve|retriever", r"ретривер"),
]


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
            qn = norm(q)
            an = norm(a)

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
            if re.search(r"\bназывают\s+ЭТИМ\s+эффектом\b", q, re.I):
                issues.append(f"{prefix}: «ЭТИМ эффектом» → ИМ (пример 10)")
            for q_pat, a_pat in COGNATE_CHECKS:
                if re.search(q_pat, qn, re.I) and re.search(a_pat, an, re.I):
                    issues.append(f"{prefix}: однокоренность вопрос/ответ ({q_pat}) (пример 5)")
                    break
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
