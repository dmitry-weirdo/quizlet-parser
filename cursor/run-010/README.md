# Cursor batch run-010

**50** сообщений (seed=42). Карточки из run-009; **`entities`** — объекты `{name, type}`.

Правила: [`quizlet-rules.md`](../../hermes/quizlet-rules.md). Типы: [`text_parsing_guide.md`](../../docs/text_parsing_guide.md).

Golden overlay: `apelsinovaya-sdelka` из [`parsing-examples.json`](../../parsing-examples/parsing-examples.json).

## Статистика

- **50** examples, **102** cards
- Источник: [`candidates.json`](candidates.json)

## Новое в run-010 (vs run-009)

| Изменение | Описание |
|-----------|----------|
| `entities[].type` | YEAR, PERSONALIA_MALE, COUNTRY, … или `""` если не определимо |
| `apelsinovaya-sdelka` | Golden typed entities verbatim |
| Карточки | Без изменений (run-009) |

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 50 examples с typed entities |
| `parsing-examples-cursor.txt` | TXT + ENTITIES[name, type] |
| `build_output.py` | Источник EXAMPLES |
| `lint_cards.py` | Per-pair lint + type validation |
