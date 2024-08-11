from aiogram.filters import StateFilter
from bot_utils.states import Schedule

ScheduleStateFilter = StateFilter(
    Schedule.tomorrow_schedule,
    Schedule.week_schedule,
    Schedule.start,
)
