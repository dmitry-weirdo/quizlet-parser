# Справочник: факт → карточки Quizlet

Правила преобразования структурированных фактов в карточки по образцу модулей в `quizlet-modules/`.

## Формат вывода

Одна карточка на строку, поля разделены табуляцией:

```
вопрос	ответ
```

Импорт: Quizlet → Create → Import → Copy and paste text.

## Типы фактов

| Тип | JSON-поля | Карточки |
|-----|-----------|----------|
| `PERSON` | `name`, `fact`, `role`, `title`, `year` | имя→факт; «Кто …?»→имя; автор↔произведение |
| `ARTWORK` | `title`, `author`, `year`, `hint` | автор→«"название", год. Художник.»; название→описание |
| `NUMBER` | `value`, `domain` | число↔«Сколько …?» |
| `YEAR` | `year`, `event`, `alias` | год↔«В каком году …?»; прозвище↔год |
| `NICKNAME` | `alias`, `entity`, `fact` | прозвище↔имя |
| `TRANSLATION` | `term`, `meaning`, `language` | термин↔перевод |
| `LOCATION` | `place`, `fact`, `alias` | место↔факт; прозвище↔город |
| `QUOTE` | `quote`, `author`, `work` | цитата↔автор/произведение |
| `TERM` | `term`, `fact`, `answerHint` | термин↔определение |
| `RELATION` | `relation`, связанные поля | ЧГК-заготовки с ОН/ОНА/НЕМ |

## Паттерны из модулей

### 1. Термин → определение (~30%)

**Факт:** Моаи — статуи на острове Пасхи.

```json
{ "type": "TERM", "term": "Моаи", "fact": "Статуи на острове Пасхи" }
```

**Карточка:** `Моаи` → `Статуи на острове Пасхи`

### 2. Обратная связь (~15%)

**Факт:** Гарри Поттер — «Мальчик, который выжил».

```json
{ "type": "NICKNAME", "alias": "Мальчик, который выжил", "entity": "Гарри Поттер" }
```

**Карточки:**
- `Мальчик, который выжил` → `Прозвище Гарри Поттера.`
- `Гарри Поттер` → `Мальчик, который выжил`

### 3. Wh-вопрос (~15%)

**Факт:** на Земле 14 восьмитысячников.

```json
{ "type": "NUMBER", "value": "14", "domain": "на Земле восьмитысячников" }
```

**Карточки:**
- `14` → `Сколько на Земле восьмитысячников?`
- `на Земле восьмитысячников` → `14`

### 4. ЧГК-заготовки с местоимениями (~30%)

**Факт:** Столовая гора на Капском полуострове.

```json
{
  "type": "RELATION",
  "relation": "LOCATED_IN",
  "child": "Столовая гора",
  "parent": "Капский полуостров"
}
```

**Карточки:**
- `Капский полуостров` → `Столовая гора находится на НЁМ.`
- `Столовая гора` → `На Капском полуострове находится ОНА.`

Местоимения: `ОН/ОНА/ОНИ`, `НЁМ/НЕЙ/НИХ`, `НЕГО/НЕЁ` — через морфологию (`mystem` или эвристики).

### 5. «Должен щёлкать» (<1%, вручную или LLM)

**Факт:** Кока-Кола ассоциируется с Атлантой.

```json
{
  "type": "TERM",
  "term": "Кока-Кола",
  "extra": { "clickable": "true", "clickHint": "Атланту" }
}
```

**Карточка:** `Кока-Кола` → `Какой термин должен щёлкать на Атланту?`

### 6. Мета-подсказки (~5%)

Поле `answerHint`: «тремя словами», «через запятую по алфавиту».

```json
{
  "type": "TERM",
  "term": "Хронограф",
  "fact": "Памятник древнерусской литературы...",
  "answerHint": "Назовите варианты названия из одного и двух слов."
}
```

## Цепочки карточек

Из одного факта генерируйте **2–4 карточки** с разных сторон:

1. **Прямая:** термин → определение
2. **Обратная:** определение/вопрос → термин
3. **Контекстная:** связанная сущность → заготовка с местоимением
4. **Уточняющая:** число, год, автор, перевод

## Запуск генератора

### Из Telegram JSON (рекомендуется)

Экспорт чата из Telegram Desktop → **Export chat history** → JSON → положить `result.json` в `telegram-export-json/`.

```bash
mvn package
java -jar target/quizlet-parser-1.0.0-SNAPSHOT.jar \
  --telegram-json telegram-export-json/result.json \
  -o output/cards.txt \
  --output-examples output/parsing-examples.json
```

Quizlet TSV (`-o`) и формат parsing-examples пишутся **параллельно**:
- `output/cards.txt` — TSV для импорта в Quizlet (как раньше)
- `output/parsing-examples.json` — тот же schema, что `parsing-examples/parsing-examples.json`
- `output/parsing-examples.txt` — человекочитаемый вид (создаётся автоматически рядом с JSON)

Дополнительные опции:

- `--dump-facts output/facts.json` — сохранить промежуточный `StructuredFact` для отладки
- `--fetch-wiki` — для сообщений только со ссылкой подтянуть первое предложение из Wikipedia API
- `--skip-link-only` — пропустить сообщения, где только URL без текста
- `--skip-orphan` — пропустить короткие заметки без «—», «:», «?» и без ссылок
- `--no-examples-overlay` — не подставлять эталон из `parsing-examples.json`
- `--output-examples path.json` — дополнительно сохранить результат в формате parsing-examples (JSON + `.txt`)
- `--output-examples-txt path.txt` — явный путь для TXT (по умолчанию — рядом с JSON, та же база имени)

### Эталон parsing-examples.json

Файл [`parsing-examples/parsing-examples.json`](../parsing-examples/parsing-examples.json) — **эталон качества**. Если текст сообщения совпадает с `text` в примере, используются готовые `cards` (без эвристик).

Формат:

```json
{
  "examples": [
    {
      "id": "red-apple-tarantino",
      "text": "Red Apple — вымышленный бренд сигарет в фильмах Тарантино",
      "tags": ["term", "multi-card"],
      "cards": [
        { "question": "...", "answer": "..." }
      ]
    }
  ]
}
```

- `id` — имя для отчёта и тестов
- `text` — plain text как в Telegram (пробелы нормализуются)
- `cards` — 1–5 карточек в стиле `quizlet-modules`

**TXT-вид** (файл `parsing-examples.txt` или `--output-examples` → `.txt`):

```
===== red-apple-tarantino =====
TEXT:
Red Apple — вымышленный бренд сигарет в фильмах Тарантино

TAGS: term, multi-card

CARDS:
[1]
Q: ...
A: ...

---
```

Каждый блок — одно исходное сообщение (или один `StructuredFact` при `-i`) и все сгенерированные для него карточки.

**Добавляйте примеры** — для совпадающих текстов карточки будут точными.

Отладка эвристик (без overlay):

```bash
java -jar target/quizlet-parser-1.0.0-SNAPSHOT.jar \
  --examples-report parsing-examples/parsing-examples.json
```

Вывод: `[PASS]` / `[FAIL]` по каждому примеру, missing cards, первый полученный результат.

### Из готового JSON фактов

```bash
java -jar target/quizlet-parser-1.0.0-SNAPSHOT.jar \
  -i examples/facts.json \
  -o output/cards.txt
```

Общие опции:
- `--mystem` — принудительно использовать mystem (если установлен)
- `--llm-url`, `--llm-key` — опциональное LLM-обогащение (заглушка)

## Вход из Telegram JSON

Цепочка обработки:

```
result.json → TelegramJsonReader → HeuristicFactParser → StructuredFact → CardGenerator → cards.txt
```

Классы в пакете `com.quizlet.parser.telegram`:

| Класс | Роль |
|-------|------|
| `TelegramJsonReader` | читает экспорт, пропускает service-сообщения |
| `MessageTextNormalizer` | склеивает `text` (строка или массив) в plain text + links |
| `HeuristicFactParser` | эвристики → `StructuredFact` |
| `WikipediaTitleExtractor` | заголовок статьи из URL slug |

Распознаваемые паттерны сообщений:

| Сообщение | → тип |
|-----------|-------|
| `Бродский: Если Евтушенко...` | `QUOTE` |
| `Украденное письмо — Эдгар Аллан По — [wiki]` | `ARTWORK` |
| `Кончина Фидельки [link]` | `ARTWORK` |
| `[wiki] — Евтушенко` | `TERM` / `PERSON` |
| только `[wiki]` | `TERM` (название из slug) |
| `Птицы — комедия Аристофана` | `TERM` |
| `сон жены рыбака — 1814 год` | `TERM` + `YEAR` |
| `X находится в Y` | `RELATION` |
| `...?` | `TERM` (вопрос как факт) |
| одна фраза | `TERM` (term = fact) |

Хештеги (`#цитаты`, `#числа`) попадают в `extra.category`.

## Ограничения без LLM

| Возможно | Невозможно |
|----------|------------|
| Шаблоны по типу факта | Идеальный разбор всех свободных заметок |
| Telegram JSON → эвристический парсинг | Энциклопедические ассоциации («должен щёлкать») |
| Морфология для ОН/НЕМ | Креативный выбор «угла» вопроса |
| Обратные и wh-карточки | Ирония, отсылки, длинный контекст |
| `--fetch-wiki` для link-only | HTML-экспорт Telegram (используйте JSON) |

## Редактирование шаблонов

Шаблоны в [`src/main/resources/templates.yaml`](../src/main/resources/templates.yaml). Плейсхолдеры:

- `{field}` — значение поля
- `{field:genitive}` — родительный падеж
- `{field:prepositional}` — предложный падеж
- `{field:prepositional_phrase}` — «на/в …»
- `{field:pronoun_nominative}` — ОН/ОНА/ОНИ
- `{field:pronoun_prepositional}` — НЁМ/НЕЙ/НИХ
