from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from general_utils.constants import GENDER_CHOICES
from tgbot.handlers.contract import manage_data


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=GENDER_CHOICES[0][1] + '🤵‍♂️️',
                             callback_data=GENDER_CHOICES[0][0]),
        InlineKeyboardButton(text=GENDER_CHOICES[1][1] + '️👩️️️',
                             callback_data=GENDER_CHOICES[1][0])
    ]]

    return InlineKeyboardMarkup(buttons)


def get_photo_cntrct_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text='⬆️ Загрузить фотографии машины 📷',
                callback_data=manage_data.SEND_PHOTOS_CAR_CONTRACT)
        ],
        [
            InlineKeyboardButton(
                text='⬇️ Скачать договор 📝',
                callback_data=manage_data.DOWNLOAD_CONTRACT_FILE)
        ],
        [
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_contract_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text='⬇️ Скачать фотографии машины 📷️',
                callback_data=manage_data.DOWNLOAD_CONTRACT_PHOTOS)
        ],
        [
            InlineKeyboardButton(
                text='⬇️ Скачать договор 📝',
                callback_data=manage_data.DOWNLOAD_CONTRACT_FILE)
        ],
        [
            InlineKeyboardButton(
                text='🚘 Информация о машине 🚘',
                callback_data=manage_data.GET_INFO_ABOUT_MY_CAR,
            )
        ],
        [
            InlineKeyboardButton(
                text='🚔 Мои штрафы 🚔',
                callback_data=manage_data.MY_FINES_MENU,
            )
        ],
        [
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_my_fines_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text='🚔 Все штрафы',
                                 callback_data=manage_data.MY_ALL_FINES)
        ],
        [
            InlineKeyboardButton(text='✅ Оплаченные штрафы',
                                 callback_data=manage_data.MY_PAID_FINES)
        ],
        [
            InlineKeyboardButton(text='❓ Неоплаченные штрафы',
                                 callback_data=manage_data.MY_UNPAID_FINES)
        ],
        [
            InlineKeyboardButton('Назад ⬅️',
                                 callback_data=manage_data.TO_MAIN_MENU)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_pd_accept_decline_keyboard():
    buttons = [[
        InlineKeyboardButton(text='Договор ✅',
                             callback_data=manage_data.CORRECT),
        InlineKeyboardButton(text='Ошибка ❌',
                             callback_data=manage_data.WRONG)
    ]]

    return InlineKeyboardMarkup(buttons)
