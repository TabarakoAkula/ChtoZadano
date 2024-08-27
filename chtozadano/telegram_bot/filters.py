from aiogram.filters import StateFilter
from states import (
    Account,
    AddHomeworkFast,
    AddHomeworkSlow,
    EditHomework,
    Homework,
    Schedule,
)

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

AddHomeworkFastStateFilter = StateFilter(
    AddHomeworkFast.choose_subject,
    AddHomeworkFast.add_descriptions_images,
    AddHomeworkFast.add_files,
)

AddHomeworkSlowStateFilter = StateFilter(
    AddHomeworkSlow.choose_subject,
    AddHomeworkSlow.add_descriptions_images,
    AddHomeworkSlow.add_files,
)

PublishHomeworkStateFilter = StateFilter(
    AddHomeworkFast.add_files,
    AddHomeworkFast.add_descriptions_images,
)

EditHomeworkStateFilter = StateFilter(
    EditHomework.start,
    EditHomework.edit_text,
)
