# Cursor batch run-005

**50** случайных Telegram-сообщений из `result.json` (seed=42, без run-001…004 и golden).

Правила: [`hermes/quizlet-rules.md`](../../hermes/quizlet-rules.md) (примеры 1–10).

## Статистика

- **50** examples, **80** cards
- Источник: [`candidates.json`](candidates.json), [`extract_candidates.py`](extract_candidates.py)

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 50 examples |
| `parsing-examples-cursor.txt` | Человекочитаемый вид + message_id |
| `build_output.py` | Скрипт сборки |

Сравнение с [`run-004`](../run-004/) — тот же стиль ЧГК, но новые сообщения и больший объём.
