from itertools import zip_longest

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from rentcars.models import Car, Fine
from tgbot.handlers.admin import manage_data
from general_utils.utils import get_verbose_date


def get_admin_main_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton('👥 Все юзеры 👥',
                                 callback_data=manage_data.GET_ALL_USERS),
            InlineKeyboardButton('👥 Арендаторы 📝',
                                 callback_data=manage_data.GET_ARENDATORS)
        ],
        [
            InlineKeyboardButton('🚘 Таксопарк 🚘',
                                 callback_data=manage_data.CARS_MENU)
        ],
        [
            InlineKeyboardButton('🚔 Штрафы 🚔',
                                 callback_data=manage_data.FINES_MENU)
        ],
        [
            InlineKeyboardButton(
                '❓Неподтвержденные договоры❓',
                callback_data=manage_data.GET_UNAPPROVED_CONTRACTS)
        ],
        [
            InlineKeyboardButton('✅ Закрыть ✅',
                                 callback_data=manage_data.REMOVE_KEYBOARD)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_set_car_to_contract_keyboard(contract_id: int, free_cars: list[Car]):
    """
    Get keyboard with buttons with
    callback data = BASE_FOR_SET_CAR_TO_CONTRACT_contractId_carId
    """
    buttons = [
        [
            InlineKeyboardButton(
                f'🚘 {car.license_plate} {car.model}',
                callback_data=(
                        manage_data.BASE_FOR_SET_CAR_TO_CONTRACT +
                        str(contract_id) + '_' + str(car.id)
                )
            )
        ]
        for car in free_cars
    ]

    buttons.append(
        [InlineKeyboardButton('Потом ↩️',
                              callback_data=manage_data.DELETE_MESSAGE)]
    )

    return InlineKeyboardMarkup(buttons)


def get_approve_contract_keyboard(contract_id: int,
                                  is_car_exists: bool = True):
    """
    If car of contract does not exists - return button for menu setting car
    Else return button for approving contract
    """
    if is_car_exists is True:
        buttons = [
            [
                InlineKeyboardButton(
                    'Подтвердить ✅',
                    callback_data=(
                            manage_data.BASE_FOR_APPROVE_CONTRACT +
                            str(contract_id))),
                InlineKeyboardButton(
                    'Изменить 🚘',
                    callback_data=(
                            manage_data.SET_CAR_TO_CONTRACT_MENU +
                            str(contract_id))),
            ],
            [
                InlineKeyboardButton('Потом ↩️',
                                     callback_data=manage_data.DELETE_MESSAGE)
            ]
        ]
    else:
        buttons = [[
            InlineKeyboardButton(
                'Назначить 🚘',
                callback_data=(
                        manage_data.SET_CAR_TO_CONTRACT_MENU +
                        str(contract_id))),
            InlineKeyboardButton('Потом ↩️',
                                 callback_data=manage_data.DELETE_MESSAGE)
        ]]

    return InlineKeyboardMarkup(buttons)


def get_cars_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton('🚘 Все машины 🚘',
                                 callback_data=manage_data.GET_ALL_CARS)
        ],
        [
            InlineKeyboardButton('🚘 Арендованные машины 🔒',
                                 callback_data=manage_data.GET_RENTED_CARS)
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_fines_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton('🚔 Все штрафы',
                                 callback_data=manage_data.GET_ALL_FINES),
        ],
        [
            InlineKeyboardButton('✅ Оплаченные штрафы',
                                 callback_data=manage_data.GET_PAID_FINES),
        ],
        [
            InlineKeyboardButton('❓Неоплаченные штрафы',
                                 callback_data=manage_data.GET_UNPAID_FINES),
        ],
        [
            InlineKeyboardButton('➕ Добавить новый штраф',
                                 callback_data=manage_data.ADD_NEW_FINE_MENU),
        ],
        [
            InlineKeyboardButton(
                '✔️ Отметить оплаченный',
                callback_data=manage_data.SET_FINE_IS_PAID_MENU),
        ],
        [
            InlineKeyboardButton('Назад ⬅️', callback_data=manage_data.BACK)
        ]
    ]

    return InlineKeyboardMarkup(buttons)


def get_add_new_fine_menu(all_cars: list[Car]):
    buttons = []
    for car1, car2, car3 in zip_longest(all_cars[::3], all_cars[1::3],
                                        all_cars[2::3]):
        subbuttons = []
        if car1:
            subbuttons.append(
                InlineKeyboardButton(
                    f'🚘 {car1.license_plate[:-3]}',
                    callback_data=(manage_data.BASE_FOR_ADD_NEW_FINE +
                                   str(car1.id)))
            )
        if car2:
            subbuttons.append(
                InlineKeyboardButton(
                    f'🚘 {car2.license_plate[:-3]}',
                    callback_data=(manage_data.BASE_FOR_ADD_NEW_FINE +
                                   str(car2.id)))
            )
        if car3:
            subbuttons.append(
                InlineKeyboardButton(
                    f'🚘 {car3.license_plate[:-3]}',
                    callback_data=(manage_data.BASE_FOR_ADD_NEW_FINE +
                                   str(car3.id)))
            )
        buttons.append(subbuttons)

    buttons.append([
        InlineKeyboardButton('Назад ⬅️',
                             callback_data=manage_data.FINES_MENU)
    ])

    return InlineKeyboardMarkup(buttons)


def get_set_fine_is_paid_keyboard(unpaid_fines: list[Fine]):
    buttons = [
        [
            InlineKeyboardButton(
                f'🚔 {fine.car.license_plate[:-3]} - '
                f'{fine.amount} руб. {get_verbose_date(fine.date)}',
                callback_data=(manage_data.BASE_FOR_SET_FINE_IS_PAID +
                               str(fine.id))
            )
        ]
        for fine in unpaid_fines
    ]
    buttons.append([
        InlineKeyboardButton('Назад ⬅️',
                             callback_data=manage_data.FINES_MENU)
    ])
    return InlineKeyboardMarkup(buttons)
