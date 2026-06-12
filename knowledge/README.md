# knowledge — human-in-the-loop card generation

Архитектура: [`docs/feedback_learning_architecture.md`](../docs/feedback_learning_architecture.md)

## Setup

```bash
pip install -r knowledge/requirements.txt
# опционально для лучшего RAG:
# pip install sentence-transformers
```

## Quick start

```bash
# 1. Импорт parsing-examples, quizlet-modules, rules, candidates
python -m knowledge bootstrap

# 2a. Batch из candidates (cards-llm пилот)
python -m knowledge prepare-batch --batch 001

# 2b. Batch из случайных сообщений result.json (без старых генераций)
python -m knowledge prepare-batch --batch 003 --from-telegram --seed 99

# 3. Собрать RAG-prompt для Cursor
python -m knowledge build-prompt --batch 001
# → knowledge/prompts/batch-001.md

# 4. Сгенерировать/править карточки в Cursor → knowledge/draft/batch-001.txt

# 5. Сохранить правки как corrections
python -m knowledge ingest --batch 001

# 6. Одобрить хорошие примеры
python -m knowledge promote --id soviet-aeroflot-pen-packets --batch 001
# или все с карточками в батче:
python -m knowledge promote --all --batch 001
```

## Структура

| Путь | Описание |
|------|----------|
| `rules/` | quizlet-rules, entity guide |
| `examples/golden/` | одобренные few-shot примеры |
| `corrections/` | diff before→after после ingest |
| `style_pairs.json` | 7222 пар из quizlet-modules |
| `draft/` | рабочие батчи для ревью (.txt + .json) |
| `generations/` | snapshot до правок |
| `prompts/` | собранные RAG-prompt'ы |
| `.index/` | векторный индекс (не в git) |

## Исходные данные (read-only)

- `parsing-examples/parsing-examples.json`
- `hermes/quizlet-rules.md`
- `docs/text_parsing_guide.md`
- `quizlet-modules/`
- `cursor/cards-llm/candidates.json`
