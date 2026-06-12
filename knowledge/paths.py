"""Paths for the knowledge store (repo-root relative)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE = ROOT / "knowledge"

RULES_DIR = KNOWLEDGE / "rules"
RULES_CORE = RULES_DIR / "core.md"
RULES_NEGATIVE_DIR = RULES_DIR / "negative"
RULES_POSITIVE_DIR = RULES_DIR / "positive"
RULES_JSON = RULES_DIR / "rules.json"

EXAMPLES_GOLDEN = KNOWLEDGE / "examples" / "golden"
EXAMPLES_DRAFT = KNOWLEDGE / "examples" / "draft"
CORRECTIONS_DIR = KNOWLEDGE / "corrections"
STYLE_PAIRS = KNOWLEDGE / "style_pairs.json"
ENTITY_CACHE = KNOWLEDGE / "entity_cache.json"
REVIEW_QUEUE = KNOWLEDGE / "review_queue.json"
INDEX_DIR = KNOWLEDGE / ".index"
INDEX_META = INDEX_DIR / "meta.json"
INDEX_VECTORS = INDEX_DIR / "vectors.npy"

BATCHES_DIR = KNOWLEDGE / "batches"
GENERATIONS_DIR = KNOWLEDGE / "generations"
DRAFT_DIR = KNOWLEDGE / "draft"
PROMPTS_DIR = KNOWLEDGE / "prompts"
REVIEWS_DIR = KNOWLEDGE / "reviews"

PARSING_EXAMPLES = ROOT / "parsing-examples" / "parsing-examples.json"
CURSOR_EXAMPLES = ROOT / "cursor" / "cards-llm" / "parsing-examples-cursor.json"
CURSOR_CANDIDATES = ROOT / "cursor" / "cards-llm" / "candidates.json"
CURSOR_GENERATIONS = ROOT / "cursor" / "cards-llm" / "generations"
CURSOR_BATCHES = ROOT / "cursor" / "cards-llm" / "batches"
QUIZLET_RULES = ROOT / "hermes" / "quizlet-rules.md"
QUIZLET_RULES_BAD = ROOT / "hermes" / "quizlet-rules-bad.md"
TEXT_PARSING_GUIDE = ROOT / "docs" / "text_parsing_guide.md"
QUIZLET_MODULES = ROOT / "quizlet-modules"
ENTITIES_QUEUE = ROOT / "cursor" / "entities-llm" / "entities_queue.json"
GENERATE_PROMPT_TEMPLATE = ROOT / "cursor" / "cards-llm" / "generate_cards_prompt.md"

BATCH_SIZE = 5
