import datetime
from datetime import timedelta
from typing import Callable

from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

from telegram import ParseMode, Update, error
from telegram.error import BadRequest, Unauthorized
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from general_utils.utils import get_verbose_date

from tgbot.handlers.admin import (static_text, utils, keyboard_utils,
                                  manage_data)
from tgbot.models import User

from rentcars.models import Contract, PersonalData, Car, Fine
from rentcars import validators

CAR, FINE_DATE, FINE_TIME, FINE_AMOUNT, FINE_SCREEN = range(1, 6)


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
    elif data == manage_data.CLOSE_CONTRACT_MENU:
        active_contracts = Contract.get_active_contracts()
        query.edit_message_text(
            text=static_text.CLOSE_CONTRACT_MENU_TEXT,
            reply_markup=keyboard_utils.get_close_contract_menu_keyboard(
                active_contracts
            )
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
                               f'{arendator_pd.middle_name}')
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
        try:
            query.edit_message_text(
                text=text,
                reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data == manage_data.GET_ARENDATORS:
        text = utils.get_text_all_arendators()
        try:
            query.edit_message_text(
                text=text,
                reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
            )
        except error.BadRequest:
            return
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
        current_text = current_text.replace(
            static_text.CONTRACT_CANT_BE_APPROVED, ''
        )
        if not current_contract.car_photos.exists():
            is_car_exists = current_contract.car is not None
            keyboard = keyboard_utils.get_approve_contract_keyboard(
                current_contract.id, is_car_exists
            )
            try:
                query.edit_message_text(
                    text=current_text + static_text.CONTRACT_CANT_BE_APPROVED,
                    reply_markup=keyboard,
                )
            except error.BadRequest:
                return

            return
        current_contract.is_approved = True
        current_contract.approved_at = now()
        current_contract.closed_at = now().replace(year=now().year + 1)
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
        )

        # Create contract file and send to user and admin
        utils.create_and_save_contract_file(
            contract=current_contract,
            admin_id=chat_id,
            context=context
        )
    elif data.startswith(manage_data.BASE_FOR_DELETE_CONTRACT):
        contract_id = int(data.split('_')[-1])
        Contract.objects.get(id=contract_id).delete()
        query.edit_message_text(
            text=(current_text+'\n\n✅ Договор УДАЛЕН ✅')
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
                f'{fine.get_datetime_in_str()}\n\n'
                f'✅ Оплачен ✅')
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_fines_menu_keyboard()
        )
    # Adding new fine
    elif data.startswith(manage_data.BASE_FOR_ADD_NEW_FINE):
        car_id = int(data.split('_')[-1])
        car = Car.objects.get(id=car_id)
        context.user_data[CAR] = car
        query.edit_message_text(
            text=static_text.ASK_DATE_FINE.format(
                license_plate=car.license_plate),
            parse_mode=ParseMode.HTML,
        )

        return FINE_DATE

    # Close active contract
    elif data.startswith(manage_data.BASE_FOR_CLOSE_CONTRACT):
        contract_id = int(data.split('_')[-1])
        active_contract = Contract.objects.get(id=contract_id)
        created_at = active_contract.get_created_at_in_str()
        approved_at = active_contract.get_approved_at_in_str()
        closed_at = active_contract.get_closed_at_in_str()
        user_name = active_contract.get_full_name_user()

        if active_contract.car:
            car_name = active_contract.car.get_short_info()
        else:
            car_name = 'Машина не назначена'

        text = static_text.ABOUT_CONTRACT.format(
            user_name=user_name,
            created_at=created_at,
            approved_at=approved_at,
            car_name=car_name
        )
        text += static_text.CLOSED_AT_CONTRACT.format(closed_at=closed_at)
        text += static_text.ASK_ACCEPT_CLOSE_CONTRACT
        keyboard = keyboard_utils.get_accept_close_contract_menu_keyboard(
            active_contract
        )

        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
    elif data.startswith(manage_data.BASE_FOR_ACCEPT_CLOSE_CONTRACT):
        contract_id = int(data.split('_')[-1])
        active_contract = Contract.objects.get(id=contract_id)
        active_contract.closed_at = now()
        active_contract.save()

        text = current_text.split('Конец аренды')[0]
        text += f'Конец аренды: {active_contract.get_closed_at_in_str()}\n\n'
        text += static_text.CONTRACT_IS_CLOSED

        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
        )

        text = text.replace('❗ Договор:', '❗ Внимание ❗')
        text = text.replace('✅ Договор завершен ✅',
                            '✅ Ваш договор ЗАВЕРШЕН ✅')
        try:
            context.bot.send_message(
                chat_id=active_contract.user.user_id,
                text=text,
            )
        except Unauthorized:
            return


def fine_date_handler(update: Update, context: CallbackContext):
    input_date = update.message.text

    try:
        validators.date_validate(input_date)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return FINE_DATE

    context.user_data[FINE_DATE] = input_date

    update.message.reply_text(
        text=static_text.ASK_TIME_FINE,
        parse_mode=ParseMode.HTML,
    )

    return FINE_TIME


def fine_time_handler(update: Update, context: CallbackContext):
    input_time = update.message.text

    try:
        validators.time_validate(input_time)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return FINE_TIME

    context.user_data[FINE_TIME] = input_time

    update.message.reply_text(
        text=static_text.ASK_AMOUNT_FINE,
        parse_mode=ParseMode.HTML,
    )

    return FINE_AMOUNT


def fine_amount_handler(update: Update, context: CallbackContext):
    input_amount = update.message.text
    try:
        input_amount = int(input_amount)
    except ValueError as e:
        update.message.reply_text('Сумма штрафа должна быть ТОЛЬКО числом. '
                                  'Например, 1500.\n\nПовторите ввод')
        return FINE_AMOUNT

    context.user_data[FINE_AMOUNT] = input_amount

    update.message.reply_text(
        text=static_text.ASK_SCREENSHOT_FINE,
        parse_mode=ParseMode.HTML
    )

    return FINE_SCREEN


def fine_screenshot_handler(update: Update, context: CallbackContext):
    # Temporary file for caching image before create a PhotoCarContract obj
    img_temp = NamedTemporaryFile(delete=True)

    file = update.message.photo[-1].get_file()
    path = file.download(out=img_temp)

    img_temp.flush()

    # Create new Fine and save downloaded image in it
    new_fine = Fine(
        car=context.user_data[CAR],
        datetime=(f'{context.user_data[FINE_DATE]} '
                  f'{context.user_data[FINE_TIME]}'),
        amount=context.user_data[FINE_AMOUNT],
        screenshot=File(img_temp),
        screenshot_id=file.file_id
    )
    new_fine.save()

    text_for_admin = static_text.NEW_FINE_IS_CREATED.format(
        license_plate=new_fine.car.license_plate,
        date=new_fine.get_datetime_in_str(),
        amount=new_fine.amount,
    )

    if not new_fine.contract:
        text_for_admin += '❗В эту дату машина не была арендована'
        update.message.reply_text(
            text=text_for_admin,
        )
        return ConversationHandler.END

    is_message_to_user_sent: bool = True
    # Send info about new fine to user
    text_for_user = static_text.MESSAGE_NEW_FINE_USER.format(
        license_plate=new_fine.car.license_plate,
        date=new_fine.get_datetime_in_str(),
        amount=new_fine.amount,
    )
    try:
        # Send about fine and screenshot to user
        if new_fine.screenshot:
            screen = (new_fine.screenshot_id if new_fine.screenshot_id
                      else new_fine.screenshot)
            context.bot.send_photo(
                chat_id=new_fine.user.user_id,
                photo=screen,
                caption=text_for_user
            )
        else:
            context.bot.send_message(
                chat_id=new_fine.user.user_id,
                text=text_for_user,
            )
    except BadRequest:
        is_message_to_user_sent = False
    except Unauthorized:
        is_message_to_user_sent = False

    # Send to admin full info about user in New Fine
    user_pd = new_fine.user.personal_data
    user_name = (f'{user_pd.last_name} {user_pd.first_name[0]}.'
                 f'{user_pd.middle_name[0]}.')
    url_to_user = (f'@{new_fine.user.username}' if new_fine.user.username
                   else 'Не указан никнейм:(')
    text_for_admin += static_text.NEW_FINE_ABOUT_USER.format(
        user_name=user_name,
        url_to_user=url_to_user,
        telegram_id=new_fine.user.user_id,
        phone_number=user_pd.phone_number,
    )
    text_for_admin += (static_text.MESSAGE_TO_USER_SENT
                       if is_message_to_user_sent
                       else static_text.MESSAGE_TO_USER_NOT_SENT)
    update.message.reply_text(
        text=text_for_admin
    )

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /admin')
    return ConversationHandler.END


def get_conversation_handler_for_fine():
    """Return Conversation handler for /contract"""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                admin_commands_handler,
                pattern=f'^{manage_data.BASE_FOR_ADD_NEW_FINE}',
                pass_user_data=True),
        ],
        states={
            FINE_DATE: [
                MessageHandler(Filters.text, fine_date_handler)
            ],
            FINE_TIME: [
                MessageHandler(Filters.text, fine_time_handler)
            ],
            FINE_AMOUNT: [
                MessageHandler(Filters.text, fine_amount_handler)
            ],
            FINE_SCREEN: [
                MessageHandler(Filters.photo, fine_screenshot_handler)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
