"""Human-readable .txt format for card review (compatible with cards-llm)."""
from __future__ import annotations

import json
import re
from pathlib import Path


def slug_from_text(text: str) -> str:
    words = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())[:6]
    return "-".join(words) if words else "example"


def examples_to_txt(examples: list[dict]) -> str:
    blocks: list[str] = []
    for ex in examples:
        lines = [f"===== {ex.get('id', 'unknown')} =====", "TEXT:"]
        lines.append(ex.get("text", ""))
        if ex.get("message_id") is not None:
            lines.append(f"\nMESSAGE_ID: {ex['message_id']}")
        tags = ex.get("tags") or []
        if tags:
            lines.append(f"\nTAGS: {', '.join(tags)}")
        entities = ex.get("entities") or []
        if entities:
            lines.append("\nENTITIES:")
            for ent in entities:
                if isinstance(ent, dict):
                    name = ent.get("name", "")
                    etype = ent.get("type") or ""
                    suffix = f" [{etype}]" if etype else " [(no type)]"
                    lines.append(f"  - {name}{suffix}")
        cards = ex.get("cards") or []
        if cards:
            lines.append("\nCARDS:")
            for i, card in enumerate(cards, 1):
                lines.append(f"[{i}]")
                lines.append(f"Q: {card.get('question', '')}")
                lines.append(f"A: {card.get('answer', '')}")
                logic = card.get("logic", "")
                if logic:
                    lines.append(f"LOGIC: {logic}")
                lines.append("")
        lines.append("---")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks).rstrip() + "\n"


def _parse_entities(lines: list[str], start: int) -> tuple[list[dict], int]:
    entities: list[dict] = []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("CARDS:") or line.startswith("=====") or line == "---":
            break
        m = re.match(r"^-\s+(.+?)(?:\s+\[([^\]]*)\])?$", line)
        if m:
            name = m.group(1).strip()
            etype = (m.group(2) or "").strip()
            if etype == "(no type)":
                etype = ""
            entities.append({"name": name, "type": etype})
        i += 1
    return entities, i


def _parse_cards(lines: list[str], start: int) -> tuple[list[dict], int]:
    cards: list[dict] = []
    i = start
    current: dict | None = None
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("=====") or line == "---":
            break
        m_idx = re.match(r"^\[(\d+)\]$", line)
        if m_idx:
            if current and (current.get("question") or current.get("answer")):
                cards.append(current)
            current = {"question": "", "answer": "", "logic": ""}
            i += 1
            continue
        if current is None:
            i += 1
            continue
        if line.startswith("Q:"):
            current["question"] = line[2:].strip()
        elif line.startswith("A:"):
            current["answer"] = line[2:].strip()
        elif line.startswith("LOGIC:"):
            current["logic"] = line[6:].strip()
        i += 1
    if current and (current.get("question") or current.get("answer")):
        cards.append(current)
    return cards, i


def txt_to_examples(text: str) -> list[dict]:
    examples: list[dict] = []
    chunks = re.split(r"\n===== ", text)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        if not chunk.startswith("====="):
            chunk = "===== " + chunk
        header_m = re.match(r"===== (.+?) =====\s*", chunk)
        if not header_m:
            continue
        ex_id = header_m.group(1).strip()
        body = chunk[header_m.end() :]
        lines = body.splitlines()
        ex: dict = {"id": ex_id, "text": "", "tags": [], "entities": [], "cards": []}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == "TEXT:":
                i += 1
                text_lines: list[str] = []
                while i < len(lines):
                    s = lines[i]
                    if s.strip().startswith("MESSAGE_ID:"):
                        break
                    if s.strip().startswith("TAGS:"):
                        break
                    if s.strip() == "ENTITIES:":
                        break
                    if s.strip().startswith("CARDS:"):
                        break
                    if s.strip().startswith("====="):
                        break
                    text_lines.append(s)
                    i += 1
                ex["text"] = "\n".join(text_lines).strip()
                continue
            if line.startswith("MESSAGE_ID:"):
                ex["message_id"] = int(line.split(":", 1)[1].strip())
                i += 1
                continue
            if line.startswith("TAGS:"):
                tags_raw = line.split(":", 1)[1].strip()
                ex["tags"] = [t.strip() for t in tags_raw.split(",") if t.strip()]
                i += 1
                continue
            if line == "ENTITIES:":
                entities, i = _parse_entities(lines, i + 1)
                ex["entities"] = entities
                continue
            if line == "CARDS:":
                cards, i = _parse_cards(lines, i + 1)
                ex["cards"] = cards
                continue
            i += 1
        examples.append(ex)
    return examples


def read_examples_json(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("examples", [])


def write_examples_json(path: Path, examples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")


def sync_txt_to_json(txt_path: Path, json_path: Path) -> list[dict]:
    examples = txt_to_examples(txt_path.read_text(encoding="utf-8"))
    write_examples_json(json_path, examples)
    return examples


def sync_json_to_txt(json_path: Path, txt_path: Path) -> None:
    examples = read_examples_json(json_path)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(examples_to_txt(examples), encoding="utf-8")
