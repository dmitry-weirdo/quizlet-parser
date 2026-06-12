"""Local RAG index: files in git + numpy vectors in knowledge/.index/."""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from knowledge.paths import (
    CORRECTIONS_DIR,
    EXAMPLES_GOLDEN,
    INDEX_DIR,
    INDEX_META,
    INDEX_VECTORS,
    STYLE_PAIRS,
)

_EMBED_DIM = 384
_MODEL = None
_MODEL_FAILED = False


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9]+", text.lower())


def hash_embed(text: str, dim: int = _EMBED_DIM) -> np.ndarray:
    vec = np.zeros(dim, dtype=np.float32)
    tokens = tokenize(text)
    if not tokens:
        return vec
    for token in tokens:
        for i in range(3):
            key = f"{token}:{i}" if i else token
            h = hash(key) % dim
            vec[h] += 1.0
    n = float(np.linalg.norm(vec))
    if n > 0:
        vec /= n
    return vec


def _load_model():
    global _MODEL, _MODEL_FAILED
    if _MODEL is not None or _MODEL_FAILED:
        return _MODEL
    try:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    except Exception:
        _MODEL_FAILED = True
        _MODEL = None
    return _MODEL


def embed(text: str) -> np.ndarray:
    model = _load_model()
    if model is not None:
        vec = model.encode(text, normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32)
    return hash_embed(text)


def _record_text(rec: dict) -> str:
    kind = rec.get("kind")
    if kind == "example":
        parts = [rec.get("text", "")]
        for c in rec.get("cards") or []:
            parts.append(c.get("question", ""))
            parts.append(c.get("answer", ""))
        return " ".join(parts)
    if kind == "correction":
        parts = [
            rec.get("comment", ""),
            json.dumps(rec.get("before", {}), ensure_ascii=False),
            json.dumps(rec.get("after", {}), ensure_ascii=False),
        ]
        return " ".join(parts)
    if kind == "style":
        return f"{rec.get('answer', '')} {rec.get('question', '')}"
    return rec.get("text", "")


def _load_golden_records() -> list[dict]:
    records: list[dict] = []
    if not EXAMPLES_GOLDEN.exists():
        return records
    for path in sorted(EXAMPLES_GOLDEN.glob("*.json")):
        ex = json.loads(path.read_text(encoding="utf-8"))
        records.append(
            {
                "id": ex.get("id", path.stem),
                "kind": "example",
                "path": str(path.relative_to(EXAMPLES_GOLDEN.parents[1])),
                "text": ex.get("text", ""),
                "tags": ex.get("tags") or [],
                "category": "",
                "cards": ex.get("cards") or [],
            }
        )
    return records


def _load_correction_records() -> list[dict]:
    records: list[dict] = []
    if not CORRECTIONS_DIR.exists():
        return records
    for path in sorted(CORRECTIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else [data]
        for i, item in enumerate(items):
            records.append(
                {
                    "id": f"{path.stem}:{i}",
                    "kind": "correction",
                    "path": str(path.relative_to(CORRECTIONS_DIR.parents[1])),
                    "comment": item.get("comment", ""),
                    "before": item.get("before", {}),
                    "after": item.get("after", {}),
                    "tags": item.get("tags") or [],
                    "example_id": item.get("example_id", ""),
                }
            )
    return records


def _load_style_records() -> list[dict]:
    if not STYLE_PAIRS.exists():
        return []
    pairs = json.loads(STYLE_PAIRS.read_text(encoding="utf-8"))
    if isinstance(pairs, dict):
        pairs = pairs.get("pairs", [])
    records: list[dict] = []
    for i, p in enumerate(pairs):
        records.append(
            {
                "id": f"style-{i}",
                "kind": "style",
                "path": "knowledge/style_pairs.json",
                "answer": p.get("answer", ""),
                "question": p.get("question", ""),
                "category": p.get("category", ""),
                "has_placeholder": p.get("has_placeholder", False),
            }
        )
    return records


def rebuild_index() -> dict:
    records = _load_golden_records() + _load_correction_records() + _load_style_records()
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if not records:
        INDEX_META.write_text(json.dumps({"count": 0, "backend": _backend_name()}, indent=2), encoding="utf-8")
        np.save(INDEX_VECTORS, np.zeros((0, _EMBED_DIM), dtype=np.float32))
        return {"count": 0, "backend": _backend_name()}

    vectors = np.vstack([embed(_record_text(r)) for r in records])
    meta = {
        "count": len(records),
        "backend": _backend_name(),
        "records": records,
    }
    INDEX_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    np.save(INDEX_VECTORS, vectors)
    return {"count": len(records), "backend": _backend_name()}


def _backend_name() -> str:
    return "sentence-transformers" if _load_model() is not None else "hash-fallback"


def _load_index() -> tuple[list[dict], np.ndarray]:
    if not INDEX_META.exists() or not INDEX_VECTORS.exists():
        rebuild_index()
    meta = json.loads(INDEX_META.read_text(encoding="utf-8"))
    vectors = np.load(INDEX_VECTORS)
    return meta.get("records", []), vectors


def search(query: str, kind: str | None = None, top_k: int = 5, min_score: float = 0.15) -> list[dict]:
    records, vectors = _load_index()
    if len(records) == 0:
        return []
    q = embed(query)
    scores = vectors @ q
    ranked = sorted(range(len(records)), key=lambda i: float(scores[i]), reverse=True)
    out: list[dict] = []
    for i in ranked:
        if kind and records[i].get("kind") != kind:
            continue
        score = float(scores[i])
        if score < min_score:
            continue
        hit = dict(records[i])
        hit["score"] = round(score, 4)
        out.append(hit)
        if len(out) >= top_k:
            break
    return out


def search_style_by_category(query: str, category: str | None = None, top_k: int = 3) -> list[dict]:
    hits = search(query, kind="style", top_k=top_k * 4, min_score=0.05)
    if category:
        cat_hits = [h for h in hits if h.get("category") == category]
        if cat_hits:
            return cat_hits[:top_k]
    placeholder = [h for h in hits if h.get("has_placeholder")]
    if placeholder:
        return placeholder[:top_k]
    return hits[:top_k]
