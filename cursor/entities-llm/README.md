# entities-llm: категоризация ответов quizlet-modules

Классификация **агентом Cursor** (не эвристики). Контекст: `answer` + `sample_questions`.

Источник: [`quizlet-modules/`](../../quizlet-modules/). Типы: [`text_parsing_guide.md`](../../docs/text_parsing_guide.md).

## Прогресс

| Метрика | Значение |
|---------|----------|
| Уникальных ответов | 6270 |
| Классифицировано | 375 (6.0%) |
| Pilot (batch-pilot) | 20 сущностей |
| Батчей готово | 3 / 51 |
| С типом | 221 |
| Unmapped | 154 |

## Workflow

```bash
python cursor/entities-llm/extract_for_llm.py
python cursor/entities-llm/split_batches.py
# LLM-агент: batches/batch-NNN.json -> classifications/batch-NNN.json
python cursor/entities-llm/merge_classifications.py
```

Инструкция агенту: [`classify_prompt.md`](classify_prompt.md).

Эвристический baseline: [`entities-from-quizlet-cards/`](../entities-from-quizlet-cards/).
