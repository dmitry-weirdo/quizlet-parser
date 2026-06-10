# Cursor batch run-009

**50** сообщений (seed=42). Полная перегенерация карточек + поле **`entities`** на каждый example.

Правила: [`quizlet-rules.md`](../../hermes/quizlet-rules.md). Golden overlay: [`parsing-examples.json`](../../parsing-examples/parsing-examples.json) (`apelsinovaya-sdelka`).

База стиля: [`run-004`](../run-004/). Исправления run-008: однокоренность **только внутри пары** Q/A.

## Статистика

- **50** examples, **102** cards
- Источник: [`candidates.json`](candidates.json)

## Новое в run-009

| Изменение | Описание |
|-----------|----------|
| `entities` | Реалии, извлечённые из текста (+ wiki в cards) |
| `apelsinovaya-sdelka` | Golden verbatim из parsing-examples.json |
| Пример 5 | «апельсины» в вопросе про Израиль — OK |
| Пример 10 | bloom-filter: **ИМ**, не «ЭТИМ фильтром» |

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 50 examples с entities |
| `parsing-examples-cursor.txt` | TXT + ENTITIES + message_id |
| `build_output.py` | Источник EXAMPLES |
| `lint_cards.py` | Per-pair lint |
