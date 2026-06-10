# Cursor batch run-008

Те же **50** сообщений (seed=42). База: [`run-007`](../run-007/). Правки по **примеру 5** (и **10**) из [`quizlet-rules.md`](../../hermes/quizlet-rules.md): в вопросе нет слов и однокоренных форм из ответа.

## Статистика

- **50** examples, **101** cards
- Источник: [`candidates.json`](candidates.json)

## Исправления run-007 → run-008 (пример 5)

| id | Было | Стало |
|----|------|-------|
| `apelsinovaya-sdelka` | «сделку… апельсинами… ЭТИМ» | описательно, без корней ответа |
| `ai-slop` | «от **нейросетей**» | «от генеративных моделей» |
| `tysyacha-bogov` | «**Тыща** богов» | без «тыща» в вопросе |
| `bloom-filter` | «**фильтр**… ЭТИМ» | «…называют **ИМ**» (пример 10) |
| `blood-bell-cologne` | «**колокол**… Blutglocke» | «предмет с мрачным прозвищем» |
| `retriever-etymology` | **retrieve** / **retriever** | «собак-апортировщиков» |
| `hms-zubian` | Zulu + Nubian в вопросе | «двух британских эсминцев» |
| `crimea-trolleybus` | «**троллейбус**ная линия» | «линия на электротранспорте» |

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 50 examples |
| `parsing-examples-cursor.txt` | Человекочитаемый вид + message_id |
| `build_output.py` | Генерация JSON/TXT/README |
| `lint_cards.py` | Проверка правил quizlet-rules |
