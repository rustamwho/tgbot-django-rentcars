import datetime
import io

from telegram import ParseMode, Update, error
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)
from telegram import InputMediaPhoto

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.utils.timezone import now

from general_utils.utils import get_text_about_car, get_finish_personal_data
from tgbot.models import User
from tgbot.handlers.contract import (static_text, keyboard_utils, manage_data,
                                     utils)

from rentcars.models import Contract, PhotoCarContract, Fine

ACCEPT = 'ACCEPT_PD'
GETTING_PHOTO_CAR = 'GETTING_PHOTO_CAR'


def start_contract(update: Update, context: CallbackContext) -> None:
    """When getting command /contract."""
    u = User.get_user(update, context)

    active_contract = u.get_active_contract()

    if active_contract:
        # If admin not set car into contract (Contract file not created)
        if not active_contract.file:
            update.message.reply_text(
                text=static_text.CONTRACT_NOT_EXISTS_FILE
            )
            return

        # When photos of car in contract does not exists
        if not active_contract.car_photos.all().exists():
            text = static_text.CONTRACT_EXISTS_NO_PHOTO
            if active_contract.car:
                text += static_text.CONTRACT_EXISTS_CAR.format(
                    car_info=active_contract.car.get_short_info()
                )
            update.message.reply_text(
                text=text,
                reply_markup=keyboard_utils.get_photo_cntrct_keyboard()
            )
            return

        # When exists active contract with car photos
        days = (active_contract.closed_at - now()).days
        if active_contract.is_approved:
            text = f'До конца действия договора осталось {days} дней.'
        else:
            text = '⏳ Договор не подтвержден администратором'
        if active_contract.car:
            text += static_text.CONTRACT_EXISTS_CAR.format(
                car_info=active_contract.car.get_short_info()
            )
        update.message.reply_text(
            text=text,
            reply_markup=keyboard_utils.get_contract_main_menu_keyboard(),
        )
        return

    # Active contract does not exists

    # Personal data of user is exist -> ready to create a contract
    if hasattr(u, 'personal_data'):
        update.message.reply_text(text='Ваши персональные данные известны. ')

        # Send all Personal Data with keyboard for accepting
        text = 'Ваши данные:\n' + get_finish_personal_data(u)
        update.effective_message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_pd_accept_decline_keyboard(),
        )

        return

    # The user's personal data is unknown
    context.bot.send_message(
        chat_id=u.user_id,
        parse_mode=ParseMode.HTML,
        text=static_text.PERSONAL_DATA_NOT_EXISTS
    )


def contract_menu_handler(update: Update,
                          context: CallbackContext) -> str or None:
    query = update.callback_query
    data = query.data
    u = User.get_user(update, context)

    current_text = update.effective_message.text

    if data == manage_data.GET_INFO_ABOUT_MY_CAR:
        active_contract = u.get_active_contract()
        if not active_contract.car:
            try:
                query.edit_message_text(
                    text=static_text.CONTRACT_NOT_EXISTS_CAR,
                    reply_markup=keyboard_utils.get_contract_main_menu_keyboard()
                )
            except error.BadRequest:
                return
            return
        car = active_contract.car
        text = '<b>Ваша машина:</b>\n' + get_text_about_car(car)
        try:
            query.edit_message_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard_utils.get_contract_main_menu_keyboard(),
            )
        except error.BadRequest:
            return
    # Menu about contract with curren user
    elif data == manage_data.ABOUT_CONTRACT_MENU:
        active_contract = u.get_active_contract()
        created_at = active_contract.get_created_at_in_str()
        approved_at = active_contract.get_approved_at_in_str()
        closed_at = active_contract.get_closed_at_in_str()
        if not approved_at:
            approved_at = 'Договор не подтвержден'
            closed_at = 'Договор не подтвержден'
        if active_contract.car:
            car_name = active_contract.car.get_short_info()
        else:
            car_name = 'Машина не назначена'
        text = static_text.ABOUT_CONTRACT_MENU_TEXT.format(
            created_at=created_at,
            approved_at=approved_at,
            closed_at=closed_at,
            car_name=car_name,
        )
        query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_contract_contract_menu_keyboard()
        )
    # Main menu of user's fines
    elif data == manage_data.MY_FINES_MENU:
        # Calculate all fines and unpaid_fines
        all_fines_count = u.get_user_fines_count()
        unpaid_fines_count = u.get_user_fines_count(is_paid=False)

        text = static_text.MY_FINES_MENU_TEXT.format(
            all_fines_count=all_fines_count,
            unpaid_fines_count=unpaid_fines_count,
        )
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
        )
    elif data == manage_data.SET_FINE_IS_PAID_MENU:
        unpaid_fines = u.get_user_paid_or_unpaid_fines(is_paid=False)
        if unpaid_fines:
            query.edit_message_text(
                text=static_text.SET_FINE_IS_PAID_MENU_TEXT,
                reply_markup=keyboard_utils.get_set_fine_is_paid_keyboard(
                    unpaid_fines)
            )
        else:
            try:
                query.edit_message_text(
                    text=static_text.MY_UNPAID_FINES_DOES_NOT_EXISTS,
                    reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
                )
            except error.BadRequest:
                return
    elif data == manage_data.TO_MAIN_MENU:
        query.edit_message_reply_markup(
            reply_markup=keyboard_utils.get_contract_main_menu_keyboard()
        )
    elif data == manage_data.REMOVE_KEYBOARD:
        query.edit_message_text(text=current_text)


def contract_commands_handler(update: Update,
                              context: CallbackContext) -> str or None:
    query = update.callback_query
    data = query.data
    u = User.get_user(update, context)

    current_text = update.effective_message.text

    if data == manage_data.PD_IS_CORRECT:
        query.edit_message_text(
            query.message.text
        )
        new_contract = Contract(
            user=u,
            closed_at=now().replace(year=now().year + 1)
        )
        new_contract.save()

        pd = u.personal_data
        user_name = f'{pd.last_name} {pd.first_name[0]}.{pd.middle_name[0]}.'
        text_for_admins = static_text.USER_WANT_CREATE_CONTRACT.format(
            user_name=user_name
        )

        admins = User.objects.filter(is_admin=True)

        for admin in admins:
            context.bot.send_message(
                chat_id=admin.user_id,
                text=text_for_admins
            )

        # create_save_send_contract(u, context)
    elif data == manage_data.PD_IS_WRONG:
        query.edit_message_text(
            text=static_text.PERSONAL_DATA_WRONG,
            parse_mode=ParseMode.HTML
        )

    elif data == manage_data.DOWNLOAD_CONTRACT_FILE:
        current_contract = u.get_active_contract()
        query.edit_message_text(
            text=current_text + '\n\n👀 Сейчас отправлю договор.'
        )
        context.bot.send_document(
            chat_id=u.user_id,
            document=current_contract.file,
            filename=current_contract.file.name
        )
    elif data == manage_data.DOWNLOAD_CONTRACT_PHOTOS:
        current_contract = u.get_active_contract()
        contract_photos = current_contract.car_photos.all()
        query.edit_message_text(
            text=(current_text + f'\n\n'
                                 f'👀 Сейчас отправлю все '
                                 f'{len(contract_photos)} фотографий.')
        )
        send_contract_photos_to_user(u, contract_photos, context)

    elif data == manage_data.MY_ALL_FINES:
        limit = 10
        all_fines = u.get_user_all_fines(limit=limit)
        all_fines_count = len(all_fines) if all_fines else 0
        if all_fines:
            text_fines = utils.get_text_with_fines(all_fines)
            text = static_text.MY_ALL_FINES_LIMIT.format(
                all_fines_count=all_fines_count,
                limit=limit,
                text_fines=text_fines,
            )
        else:
            text = static_text.MY_ALL_FINES_DOES_NOT_EXISTS

        try:
            query.edit_message_text(
                text=text,
                reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data == manage_data.MY_PAID_FINES:
        paid_fines = u.get_user_paid_or_unpaid_fines(is_paid=True)
        if paid_fines:
            text_fines = utils.get_text_with_fines(paid_fines)
            text = static_text.MY_PAID_FINES.format(text_fines=text_fines)
        else:
            text = static_text.MY_PAID_FINES_DOES_NOT_EXISTS

        try:
            query.edit_message_text(
                text=text,
                reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data == manage_data.MY_UNPAID_FINES:
        unpaid_fines = u.get_user_paid_or_unpaid_fines(is_paid=False)
        if unpaid_fines:
            text_fines = utils.get_text_with_fines(unpaid_fines)
            text = static_text.MY_UNPAID_FINES.format(text_fines=text_fines)
        else:
            text = static_text.MY_UNPAID_FINES_DOES_NOT_EXISTS

        try:
            query.edit_message_text(
                text=text,
                reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
            )
        except error.BadRequest:
            return
    elif data.startswith(manage_data.BASE_FOR_SET_FINE_IS_PAID):
        fine_id = int(data.split('_')[-1])
        fine = Fine.objects.get(id=fine_id)
        fine.is_paid = True
        fine.save()

        text = (f'Штраф:\n'
                f'{fine.amount} руб. {fine.get_datetime_in_str()}\n\n'
                f'✅ Оплачен ✅')
        query.edit_message_text(
            text=text,
            reply_markup=keyboard_utils.get_my_fines_menu_keyboard()
        )


def send_contract_photos_to_user(u: User, contract_photos,
                                 context: CallbackContext):
    """Send car's photos of contract with current user."""
    # Create list of InputMediaPhoto for sending images as album
    media = [
        InputMediaPhoto(photo.file_id) if photo.file_id
        else InputMediaPhoto(photo.image)
        for photo in contract_photos
    ]

    # Maximum 10 InputMediaPhoto in one message
    if len(media) // 10 < 1:
        # Send all <10 photos to user
        context.bot.send_media_group(
            chat_id=u.user_id,
            media=media,
            timeout=1000,
        )
    else:
        # Send all photos to User
        # as multiple messages with albums of 10 images
        current_media = []
        while media:
            if len(current_media) < 10:
                current_media.append(media.pop())
            if len(current_media) == 10:
                context.bot.send_media_group(
                    chat_id=u.user_id,
                    media=current_media,
                    timeout=1000,
                )
                current_media.clear()

        if current_media:
            context.bot.send_media_group(
                chat_id=u.user_id,
                media=current_media,
                timeout=1000,
            )


def getting_photos_car_start_handler(update: Update,
                                     context: CallbackContext) -> str:
    """Handler for asking to send car photos."""
    update.effective_message.edit_text(
        text=static_text.ASK_CAR_PHOTOS,
        parse_mode=ParseMode.HTML,
    )

    return GETTING_PHOTO_CAR


def getting_photos_car_handler(update: Update,
                               context: CallbackContext) -> str:
    """Handler for receiving photos and save them."""
    u = User.get_user(update, context)

    current_contract = u.get_active_contract()

    # Name photo
    photos_count = current_contract.car_photos.count() + 1
    user_name = u.username if u.username else u.user_id
    photoname = f'{user_name}_{photos_count}.jpg'

    # Temporary file for caching image before create a PhotoCarContract obj
    img_temp = NamedTemporaryFile(delete=True)

    file = update.message.photo[-1].get_file()
    path = file.download(out=img_temp)

    img_temp.flush()

    # Create new PhotoCarContract and save downloaded image in it
    new_photo = PhotoCarContract(
        contract=current_contract,
        file_id=file.file_id
    )
    new_photo.save()
    new_photo.image.save(photoname, File(img_temp))

    update.message.reply_text(
        text=f'Фотография {photos_count} сохранена.\n'
             f'После отправки всех фотографий, введите "Готово"'
    )

    return GETTING_PHOTO_CAR


def stop_getting_car_photos_handler(update: Update,
                                    context: CallbackContext) -> str:
    """When user send 'Готово'. Conversation will be closed."""
    u = User.get_user(update, context)

    current_contract = u.get_active_contract()
    photos_count = current_contract.car_photos.count()

    update.message.reply_text(
        text=(f'Всего загружено {photos_count} фотографий.\n'
              f'Все сохранено и не подлежит редактированию.')
    )

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /contract')
    return ConversationHandler.END


def get_conversation_handler_get_contract_car_photos():
    """Return Conversation handler for getting car photos of contract."""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                getting_photos_car_start_handler,
                pattern=f'^{manage_data.GET_PHOTOS_CAR_CONTRACT}$')
        ],
        states={
            GETTING_PHOTO_CAR: [
                MessageHandler(Filters.photo, getting_photos_car_handler,
                               run_async=True),
                MessageHandler(Filters.text(['Готово']),
                               stop_getting_car_photos_handler)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
