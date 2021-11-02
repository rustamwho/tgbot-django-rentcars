from datetime import timedelta
from typing import Callable

from django.utils.timezone import now

from telegram import ParseMode, Update, error
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from general_utils.utils import get_verbose_date

from tgbot.handlers.admin import (static_text, utils, keyboard_utils,
                                  manage_data)
from tgbot.models import User

from rentcars.models import Contract, PersonalData, Car, Fine

FINE_DATE, FINE_AMOUNT = range(1, 3)


def admin_only_handler(func: Callable):
    def wrapper(update: Update, context: CallbackContext):
        u = User.get_user(update, context)
        if u.is_admin:
            return func(update, context)
        else:
            update.message.reply_text(static_text.only_for_admins)
            return

    return wrapper


@admin_only_handler
def admin_start(update: Update, context) -> None:
    """ Show help info about all secret admins commands """
    update.message.reply_text(
        text=static_text.ADMIN_MENU_BASE,
        reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
    )


@admin_only_handler
def admin_menu_handler(update: Update, context) -> None:
    query = update.callback_query
    data = query.data

    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == manage_data.BASE_ADMIN_MENU:
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
        )
    elif data == manage_data.CARS_MENU:
        all_cars_count = Car.objects.count()
        # Very slow because cars count little
        # (may update to search with contracts)
        rented_cars_count = len(Car.get_busy_cars())
        query.edit_message_text(
            text=static_text.COUNT_CARS.format(
                all_cars_count=all_cars_count,
                rented_cars_count=rented_cars_count),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_cars_menu_keyboard(),
        )
    # Menu with free cars for setting car to current contract
    elif data.startswith(manage_data.SET_CAR_TO_CONTRACT_MENU):
        contract_id = int(data.split('_')[-1])

        Contract.objects.filter(id=contract_id).update(car=None)
        if 'Назначена машина' in current_text:
            current_text = (current_text.split('\n\n')[0] +
                            '\n\n❗Машина не назначена')

        free_cars = [car for car in Car.objects.all() if car.is_busy is False]
        if not free_cars:
            query.edit_message_text(
                text=current_text + '\n\n✖️Нет свободных машин✖️'
            )
            return

        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_set_car_to_contract_keyboard(
                contract_id, free_cars
            )
        )
    elif data == manage_data.FINES_MENU:
        all_fines_count = Fine.objects.count()
        unpaid_fines_count = Fine.objects.filter(is_paid=False).count()
        query.edit_message_text(
            text=static_text.COUNT_FINES.format(
                all_fines_count=all_fines_count,
                unpaid_fines_count=unpaid_fines_count),
            reply_markup=keyboard_utils.get_fines_menu_keyboard()
        )
    elif data == manage_data.ADD_NEW_FINE_MENU:
        all_cars = Car.objects.all()
        query.edit_message_text(
            text='Выберите машину для добавления штрафа',
            reply_markup=keyboard_utils.get_add_new_fine_menu(all_cars)
        )
    elif data == manage_data.SET_FINE_IS_PAID_MENU:
        unpaid_fines = Fine.objects.filter(is_paid=False)
        query.edit_message_text(
            text='Выберите штраф, который будет отмечен оплаченным',
            reply_markup=keyboard_utils.get_set_fine_is_paid_keyboard(
                unpaid_fines)
        )
    elif data == manage_data.BACK:
        query.edit_message_reply_markup(
            keyboard_utils.get_admin_main_menu_keyboard()
        )
    elif data == manage_data.REMOVE_KEYBOARD:
        query.edit_message_text(
            text=current_text,
        )
    elif data == manage_data.DELETE_MESSAGE:
        query.delete_message()


@admin_only_handler
def stats(update: Update, context) -> None:
    """ Show help info about all secret admins commands """
    text = static_text.users_amount_stat.format(
        user_count=User.objects.count(),
        # count may be ineffective if there are a lot of users.
        active_24=User.objects.filter(
            updated_at__gte=now() - timedelta(hours=24)).count()
    )
    update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@admin_only_handler
def export_users(update: Update, context) -> None:
    # in values argument you can specify which fields should be returned in output csv
    users = User.objects.all().values()
    csv_users = utils._get_csv_from_qs_values(users)
    context.bot.send_document(chat_id=update.message.chat_id,
                              document=csv_users)


def send_unapproved_contracts(admin_id: int,
                              context: CallbackContext) -> None:
    """
    Send to admin with receiving admin_id all unapproved contracts with
    keyboard for approving.
    """
    unapproved_contracts = Contract.objects.filter(is_approved=False)
    for unapproved_contract in unapproved_contracts:
        is_car_exists = unapproved_contract.car is not None
        keyboard = keyboard_utils.get_approve_contract_keyboard(
            unapproved_contract.id, is_car_exists
        )
        arendator_pd: PersonalData = unapproved_contract.user.personal_data
        arendator_full_name = (f'{arendator_pd.last_name} '
                               f'{arendator_pd.first_name} '
                               f'{arendator_pd.last_name}')
        created_at = get_verbose_date(unapproved_contract.created_at)
        closed_at = get_verbose_date(unapproved_contract.closed_at)
        text = static_text.TEXT_FOR_APPROVE_CONTRACT.format(
            name_arendator=arendator_full_name,
            created_at=created_at,
            closed_at=closed_at,
        )
        if is_car_exists:
            text += (f'\n\nНазначена машина: '
                     f'{unapproved_contract.car.license_plate}')
        else:
            text += '\n\n❗Машина не назначена'
        context.bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )


@admin_only_handler
def admin_commands_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = query.data

    chat_id = update.effective_message.chat_id
    current_text = update.effective_message.text

    if data == manage_data.GET_ALL_USERS:
        text = utils.get_text_all_users()
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
        )
    elif data == manage_data.GET_ARENDATORS:
        text = utils.get_text_all_arendators()
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
        )
    elif data == manage_data.GET_UNAPPROVED_CONTRACTS:
        unapproved = Contract.objects.filter(is_approved=False).exists()
        # If unapproved contracts exists, send contracts for approve
        if unapproved:
            query.edit_message_text(
                text=static_text.NOW_SEND_UNAPPROVED_CONTRACTS
            )
            send_unapproved_contracts(chat_id, context)
        else:
            try:
                query.edit_message_text(
                    text=static_text.UNAPPROVED_CONTACTS_NOT_EXISTS,
                    reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
                )
            except error.BadRequest:
                return
    # Approving contract
    elif data.startswith(manage_data.BASE_FOR_APPROVE_CONTRACT):
        contract_id = int(data.split('_')[-1])
        current_contract = Contract.objects.get(id=contract_id)
        current_contract.is_approved = True
        current_contract.approved_at = now().date()
        current_contract.save()

        query.edit_message_text(
            text=current_text + static_text.CONTRACT_IS_APPROVED
        )
    # Set car to contract
    elif data.startswith(manage_data.BASE_FOR_SET_CAR_TO_CONTRACT):
        contract_id, car_id = (int(x) for x in data.split('_')[-2:])
        current_contract = Contract.objects.get(id=contract_id)
        current_car = Car.objects.get(id=car_id)
        current_contract.car = current_car
        current_contract.save()

        current_text = current_text.replace('\n\n❗Машина не назначена', '')
        query.edit_message_text(
            text=(current_text +
                  f'\n\nНазначена машина: {current_car.license_plate}'),
            reply_markup=keyboard_utils.get_approve_contract_keyboard(
                contract_id=contract_id)
        )
    elif data == manage_data.GET_ALL_CARS:
        all_cars = Car.objects.all()
        text = '<b>Все автомобили:</b>\n\n'
        for i, car in enumerate(all_cars, 1):
            text += f'<b>{i}</b>. {car.license_plate}\t{car.model}.\n'
        if text == current_text:
            text += '\nНичего не поменялось.'
        try:
            query.edit_message_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard_utils.get_cars_menu_keyboard(),
            )
        except error.BadRequest:
            return
    elif data == manage_data.GET_RENTED_CARS:
        all_rented_cars = Car.get_busy_cars()

        if not all_rented_cars:
            text = 'Арендованных машин нет'
        else:
            text = '<b>Арендованные автомобили:</b>\n\n'
            for i, car in enumerate(all_rented_cars, 1):
                text += f'<b>{i}.</b> {car.license_plate}\t{car.model}.\n'

        try:
            query.edit_message_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard_utils.get_cars_menu_keyboard(),
            )
        except error.BadRequest:
            return
    elif data == manage_data.GET_ALL_FINES:
        try:
            query.edit_message_text(
                text=utils.get_text_all_fines(),
                reply_markup=keyboard_utils.get_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data == manage_data.GET_PAID_FINES:
        try:
            query.edit_message_text(
                text=utils.get_text_paid_fines(),
                reply_markup=keyboard_utils.get_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data == manage_data.GET_UNPAID_FINES:
        try:
            query.edit_message_text(
                text=utils.get_text_unpaid_fines(),
                reply_markup=keyboard_utils.get_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data.startswith(manage_data.BASE_FOR_SET_FINE_IS_PAID):
        fine_id = int(data.split('_')[-1])
        fine = Fine.objects.get(id=fine_id)
        fine.is_paid = True
        fine.save()

        text = (f'Штраф:\n'
                f'{fine.car.license_plate[:-3]} - {fine.amount} руб. '
                f'{get_verbose_date(fine.date)}\n\n'
                f'✅ Оплачен ✅')
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_fines_menu_keyboard()
        )
    elif data.startswith(manage_data.BASE_FOR_ADD_NEW_FINE):
        car_id = int(data.split('_')[-1])
        car = Car.objects.get(id=car_id)
        context.user_data['car'] = car
        query.edit_message_text(
            text=f'Выбрана машина:\n{car.license_plate}\n\nВведите дату'
        )

        return FINE_DATE


def fine_date_handler(update: Update, context: CallbackContext):
    input_date = update.message.text
    # TODO: Добавить общение с юзером по поводу добавления штрафа
    # Машина уже в context.user_data
    print(context.user_data['car'].model)


def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /contract')
    return ConversationHandler.END


def get_conversation_handler_for_fine():
    """Return Conversation handler for /contract"""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_commands_handler,
                pattern=f'^{manage_data.BASE_FOR_ADD_NEW_FINE}', pass_user_data=True),
        ],
        states={
            FINE_DATE: [
                MessageHandler(Filters.text, fine_date_handler)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
