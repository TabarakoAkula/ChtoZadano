from aiogram.filters import StateFilter
from bot_utils.states import Account, Schedule, Settings

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

SettingsStateFilter = StateFilter(
    Settings.start,
    Settings.change_quotes,
    Settings.change_chat_mode,
)
