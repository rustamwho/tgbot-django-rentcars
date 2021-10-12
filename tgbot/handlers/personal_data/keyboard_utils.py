from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_personal_data_edit_keyboard():
    button = [[
        InlineKeyboardButton('Отредактировать', callback_data='EDIT_PD')
    ]]

    return InlineKeyboardMarkup(button)
