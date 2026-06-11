"""Split candidates.json into batch files (5 messages each)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CANDIDATES = ROOT / "candidates.json"
BATCHES_DIR = ROOT / "batches"
BATCH_SIZE = 5


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if not CANDIDATES.exists():
        print("Run extract_candidates.py first", file=sys.stderr)
        return 1

    items = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    for old in BATCHES_DIR.glob("batch-*.json"):
        old.unlink()

    n_batches = math.ceil(len(items) / BATCH_SIZE)
    for i in range(n_batches):
        chunk = items[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        out = BATCHES_DIR / f"batch-{i + 1:03d}.json"
        out.write_text(json.dumps(chunk, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"batches: {n_batches} x up to {BATCH_SIZE} -> {BATCHES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
