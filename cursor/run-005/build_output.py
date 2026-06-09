"""Build run-005 parsing-examples from curated examples."""
import json
from pathlib import Path

EXAMPLES = [
    {
        "id": "gutenberg-project",
        "message_id": 4658,
        "text": "https://ru.wikipedia.org/wiki/Проект_«Гутенберг» — паблик цифровая библиотека аж с 1971 года!",
        "tags": ["link+comment", "term", "history"],
        "cards": [
            {"question": "Проект «Гутенберг» — публичная цифровая библиотека, основанная Майклом Хартом В ЭТОМ ГОДУ.", "answer": "1971", "logic": "Только год → В ЭТОМ ГОДУ (пример 6)."},
            {"question": "Основателем проекта «Гутенберг» считается ОН.", "answer": "Майкл Харт", "logic": "Персоналия → ОН. Имя из ru.wikipedia."},
        ],
    },
    {
        "id": "tysyacha-bogov",
        "message_id": 59,
        "text": 'аааа, это я в тв-свояке услышал как ответ "Тыща богов" 😁',
        "tags": ["text-only", "quote", "tv"],
        "cards": [
            {"question": "В «Своей игре» звучал ответ «Тыща…» — ЭТО слово должно стоять на месте многоточия.", "answer": "богов", "logic": "Ответ не в вопросе целиком (пример 5)."},
            {"question": "Фразу «Тыща богов» в нормативной орфографии пишут с буквой «я» в середине первого слова — ЭТО.", "answer": "Тысяча", "logic": "Разговорное «тыща» → «тысяча»."},
        ],
    },
    {
        "id": "colt-peacemaker",
        "message_id": -999900455,
        "text": "Миротворец — модель Кольта",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Револьвер Colt Single Action Army получил прозвище ЭТО.", "answer": "Миротворец", "logic": "Термин в ответе, не в вопросе."},
            {"question": "Прозвище «Миротворец» закрепилось за продукцией ЭТОГО оружейника.", "answer": "Сэмюэл Кольт", "logic": "Полное имя из ru.wikipedia (пример 8)."},
        ],
    },
    {
        "id": "gloria-scott",
        "message_id": 5453,
        "text": "Глория Скотт — в тексте нужно было читать каждое третье слово (Шерлок Холмс)",
        "tags": ["text-only", "literature", "multi-card"],
        "cards": [
            {"question": "В рассказе о сыщике из Бейкер-стрит шифр читали, выбирая каждое третье слово; рассказ называется ТАК.", "answer": "Глория Скотт", "logic": "Не «Шерлок Холмс» в ответе — название рассказа (пример 10)."},
            {"question": "Рассказ «Глория Скотт» входит в цикл произведений об ОН.", "answer": "Шерлок Холмс", "logic": "Обратная карточка. ОН вместо «кто»."},
        ],
    },
    {
        "id": "er-riyad",
        "message_id": 344,
        "text": "Эр-Рияд значит «сады»?",
        "tags": ["text-only", "question", "term"],
        "cards": [
            {"question": "Название столицы Саудовской Аравии с арабского переводится как ЭТО.", "answer": "сады", "logic": "Исходный вопрос переформулирован с ЭТО."},
        ],
    },
    {
        "id": "ai-slop",
        "message_id": 4109,
        "text": "Ai slop — нейропомоии",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Низкокачественный массовый контент от нейросетей в сленге называют ЭТИМ.", "answer": "нейропомои", "logic": "Термин из сообщения, без «что такое»."},
            {"question": "«Нейропомои» — русский сленговый эквивалент английского выражения, которое пишут ЭТИМИ двумя словами — на английском.", "answer": "AI slop", "logic": "Английский ответ объявлен (пример 3)."},
        ],
    },
    {
        "id": "apelsinovaya-sdelka",
        "message_id": 4805,
        "text": "апельсиновая сделка — СССР и Израиль — отсюда Чебурашка приехал",
        "tags": ["text-only", "term", "multi-card"],
        "cards": [
            {"question": "Советско-израильскую торговую сделку, связанную с апельсинами, называют ЭТИМ.", "answer": "апельсиновая сделка", "logic": "Термин в ответе."},
            {"question": "По популярной версии, Чебурашка приехал в СССР из ящика с апельсинами из ЭТОЙ страны.", "answer": "Израиль", "logic": "Вторая реалия из сообщения."},
        ],
    },
    {
        "id": "miracle-on-grass",
        "message_id": 3625,
        "text": "https://ru.wikipedia.org/wiki/Футбольный_матч_США_—_Англия_(1950) — чудо на газоне",
        "tags": ["link+comment", "term", "sport"],
        "cards": [
            {"question": "Победу сборной США над Англией на ЧМ-1950 называют ЭТИМ.", "answer": "чудо на газоне", "logic": "Прозвище из комментария."},
            {"question": "«Чудо на газоне» произошло В ЭТОМ ГОДУ.", "answer": "1950", "logic": "Только год → В ЭТОМ ГОДУ."},
        ],
    },
    {
        "id": "buratino-nose",
        "message_id": 3683,
        "text": "у Буратино, в отличие от Пиноккио, нос от лжи не рос.",
        "tags": ["text-only", "literature"],
        "cards": [
            {"question": "У ЭТОГО деревянного мальчика нос от лжи не увеличивался.", "answer": "Буратино", "logic": "Спросили Буратино, не Пиноккио."},
            {"question": "У итальянского Пиноккио при лжи увеличивался ЭТО.", "answer": "нос", "logic": "Обратная реалия из контраста."},
        ],
    },
    {
        "id": "qed",
        "message_id": 3259,
        "text": "qed — как расшифровываются латинские слова?",
        "tags": ["text-only", "question", "term"],
        "cards": [
            {"question": "Аббревиатуру Q.E.D. раскрывают ЭТОЙ латинской фразой.", "answer": "quod erat demonstrandum", "logic": "Латынь в ответе; вопрос без «как»."},
        ],
    },
    {
        "id": "rynda-kupel",
        "message_id": -999894157,
        "text": "Рынду используют как купель для младенцев. Купель — это крещение?",
        "tags": ["text-only", "question", "term"],
        "cards": [
            {"question": "Сосуд для обряда крещения младенцев называют ЭТИМ.", "answer": "купель", "logic": "Купель — не сам обряд."},
            {"question": "Рынду в старину использовали как ЭТО для крещения.", "answer": "купель", "logic": "Связь предмета и обряда."},
        ],
    },
    {
        "id": "james-whatman",
        "message_id": 3537,
        "text": "https://ru.wikipedia.org/wiki/Ватман — Джеймс Уотмэн",
        "tags": ["link+comment", "person", "term"],
        "cards": [
            {"question": "Плотную чертежную бумагу называют по фамилии английского фабриканта — ОН.", "answer": "Джеймс Уотман", "logic": "ru.wikipedia: Уотман (не Уотмэн из опечатки сообщения)."},
        ],
    },
    {
        "id": "immortal-jellyfish",
        "message_id": 1627,
        "text": "Есть бессмертные медузы",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "«Биологически бессмертной» называют медузу ЭТОГО вида — латинское название.", "answer": "Turritopsis dohrnii", "logic": "Латынь в ответе; вид из ru.wikipedia."},
        ],
    },
    {
        "id": "orpheus-maenads",
        "message_id": -999900584,
        "text": "https://ru.wikipedia.org/wiki/Орфей — кем был убит Офей (кем-то связанным с Вакхом)",
        "tags": ["link+comment", "person", "mythology"],
        "cards": [
            {"question": "В мифе певца растерзали спутницы Вакха — ЭТИ.", "answer": "менады", "logic": "Не «Орфей» в ответе — кто убил."},
            {"question": "Менады в мифологии связаны с богом, которого римляне называли ЭТИМ.", "answer": "Вакх", "logic": "Вторая реалия из подсказки."},
        ],
    },
    {
        "id": "hms-zubian",
        "message_id": -999893521,
        "text": "эсминец (или другой корабль?) из двух частей двух других кораблей.",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Корабль, собранный из частей HMS Zulu и HMS Nubian, назывался ЭТИМ — на английском.", "answer": "HMS Zubian", "logic": "Английский ответ объявлен."},
        ],
    },
    {
        "id": "palmer-pilgrim",
        "message_id": 4361,
        "text": "palmer —  паломник\n\n#английский",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Средневекового паломника, вернувшегося с Святой земли, в английском называли ЭТИМ словом — на английском.", "answer": "palmer", "logic": "Прямая пара из сообщения."},
            {"question": "Слово «palmer» переводится на русский как ЭТО.", "answer": "паломник", "logic": "Обратная карточка."},
        ],
    },
    {
        "id": "maupertuis-geoid",
        "message_id": -999894364,
        "text": "кто доказал, что земля не идеальный круг, а геоид (путешествие)? Пьер Матьюртири?",
        "tags": ["text-only", "question", "person"],
        "cards": [
            {"question": "Лапландскую экспедицию, подтвердившую сплюснутость Земли у полюсов, возглавлял ОН.", "answer": "Пьер Луи Моро де Мопертюи", "logic": "«Кто» → ОН. Имя из ru.wikipedia (не «Матьюртири»)."},
        ],
    },
    {
        "id": "tony-award",
        "message_id": 1072,
        "text": "Тони — театральная премия",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Главную американскую театральную премию называют ЭТИМ.", "answer": "Тони", "logic": "Термин в ответе."},
        ],
    },
    {
        "id": "hearts-are-trumps",
        "message_id": 2050,
        "text": "Hearts are trumps — картина Милле",
        "tags": ["text-only", "artwork"],
        "cards": [
            {"question": "Картину «Hearts are Trumps» написал ОН.", "answer": "Джон Эверетт Милле", "logic": "Полное имя (пример 8)."},
            {"question": "Джон Эверетт Милле принадлежал к художественному течению, которое называют ЭТИМ.", "answer": "прерафаэлиты", "logic": "Дополнение из ru.wikipedia."},
        ],
    },
    {
        "id": "total-war-speech",
        "message_id": 3353,
        "text": "https://ru.wikipedia.org/wiki/Речь_о_тотальной_войне",
        "tags": ["link-only", "quote", "person"],
        "cards": [
            {"question": "«Речь о тотальной войне» в берлинском Спортпаласте произнесена ОН.", "answer": "Йозеф Геббельс", "logic": "Link-only: автор из Wikipedia."},
            {"question": "«Речь о тотальной войне» прозвучала В ЭТОМ ГОДУ.", "answer": "1943", "logic": "Только год → В ЭТОМ ГОДУ."},
        ],
    },
    {
        "id": "man-in-high-castle",
        "message_id": -999894584,
        "text": "Человек в высоком замке— Филипп Дик",
        "tags": ["text-only", "literature"],
        "cards": [
            {"question": "Роман «Человек в высоком замке» написал ОН.", "answer": "Филип Киндред Дик", "logic": "Полное имя из ru.wikipedia."},
        ],
    },
    {
        "id": "vatel-suicide",
        "message_id": -999892900,
        "text": "повар, который покончил с собой из-за несвежей воды — Ватель?",
        "tags": ["text-only", "question", "person"],
        "cards": [
            {"question": "Придворный повар, покончивший с собой из-за срыва поставок к пиру, — ОН.", "answer": "Франсуа Ватель", "logic": "«Кто» → ОН. Полное имя."},
        ],
    },
    {
        "id": "scooby-doo",
        "message_id": 3166,
        "text": "https://ru.wikipedia.org/wiki/Скуби-Ду\n\nчерез дефис\nчетверка/пятерка героев\nисследуют сверхъестественное\nсамый долгий мультсериал (КРГ(",
        "tags": ["link+comment", "term", "multi-card"],
        "cards": [
            {"question": "Имя пса из мультфраншизы о команде, расследующей сверхъестественное, пишут через дефис — ЭТО.", "answer": "Скуби-Ду", "logic": "Не «Скуби-Ду» в вопросе (пример 10)."},
            {"question": "Команду подростков и пса в оригинале называют ЭТИМ — на английском.", "answer": "Mystery Inc.", "logic": "Английский ответ объявлен."},
        ],
    },
    {
        "id": "yeltsin-memoirs",
        "message_id": 1196,
        "text": '"Исповедь на заданную тему" — мемуары? Ельцина',
        "tags": ["text-only", "question", "person"],
        "cards": [
            {"question": "Мемуары «Исповедь на заданную тему» написал ОН.", "answer": "Борис Николаевич Ельцин", "logic": "Полное имя (пример 8)."},
        ],
    },
    {
        "id": "metics-athens",
        "message_id": 4537,
        "text": "Метеки\n\nhttps://ru.wikipedia.org/wiki/Метэки",
        "tags": ["link+comment", "term"],
        "cards": [
            {"question": "В Древних Афинах свободных переселенцев без гражданских прав называли ЭТИМ.", "answer": "метэки", "logic": "Термин из Wikipedia."},
        ],
    },
    {
        "id": "flea-rhcp",
        "message_id": -999906266,
        "text": "flea — блоха + рхчп",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Слово «блоха» на английский переводится ЭТИМ.", "answer": "flea", "logic": "Английский ответ (пример 3)."},
            {"question": "Бас-гитариста Red Hot Chili Peppers в англоязычной среде зовут по прозвищу, совпадающему с ЭТИМ словом — на английском.", "answer": "Flea", "logic": "Вторая реалия из «рхчп»."},
        ],
    },
    {
        "id": "guano-terentyev",
        "message_id": -999902027,
        "text": "Последний вопрос в туре Терентьева — про говно, гуано, помет бобра итд",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Высушенный помёт морских птиц, используемый как удобрение, называется ЭТИМ.", "answer": "гуано", "logic": "Одна реалия из перечисления."},
            {"question": "Помёт бобра в контексте вопроса Терентьева — ЭТО.", "answer": "кастореум", "logic": "Вторая реалия из ряда «помет бобра»."},
        ],
    },
    {
        "id": "rigorism",
        "message_id": 3740,
        "text": "https://ru.wikipedia.org/wiki/Ригоризм — ригоризм, ригорист",
        "tags": ["link+comment", "term"],
        "cards": [
            {"question": "Бескомпромиссно строгую моральную позицию называют ЭТИМ.", "answer": "ригоризм", "logic": "Не «ригоризм» в вопросе (пример 10)."},
            {"question": "Приверженца такой позиции называют ЭТИМ.", "answer": "ригорист", "logic": "Вторая форма из сообщения."},
        ],
    },
    {
        "id": "katarina-witt",
        "message_id": 32,
        "text": "Катарина Витт — красивая фигуристка из ГДР",
        "tags": ["text-only", "person"],
        "cards": [
            {"question": "Двукратную олимпийскую чемпионку по фигурному катанию из ГДР звали ЭТО.", "answer": "Катарина Витт", "logic": "Имя+фамилия в ответе."},
            {"question": "Катарина Витт представляла на Олимпиадах ЭТУ страну.", "answer": "ГДР", "logic": "Вторая реалия из сообщения."},
        ],
    },
    {
        "id": "big-lebowski-walrus",
        "message_id": 4750,
        "text": "большой лебовски — я морж",
        "tags": ["text-only", "quote"],
        "cards": [
            {"question": "В «Большом Лебовски» герой цитирует песню The Beatles — ЭТО её название на английском.", "answer": "I Am the Walrus", "logic": "Английский ответ объявлен."},
        ],
    },
    {
        "id": "lonely-rooster",
        "message_id": 3252,
        "text": "Очень одинокий петух — картина? из Карлсона",
        "tags": ["text-only", "question", "literature"],
        "cards": [
            {"question": "Картину с подписью «Очень одинокий петух» нарисовал ОН.", "answer": "Карлсон", "logic": "Персонаж из сказки."},
        ],
    },
    {
        "id": "prokofiev-stone-flower",
        "message_id": 1410,
        "text": "40. ЭТОТ человек с одинаковыми именем-отчеством прочитал «Малахитовую шкатулку» в зрелом возрасте и был очень впечатлен.\n\nОтвет: (Сергей) Прокофьев.\nКомментарий: После прочтения создал балет «Каменный цветок».",
        "tags": ["text-only", "person", "artwork"],
        "cards": [
            {"question": "После чтения «Малахитовой шкатулки» Сергей Сергеевич Прокофьев создал балет ЭТО.", "answer": "Каменный цветок", "logic": "Полное имя в вопросе (пример 8)."},
            {"question": "Балет «Каменный цветок» написал ОН.", "answer": "Сергей Сергеевич Прокофьев", "logic": "Обратная карточка."},
        ],
    },
    {
        "id": "bloom-filter",
        "message_id": 5485,
        "text": "https://ru.wikipedia.org/wiki/Фильтр_Блума",
        "tags": ["link-only", "term"],
        "cards": [
            {"question": "Вероятностную структуру данных для проверки принадлежности элемента множеству называют ЭТИМ.", "answer": "фильтр Блума", "logic": "Не «Блума» в вопросе (пример 10)."},
            {"question": "Автором идеи такого фильтра считается ОН.", "answer": "Бёртон Блум", "logic": "Эпоним из Wikipedia."},
        ],
    },
    {
        "id": "alferov-nobel",
        "message_id": -999905918,
        "text": "Алфероф — НП по физике 2000 года",
        "tags": ["text-only", "person"],
        "cards": [
            {"question": "Нобелевскую премию по физике 2000 года получил ОН.", "answer": "Жорес Алфёров", "logic": "Правильное написание фамилии (пример 7)."},
            {"question": "Жорес Алфёров и Герберт Крёмер получили премию за разработки в области ЭТО.", "answer": "гетероструктур", "logic": "Вторая реалия из Wikipedia."},
        ],
    },
    {
        "id": "charlie-kirk",
        "message_id": 4324,
        "text": "https://ru.wikipedia.org/wiki/Убийство_Чарли_Кирка",
        "tags": ["link-only", "person"],
        "cards": [
            {"question": "Статья в русской Wikipedia посвящена гибели ЭТОГО американского политического деятеля.", "answer": "Чарли Кирк", "logic": "Нейтральный факт из заголовка статьи."},
            {"question": "Событие из статьи произошло В ЭТУ ДАТУ.", "answer": "10 сентября 2025", "logic": "Полная дата → В ЭТУ ДАТУ."},
        ],
    },
    {
        "id": "crouching-tiger",
        "message_id": 1647,
        "text": "крадущийся тигр, затаившийся дракон",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Фильм Энга Ли 2000 года в русском прокате вышел под названием, начинающимся с ЭТИХ слов.", "answer": "Крадущийся тигр, затаившийся дракон", "logic": "Текст сообщения — русское название."},
            {"question": "Оригинальное название того же фильма на английском — ЭТО.", "answer": "Crouching Tiger, Hidden Dragon", "logic": "Английский в ответе."},
        ],
    },
    {
        "id": "train-from-nowhere",
        "message_id": 2558,
        "text": "Поезд из ниоткуда — роман без глаголов",
        "tags": ["text-only", "literature"],
        "cards": [
            {"question": "Экспериментальный роман почти без глаголов называется ЭТИМ.", "answer": "Поезд из ниоткуда", "logic": "Особенность формы из сообщения."},
            {"question": "«Поезд из ниоткуда» написал ОН.", "answer": "Эдмунд Гисе", "logic": "Автор из ru.wikipedia."},
        ],
    },
    {
        "id": "swanns-way",
        "message_id": 307,
        "text": "https://ru.wikipedia.org/wiki/По_направлению_к_Свану",
        "tags": ["link-only", "literature"],
        "cards": [
            {"question": "Первая часть цикла «В поисках утраченного времени» называется ЭТИМ.", "answer": "По направлению к Свану", "logic": "Link-only: Пруст."},
            {"question": "Цикл «В поисках утраченного времени» написал ОН.", "answer": "Марсель Пруст", "logic": "Автор из Wikipedia."},
        ],
    },
    {
        "id": "shokoladnitsa-butterfly",
        "message_id": 203,
        "text": "https://solomeya-lutova.livejournal.com/14392.html — на самом деле такой бабочки не существует, это народное название какого-то другого вида",
        "tags": ["link+comment", "term"],
        "cards": [
            {"question": "Народное название «шоколадница» часто ошибочно приписывают бабочке ЭТОГО вида.", "answer": "крапивница", "logic": "Суть заметки из комментария."},
        ],
    },
    {
        "id": "blood-bell-cologne",
        "message_id": 103,
        "text": "Кровавый колокол в Кёльне ⬇️",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "В Кёльнском соборе колокол с мрачным прозвищем называют ЭТИМ по-немецки — на немецком.", "answer": "Blutglocke", "logic": "Английский/немецкий ответ объявлен."},
            {"question": "«Кровавый колокол» находится ТАМ.", "answer": "в Кёльнском соборе", "logic": "ТАМ вместо названия."},
        ],
    },
    {
        "id": "retriever-etymology",
        "message_id": 3528,
        "text": "https://ru.wikipedia.org/wiki/Ретривер\n\nСобака с английской этимологией породы",
        "tags": ["link+comment", "term"],
        "cards": [
            {"question": "Группу охотничьих собак, название которой происходит от to retrieve, называют ЭТИМ.", "answer": "ретривер", "logic": "Этимология из комментария."},
            {"question": "Глагол retrieve в контексте охоты переводится как «приносить обратно» — от него названа ЭТА группа пород.", "answer": "ретривер", "logic": "Связь этимологии и названия."},
        ],
    },
    {
        "id": "shield-of-achilles",
        "message_id": 4723,
        "text": "Щит Ахилла — подробное описание есть",
        "tags": ["text-only", "literature"],
        "cards": [
            {"question": "Подробное описание щита Ахилла содержится в ЭТОМ произведении.", "answer": "Илиада", "logic": "Экфрасис в «Илиаде»."},
            {"question": "Щит Ахилла выковал для героя ЭТОТ бог.", "answer": "Гефест", "logic": "Вторая реалия из мифа."},
        ],
    },
    {
        "id": "actaeon",
        "message_id": -999904202,
        "text": "https://ru.wikipedia.org/wiki/Актеон",
        "tags": ["link-only", "person", "mythology"],
        "cards": [
            {"question": "Охотника, превращённого в оленя, звали ЭТИМ.", "answer": "Актеон", "logic": "Link-only."},
            {"question": "Актеона по мифу наказала ОНА.", "answer": "Артемида", "logic": "ОНА вместо «кто»."},
        ],
    },
    {
        "id": "itzpapalotl",
        "message_id": 4293,
        "text": "Обсидиановая бабочка — ацтеки",
        "tags": ["text-only", "term", "mythology"],
        "cards": [
            {"question": "Ацтекскую богиню, чьё имя переводят как «обсидиановая бабочка», звали ЭТИМ.", "answer": "Ицпапалотль", "logic": "Термин из сообщения."},
        ],
    },
    {
        "id": "tintoretto",
        "message_id": -999905457,
        "text": "Тинторетто — сын красильщика / маленький красильщик",
        "tags": ["text-only", "person", "term"],
        "cards": [
            {"question": "Прозвище венецианского художника переводят как «маленький красильщик» — ЭТО его имя.", "answer": "Якопо Тинторетто", "logic": "Полное имя (пример 8)."},
        ],
    },
    {
        "id": "shotgun-wedding",
        "message_id": -999902145,
        "text": "shotgun wedding",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Поспешный брак из-за незапланированной беременности на английском называют ЭТИМ — на английском.", "answer": "shotgun wedding", "logic": "Английский термин."},
        ],
    },
    {
        "id": "christina-ricci-wednesday",
        "message_id": 4310,
        "text": "Кристина Ричи — Актриса Уэнсдэй",
        "tags": ["text-only", "person"],
        "cards": [
            {"question": "Уэнсдэй Аддамс в фильмах 1990-х сыграла ОНА.", "answer": "Кристина Риччи", "logic": "ОНА вместо «кто». Фамилия по ru.wikipedia."},
        ],
    },
    {
        "id": "golden-calf-bender",
        "message_id": 902,
        "text": "Золотой телец — изучить сюжет.",
        "tags": ["text-only", "literature"],
        "cards": [
            {"question": "В романе Ильфа и Петрова Остап Бендер охотится за миллионером Корейко — роман называется ЭТИМ.", "answer": "Золотой телёнок", "logic": "Сюжет из сообщения."},
            {"question": "Главного авантюриста «Золотого телёнка» зовут ЭТИМ.", "answer": "Остап Бендер", "logic": "Персонаж."},
        ],
    },
    {
        "id": "crimea-trolleybus",
        "message_id": -999900491,
        "text": "длиинная троллейбусная линия — ялта — симферополь",
        "tags": ["text-only", "term"],
        "cards": [
            {"question": "Самую длинную междугороднюю троллейбусную линию в мире проложили между Симферополем и Ялтой — её называют ЭТИМ.", "answer": "Крымский троллейбус", "logic": "География из сообщения."},
        ],
    },
    {
        "id": "winterhalder-ski-lift",
        "message_id": 5289,
        "text": "Роберт Винтерхальдер —изобрел горнолыжный подъемник",
        "tags": ["text-only", "person"],
        "cards": [
            {"question": "Ранний горнолыжный подъёмник запатентовал ОН.", "answer": "Роберт Винтерхальдер", "logic": "Полное имя в ответе."},
        ],
    },
]


def main():
    out = Path(__file__).parent
    payload = {"examples": [{k: v for k, v in ex.items() if k != "message_id"} for ex in EXAMPLES]}
    (out / "parsing-examples-cursor.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = []
    total_cards = 0
    for ex in EXAMPLES:
        lines.append(f"===== {ex['id']} =====")
        lines.append("TEXT:")
        lines.append(ex["text"])
        lines.append("")
        lines.append(f"MESSAGE_ID: {ex['message_id']}")
        lines.append("")
        if ex.get("tags"):
            lines.append("TAGS: " + ", ".join(ex["tags"]))
            lines.append("")
        lines.append("CARDS:")
        for i, card in enumerate(ex["cards"], 1):
            total_cards += 1
            lines.append(f"[{i}]")
            lines.append("Q: " + card["question"])
            lines.append("A: " + card["answer"])
            if card.get("logic"):
                lines.append("LOGIC: " + card["logic"])
            lines.append("")
        lines.append("---")
        lines.append("")
    (out / "parsing-examples-cursor.txt").write_text("\n".join(lines), encoding="utf-8")

    readme = f"""# Cursor batch run-005

**50** случайных Telegram-сообщений из `result.json` (seed=42, без run-001…004 и golden).

Правила: [`hermes/quizlet-rules.md`](../../hermes/quizlet-rules.md) (примеры 1–10).

## Статистика

- **50** examples, **{total_cards}** cards
- Источник: [`candidates.json`](candidates.json), [`extract_candidates.py`](extract_candidates.py)

## Файлы

| Файл | Описание |
|------|----------|
| `parsing-examples-cursor.json` | 50 examples |
| `parsing-examples-cursor.txt` | Человекочитаемый вид + message_id |
| `build_output.py` | Скрипт сборки |

Сравнение с [`run-004`](../run-004/) — тот же стиль ЧГК, но новые сообщения и больший объём.
"""
    (out / "README.md").write_text(readme, encoding="utf-8")
    print(f"examples: {len(EXAMPLES)}, cards: {total_cards}")


if __name__ == "__main__":
    main()
