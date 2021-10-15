from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.admin import manage_data


def get_admin_main_keyboard():
    buttons = [[
        InlineKeyboardButton('Получить список всех пользователей',
                             callback_data=manage_data.GET_ALL_USERS)
    ]]

    return InlineKeyboardMarkup(buttons)
