# Инструкция: классификация батча сущностей

Для каждой записи из `batches/batch-NNN.json` определи **тип сущности** (поле `answer`).

Используй `sample_questions` для disambiguation.

## Допустимые типы

`NUMBER`, `YEAR`, `DATE`, `CHARACTER_MALE`, `CHARACTER_FEMALE`, `BRAND`, `NICKNAME`, `IDIOM`, `COUNTRY`, `CITY`, `STATE`, `PERSONALIA_MALE`, `PERSONALIA_FEMALE`, `GOD`, `GODDESS`, `MOVIE`, `PAINTING`, `ENGRAVING`, `QUOTE`, `SONG`, `LANGUAGE`, `SHIP`, `AIRPLANE`, `THEATRICAL_PIECE`, `NOVELLA`, `NOVEL`, `POEM`, `GAME`, `ILLNESS`, `BATTLE`, `MILITARY_OPERATION`, `CURRENCY`, `AWARD`, `ORDER`, `TEAM`, `RACE`

Пустая строка `""` — если тип не определён.

## Правила

1. **Род и падеж не кодируй** — только тип.
2. **Составные ответы** (`A / B`, `A и B`) → `""`.
3. **Общие термины** без типа в guide → `""`. Если тип есть в guide — используй его (роман → `NOVEL`, битва → `BATTLE`, Wordle → `GAME`, рупия → `CURRENCY`).
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

`batches/batch-pilot.json` (20 сущностей) → `classifications/batch-pilot.json`.

## Важно

Классификацию выполняет **LLM-агент** (Cursor), не Python-эвристики.

После записи `classifications/batch-NNN.json`:

```bash
python cursor/entities-llm/merge_classifications.py
```

Приоритет merge: `batch-pilot` < `batch-001` < `batch-002` … (поздний перекрывает ранний).
