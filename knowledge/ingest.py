"""Ingest human edits: diff draft vs generation snapshot → corrections."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from knowledge.paths import CORRECTIONS_DIR, DRAFT_DIR, GENERATIONS_DIR, RULES_JSON
from knowledge.retrieval import rebuild_index
from knowledge.text_format import read_examples_json, sync_txt_to_json, write_examples_json


def _card_key(card: dict) -> str:
    return f"{card.get('question', '')}\0{card.get('answer', '')}"


def _diff_cards(before_cards: list[dict], after_cards: list[dict]) -> list[dict]:
    changes: list[dict] = []
    max_len = max(len(before_cards), len(after_cards))
    for i in range(max_len):
        b = before_cards[i] if i < len(before_cards) else None
        a = after_cards[i] if i < len(after_cards) else None
        if b is None and a is not None:
            changes.append({"card_index": i, "action": "add", "before": None, "after": a})
        elif a is None and b is not None:
            changes.append({"card_index": i, "action": "reject", "before": b, "after": None})
        elif b is not None and a is not None and _card_key(b) != _card_key(a):
            changes.append({"card_index": i, "action": "edit", "before": b, "after": a})
    return changes


def _diff_examples(before: list[dict], after: list[dict]) -> list[dict]:
    before_by_id = {ex.get("id"): ex for ex in before}
    after_by_id = {ex.get("id"): ex for ex in after}
    all_ids = list(dict.fromkeys(list(before_by_id) + list(after_by_id)))
    results: list[dict] = []
    for eid in all_ids:
        b = before_by_id.get(eid, {})
        a = after_by_id.get(eid, {})
        card_changes = _diff_cards(b.get("cards") or [], a.get("cards") or [])
        entity_changed = (b.get("entities") or []) != (a.get("entities") or [])
        if not card_changes and not entity_changed:
            continue
        for ch in card_changes:
            results.append(
                {
                    "example_id": eid,
                    "message_id": a.get("message_id") or b.get("message_id"),
                    "card_index": ch["card_index"],
                    "action": ch["action"],
                    "before": ch["before"],
                    "after": ch["after"],
                    "comment": (ch.get("after") or {}).get("logic", "") if ch.get("after") else "",
                    "tags": a.get("tags") or b.get("tags") or [],
                }
            )
    return results


def _append_rule_candidate(comment: str, example_id: str) -> None:
    if not comment or len(comment) < 10:
        return
    rules_path = RULES_JSON
    data = {"rules": []}
    if rules_path.exists():
        data = json.loads(rules_path.read_text(encoding="utf-8"))
    rid = f"candidate-{example_id}-{len(data.get('rules', []))}"
    data.setdefault("rules", []).append(
        {
            "id": rid,
            "text": comment,
            "type": "candidate",
            "tags": [],
            "enabled": False,
            "source_correction_example": example_id,
        }
    )
    rules_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def ingest_batch(batch: str, from_txt: bool = True) -> dict:
    batch_id = f"batch-{int(batch):03d}" if batch.isdigit() else batch
    draft_json = DRAFT_DIR / f"{batch_id}.json"
    draft_txt = DRAFT_DIR / f"{batch_id}.txt"
    snapshot = GENERATIONS_DIR / f"{batch_id}.json"

    if not snapshot.exists():
        raise SystemExit(f"Snapshot missing: {snapshot}. Run prepare-batch first.")
    if from_txt and draft_txt.exists():
        sync_txt_to_json(draft_txt, draft_json)
    elif not draft_json.exists():
        raise SystemExit(f"Draft missing: {draft_json}")

    before = read_examples_json(snapshot)
    after = read_examples_json(draft_json)
    changes = _diff_examples(before, after)

    CORRECTIONS_DIR.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_files: list[str] = []
    by_example: dict[str, list] = {}
    for ch in changes:
        by_example.setdefault(ch["example_id"], []).append(ch)

    for eid, items in by_example.items():
        out_path = CORRECTIONS_DIR / f"{today}-{eid}.json"
        out_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        out_files.append(str(out_path.name))
        for item in items:
            logic = ""
            if item.get("after") and isinstance(item["after"], dict):
                logic = item["after"].get("logic", "")
            if logic and "всегда" in logic.lower():
                _append_rule_candidate(logic, eid)

    index_stats = rebuild_index()
    return {
        "batch": batch_id,
        "changes": len(changes),
        "correction_files": out_files,
        "index": index_stats,
    }
