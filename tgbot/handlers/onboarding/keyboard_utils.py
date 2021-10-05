from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import author_button_text, secret_level_button_text


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        InlineKeyboardButton(author_button_text, url="https://t.me/rustamwho"),
        InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}')
    ]]

    return InlineKeyboardMarkup(buttons)
