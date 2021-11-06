import datetime
import io

from pytils.translit import slugify

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)
from telegram import InputMediaPhoto

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.forms.models import model_to_dict
from django.utils.timezone import now

from general_utils.utils import get_verbose_date
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User
from tgbot.handlers.contract import static_text, keyboard_utils, manage_data

from rentcars.utils.contracts import create_contract
from rentcars.models import Contract, PhotoCarContract

ACCEPT = 'ACCEPT_PD'
GETTING_PHOTO_CAR = 'GETTING_PHOTO_CAR'


def start_contract(update: Update, context: CallbackContext) -> str:
    """When getting command /contract."""
    u = User.get_user(update, context)

    # If contracts with current user does exists
    # Send remaining time of the contract
    """if u.contracts.exists():
        valid_contracts = u.contracts.filter(closed_at__gte=now().date())"""
    active_contract = u.get_active_contract()
    if active_contract:
        # When photos of car in contract does not exists
        if not active_contract.car_photos.all().exists():
            update.message.reply_text(
                text=static_text.CONTRACT_EXISTS_NO_PHOTO,
                reply_markup=keyboard_utils.get_photo_cntrct_keyboard()
            )
            return ConversationHandler.END

        days = (active_contract.closed_at - now().date()).days
        update.message.reply_text(
            text=f'До конца действия договора осталось {days} дней.',
            reply_markup=keyboard_utils.get_contract_commands_keyboard(),
        )
        return ConversationHandler.END

    if hasattr(u, 'personal_data'):
        update.message.reply_text(text='Ваши персональные данные известны. ')

        # Send all Personal Data with keyboard for accepting
        text = get_finish_personal_data(u)
        update.effective_message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_pd_accept_decline_keyboard(),
        )

        return ACCEPT

    context.bot.send_message(
        chat_id=u.user_id,
        text=static_text.PERSONAL_DATA_NOT_EXISTS
    )

    return ConversationHandler.END


def get_finish_personal_data(user: User) -> str:
    """Beautiful formatting text with personal data's."""

    pd = model_to_dict(user.personal_data, exclude='user')

    pd['gender'] = GENDER_CHOICES[pd['gender']][1]
    pd['birthday'] = datetime.date.strftime(pd['birthday'], '%d.%m.%Y')
    pd['passport_date_of_issue'] = datetime.date.strftime(
        pd['passport_date_of_issue'], '%d.%m.%Y'
    )

    text = static_text.PERSONAL_DATA.format(**pd)

    return text


def contract_menu_handler(update: Update,
                          context: CallbackContext) -> str:
    query = update.callback_query
    data = query.data

    current_text = update.effective_message.text

    if data == manage_data.REMOVE_KEYBOARD:
        query.edit_message_text(text=current_text)

    return ConversationHandler.END


def download_existing_contract_handler(update: Update,
                                       context: CallbackContext) -> str:
    """Send existing contract with current user"""
    u = User.get_user(update, context)
    current_text = update.effective_message.text
    query = update.callback_query
    data = query.data

    current_contract = u.get_active_contract()

    if data == manage_data.DOWNLOAD_CONTRACT_FILE:
        query.edit_message_text(
            text=current_text + '\n\nСейчас отправлю договор.'
        )
        context.bot.send_document(
            chat_id=u.user_id,
            document=current_contract.file,
            filename=current_contract.file.name
        )
    elif data == manage_data.DOWNLOAD_CONTRACT_PHOTOS:
        contract_photos = current_contract.car_photos.all()
        query.edit_message_text(
            text=(current_text + f'\n\n'
                                 f'Сейчас отправлю все {len(contract_photos)} '
                                 f'фотографий.')
        )

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

    return ConversationHandler.END


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


def create_save_send_contract(u: User,
                              context: CallbackContext) -> None:
    """Create contract .docx with user and save Contract object."""
    # Create new contract file
    new_contract = create_contract(u)

    # Create Contract object with new contract file
    new_contract_io = io.BytesIO()
    new_contract.save(new_contract_io)
    new_contract_io.seek(0)
    contr = Contract(
        user=u,
        file=File(new_contract_io,
                  name=(slugify(u.personal_data.last_name) +
                        str(now().date()) + '.docx')),
        closed_at=now() + datetime.timedelta(days=10)
    )
    contr.save()

    context.bot.send_message(
        chat_id=u.user_id,
        text='Сейчас пришлю договор. Его надо будет распечатать и подписать.'
    )

    """
    Or else:
    filename=(
                u.personal_data.last_name + ' ' + u.personal_data.first_name +
                ' ' + get_verbose_date(contr.created_at) + '.docx')
    """
    context.bot.send_document(
        chat_id=u.user_id,
        document=contr.file,
        filename=contr.file.name
    )

    admins = User.objects.filter(is_admin=True)

    if not admins:
        return

    name_user = (f'{u.personal_data.last_name} {u.personal_data.first_name} '
                 f'{u.personal_data.middle_name}')
    contract_closed_at = get_verbose_date(contr.closed_at)
    text_for_moderators = (
        f'Сформирован новый договор с {name_user}.\n'
        f'Срок действия договора - до {contract_closed_at}.'
    )
    contr = u.get_active_contract()
    for admin in admins:
        context.bot.send_message(
            chat_id=admin.user_id,
            text=text_for_moderators
        )
        context.bot.send_document(
            chat_id=admin.user_id,
            document=contr.file,
            filename=contr.file.name
        )


def accept_pd_handler(update: Update, context: CallbackContext) -> str:
    """After touch accept or decline buttons of pd."""
    query = update.callback_query
    data = query.data

    if data == manage_data.CORRECT:
        u = User.get_user(update, context)
        query.edit_message_text(
            query.message.text
        )
        create_save_send_contract(u, context)

        return ConversationHandler.END

    elif data == manage_data.WRONG:
        query.edit_message_text(
            text=static_text.PERSONAL_DATA_WRONG,
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /contract')
    return ConversationHandler.END


def get_conversation_handler_for_contract():
    """Return Conversation handler for /contract"""
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('contract', start_contract),
            CallbackQueryHandler(
                contract_menu_handler,
                pattern=f'^{manage_data.BASE_FOR_CONTRACT_MENU}'),
            CallbackQueryHandler(
                download_existing_contract_handler,
                pattern=f'^{manage_data.BASE_FOR_DOWNLOAD_CONTRACT}'),
            CallbackQueryHandler(
                getting_photos_car_start_handler,
                pattern=f'^{manage_data.SEND_PHOTOS_CAR_CONTRACT}$')
        ],
        states={
            ACCEPT: [
                CallbackQueryHandler(accept_pd_handler,
                                     pattern=f'^{manage_data.BASE_FOR_ACCEPT}')
            ],
            GETTING_PHOTO_CAR: [
                MessageHandler(Filters.photo, getting_photos_car_handler),
                MessageHandler(Filters.text(['Готово']),
                               stop_getting_car_photos_handler)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
