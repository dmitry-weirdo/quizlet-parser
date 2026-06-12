"""Import existing repo data into knowledge/."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from knowledge.paths import (
    CURSOR_CANDIDATES,
    CURSOR_EXAMPLES,
    ENTITIES_QUEUE,
    EXAMPLES_GOLDEN,
    KNOWLEDGE,
    PARSING_EXAMPLES,
    QUIZLET_RULES,
    QUIZLET_RULES_BAD,
    REVIEW_QUEUE,
    RULES_CORE,
    RULES_DIR,
    RULES_JSON,
    RULES_NEGATIVE_DIR,
    STYLE_PAIRS,
    TEXT_PARSING_GUIDE,
    ENTITY_CACHE,
)
from knowledge.retrieval import rebuild_index
from knowledge.style_pairs import load_style_pairs
from knowledge.text_format import read_examples_json


def _ensure_dirs() -> None:
    for d in (
        RULES_DIR,
        RULES_NEGATIVE_DIR,
        KNOWLEDGE / "examples" / "golden",
        KNOWLEDGE / "corrections",
        KNOWLEDGE / "batches",
        KNOWLEDGE / "generations",
        KNOWLEDGE / "draft",
        KNOWLEDGE / "prompts",
        KNOWLEDGE / "reviews",
    ):
        d.mkdir(parents=True, exist_ok=True)


def _import_rules() -> None:
    if QUIZLET_RULES.exists():
        shutil.copy2(QUIZLET_RULES, RULES_CORE)
    if TEXT_PARSING_GUIDE.exists():
        shutil.copy2(TEXT_PARSING_GUIDE, RULES_DIR / "entity_types.md")
    if QUIZLET_RULES_BAD.exists():
        shutil.copy2(QUIZLET_RULES_BAD, RULES_NEGATIVE_DIR / "bad.md")
    rules = [
        {
            "id": "core-quizlet-rules",
            "text": "См. knowledge/rules/core.md",
            "type": "positive",
            "tags": ["cards"],
            "enabled": True,
            "source": "hermes/quizlet-rules.md",
        },
        {
            "id": "entity-types-guide",
            "text": "См. knowledge/rules/entity_types.md",
            "type": "reference",
            "tags": ["entities"],
            "enabled": True,
            "source": "docs/text_parsing_guide.md",
        },
        {
            "id": "negative-bad-examples",
            "text": "См. knowledge/rules/negative/bad.md",
            "type": "negative",
            "tags": ["cards"],
            "enabled": True,
            "source": "hermes/quizlet-rules-bad.md",
        },
    ]
    RULES_JSON.write_text(json.dumps({"rules": rules}, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_golden_example(ex: dict) -> None:
    ex = dict(ex)
    ex["status"] = "golden"
    out = EXAMPLES_GOLDEN / f"{ex['id']}.json"
    out.write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")


def _import_examples() -> int:
    seen: set[str] = set()
    count = 0
    for path in (PARSING_EXAMPLES, CURSOR_EXAMPLES):
        if not path.exists():
            continue
        for ex in read_examples_json(path):
            eid = ex.get("id")
            if not eid or eid in seen:
                continue
            seen.add(eid)
            _write_golden_example(ex)
            count += 1
    return count


def _import_style_pairs() -> int:
    pairs = load_style_pairs()
    payload = {"source": "quizlet-modules", "count": len(pairs), "pairs": pairs}
    STYLE_PAIRS.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return len(pairs)


def _import_entity_cache() -> int:
    if not ENTITIES_QUEUE.exists():
        ENTITY_CACHE.write_text(json.dumps({"entities": []}, indent=2), encoding="utf-8")
        return 0
    data = json.loads(ENTITIES_QUEUE.read_text(encoding="utf-8"))
    entities = data.get("entities", [])
    slim = [
        {
            "answer": e.get("answer"),
            "frequency": e.get("frequency"),
            "sample_questions": (e.get("sample_questions") or [])[:3],
        }
        for e in entities
    ]
    ENTITY_CACHE.write_text(
        json.dumps({"count": len(slim), "entities": slim}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(slim)


def _import_review_queue() -> int:
    if not CURSOR_CANDIDATES.exists():
        REVIEW_QUEUE.write_text(json.dumps({"items": []}, indent=2), encoding="utf-8")
        return 0
    candidates = json.loads(CURSOR_CANDIDATES.read_text(encoding="utf-8"))
    items = []
    for c in candidates:
        items.append(
            {
                "message_id": c.get("message_id"),
                "text": c.get("text"),
                "links": c.get("links") or [],
                "tags_hint": c.get("tags_hint") or [],
                "status": "pending",
            }
        )
    REVIEW_QUEUE.write_text(
        json.dumps({"source": "cursor/cards-llm/candidates.json", "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return len(items)


def run_bootstrap() -> dict:
    _ensure_dirs()
    stats = {
        "golden_examples": _import_examples(),
        "style_pairs": _import_style_pairs(),
        "entity_cache": _import_entity_cache(),
        "review_queue": _import_review_queue(),
    }
    _import_rules()
    index_stats = rebuild_index()
    stats["index"] = index_stats
    return stats
