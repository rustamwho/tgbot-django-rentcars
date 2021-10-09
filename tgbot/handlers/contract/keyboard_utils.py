from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from general_utils.constants import GENDER_CHOICES


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=value, callback_data=key) for key, value in
        GENDER_CHOICES
    ]]

    return InlineKeyboardMarkup(buttons)
