# Инструкция: генерация карточек из Telegram

Карточки генерирует **LLM-агент** (Cursor), не Python-эвристики.

## Референсы (прочитать перед генерацией)

1. [`hermes/quizlet-rules.md`](../../hermes/quizlet-rules.md) — правила и примеры хорошо/плохо
2. [`parsing-examples/parsing-examples.json`](../../parsing-examples/parsing-examples.json) — 7 golden examples
3. [`docs/text_parsing_guide.md`](../../docs/text_parsing_guide.md) — типы entities и формы замен
4. [`style_samples.json`](style_samples.json) — стиль вопросов из quizlet-modules

## Вход / выход

- Вход: `batches/batch-NNN.json` (5 сообщений)
- Выход: `generations/batch-NNN.json` — массив examples в том же формате + `message_id`

После записи:

```bash
python cursor/cards-llm/log_llm_call.py --id gen-batch-001 --operation generate_cards \
  --batch batch-001.json --messages 5 --generation batch-001.json \
  --tool-calls '[{"tool":"WebFetch","url":"...","purpose":"..."}]'
```

## Алгоритм на каждое сообщение

1. Определи тип: `text-only` / `link-only` / `link+comment` / `question`
2. Выдели `entities`: `{name, type}` (type из guide или `""`)
3. Факты:
   - есть ссылка → прочитай страницу (приоритет ru.wikipedia.org)
   - неполные имена → дополни из ru.wikipedia
   - текст — вопрос → найди ответ, переформулируй вопрос (ОН/ТАК, не «Кто»)
4. Сгенерируй 1–4 карточки на интересные реалии
5. Каждая карточка: `question`, `answer`, `logic`
6. Самопроверка по quizlet-rules

## Чеклист

- [ ] Нет «Кто», «Когда», «Сколько» в вопросе
- [ ] Персоналии → ОН/ОНА/ИМ/ЕЙ (согласование)
- [ ] Год → В ЭТОМ ГОДУ; дата → В ЭТУ ДАТУ; число → СТОЛЬКО
- [ ] Официальные названия → вопрос с ТАК, ответ полный
- [ ] «звали ТАК», не «звали ОН»
- [ ] Нет слов/корней ответа в вопросе этой пары
- [ ] Ответ ≤ 12 слов
- [ ] Имена из русской Wikipedia, полное имя+фамилия
- [ ] Английский ответ → язык объявлен в вопросе

## Формат выхода (один example)

```json
{
  "message_id": -999900123,
  "id": "slug-from-text",
  "text": "исходный текст сообщения",
  "tags": ["text-only", "multi-card"],
  "entities": [
    {"name": "Иосиф Бродский", "type": "PERSONALIA_MALE"}
  ],
  "cards": [
    {
      "question": "ОН сказал: «...»",
      "answer": "Иосиф Бродский",
      "logic": "..."
    }
  ]
}
```

`message_id` обязателен в generations; в финальном `parsing-examples-cursor.json` его нет.
