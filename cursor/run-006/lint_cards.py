"""Lint run-006 cards for common quizlet-rules violations."""
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
    # strip placeholders
    q_clean = re.sub(r"\b(это|эти|этим|этого|этой|этом|эту|эта|он|она|его|её|её|им|ней|нем|них|так|такой|такая|такое|такие|там)\b", "", q)
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
            if re.search(r"\bназывается ТАК\b", q):
                issues.append(f"{prefix}: «называется ТАК» для имени собственного")
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
