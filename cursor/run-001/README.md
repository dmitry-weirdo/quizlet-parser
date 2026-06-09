# Cursor batch: parsing-examples

Разовый батч из **20** Telegram-сообщений в формате [`parsing-examples/parsing-examples.json`](../../parsing-examples/parsing-examples.json).

Правила генерации: [`hermes/quizlet-rules.md`](../../hermes/quizlet-rules.md).

Источник сообщений: [`telegram-export-json/result.json`](../../telegram-export-json/result.json) (октябрь–ноябрь 2023).

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 20 examples с полем `logic` на каждой карточке |
| `parsing-examples-cursor.txt` | Человекочитаемый вид |

## Отбор сообщений

| # | id | Telegram message id | tags |
|---|-----|---------------------|------|
| 1 | pismo-generalu-z | -999907461 | link-only, quote, person |
| 2 | konchina-fidelki | -999907459 | link+comment, artwork, multi-card |
| 3 | storozhevaya-sobaka | -999907458 | text-only, question, literature |
| 4 | effekt-flinna | -999907457 | link-only, term |
| 5 | ukradennoe-pismo | -999907454 | link+comment, literature, multi-card |
| 6 | kirbi-hulk | -999907452 | text-only, person, term |
| 7 | devushka-v-pautine | -999907446 | link-only, literature, artwork |
| 8 | kundeo | -999907369 | text-only, term |
| 9 | stonehenge-chubb | -999907372 | link+comment, person, multi-card |
| 10 | phil-knight-nike | -999907215 | link+comment, person |
| 11 | river-poker | -999907207 | text-only, question, term |
| 12 | cloud-nine | -999907095 | text-only, quote, term |
| 13 | svyashchennaya-rimskaya-imperiya | -999907033 | link+comment, quote, person |
| 14 | skuf | -999907029 | text-only, question, term |
| 15 | velcro | -999906614 | link+comment, term, multi-card |
| 16 | manchester-liverpool | -999906196 | text-only, quote |
| 17 | hulk-jekyll | -999907450 | text-only, term, quote |
| 18 | pontifex | -999907445 | text-only, term, question |
| 19 | tanki-po-prage | -999907455 | link+comment, quote, person |
| 20 | dovlatov-menu | -999906315 | text-only, quote, person |

Исключены сообщения, уже попавшие в `parsing-examples/parsing-examples.json` (Бродский, Чарльз 19 века, Дюрер, Нерон, Red Apple).

## Статистика

- **20** examples, **52** cards всего
- **3** link-only, **7** link+comment, **10** text-only
- **5** examples с ≥3 карточками (multi-card)
