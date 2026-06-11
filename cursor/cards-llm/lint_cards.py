"""Lint cards-llm output against quizlet-rules heuristics."""
import json
import re
import sys
from pathlib import Path

VALID_TYPES = {
    "",
    "NUMBER",
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
    "STREET",
    "RIVER",
    "PERSONALIA_MALE",
    "PERSONALIA_FEMALE",
    "GOD",
    "GODDESS",
    "NATIONALITY",
    "MOVIE",
    "CARTOON",
    "PAINTING",
    "ENGRAVING",
    "QUOTE",
    "SONG",
    "MUSICAL_BAND",
    "LANGUAGE",
    "SHIP",
    "AIRPLANE",
    "THEATRICAL_PIECE",
    "NOVELLA",
    "SHORT_STORY",
    "ARTICLE",
    "ESSAY",
    "NOVEL",
    "POEM",
    "BOOK",
    "SPEECH",
    "GAME",
    "ILLNESS",
    "BATTLE",
    "MILITARY_OPERATION",
    "CURRENCY",
    "AWARD",
    "ORDER",
    "TEAM",
    "RACE",
    "BUILDING",
    "SCULPTURE",
    "CLOTHING",
    "ABBREVIATION",
    "EFFECT",
    "INDEX",
    "EXPERIMENT",
    "THEOREM",
    "TRIAL",
    "COLOR",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def entity_names(entities: list) -> list[str]:
    out = []
    for e in entities:
        if isinstance(e, dict):
            out.append(e["name"])
    return out


def strip_placeholders(q: str) -> str:
    return re.sub(
        r"\b(это|эти|этим|этого|этой|этом|эту|эта|он|она|оно|его|её|им|ней|нем|них|"
        r"так|такой|такая|такое|такие|там|делал|сделал|столько)\b",
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
        if word in q:
            return True
    return False


def word_count(s: str) -> int:
    return len(s.split())


def lint_examples(examples: list) -> list[str]:
    issues = []
    for ex in examples:
        eid = ex["id"]
        entities = ex.get("entities") or []
        if not entities:
            issues.append(f"{eid}: пустой entities")
        if not ex.get("cards"):
            issues.append(f"{eid}: нет cards")

        for j, ent_item in enumerate(entities, 1):
            if "name" not in ent_item:
                issues.append(f"{eid}: entities[{j}] без name")
            t = ent_item.get("type", "")
            if t not in VALID_TYPES:
                issues.append(f"{eid}: entities[{j}] неизвестный type «{t}»")

        entity_norm = {norm(n) for n in entity_names(entities)}
        for i, card in enumerate(ex.get("cards", []), 1):
            q = card.get("question", "")
            a = card.get("answer", "")
            prefix = f"{eid}[{i}]"

            if not card.get("logic"):
                issues.append(f"{prefix}: нет logic")
            if word_count(a) > 12:
                issues.append(f"{prefix}: ответ >12 слов ({word_count(a)})")
            if re.search(r"\bКто\b", q):
                issues.append(f"{prefix}: содержит «Кто»")
            if re.search(r"\bКогда\b", q):
                issues.append(f"{prefix}: содержит «Когда»")
            if re.search(r"\bСколько\b", q):
                issues.append(f"{prefix}: содержит «Сколько»")
            if re.search(r"\bчто такое\b", q, re.I):
                issues.append(f"{prefix}: содержит «что такое»")
            if re.search(r"\bзвали\s+ОН\b", q, re.I):
                issues.append(f"{prefix}: «звали ОН» → звали ТАК")
            if answer_tokens_in_question(q, a):
                issues.append(f"{prefix}: ответ «{a}» (или часть) в вопросе")

            an = norm(a)
            if (
                an
                and not re.match(r"^[\d.:,\-\s]+$", an)
                and not re.match(r"^[a-z .,'\-«»]+$", an)
                and an not in entity_norm
                and not any(an in en or en in an for en in entity_norm if len(en) > 3)
            ):
                issues.append(f"{prefix}: ответ «{a}» не в entities")
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
