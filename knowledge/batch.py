"""Batch preparation from review queue."""
from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

from knowledge.paths import (
    BATCH_SIZE,
    BATCHES_DIR,
    CURSOR_GENERATIONS,
    DRAFT_DIR,
    GENERATIONS_DIR,
    REVIEW_QUEUE,
)
from knowledge.telegram_sample import record_sampled_batch, sample_messages
from knowledge.text_format import (
    examples_to_txt,
    read_examples_json,
    slug_from_text,
    write_examples_json,
)


def _batch_num(batch: str) -> int:
    return int(batch.lstrip("0") or "0") if batch.isdigit() else int(batch)


def load_queue() -> list[dict]:
    data = json.loads(REVIEW_QUEUE.read_text(encoding="utf-8"))
    return data.get("items", [])


def queue_messages_for_batch(batch: str) -> list[dict]:
    n = _batch_num(batch)
    items = load_queue()
    start = (n - 1) * BATCH_SIZE
    return items[start : start + BATCH_SIZE]


def _message_to_shell(msg: dict) -> dict:
    text = msg.get("text", "")
    return {
        "message_id": msg.get("message_id"),
        "id": slug_from_text(text),
        "text": text,
        "tags": list(msg.get("tags_hint") or []),
        "entities": [],
        "cards": [],
    }


def prepare_batch(
    batch: str,
    *,
    from_telegram: bool = False,
    seed: int | None = None,
    count: int | None = None,
    force: bool = False,
) -> dict:
    batch_id = f"batch-{int(batch):03d}" if batch.isdigit() else batch
    n = count or BATCH_SIZE

    if from_telegram:
        messages = sample_messages(count=n, seed=seed)
        record_sampled_batch(batch_id, messages, seed)
        source = "telegram-export-json/result.json"
    else:
        messages = queue_messages_for_batch(batch)
        if not messages:
            raise SystemExit(f"No messages for {batch_id} in review_queue")
        source = "review_queue"

    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    batch_input = BATCHES_DIR / f"{batch_id}.json"
    batch_input.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")

    gen_path = GENERATIONS_DIR / f"{batch_id}.json"
    draft_json = DRAFT_DIR / f"{batch_id}.json"
    draft_txt = DRAFT_DIR / f"{batch_id}.txt"

    cursor_gen = CURSOR_GENERATIONS / f"{batch_id}.json"

    if from_telegram or force:
        examples = [_message_to_shell(m) for m in messages]
        GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)
        write_examples_json(gen_path, [dict(ex) for ex in examples])
    else:
        examples: list[dict] = []
        if cursor_gen.exists():
            examples = read_examples_json(cursor_gen)
        elif draft_json.exists():
            examples = read_examples_json(draft_json)
        else:
            examples = [_message_to_shell(m) for m in messages]

        if not gen_path.exists():
            GENERATIONS_DIR.mkdir(parents=True, exist_ok=True)
            if cursor_gen.exists():
                shutil.copy2(cursor_gen, gen_path)
            else:
                write_examples_json(gen_path, [dict(ex) for ex in examples])

    write_examples_json(draft_json, examples)
    draft_txt.write_text(examples_to_txt(examples), encoding="utf-8")

    return {
        "batch": batch_id,
        "messages": len(messages),
        "examples": len(examples),
        "message_ids": [m["message_id"] for m in messages],
        "draft_json": str(draft_json.relative_to(DRAFT_DIR.parents[1])),
        "draft_txt": str(draft_txt.relative_to(DRAFT_DIR.parents[1])),
        "snapshot": str(gen_path.relative_to(GENERATIONS_DIR.parents[1])),
        "source": source if from_telegram else ("cursor/cards-llm" if cursor_gen.exists() else "shell"),
        "seed": seed,
    }
