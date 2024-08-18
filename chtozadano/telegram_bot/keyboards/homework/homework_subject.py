from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def homework_subject_in_kb(subjects: list, add: bool) -> InlineKeyboardMarkup:
    inline_list = []
    counter = 1
    temp_list = []
    last_subject = subjects[-1]
    for i in subjects:
        i = i[0].upper() + i[1:]
        if add:
            temp_list.append(
                InlineKeyboardButton(
                    text=i,
                    callback_data=f"add_hw_subject_{i}",
                ),
            )
        else:
            temp_list.append(
                InlineKeyboardButton(
                    text=i,
                    callback_data=f"homework_subject_{i}",
                ),
            )
        if counter % 2 == 0 and i != last_subject:
            inline_list.append(temp_list)
            temp_list = []
        elif i.lower() == last_subject:
            inline_list.append(temp_list)
        counter += 1
    return InlineKeyboardMarkup(inline_keyboard=inline_list)
