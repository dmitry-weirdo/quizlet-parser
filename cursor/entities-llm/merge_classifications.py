"""Merge agent classification batches into by-type.json and unmapped.json."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path


def _batch_priority(name: str) -> int:
    if name == "batch-pilot.json":
        return 0
    m = re.match(r"batch-(\d+)\.json", name)
    return int(m.group(1)) if m else 999

ROOT = Path(__file__).parent
QUEUE = ROOT / "entities_queue.json"
CLASS_DIR = ROOT / "classifications"

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
    "PERSONALIA_MALE",
    "PERSONALIA_FEMALE",
    "GOD",
    "GODDESS",
    "MOVIE",
    "PAINTING",
    "ENGRAVING",
    "QUOTE",
    "SONG",
    "LANGUAGE",
    "SHIP",
    "AIRPLANE",
    "THEATRICAL_PIECE",
    "NOVELLA",
    "NOVEL",
    "POEM",
    "BOOK",
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
}

TYPE_ORDER = sorted(t for t in VALID_TYPES if t)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not QUEUE.exists():
        print("Run extract_for_llm.py first", file=sys.stderr)
        return 1

    queue_data = json.loads(QUEUE.read_text(encoding="utf-8"))
    expected_answers = {e["answer"] for e in queue_data["entities"]}

    batch_files = sorted(CLASS_DIR.glob("batch-*.json"), key=lambda p: _batch_priority(p.name))
    if not batch_files:
        print("No classifications yet", file=sys.stderr)
        return 1

    classified: dict[str, str] = {}
    errors: list[str] = []

    for bf in batch_files:
        items = json.loads(bf.read_text(encoding="utf-8"))
        for item in items:
            ans = item.get("answer", "")
            typ = item.get("type", "")
            if typ not in VALID_TYPES:
                errors.append(f"{bf.name}: invalid type {typ!r} for {ans!r}")
                typ = ""
            classified[ans] = typ

    missing = expected_answers - set(classified.keys())
    extra = set(classified.keys()) - expected_answers

    by_type: dict[str, list[str]] = {t: [] for t in TYPE_ORDER if t}
    unmapped: list[str] = []

    for ans, typ in classified.items():
        if not typ:
            unmapped.append(ans)
        else:
            by_type.setdefault(typ, []).append(ans)

    for t in by_type:
        by_type[t].sort(key=str.lower)
    unmapped.sort(key=str.lower)

    all_batches = list((ROOT / "batches").glob("batch-*.json"))
    n_batches_total = len([b for b in all_batches if b.name != "batch-pilot.json"])
    pilot_done = (CLASS_DIR / "batch-pilot.json").exists()
    stats = {
        "total_cards": queue_data["total_cards"],
        "unique_answers": queue_data["unique_answers"],
        "classified": len(classified),
        "missing": len(missing),
        "pilot_done": pilot_done,
        "pilot_classified": sum(
            1 for bf in batch_files if bf.name == "batch-pilot.json"
        )
        and len(json.loads((CLASS_DIR / "batch-pilot.json").read_text(encoding="utf-8")))
        if pilot_done
        else 0,
        "batches_done": len([b for b in batch_files if b.name != "batch-pilot.json"]),
        "batches_total": n_batches_total,
        "complete_percent": round(100 * len(classified) / len(expected_answers), 1),
        "mapped": sum(len(v) for v in by_type.values()),
        "unmapped": len(unmapped),
        "per_type": {t: len(by_type.get(t, [])) for t in sorted(by_type)},
        "errors": errors[:50],
        "missing_sample": sorted(missing)[:20],
        "extra_sample": sorted(extra)[:20],
    }

    (ROOT / "by-type.json").write_text(
        json.dumps({k: by_type[k] for k in sorted(by_type)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (ROOT / "unmapped.json").write_text(
        json.dumps(unmapped, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # README
    readme = f"""# entities-llm: категоризация ответов quizlet-modules

Классификация **агентом Cursor** (не эвристики). Контекст: `answer` + `sample_questions`.

Источник: [`quizlet-modules/`](../../quizlet-modules/). Типы: [`text_parsing_guide.md`](../../docs/text_parsing_guide.md).

## Прогресс

| Метрика | Значение |
|---------|----------|
| Уникальных ответов | {stats['unique_answers']} |
| Классифицировано | {stats['classified']} ({stats['complete_percent']}%) |
| Pilot (batch-pilot) | {stats['pilot_classified']} сущностей |
| Батчей готово | {stats['batches_done']} / {stats['batches_total']} |
| С типом | {stats['mapped']} |
| Unmapped | {stats['unmapped']} |

## Workflow

```bash
python cursor/entities-llm/extract_for_llm.py
python cursor/entities-llm/split_batches.py
# LLM-агент: batches/batch-NNN.json -> classifications/batch-NNN.json
python cursor/entities-llm/merge_classifications.py
```

Инструкция агенту: [`classify_prompt.md`](classify_prompt.md).

Эвристический baseline: [`entities-from-quizlet-cards/`](../entities-from-quizlet-cards/).
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")

    print(
        f"classified: {stats['classified']}/{stats['unique_answers']} "
        f"({stats['complete_percent']}%), batches: {stats['batches_done']}/{stats['batches_total']}, "
        f"mapped: {stats['mapped']}, unmapped: {stats['unmapped']}"
    )
    if errors:
        print(f"warnings: {len(errors)}")
    if missing and len(batch_files) == n_batches_total:
        print(f"missing: {len(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
