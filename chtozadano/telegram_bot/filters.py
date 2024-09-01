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
    AddHomeworkFast.add_data,
)

AddHomeworkFastDescriptionStateFilter = StateFilter(
    AddHomeworkFast.add_descriptions_images,
    AddHomeworkFast.add_data,
)

AddHomeworkSlowStateFilter = StateFilter(
    AddHomeworkSlow.choose_subject,
    AddHomeworkSlow.add_files,
)

PublishHomeworkStateFilter = StateFilter(
    AddHomeworkSlow.add_descriptions_images,
    AddHomeworkSlow.add_files,
)

EditHomeworkStateFilter = StateFilter(
    EditHomework.start,
    EditHomework.edit_text,
)

AddHwChooseSubjectStateFilter = StateFilter(
    AddHomeworkSlow.choose_subject,
    AddHomeworkFast.choose_subject,
)

StopAddHomeworkStateFilter = StateFilter(
    AddHomeworkFast.add_data,
    AddHomeworkFast.add_descriptions_images,
    AddHomeworkFast.choose_subject,
    AddHomeworkSlow.add_files,
    AddHomeworkSlow.add_descriptions_images,
    AddHomeworkSlow.choose_subject,
)
