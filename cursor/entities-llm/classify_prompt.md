# Инструкция: классификация батча сущностей

Для каждой записи из `batches/batch-NNN.json` определи **тип сущности** (поле `answer`).

Используй `sample_questions` для disambiguation.

## Допустимые типы

`NUMBER`, `YEAR`, `DATE`, `CHARACTER_MALE`, `CHARACTER_FEMALE`, `BRAND`, `NICKNAME`, `IDIOM`, `COUNTRY`, `CITY`, `STATE`, `PERSONALIA_MALE`, `PERSONALIA_FEMALE`, `GOD`, `GODDESS`, `MOVIE`, `PAINTING`, `ENGRAVING`, `QUOTE`, `SONG`, `LANGUAGE`

Пустая строка `""` — если тип не определён.

## Правила

1. **Род и падеж не кодируй** — только тип.
2. **Составные ответы** (`A / B`, `A и B`) → `""`.
3. **Общие термины** без типа в guide (турнюр, машина Голдберга) → `""`.
4. **Персонаж vs персоналия**: вымышленный → `CHARACTER_*`; реальный человек → `PERSONALIA_*`.
5. **Мифология**: бог/богиня → `GOD` / `GODDESS`; мифический герой → `CHARACTER_*`.
6. Смотри на вопрос: «Близнецы» + Шварценеггер → `MOVIE`; «14» + восьмитысячники → `NUMBER`.

## Формат выхода

Запиши `classifications/batch-NNN.json`:

```json
[
  {"answer": "точная строка из входа", "type": "MOVIE"},
  {"answer": "турнюр", "type": ""}
]
```

Каждый `answer` из входа — ровно один раз, в том же порядке.

Справочник: [`docs/text_parsing_guide.md`](../../docs/text_parsing_guide.md).  
Golden: [`parsing-examples/parsing-examples.json`](../../parsing-examples/parsing-examples.json).

## Pilot

Для проверки пайплайна: `batches/batch-pilot.json` (20 сущностей, топ по frequency) → `classifications/batch-pilot.json`.
