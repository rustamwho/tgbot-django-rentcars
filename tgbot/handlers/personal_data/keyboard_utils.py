from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.personal_data import manage_data

from general_utils.constants import GENDER_CHOICES


def get_start_initialization_pd_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Заполнить 🛠',
                callback_data=manage_data.START_INITIALIZATION_PD),
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_keyboard_for_address_similar():
    buttons = [[
        InlineKeyboardButton(text='Совпадает', callback_data='similar_addr'),
        InlineKeyboardButton(text='Другой', callback_data='diff_addr'),
    ]]

    return InlineKeyboardMarkup(buttons)


def get_pd_accept_decline_keyboard():
    buttons = [[
        InlineKeyboardButton(text='Верно ✅',
                             callback_data=manage_data.CORRECT),
        InlineKeyboardButton(text='Ошибка ❌',
                             callback_data=manage_data.WRONG)
    ]]

    return InlineKeyboardMarkup(buttons)


def get_keyboard_for_gender():
    buttons = [[
        InlineKeyboardButton(text=GENDER_CHOICES[0][1] + '🤵‍♂️️',
                             callback_data=GENDER_CHOICES[0][0]),
        InlineKeyboardButton(text=GENDER_CHOICES[1][1] + '️👩️️️',
                             callback_data=GENDER_CHOICES[1][0])

    ]]

    return InlineKeyboardMarkup(buttons)


def get_personal_data_edit_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Редактировать 🛠',
                                 callback_data=manage_data.MENU_EDIT_PD_MAIN),
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def get_all_types_pd_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Личные данные 👤',
                                 callback_data=manage_data.MENU_EDIT_PD_PD),
            InlineKeyboardButton('Контакты 🗂',
                                 callback_data=manage_data.MENU_EDIT_CONTACTS)
        ],
        [
            InlineKeyboardButton('Паспорт 📙',
                                 callback_data=manage_data.MENU_EDIT_PASSPORT),
            InlineKeyboardButton('Близкий человек 🫂',
                                 callback_data=manage_data.MENU_EDIT_CLOSE_PERSON)
        ],
        [
            InlineKeyboardButton('Закрыть ❌',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_pd_pd_keyboard():
    buttons = [
        [
            InlineKeyboardButton('Фамилия 📝',
                                 callback_data=manage_data.EDIT_PD_LAST_NAME),
            InlineKeyboardButton('Имя 📝',
                                 callback_data=manage_data.EDIT_PD_FIRST_NAME)
        ],
        [
            InlineKeyboardButton(
                'Отчество 📝', callback_data=manage_data.EDIT_PD_MIDDLE_NAME),
            InlineKeyboardButton('Пол 🙎‍♂️🙍‍♀️',
                                 callback_data=manage_data.EDIT_PD_GENDER)
        ],
        [
            InlineKeyboardButton('Дата рождения 🎂',
                                 callback_data=manage_data.EDIT_PD_BIRTHDAY)
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_pd_contacts_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Номер телефона 📞',
                callback_data=manage_data.EDIT_PD_PHONE_NUMBER),
            InlineKeyboardButton('Почта 📧',
                                 callback_data=manage_data.EDIT_PD_EMAIL)
        ],
        [
            InlineKeyboardButton(
                'Прописка 📬',
                callback_data=manage_data.EDIT_PD_ADDRESS_REGISTRATION),
            InlineKeyboardButton(
                'Место жительства 📬',
                callback_data=manage_data.EDIT_PD_ADDRESS_RESIDENCE)
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_pd_passport_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Серия *️⃣',
                callback_data=manage_data.EDIT_PD_PASSPORT_SERIAL),
            InlineKeyboardButton(
                'Номер #️⃣',
                callback_data=manage_data.EDIT_PD_PASSPORT_NUMBER)
        ],
        [
            InlineKeyboardButton(
                'Кем выдан 📑',
                callback_data=manage_data.EDIT_PD_PASSPORT_ISSUED_BY),
            InlineKeyboardButton(
                'Когда выдан 📅',
                callback_data=manage_data.EDIT_PD_PASSPORT_ISSUED_AT)
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_pd_close_person_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Имя 📝',
                callback_data=manage_data.EDIT_PD_CLOSE_PERSON_NAME),
            InlineKeyboardButton(
                'Номер телефона 📞',
                callback_data=manage_data.EDIT_PD_CLOSE_PERSON_PHONE)
        ],
        [
            InlineKeyboardButton(
                'Адрес 📬',
                callback_data=manage_data.EDIT_PD_CLOSE_PERSON_ADDRESS)
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_exist_active_contract_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                'Номер телефона 📞',
                callback_data=manage_data.EDIT_PD_PHONE_NUMBER),
            InlineKeyboardButton('Почта 📧',
                                 callback_data=manage_data.EDIT_PD_EMAIL)
        ],
        [
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)
