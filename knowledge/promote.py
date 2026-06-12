"""Promote reviewed examples to golden pool."""
from __future__ import annotations

import json
from pathlib import Path

from knowledge.paths import DRAFT_DIR, EXAMPLES_GOLDEN, PARSING_EXAMPLES
from knowledge.retrieval import rebuild_index
from knowledge.text_format import read_examples_json


def promote_example(example_id: str, batch: str | None = None) -> dict:
    ex: dict | None = None
    if batch:
        batch_id = f"batch-{int(batch):03d}" if batch.isdigit() else batch
        draft = DRAFT_DIR / f"{batch_id}.json"
        if not draft.exists():
            raise SystemExit(f"Draft not found: {draft}")
        for item in read_examples_json(draft):
            if item.get("id") == example_id:
                ex = item
                break
    if ex is None:
        for path in DRAFT_DIR.glob("*.json"):
            for item in read_examples_json(path):
                if item.get("id") == example_id:
                    ex = item
                    break
            if ex:
                break
    if ex is None:
        raise SystemExit(f"Example not found: {example_id}")

    ex = dict(ex)
    ex["status"] = "golden"
    out = EXAMPLES_GOLDEN / f"{example_id}.json"
    EXAMPLES_GOLDEN.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")

    _sync_parsing_examples(ex)
    index_stats = rebuild_index()
    return {"id": example_id, "golden_path": str(out.relative_to(EXAMPLES_GOLDEN.parents[1])), "index": index_stats}


def promote_all_in_batch(batch: str) -> dict:
    batch_id = f"batch-{int(batch):03d}" if batch.isdigit() else batch
    draft = DRAFT_DIR / f"{batch_id}.json"
    if not draft.exists():
        raise SystemExit(f"Draft not found: {draft}")
    promoted = []
    for item in read_examples_json(draft):
        if item.get("cards"):
            result = promote_example(item["id"], batch=batch)
            promoted.append(result["id"])
    return {"batch": batch_id, "promoted": promoted}


def _sync_parsing_examples(ex: dict) -> None:
    """Append to parsing-examples.json if not already present (by id)."""
    if not PARSING_EXAMPLES.exists():
        return
    data = json.loads(PARSING_EXAMPLES.read_text(encoding="utf-8"))
    examples = data.get("examples", [])
    ids = {e.get("id") for e in examples}
    if ex.get("id") in ids:
        for i, e in enumerate(examples):
            if e.get("id") == ex.get("id"):
                examples[i] = _strip_for_parsing_examples(ex)
                break
    else:
        examples.append(_strip_for_parsing_examples(ex))
    data["examples"] = examples
    PARSING_EXAMPLES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _strip_for_parsing_examples(ex: dict) -> dict:
    out = {
        "id": ex.get("id"),
        "text": ex.get("text"),
        "tags": ex.get("tags") or [],
    }
    if ex.get("entities"):
        out["entities"] = ex["entities"]
    cards = []
    for c in ex.get("cards") or []:
        card = {"question": c.get("question"), "answer": c.get("answer")}
        if c.get("logic"):
            card["logic"] = c["logic"]
        cards.append(card)
    out["cards"] = cards
    return out


def approve_rule(rule_id: str) -> dict:
    from knowledge.paths import RULES_JSON

    data = json.loads(RULES_JSON.read_text(encoding="utf-8"))
    for rule in data.get("rules", []):
        if rule.get("id") == rule_id:
            rule["enabled"] = True
            rule["type"] = "positive"
            RULES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"id": rule_id, "enabled": True}
    raise SystemExit(f"Rule not found: {rule_id}")
