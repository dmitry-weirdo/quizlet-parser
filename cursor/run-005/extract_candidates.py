import json
import random
import re
from pathlib import Path

USED_IDS = {
    -999907461, -999907459, -999907458, -999907457, -999907454, -999907452,
    -999907446, -999907369, -999907372, -999907215, -999907207, -999907095,
    -999907033, -999907029, -999906614, -999906196, -999907450, -999907445,
    -999907455, -999906315,
}
SKIP_PATTERN = re.compile(
    r"This reply|Привет, Дюся|триггер на|как успокоить",
    re.IGNORECASE,
)


def plain_text(msg):
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


def is_golden(text):
    snippets = [
        "Бродский: Если Евтушенко против",
        "Чарльз из 19 века",
        "Red Apple",
        "Nero fiddled",
        "странная байка: Нерон",
        '"Меланхолия"',
    ]
    return any(s in text for s in snippets)


def is_skipped(text):
    return bool(SKIP_PATTERN.search(text))


def main():
    root = Path(__file__).resolve().parents[2]
    data = json.loads(
        (root / "telegram-export-json" / "result.json").read_text(encoding="utf-8")
    )
    cands = []
    for m in data["messages"]:
        if m.get("type") != "message":
            continue
        mid = m["id"]
        if mid in USED_IDS:
            continue
        text = plain_text(m)
        if is_golden(text) or is_skipped(text):
            continue
        if len(text) < 12:
            continue
        has_link = bool(re.search(r"https?://", text))
        cands.append(
            {
                "message_id": mid,
                "text": text,
                "has_link": has_link,
                "link_only": has_link and len(re.sub(r"https?://\S+", "", text).strip()) < 5,
            }
        )

    random.seed(42)
    random.shuffle(cands)
    picked = cands[:50]
    out = Path(__file__).parent
    (out / "candidates.json").write_text(
        json.dumps(picked, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("total", len(cands), "picked", len(picked))


if __name__ == "__main__":
    main()
