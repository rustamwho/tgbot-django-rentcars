from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from rentcars.models import Car
from tgbot.handlers.admin import manage_data


def get_admin_main_menu_keyboard():
    buttons = [
        [
            InlineKeyboardButton('👥 Все пользователи 👥',
                                 callback_data=manage_data.GET_ALL_USERS),
            InlineKeyboardButton('👥 Арендаторы 📝',
                                 callback_data=manage_data.GET_ARENDATORS)
        ],
        [
            InlineKeyboardButton('🚘 Таксопарк 🚘',
                                 callback_data=manage_data.CARS_MENU)
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
