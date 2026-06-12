"""Sample random Telegram messages from result.json for new batches."""
from __future__ import annotations

import json
import random
import re
from pathlib import Path

from knowledge.paths import (
    BATCHES_DIR,
    CURSOR_CANDIDATES,
    DRAFT_DIR,
    EXAMPLES_GOLDEN,
    GENERATIONS_DIR,
    PARSING_EXAMPLES,
    REVIEW_QUEUE,
    SAMPLED_BATCHES,
    TELEGRAM_EXPORT,
)

SKIP_PATTERN = re.compile(
    r"This reply|Привет, Дюся|триггер на|как успокоить",
    re.IGNORECASE,
)
GOLDEN_SNIPPETS = [
    "Бродский: Если Евтушенко против",
    "Чарльз из 19 века",
    "Red Apple",
    "Nero fiddled",
    "странная байка: Нерон",
    '"Меланхолия"',
    "апельсиновая сделка",
    'Меланхолия", Дюрер',
]
QUESTION_PATTERN = re.compile(r"\?|(?:^|\s)(?:кто|как|что|где|когда|зачем|почему)\s", re.I)
LINK_RE = re.compile(r"https?://\S+")


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def plain_text(msg: dict) -> str:
    t = msg.get("text", "")
    if isinstance(t, str):
        return t.strip()
    parts: list[str] = []
    for p in t:
        if isinstance(p, str):
            parts.append(p)
        elif isinstance(p, dict):
            parts.append(p.get("text", ""))
    return "".join(parts).strip()


def extract_links(msg: dict) -> list[str]:
    links: list[str] = []
    t = msg.get("text", "")
    if isinstance(t, str):
        links.extend(LINK_RE.findall(t))
    elif isinstance(t, list):
        for p in t:
            if isinstance(p, dict) and p.get("type") == "link":
                links.append(p.get("text", "").strip())
            elif isinstance(p, str):
                links.extend(LINK_RE.findall(p))
    for ent in msg.get("text_entities") or []:
        if ent.get("type") == "link":
            links.append(ent.get("text", "").strip())
    return list(dict.fromkeys(x for x in links if x))


def classify(text: str, has_link: bool, link_only: bool) -> str:
    if link_only:
        return "link_only"
    if has_link:
        return "link_comment"
    if QUESTION_PATTERN.search(text):
        return "question"
    return "text_only"


def tags_hint(kind: str) -> list[str]:
    return {
        "text_only": ["text-only"],
        "link_only": ["link-only"],
        "link_comment": ["link+comment"],
        "question": ["text-only", "question"],
    }[kind]


def message_record(msg: dict) -> dict:
    text = plain_text(msg)
    links = extract_links(msg)
    has_link = bool(links)
    rest = LINK_RE.sub("", text).strip()
    link_only = has_link and len(rest) < 5
    kind = classify(text, has_link, link_only)
    return {
        "message_id": msg["id"],
        "text": text,
        "links": links,
        "tags_hint": tags_hint(kind),
        "has_link": has_link,
        "link_only": link_only,
    }


def load_excluded_ids() -> set[int]:
    excluded: set[int] = set()

    if REVIEW_QUEUE.exists():
        for item in json.loads(REVIEW_QUEUE.read_text(encoding="utf-8")).get("items", []):
            if item.get("message_id") is not None:
                excluded.add(item["message_id"])

    if CURSOR_CANDIDATES.exists():
        for item in json.loads(CURSOR_CANDIDATES.read_text(encoding="utf-8")):
            excluded.add(item["message_id"])

    if SAMPLED_BATCHES.exists():
        for entry in json.loads(SAMPLED_BATCHES.read_text(encoding="utf-8")).get("batches", []):
            for mid in entry.get("message_ids", []):
                excluded.add(mid)

    for directory in (BATCHES_DIR, DRAFT_DIR, GENERATIONS_DIR):
        if not directory.exists():
            continue
        for path in directory.glob("batch-*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("examples", [])
            for item in items:
                if isinstance(item, dict) and item.get("message_id") is not None:
                    excluded.add(item["message_id"])

    if EXAMPLES_GOLDEN.exists():
        golden_texts = {
            normalize(json.loads(p.read_text(encoding="utf-8")).get("text", ""))
            for p in EXAMPLES_GOLDEN.glob("*.json")
        }
        if TELEGRAM_EXPORT.exists() and golden_texts:
            for m in json.loads(TELEGRAM_EXPORT.read_text(encoding="utf-8"))["messages"]:
                if m.get("type") != "message":
                    continue
                t = plain_text(m)
                if t and normalize(t) in golden_texts:
                    excluded.add(m["id"])

    if PARSING_EXAMPLES.exists():
        for ex in json.loads(PARSING_EXAMPLES.read_text(encoding="utf-8")).get("examples", []):
            t = normalize(ex.get("text", ""))
            if TELEGRAM_EXPORT.exists() and t:
                for m in json.loads(TELEGRAM_EXPORT.read_text(encoding="utf-8"))["messages"]:
                    if m.get("type") != "message":
                        continue
                    if normalize(plain_text(m)) == t:
                        excluded.add(m["id"])

    return excluded


def iter_candidate_messages(export_path: Path | None = None) -> list[dict]:
    path = export_path or TELEGRAM_EXPORT
    if not path.exists():
        raise SystemExit(f"Telegram export not found: {path}")
    excluded = load_excluded_ids()
    pool: list[dict] = []
    for m in json.loads(path.read_text(encoding="utf-8"))["messages"]:
        if m.get("type") != "message":
            continue
        if m["id"] in excluded:
            continue
        text = plain_text(m)
        if any(s in text for s in GOLDEN_SNIPPETS) or SKIP_PATTERN.search(text):
            continue
        if len(text) < 12:
            continue
        pool.append(message_record(m))
    return pool


def sample_messages(count: int = 5, seed: int | None = None) -> list[dict]:
    pool = iter_candidate_messages()
    if len(pool) < count:
        raise SystemExit(f"Not enough candidates: {len(pool)} < {count}")
    rng = random.Random(seed)
    return rng.sample(pool, count)


def record_sampled_batch(batch_id: str, messages: list[dict], seed: int | None) -> None:
    data = {"batches": []}
    if SAMPLED_BATCHES.exists():
        data = json.loads(SAMPLED_BATCHES.read_text(encoding="utf-8"))
    data.setdefault("batches", []).append(
        {
            "batch": batch_id,
            "seed": seed,
            "message_ids": [m["message_id"] for m in messages],
            "source": "telegram-export-json/result.json",
        }
    )
    SAMPLED_BATCHES.parent.mkdir(parents=True, exist_ok=True)
    SAMPLED_BATCHES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
