"""Run spaCy NER on all quizlet-modules card answers (raw PER/LOC/ORG labels)."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import spacy

ROOT = Path(__file__).parent
MODULES = ROOT.parents[1] / "quizlet-modules"
OUTPUT = ROOT / "output"
MODEL_NAME = "ru_core_news_lg"
BATCH_SIZE = 256
LABELS = ("PER", "LOC", "ORG")


@dataclass
class Card:
    card_index: int
    source_file: str
    line_no: int
    answer: str
    question: str


@dataclass
class EntitySpan:
    text: str
    label: str
    start: int
    end: int

    def to_dict(self) -> dict:
        return {"text": self.text, "label": self.label, "start": self.start, "end": self.end}


@dataclass
class NerResult:
    card: Card
    entities: list[EntitySpan] = field(default_factory=list)
    coverage: str = "no_entities"

    def to_dict(self) -> dict:
        return {
            "card_index": self.card.card_index,
            "source_file": self.card.source_file,
            "line_no": self.card.line_no,
            "answer": self.card.answer,
            "question": self.card.question,
            "entities": [e.to_dict() for e in self.entities],
            "coverage": self.coverage,
        }


def parse_cards() -> list[Card]:
    """Parse every tab-separated line from quizlet-modules (no deduplication)."""
    cards: list[Card] = []
    card_index = 0
    for path in sorted(MODULES.glob("*.txt")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "\t" not in line:
                continue
            answer, question = line.split("\t", 1)
            answer = re.sub(r"\s+", " ", answer.strip())
            question = re.sub(r"\s+", " ", question.strip())
            if not answer:
                continue
            card_index += 1
            cards.append(
                Card(
                    card_index=card_index,
                    source_file=path.name,
                    line_no=line_no,
                    answer=answer,
                    question=question,
                )
            )
    return cards


def classify_coverage(answer: str, entities: list[EntitySpan]) -> str:
    if not entities:
        return "no_entities"
    if len(entities) >= 2:
        return "multiple_entities"
    ent = entities[0]
    if ent.start == 0 and ent.end == len(answer):
        return "single_entity_full"
    return "single_entity_partial"


def extract_entities(doc) -> list[EntitySpan]:
    return [
        EntitySpan(text=ent.text, label=ent.label_, start=ent.start_char, end=ent.end_char)
        for ent in doc.ents
    ]


def run_ner(cards: list[Card], nlp) -> list[NerResult]:
    answers = [c.answer for c in cards]
    results: list[NerResult] = []
    for card, doc in zip(cards, nlp.pipe(answers, batch_size=BATCH_SIZE)):
        entities = extract_entities(doc)
        coverage = classify_coverage(card.answer, entities)
        results.append(NerResult(card=card, entities=entities, coverage=coverage))
    return results


def build_stats(results: list[NerResult]) -> dict:
    span_counts = Counter()
    coverage_counts = Counter()
    cards_with_entities = 0
    unique_answers_by_label: dict[str, set[str]] = {label: set() for label in LABELS}

    for r in results:
        coverage_counts[r.coverage] += 1
        if r.entities:
            cards_with_entities += 1
        for ent in r.entities:
            span_counts[ent.label] += 1
            if ent.label in unique_answers_by_label:
                unique_answers_by_label[ent.label].add(r.card.answer)

    return {
        "model": MODEL_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cards": len(results),
        "cards_with_entities": cards_with_entities,
        "cards_without_entities": len(results) - cards_with_entities,
        "span_counts_by_label": {label: span_counts.get(label, 0) for label in LABELS},
        "unique_answers_by_label": {label: len(unique_answers_by_label[label]) for label in LABELS},
        "coverage_counts": dict(coverage_counts),
    }


def build_by_label(results: list[NerResult]) -> dict:
    """Group by spaCy label; aggregate frequency per unique answer."""
    # answer -> {label -> {frequency, sample_questions, entities}}
    answer_data: dict[str, dict] = {}
    for r in results:
        if not r.entities:
            continue
        key = r.card.answer
        if key not in answer_data:
            answer_data[key] = {
                "answer": key,
                "frequency": 0,
                "sample_questions": [],
                "labels_seen": set(),
                "entities_by_label": defaultdict(list),
            }
        entry = answer_data[key]
        entry["frequency"] += 1
        if len(entry["sample_questions"]) < 3 and r.card.question not in entry["sample_questions"]:
            entry["sample_questions"].append(r.card.question)
        for ent in r.entities:
            entry["labels_seen"].add(ent.label)
            spans = entry["entities_by_label"][ent.label]
            span_dict = ent.to_dict()
            if span_dict not in spans:
                spans.append(span_dict)

    by_label: dict[str, list] = {label: [] for label in LABELS}
    for entry in answer_data.values():
        for label in entry["labels_seen"]:
            by_label[label].append(
                {
                    "answer": entry["answer"],
                    "frequency": entry["frequency"],
                    "sample_questions": entry["sample_questions"],
                    "entities": entry["entities_by_label"][label],
                }
            )

    for label in LABELS:
        by_label[label].sort(key=lambda x: (-x["frequency"], x["answer"]))

    return by_label


def build_no_entities(results: list[NerResult]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for r in results:
        if r.entities:
            continue
        key = r.card.answer
        if key not in grouped:
            grouped[key] = {"answer": key, "frequency": 0, "sample_questions": []}
        entry = grouped[key]
        entry["frequency"] += 1
        if len(entry["sample_questions"]) < 3 and r.card.question not in entry["sample_questions"]:
            entry["sample_questions"].append(r.card.question)

    items = list(grouped.values())
    items.sort(key=lambda x: (-x["frequency"], x["answer"]))
    return items


def write_jsonl(path: Path, items: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def build_report(stats: dict, by_label: dict, results: list[NerResult], no_entities: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# spaCy NER — отчёт по quizlet-modules\n")
    lines.append(f"- **Модель:** `{stats['model']}`")
    lines.append(f"- **Дата:** {stats['generated_at']}")
    lines.append(f"- **Карточек:** {stats['total_cards']}")
    lines.append(f"- **С сущностями:** {stats['cards_with_entities']} ({100 * stats['cards_with_entities'] / stats['total_cards']:.1f}%)")
    lines.append(f"- **Без сущностей:** {stats['cards_without_entities']} ({100 * stats['cards_without_entities'] / stats['total_cards']:.1f}%)\n")

    lines.append("## Span'ы по меткам spaCy\n")
    lines.append("| Метка | Span'ов | Уникальных ответов |")
    lines.append("|-------|---------|-------------------|")
    for label in LABELS:
        spans = stats["span_counts_by_label"][label]
        unique = stats["unique_answers_by_label"][label]
        lines.append(f"| `{label}` | {spans} | {unique} |")
    lines.append("")

    lines.append("## Покрытие ответа\n")
    lines.append("| Тип | Карточек |")
    lines.append("|-----|----------|")
    for cov, count in sorted(stats["coverage_counts"].items(), key=lambda x: -x[1]):
        lines.append(f"| `{cov}` | {count} |")
    lines.append("")

    for label in LABELS:
        items = by_label[label]
        if not items:
            continue
        lines.append(f"## Топ-20 ответов — `{label}`\n")
        lines.append("| Ответ | Частота | Пример вопроса |")
        lines.append("|-------|---------|----------------|")
        for item in items[:20]:
            q = item["sample_questions"][0] if item["sample_questions"] else ""
            if len(q) > 80:
                q = q[:77] + "..."
            lines.append(f"| {item['answer']} | {item['frequency']} | {q} |")
        lines.append("")

    partial = [r for r in results if r.coverage == "single_entity_partial"][:15]
    if partial:
        lines.append("## Примеры partial span (сущность не покрывает весь ответ)\n")
        for r in partial:
            ents = ", ".join(f"`{e.text}` ({e.label})" for e in r.entities)
            lines.append(f"- **{r.card.answer}** → {ents}")
            q = r.card.question
            if len(q) > 100:
                q = q[:97] + "..."
            lines.append(f"  - вопрос: {q}")
        lines.append("")

    multi = [r for r in results if r.coverage == "multiple_entities"][:15]
    if multi:
        lines.append("## Примеры multiple entities\n")
        for r in multi:
            ents = ", ".join(f"`{e.text}` ({e.label})" for e in r.entities)
            lines.append(f"- **{r.card.answer}** → {ents}")
        lines.append("")

    lines.append("## Топ-30 ответов без сущностей (по частоте)\n")
    for item in no_entities[:30]:
        lines.append(f"- `{item['answer']}` — {item['frequency']} карточ.")
    lines.append("")

    return "\n".join(lines)


def write_outputs(results: list[NerResult]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    stats = build_stats(results)
    by_label = build_by_label(results)
    no_entities = build_no_entities(results)

    (OUTPUT / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUTPUT / "by_label.json").write_text(
        json.dumps(by_label, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUTPUT / "no_entities.json").write_text(
        json.dumps(no_entities, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_jsonl(OUTPUT / "per_card.jsonl", [r.to_dict() for r in results])
    (OUTPUT / "report.md").write_text(
        build_report(stats, by_label, results, no_entities), encoding="utf-8"
    )


def main() -> None:
    print(f"Parsing cards from {MODULES}...")
    cards = parse_cards()
    print(f"  {len(cards)} cards")

    print(f"Loading spaCy model {MODEL_NAME}...")
    nlp = spacy.load(MODEL_NAME)

    print("Running NER...")
    results = run_ner(cards, nlp)

    print(f"Writing outputs to {OUTPUT}...")
    write_outputs(results)

    stats = json.loads((OUTPUT / "stats.json").read_text(encoding="utf-8"))
    print(f"Done. Cards with entities: {stats['cards_with_entities']}/{stats['total_cards']}")
    print(f"Report: {OUTPUT / 'report.md'}")


if __name__ == "__main__":
    main()
