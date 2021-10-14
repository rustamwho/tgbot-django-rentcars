from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from general_utils.constants import GENDER_CHOICES
from tgbot.handlers.contract.manage_data import DOWNLOAD_CONTRACT


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=GENDER_CHOICES[0][1] + '🤵‍♂️️',
                             callback_data=GENDER_CHOICES[0][0]),
        InlineKeyboardButton(text=GENDER_CHOICES[1][1] + '️👩️️️',
                             callback_data=GENDER_CHOICES[1][0])
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
        InlineKeyboardButton(text='Скачать договор', callback_data=DOWNLOAD_CONTRACT)
    ]]

    return InlineKeyboardMarkup(buttons)
