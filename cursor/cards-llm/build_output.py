"""Merge generations/*.json into parsing-examples-cursor.json + txt + llm_report.md."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
GENERATIONS = ROOT / "generations"
REPORT_JSON = ROOT / "llm_report.json"
REPORT_MD = ROOT / "llm_report.md"


def slug(text: str, message_id: int) -> str:
    base = re.sub(r"https?://\S+", "", text)
    base = re.sub(r"[^\w\s-]", "", base, flags=re.UNICODE)
    words = [w.lower() for w in base.split() if w][:4]
    s = "-".join(words) if words else f"msg-{abs(message_id)}"
    return s[:48].strip("-")


def load_generations() -> tuple[list[dict], dict[str, int]]:
    examples: list[dict] = []
    message_ids: dict[str, int] = {}
    for path in sorted(GENERATIONS.glob("batch-*.json")):
        for item in json.loads(path.read_text(encoding="utf-8")):
            item = dict(item)
            mid = item.pop("message_id", None)
            eid = item.get("id") or slug(item["text"], mid or 0)
            item["id"] = eid
            examples.append(item)
            if mid is not None:
                message_ids[eid] = mid
    return examples, message_ids


def write_txt(examples: list[dict], message_ids: dict[str, int]) -> str:
    lines: list[str] = []
    total_cards = 0
    for ex in examples:
        lines.append(f"===== {ex['id']} =====")
        lines.append("TEXT:")
        lines.append(ex["text"])
        lines.append("")
        if ex["id"] in message_ids:
            lines.append(f"MESSAGE_ID: {message_ids[ex['id']]}")
            lines.append("")
        if ex.get("tags"):
            lines.append("TAGS: " + ", ".join(ex["tags"]))
            lines.append("")
        if ex.get("entities"):
            lines.append("ENTITIES:")
            for ent in ex["entities"]:
                t = ent.get("type") or "(no type)"
                lines.append(f"  - {ent['name']} [{t}]")
            lines.append("")
        lines.append("CARDS:")
        for i, card in enumerate(ex.get("cards", []), 1):
            total_cards += 1
            lines.append(f"[{i}]")
            lines.append("Q: " + card["question"])
            lines.append("A: " + card["answer"])
            if card.get("logic"):
                lines.append("LOGIC: " + card["logic"])
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines), total_cards


def write_report_md(examples: list[dict], total_cards: int) -> None:
  report = json.loads(REPORT_JSON.read_text(encoding="utf-8")) if REPORT_JSON.exists() else {"calls": [], "totals": {}}
  lines = [
    "# LLM report: cards-llm pilot",
    "",
    f"- Examples: **{len(examples)}**",
    f"- Cards: **{total_cards}**",
    "",
    "## Calls",
    "",
    "| id | model | operation | batch | est. tokens | est. USD |",
    "|----|-------|-----------|-------|-------------|----------|",
  ]
  for c in report.get("calls", []):
    tok = c.get("tokens", {}).get("estimated_total", "")
    cost = c.get("cost_usd", {}).get("estimated")
    cost_s = f"{cost:.4f}" if cost is not None else "n/a (Cursor sub)"
    batch = (c.get("parameters") or {}).get("batch") or ""
    lines.append(
      f"| {c['id']} | {c.get('model','')} | {c.get('operation','')} | {batch} | {tok} | {cost_s} |"
    )
  lines.extend([
    "",
    "## Disclaimer",
    "",
    "Точный token usage и биллинг Cursor IDE недоступны агенту. "
    "`estimated_*` — оценка по размеру файлов (chars/4). "
    "Сверьте фактическую стоимость в [Cursor Settings](https://cursor.com/settings).",
    "",
  ])
  REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not GENERATIONS.exists() or not any(GENERATIONS.glob("batch-*.json")):
        print("No generations/*.json found", file=sys.stderr)
        return 1

    examples, message_ids = load_generations()
    payload = {"examples": [{k: v for k, v in ex.items()} for ex in examples]}
    (ROOT / "parsing-examples-cursor.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    txt, total_cards = write_txt(examples, message_ids)
    (ROOT / "parsing-examples-cursor.txt").write_text(txt, encoding="utf-8")
    write_report_md(examples, total_cards)
    print(f"examples: {len(examples)}, cards: {total_cards}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
