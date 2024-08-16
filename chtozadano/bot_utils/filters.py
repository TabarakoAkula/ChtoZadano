from aiogram.filters import StateFilter
from bot_utils.states import Account, AddHomework, Homework, Schedule

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

AddHomeworkStateFilter = StateFilter(
    AddHomework.choose_subject,
    AddHomework.add_descriptions_images,
    AddHomework.add_files,
)

PublishHomeworkStateFilter = StateFilter(
    AddHomework.add_files,
    AddHomework.add_descriptions_images,
)
