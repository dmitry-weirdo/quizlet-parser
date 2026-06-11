"""Lint run-010: quizlet-rules, per-pair cognates, typed entities."""
import json
import re
import sys
from pathlib import Path

VALID_TYPES = {
    "",
    "YEAR",
    "DATE",
    "CHARACTER_MALE",
    "CHARACTER_FEMALE",
    "BRAND",
    "NICKNAME",
    "IDIOM",
    "COUNTRY",
    "CITY",
    "STATE",
    "PERSONALIA_MALE",
    "PERSONALIA_FEMALE",
    "GOD",
    "GODDESS",
    "MOVIE",
    "PAINTING",
    "ENGRAVING",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def entity_names(entities: list) -> list[str]:
    out = []
    for e in entities:
        if isinstance(e, str):
            out.append(e)
        elif isinstance(e, dict):
            out.append(e["name"])
        else:
            raise TypeError(f"bad entity: {e!r}")
    return out


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

        for j, ent_item in enumerate(entities, 1):
            if isinstance(ent_item, str):
                issues.append(f"{eid}: entities[{j}] — строка, ожидается {{name, type}}")
                continue
            if "name" not in ent_item:
                issues.append(f"{eid}: entities[{j}] без name")
            t = ent_item.get("type", "")
            if t not in VALID_TYPES:
                issues.append(f"{eid}: entities[{j}] неизвестный type «{t}»")

        entity_norm = {norm(n) for n in entity_names(entities)}
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
