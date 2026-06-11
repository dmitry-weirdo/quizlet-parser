# cards-llm: пилот генерации карточек через LLM

**20** Telegram-сообщений → формат [`parsing-examples.json`](../../parsing-examples/parsing-examples.json).

Правила: [`quizlet-rules.md`](../../hermes/quizlet-rules.md). Стиль: [`quizlet-modules`](../../quizlet-modules/) + golden examples.

Карточки сгенерированы **LLM-агентом Cursor** (не Java/Python-эвристики).

## Статистика (run 3 — правила 13–16, без примера 17)

| Метрика | run 1 | run 2 | run 3 |
|---------|-------|-------|-------|
| Examples | 20 | 20 | 20 |
| Cards | 59 | 69 | **70** |
| Lint (однокоренность) | OK | OK | **OK** |
| text-only | 10 |
| link+comment | 4 |
| link-only | 3 |
| question-in-text | 3 |
| multi-card (≥3) | 8 |

## Workflow

```bash
python cursor/cards-llm/extract_style_samples.py
python cursor/cards-llm/extract_candidates.py
python cursor/cards-llm/split_batches.py
# LLM-агент: batches/batch-NNN.json -> generations/batch-NNN.json
python cursor/cards-llm/build_output.py
python cursor/cards-llm/lint_cards.py
```

Инструкция агенту: [`generate_cards_prompt.md`](generate_cards_prompt.md).

## Файлы

| Файл | Описание |
|------|----------|
| `candidates.json` | 20 отобранных сообщений (seed=43) |
| `style_samples.json` | 50 пар из quizlet-modules |
| `batches/` | вход агенту (по 5 сообщений) |
| `generations/` | выход агента |
| `parsing-examples-cursor.json` | итог |
| `parsing-examples-cursor.txt` | человекочитаемый вид + MESSAGE_ID |
| `llm_report.json` / `llm_report.md` | журнал вызовов LLM |

Все артефакты пилота — только в этой директории.

## Отбор сообщений (message_id)

| # | id | message_id | tags |
|---|-----|------------|------|
| 1 | soviet-aeroflot-pen-packets | 2343 | link+comment |
| 2 | santa-coal-bad-children | 4115 | text-only |
| 3 | pickle-rick-episode | -999905327 | link+comment, multi-card |
| 4 | london-traffic-light-grape | 1128 | question |
| 5 | bangkok-city-of-angels | 2161 | text-only |
| 6 | meek-inherit-earth | 3666 | text-only, quote |
| 7 | ringelmann-effect | 4507 | link-only, multi-card |
| 8 | iskat-taksi-palindrome | -999898727 | text-only |
| 9 | stevenson-suicide-club | 843 | text-only, literature |
| 10 | vienna-basilisk-mirror | 1455 | text-only |
| 11 | baron-munchausen-book | 437 | link+comment, multi-card |
| 12 | lake-vostok-cold | 5047 | text-only |
| 13 | yes-sir-est-military | -999900509 | text-only |
| 14 | koek-en-zopie | 2216 | link-only |
| 15 | zimmermann-telegram | 4214 | link-only, multi-card |
| 16 | agua-viva-jellyfish | 3355 | question |
| 17 | marsyas-apollo | 4888 | link+comment, multi-card |
| 18 | barnacles-tsushima | 1049 | text-only, history |
| 19 | nyc-five-boroughs | 1311 | text-only |
| 20 | hamburg-dinosaurs-bundesliga | 5040 | text-only, sport |

Исключены: golden из `parsing-examples.json` и 53 message_id из run-001…run-010.

## Run 3 (текущий)

Перегенерация на **тех же батчах** после удаления примера 17 (text-only без Wikipedia) и усиления проверки однокоренности в `lint_cards.py`.

Основные изменения vs run 2:
- вернули богатый контекст из Wikipedia (озеро Восток, Марсий, Рингельманн и др.);
- строгая проверка однокоренных слов во всех 70 парах (общие токены, префиксы 4–6 букв, вложенность);
- правила 13–16: «ЭТО СЛОВО», «ЭТО прозвище», реалии из текста, без однокоренности.
