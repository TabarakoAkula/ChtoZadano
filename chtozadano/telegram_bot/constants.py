import os

from aiogram import html
import dotenv

dotenv.load_dotenv()

DOMAIN_URL = os.getenv("DOMAIN_URL")
DOCKER_URL = os.getenv("DOCKER_URL")
MENU_MESSAGES = [
    "Какой сегодня чудный день🔮",
    f"″Мы все учились понемногу чему-нибудь и как-нибудь.″\n"
    f"- {html.italic('Александр Сергеевич Пушкин')}",
    f"″Учение — только свет, по народной пословице, — оно также и свобода."
    f" Ничто так не освобождает человека, как знание.″\n"
    f"- {html.italic('Иван Сергеевич Тургенев')}",
    f"″Чему бы ты ни учился, ты учишься для себя.″\n"
    f"- {html.italic('Петроний Арбитр Гай')}",
    f"″В учении нельзя останавливаться.″\n- {html.italic('Сюнь-цзы')}",
    f"″Самостоятельность головы учащегося — единственное прочное основание"
    f" всякого плодотворного учения.″\n"
    f"- {html.italic('Константин Дмитриевич Ушинский')}",
    f"″Кто ни о чем не спрашивает, тот ничему не научится.″\n"
    f"- {html.italic('Томас Фуллер')}",
    f"″Надо много учиться, чтобы знать хоть немного.″\n"
    f"- {html.italic('Шарль Луи Монтескье')}",
    f"″Тот, кто не желает учиться, — никогда не станет настоящим человеком.″\n"
    f"- {html.italic('Хосе Хулиан Марти')}",
    f"″Ученье свет, а неученье — тьма. Дело мастера боится.″\n"
    f"- {html.italic('Александр Васильевич Суворов')}",
    f"″Ни искусство, ни мудрость не могут быть достигнуты,"
    f" если им не учиться.″\n"
    f"- {html.italic('Демокрит')}",
    f"″Надо много учиться, чтобы осознать, что знаешь мало.″\n"
    f"- {html.italic('Мишель де Монтень')}",
    f"″Пока учишься чему-то новому, стареть не так мучительно.″\n"
    f"- {html.italic('Харуки Мураками')}",
    f"″Только тот, кто делает, чему-то научится.″\n"
    f"- {html.italic('Брюс Ли')}",
    f"″Никто не заставит тебя учиться. Учиться ты будешь тогда,"
    f" когда захочешь этого.″\n"
    f"- {html.italic('Ричард Бах')}",
    f"″Учитесь у всех — не подражайте никому.″\n"
    f"- {html.italic('Максим Горький')}",
    f"″Чем больше сразу учишься, тем меньше после мучишься.″\n"
    f"- {html.italic('Льюис Кэрролл')}",
    f"″Не бойся, что не знаешь — бойся, что не учишься.″\n"
    f"- {html.italic('Китайские пословицы и поговорки')}",
    f"″В школе нельзя всему научиться — нужно научиться учиться.″\n"
    f"- {html.italic('Всеволод Мейерхольд')}",
    f"″Учение без размышления бесполезно,"
    f" но и размышление без учения опасно.″\n"
    f"- {html.italic('Конфуций')}",
    f"″Ученик, который учится без желания — это птица без крыльев.″\n"
    f"- {html.italic('Саади')}",
]

WEEK_DAYS = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
}

SUBJECTS = {
    "русский язык": "rus",
    "русский": "rus",
    "математика": "math",
    "матем": "math",
    "литература": "lit",
    "литра": "lit",
    "окружающий мир": "okr",
    "окружающий": "okr",
    "окружайка": "okr",
    "английский язык": "eng",
    "английский": "eng",
    "англ": "eng",
    "немецкий язык": "ger",
    "немецкий": "ger",
    "география": "geog",
    "история": "hist",
    "ист": "hist",
    "обществознание": "soc",
    "общество": "soc",
    "общага": "soc",
    "право": "law",
    "естествознание": "nat",
    "биология": "bio",
    "био": "bio",
    "алгебра": "alg",
    "алг": "alg",
    "вероятность и статистика": "stat",
    "вероятность": "stat",
    "статистика": "stat",
    "экономка": "eco",
    "геометрия": "geom",
    "геом": "geom",
    "геома": "geom",
    "астрономия": "ast",
    "физика": "phys",
    "физ": "phys",
    "химия": "chem",
    "хим": "chem",
    "индивидуальный проект": "proj",
    "проект": "proj",
    "информатика": "ikt",
    "инф": "ikt",
    "изо": "izo",
    "музыка": "mus",
    "технология": "tech",
    "обж": "obg",
    "орксэ": "ork",
    "однкнр": "odn",
    "информация": "info",
    "классный": "class",
    "классный час": "class",
    "физкультура": "phys-c",
    "физра": "phys-c",
}
