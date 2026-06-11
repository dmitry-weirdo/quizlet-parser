"""Pick 20 diverse Telegram messages for cards-llm pilot (seed=43)."""
from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "telegram-export-json" / "result.json"
OUT = Path(__file__).parent / "candidates.json"
PICK = 20

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
    "Меланхолия\", Дюрер",
]
QUESTION_PATTERN = re.compile(r"\?|(?:^|\s)(?:кто|как|что|где|когда|зачем|почему)\s", re.I)
LINK_RE = re.compile(r"https?://\S+")


def load_used_ids() -> set[int]:
    used: set[int] = set()
    cursor = ROOT / "cursor"
    for path in cursor.glob("run-*/candidates.json"):
        for item in json.loads(path.read_text(encoding="utf-8")):
            used.add(item["message_id"])
    golden = ROOT / "parsing-examples" / "parsing-examples.json"
    if golden.exists():
        for ex in json.loads(golden.read_text(encoding="utf-8"))["examples"]:
            for m in json.loads(EXPORT.read_text(encoding="utf-8"))["messages"]:
                if m.get("type") != "message":
                    continue
                t = plain_text(m)
                if t and normalize(t) == normalize(ex["text"]):
                    used.add(m["id"])
    return used


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def plain_text(msg: dict) -> str:
    t = msg.get("text", "")
    if isinstance(t, str):
        return t.strip()
    parts = []
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
    base = {
        "text_only": ["text-only"],
        "link_only": ["link-only"],
        "link_comment": ["link+comment"],
        "question": ["text-only", "question"],
    }[kind]
    return base


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    used_ids = load_used_ids()
    data = json.loads(EXPORT.read_text(encoding="utf-8"))

    buckets: dict[str, list[dict]] = {
        "text_only": [],
        "link_comment": [],
        "link_only": [],
        "question": [],
    }

    for m in data["messages"]:
        if m.get("type") != "message":
            continue
        mid = m["id"]
        if mid in used_ids:
            continue
        text = plain_text(m)
        if any(s in text for s in GOLDEN_SNIPPETS) or SKIP_PATTERN.search(text):
            continue
        if len(text) < 12:
            continue
        links = extract_links(m)
        has_link = bool(links)
        rest = LINK_RE.sub("", text).strip()
        link_only = has_link and len(rest) < 5
        kind = classify(text, has_link, link_only)
        buckets[kind].append(
            {
                "message_id": mid,
                "text": text,
                "links": links,
                "tags_hint": tags_hint(kind),
                "has_link": has_link,
                "link_only": link_only,
            }
        )

    random.seed(43)
    targets = {
        "text_only": 10,
        "link_comment": 4,
        "link_only": 3,
        "question": 3,
    }
    picked: list[dict] = []
    for kind, n in targets.items():
        pool = buckets[kind]
        random.shuffle(pool)
        picked.extend(pool[:n])

    if len(picked) < PICK:
        rest = []
        for kind, pool in buckets.items():
            taken = {x["message_id"] for x in picked}
            rest.extend(p for p in pool if p["message_id"] not in taken)
        random.shuffle(rest)
        picked.extend(rest[: PICK - len(picked)])

    random.shuffle(picked)
    picked = picked[:PICK]
    OUT.write_text(json.dumps(picked, ensure_ascii=False, indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for p in picked:
        k = classify(p["text"], p["has_link"], p["link_only"])
        counts[k] = counts.get(k, 0) + 1
    print(f"excluded_ids: {len(used_ids)}, picked: {len(picked)}, buckets: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
