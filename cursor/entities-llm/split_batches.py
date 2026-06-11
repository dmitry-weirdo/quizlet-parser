"""Split entities_queue.json into batch files for agent classification."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).parent
QUEUE = ROOT / "entities_queue.json"
BATCHES_DIR = ROOT / "batches"
BATCH_SIZE = 125


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not QUEUE.exists():
        print("Run extract_for_llm.py first", file=sys.stderr)
        return 1

    payload = json.loads(QUEUE.read_text(encoding="utf-8"))
    entities = payload["entities"]
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)

    # clear old batches
    for old in BATCHES_DIR.glob("batch-*.json"):
        old.unlink()

    n_batches = math.ceil(len(entities) / BATCH_SIZE)
    for i in range(n_batches):
        chunk = entities[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        num = i + 1
        out = BATCHES_DIR / f"batch-{num:03d}.json"
        out.write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"batches: {n_batches} x up to {BATCH_SIZE} -> {BATCHES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
