# spaCy NER для ответов quizlet-modules

Эксперимент: прогон **всех ответов** (левая колонка TSV) из [`quizlet-modules/`](../../quizlet-modules/) через spaCy `ru_core_news_lg` без маппинга на типы из [`text_parsing_guide.md`](../../docs/text_parsing_guide.md).

## Модель и метки

Модель `ru_core_news_lg` (новостной русский) выдаёт только 3 NER-метки:

| spaCy label | Значение |
|-------------|----------|
| `PER` | персона |
| `LOC` | локация |
| `ORG` | организация |

Ответы карточек — короткие фразы, не предложения. Большая доля ответов останется без сущностей; числа, картины, песни и т.п. spaCy не размечает.

## Установка

```bash
cd c:\java\quizlet-parser
python -m venv cursor/entities-spacy-ner/.venv
cursor/entities-spacy-ner/.venv/Scripts/pip install -r cursor/entities-spacy-ner/requirements.txt
cursor/entities-spacy-ner/.venv/Scripts/python -m spacy download ru_core_news_lg
```

## Запуск

```bash
cursor/entities-spacy-ner/.venv/Scripts/python cursor/entities-spacy-ner/run_ner.py
```

## Выходные файлы (`output/`)

| Файл | Описание |
|------|----------|
| `report.md` | Человекочитаемый обзор: сводка, примеры по меткам |
| `stats.json` | Сводная статистика |
| `by_label.json` | Ответы, сгруппированные по spaCy-меткам |
| `per_card.jsonl` | Одна JSON-строка на карточку (полный лог) |
| `no_entities.json` | Уникальные ответы без разметки + частота |

## Методология

- Парсинг: `ответ<TAB>вопрос`; каждая строка с TAB — отдельная карточка (без дедупликации).
- NER только по тексту **ответа**, вопрос сохраняется для контекста в отчётах.
- Классификация покрытия: `no_entities`, `single_entity_full`, `single_entity_partial`, `multiple_entities`.
