"""Append LLM call metadata to llm_report.json."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
REPORT = ROOT / "llm_report.json"
RUN_ID = "cards-llm-pilot-2026-06-11"

# USD per 1M tokens (estimate; update if pricing changes)
PRICING = {
    "composer-2.5": {"input": 0.0, "output": 0.0},
    "default": {"input": 3.0, "output": 15.0},
}


def load_report() -> dict:
    if REPORT.exists():
        return json.loads(REPORT.read_text(encoding="utf-8"))
    return {
        "run_id": RUN_ID,
        "pricing_note": "cost_usd.exact is null for cursor_agent; estimated uses chars/4 and PRICING table",
        "calls": [],
        "totals": {},
    }


def char_count(path: Path | None) -> int:
    if path is None or not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8"))


def estimate_tokens(chars: int) -> int:
    return max(1, chars // 4)


def estimate_cost(input_tok: int, output_tok: int, model: str) -> float | None:
    rates = PRICING.get(model, PRICING["default"])
    if rates["input"] == 0 and rates["output"] == 0:
        return None
    return (input_tok * rates["input"] + output_tok * rates["output"]) / 1_000_000


def recompute_totals(report: dict) -> None:
    calls = report["calls"]
    est = sum(c.get("cost_usd", {}).get("estimated") or 0 for c in calls)
    report["totals"] = {
        "calls": len(calls),
        "wikipedia_fetches": sum(len(c.get("tool_calls", [])) for c in calls),
        "estimated_cost_usd": round(est, 4) if est else None,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--model", default="composer-2.5")
    p.add_argument("--provider", default="cursor_agent")
    p.add_argument("--operation", required=True)
    p.add_argument("--batch", default="")
    p.add_argument("--messages", type=int, default=0)
    p.add_argument("--generation", default="")
    p.add_argument("--tool-calls", default="[]", help="JSON array")
    args = p.parse_args()

    batch_path = ROOT / "batches" / args.batch if args.batch else None
    gen_path = ROOT / "generations" / args.generation if args.generation else None
    in_chars = char_count(batch_path) + char_count(ROOT / "generate_cards_prompt.md")
    out_chars = char_count(gen_path)
    in_tok = estimate_tokens(in_chars)
    out_tok = estimate_tokens(out_chars)
    cost = estimate_cost(in_tok, out_tok, args.model)

    entry = {
        "id": args.id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "provider": args.provider,
        "model": args.model,
        "operation": args.operation,
        "parameters": {
            "batch": args.batch or None,
            "messages": args.messages or None,
            "mode": "agent",
        },
        "context_files": [
            "generate_cards_prompt.md",
            "style_samples.json",
            "../../hermes/quizlet-rules.md",
            "../../parsing-examples/parsing-examples.json",
        ],
        "tool_calls": json.loads(args.tool_calls),
        "input_chars": in_chars,
        "output_chars": out_chars,
        "tokens": {
            "input": None,
            "output": None,
            "estimated_total": in_tok + out_tok,
        },
        "cost_usd": {"exact": None, "estimated": cost},
    }

    report = load_report()
    report["calls"] = [c for c in report["calls"] if c["id"] != args.id]
    report["calls"].append(entry)
    recompute_totals(report)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"logged {args.id} -> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
