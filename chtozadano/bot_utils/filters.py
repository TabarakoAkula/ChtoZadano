from aiogram.filters import StateFilter
from bot_utils.states import Account, Homework, Schedule

ScheduleStateFilter = StateFilter(
    Schedule.tomorrow_schedule,
    Schedule.week_schedule,
    Schedule.start,
)

AccountStateFilter = StateFilter(
    Account.start,
    Account.change_contacts,
    Account.become_admin,
    Account.settings,
)

HomeworkStateFilter = StateFilter(
    Homework.start,
    Homework.subject,
    Homework.find,
)
