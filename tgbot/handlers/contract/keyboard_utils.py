from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from general_utils.constants import GENDER_CHOICES


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=value, callback_data=key) for key, value in
        GENDER_CHOICES
    ]]

    return InlineKeyboardMarkup(buttons)


def get_keyboard_for_address_similar():
    buttons = [[
        InlineKeyboardButton(text='Совпадает', callback_data='similar_addr'),
        InlineKeyboardButton(text='Другой', callback_data='diff_addr'),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_keyboard_for_send_contract():
    buttons = [[
        InlineKeyboardButton(text='Скачать договор', callback_data='download')
    ]]

    return InlineKeyboardMarkup(buttons)
