from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.admin import manage_data


def get_admin_main_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Все пользователи',
                                 callback_data=manage_data.GET_ALL_USERS),
            InlineKeyboardButton('Арендаторы',
                                 callback_data=manage_data.GET_ARENDATORS)
        ],
        [
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)
