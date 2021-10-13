from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.personal_data import manage_data

from general_utils.constants import GENDER_CHOICES


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=value, callback_data=key) for key, value in
        GENDER_CHOICES
    ]]

    return InlineKeyboardMarkup(buttons)


def get_personal_data_edit_keyboard():
    button = [[
        InlineKeyboardButton('Отредактировать',
                             callback_data=manage_data.MENU_EDIT_PD_MAIN)
    ]]

    return InlineKeyboardMarkup(button)


def get_all_types_pd_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Личные данные',
                                 callback_data=manage_data.MENU_EDIT_PD_PD),
            InlineKeyboardButton('Контакты',
                                 callback_data=manage_data.MENU_EDIT_CONTACTS)
        ],
        [
            InlineKeyboardButton('Паспорт',
                                 callback_data=manage_data.MENU_EDIT_PASSPORT),
            InlineKeyboardButton('Близкий человек',
                                 callback_data=manage_data.MENU_EDIT_CLOSE_PERSON)
        ],
        [
            InlineKeyboardButton('Закрыть',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_pd_pd_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Фамилия',
                                 callback_data=manage_data.EDIT_PD_LAST_NAME),
            InlineKeyboardButton('Имя',
                                 callback_data=manage_data.EDIT_PD_FIRST_NAME)
        ],
        [
            InlineKeyboardButton(
                'Отчество', callback_data=manage_data.EDIT_PD_MIDDLE_NAME),
            InlineKeyboardButton('Пол',
                                 callback_data=manage_data.EDIT_PD_GENDER)
        ],
        [
            InlineKeyboardButton('Дата рождения',
                                 callback_data=manage_data.EDIT_PD_BIRTHDAY)
        ],
        [
            InlineKeyboardButton('Назад', callback_data=manage_data.BACK)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_pd_contacts_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Номер телефона',
                callback_data=manage_data.EDIT_PD_PHONE_NUMBER),
            InlineKeyboardButton('Почта',
                                 callback_data=manage_data.EDIT_PD_EMAIL)
        ],
        [
            InlineKeyboardButton(
                'Адрес прописки',
                callback_data=manage_data.EDIT_PD_ADDRESS_REGISTRATION),
            InlineKeyboardButton(
                'Адрес проживания',
                callback_data=manage_data.EDIT_PD_ADDRESS_RESIDENCE)
        ],
        [
            InlineKeyboardButton('Назад', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)

# TODO: Keyboard для паспорта
# TODO: Keyboard для близкого человека
