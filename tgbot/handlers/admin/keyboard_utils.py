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
            InlineKeyboardButton(
                'Неподтвержденные договоры',
                callback_data=manage_data.GET_UNAPPROVED_CONTRACTS)
        ],
        [
            InlineKeyboardButton('Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_approve_contract_keyboard(contract_id: int):
    buttons = [[
        InlineKeyboardButton(
            'Подтвердить ✅',
            callback_data=(
                    manage_data.BASE_FOR_APPROVE_CONTRACT + str(contract_id))),
        InlineKeyboardButton('Потом',
                             callback_data=manage_data.DELETE_MESSAGE)

    ]]

    return InlineKeyboardMarkup(buttons)
