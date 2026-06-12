"""Assemble RAG-augmented prompt for Cursor card generation."""
from __future__ import annotations

import json
from pathlib import Path

from knowledge.paths import (
    BATCHES_DIR,
    DRAFT_DIR,
    GENERATE_PROMPT_TEMPLATE,
    PROMPTS_DIR,
    RULES_CORE,
    RULES_DIR,
    RULES_NEGATIVE_DIR,
)
from knowledge.retrieval import search, search_style_by_category
from knowledge.style_pairs import classify_answer
from knowledge.text_format import read_examples_json


def _read_optional(path: Path, max_chars: int = 12000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n…[обрезано]…"
    return text


def _format_example_block(hit: dict, full: bool = True) -> str:
    ex_path = Path("knowledge/examples/golden") / f"{hit['id']}.json"
    if ex_path.exists():
        ex = json.loads(ex_path.read_text(encoding="utf-8"))
    else:
        ex = hit
    lines = [f"### {ex.get('id')} (score={hit.get('score', 'n/a')})", f"TEXT: {ex.get('text', '')}"]
    if ex.get("entities"):
        lines.append("ENTITIES: " + json.dumps(ex["entities"], ensure_ascii=False))
    for card in ex.get("cards") or []:
        lines.append(f"- Q: {card.get('question')}")
        lines.append(f"  A: {card.get('answer')}")
        if full and card.get("logic"):
            lines.append(f"  LOGIC: {card.get('logic')}")
    return "\n".join(lines)


def _format_correction_block(hit: dict) -> str:
    return (
        f"### correction {hit.get('id')} (score={hit.get('score')})\n"
        f"Пример: {hit.get('example_id', '')}\n"
        f"Было: {json.dumps(hit.get('before', {}), ensure_ascii=False)}\n"
        f"Стало: {json.dumps(hit.get('after', {}), ensure_ascii=False)}\n"
        f"Комментарий: {hit.get('comment', '')}"
    )


def _format_style_block(hit: dict) -> str:
    return f"- A: {hit.get('answer')} | Q: {hit.get('question')} (score={hit.get('score')})"


def build_prompt_for_batch(batch: str) -> Path:
    batch_id = f"batch-{int(batch):03d}" if batch.isdigit() else batch
    batch_path = BATCHES_DIR / f"{batch_id}.json"
    if not batch_path.exists():
        raise SystemExit(f"Batch input not found: {batch_path}. Run: prepare-batch --batch {batch}")

    messages = json.loads(batch_path.read_text(encoding="utf-8"))
    sections: list[str] = [
        "# Генерация карточек (knowledge RAG prompt)",
        "",
        "Сгенерируй карточки для сообщений в конце файла. Формат выхода — как в "
        "`knowledge/draft/{batch}.json`: массив examples с `message_id`, `id`, `text`, "
        "`tags`, `entities`, `cards[{question, answer, logic}]`.",
        "",
    ]

    sections.append("## Core rules\n")
    sections.append(_read_optional(RULES_CORE, 20000))

    entity_guide = RULES_DIR / "entity_types.md"
    if entity_guide.exists():
        sections.append("\n## Entity types (text_parsing_guide)\n")
        sections.append(_read_optional(entity_guide, 8000))

    bad = RULES_NEGATIVE_DIR / "bad.md"
    if bad.exists():
        sections.append("\n## Negative examples\n")
        sections.append(_read_optional(bad, 6000))

    if GENERATE_PROMPT_TEMPLATE.exists():
        sections.append("\n## Operational checklist\n")
        sections.append(_read_optional(GENERATE_PROMPT_TEMPLATE, 6000))

    sections.append("\n## Сообщения батча и релевантный контекст\n")
    for msg in messages:
        text = msg.get("text", "")
        sections.append(f"\n---\n\n### Сообщение (message_id={msg.get('message_id')})\n")
        sections.append(f"```\n{text}\n```\n")

        golden_hits = search(text, kind="example", top_k=3)
        if golden_hits:
            sections.append("\n**Похожие golden examples:**\n")
            for h in golden_hits:
                sections.append(_format_example_block(h))
                sections.append("")

        corr_hits = search(text, kind="correction", top_k=2)
        if corr_hits:
            sections.append("\n**Похожие прошлые правки:**\n")
            for h in corr_hits:
                sections.append(_format_correction_block(h))
                sections.append("")

        # Style: guess category from first line of text
        cat = classify_answer(text.split("\n")[-1][:40])
        style_hits = search_style_by_category(text, category=cat, top_k=3)
        if not style_hits:
            style_hits = search(text, kind="style", top_k=3)
        if style_hits:
            sections.append("\n**Стиль вопросов (quizlet-modules):**\n")
            for h in style_hits:
                sections.append(_format_style_block(h))

    sections.append(
        f"\n## Выход\n\nЗапиши результат в `knowledge/draft/{batch_id}.json` "
        f"и обнови `knowledge/draft/{batch_id}.txt`.\n"
    )

    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = PROMPTS_DIR / f"{batch_id}.md"
    out.write_text("\n".join(sections), encoding="utf-8")
    return out


def build_prompt_for_message(text: str) -> str:
    """Build a compact prompt snippet for a single message."""
    parts = [f"TEXT:\n{text}\n"]
    for h in search(text, kind="example", top_k=3):
        parts.append(_format_example_block(h))
    for h in search(text, kind="style", top_k=3):
        parts.append(_format_style_block(h))
    return "\n\n".join(parts)
