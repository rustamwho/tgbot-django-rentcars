import datetime
import io

from pytils.translit import slugify

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.timezone import now

from general_utils.utils import get_verbose_date
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User
from tgbot.handlers.contract import static_text, keyboard_utils, manage_data

from rentcars.utils.contracts import create_contract
from rentcars.models import PersonalData, Contract, PhotoCarContract
from rentcars import validators

(LAST_NAME, FIRST_NAME, MIDDLE_NAME, GENDER, BIRTHDAY, EMAIL, PHONE_NUMBER,
 PASSPORT_SERIAL, PASSPORT_NUMBER, PASSPORT_ISSUED_AT, PASSPORT_ISSUED_BY,
 ADDRESS_REGISTRATION, ADDRESS_RESIDENCE, CLOSE_PERSON_NAME,
 CLOSE_PERSON_PHONE, CLOSE_PERSON_ADDRESS) = (
    'last_name', 'first_name', 'middle_name', 'gender', 'birthday', 'email',
    'phone_number', 'passport_serial', 'passport_number',
    'passport_date_of_issue', 'passport_issued_by', 'address_registration',
    'address_of_residence', 'close_person_name', 'close_person_phone',
    'close_person_address')
ACCEPT = 'ACCEPT_PD'
GETTING_PHOTO_CAR = 'GETTING_PHOTO_CAR'


def start_contract(update: Update, context: CallbackContext) -> str:
    """When getting command /contract."""
    u = User.get_user(update, context)

    # If contracts with current user does exists
    # Send remaining time of the contract
    if u.contract.exists():
        valid_contracts = u.contract.filter(closed_at__gte=now().date())
        if valid_contracts.exists():
            valid_contract = valid_contracts.order_by('closed_at').last()

            # When photos of car in contract does not exists
            if not valid_contract.car_photos.all().exists():
                update.message.reply_text(
                    text=static_text.CONTRACT_EXISTS_NO_PHOTO,
                    reply_markup=keyboard_utils.get_photo_cntrct_keyboard()
                )
                return ConversationHandler.END

            days = (valid_contract.closed_at - now().date()).days
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
        text=static_text.NOT_EXISTS_CONTRACTS
    )
    context.bot.send_message(
        chat_id=u.user_id,
        text=static_text.ABOUT_FILLING_PERSONAL_DATA
    )

    update.message.reply_text(
        text=static_text.ASK_LAST_NAME,
        parse_mode=ParseMode.HTML
    )
    return LAST_NAME


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

    current_contract = u.contract.order_by('closed_at').last()

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
                                 f'Сейчас отправлю все {len(contract_photos)} фотографий.')
        )
        for photo in contract_photos:
            file = photo.file_id if photo.file_id else photo.image
            context.bot.send_photo(
                chat_id=u.user_id,
                photo=file,
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

    current_contract = u.contract.order_by('closed_at').last()

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

    current_contract = u.contract.order_by('closed_at').last()
    photos_count = current_contract.car_photos.count()

    update.message.reply_text(
        text=(f'Всего загружено {photos_count} фотографий.\n'
              f'Все сохранено и не подлежит редактированию.')
    )

    return ConversationHandler.END


def last_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save last name of user."""
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return LAST_NAME

    context.user_data[LAST_NAME] = text
    update.message.reply_text(
        text=static_text.ASK_FIRST_NAME,
        parse_mode=ParseMode.HTML
    )
    return FIRST_NAME


def first_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save first name of user."""
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return FIRST_NAME

    context.user_data[FIRST_NAME] = text
    update.message.reply_text(
        text=static_text.ASK_MIDDLE_NAME,
        parse_mode=ParseMode.HTML
    )
    return MIDDLE_NAME


def middle_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save patronymic of user. Send hello with full name."""
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return MIDDLE_NAME

    context.user_data[MIDDLE_NAME] = text

    u = User.get_user(update, context)
    name = (f'{context.user_data[LAST_NAME]} {context.user_data[FIRST_NAME]} '
            f'{context.user_data[MIDDLE_NAME]}')
    context.bot.send_message(
        chat_id=u.user_id,
        text=static_text.HELLO_FULL_NAME.format(name=name)
    )

    update.message.reply_text(
        text=static_text.ASK_GENDER,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_keyboard_for_gender()
    )

    return GENDER


def gender_handler(update: Update, context: CallbackContext) -> str:
    """Get and save gender of user."""
    gender = int(update.callback_query.data)
    context.user_data[GENDER] = gender

    update.effective_message.edit_text(f'Ваш пол: {GENDER_CHOICES[gender][1]}')

    update.effective_message.reply_text(
        text=static_text.ASK_BIRTHDAY,
        parse_mode=ParseMode.HTML,
    )
    return BIRTHDAY


def birthday_handler(update: Update, context: CallbackContext) -> str:
    """Get and save birthday date of user."""
    text = update.message.text

    try:
        validators.birthday_date_validate(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return BIRTHDAY

    context.user_data[BIRTHDAY] = text

    update.message.reply_text(
        text=static_text.ASK_EMAIL,
        parse_mode=ParseMode.HTML,
    )

    return EMAIL


def email_handler(update: Update, context: CallbackContext) -> str:
    """Get and save email of user."""
    text = update.message.text

    try:
        validator = EmailValidator(
            message='Адрес электронной почты должен быть правильным. '
                    'Например, rustamwho@mail.com')
        validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return EMAIL

    context.user_data[EMAIL] = text

    update.message.reply_text(
        text=static_text.ASK_PHONE_NUMBER,
        parse_mode=ParseMode.HTML,
    )

    return PHONE_NUMBER


def phone_number_handler(update: Update, context: CallbackContext) -> str:
    """Get and save phone number of user."""
    text = update.message.text

    try:
        validators.phone_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PHONE_NUMBER

    context.user_data[PHONE_NUMBER] = text

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_SERIAL,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_SERIAL


def passport_serial_handler(update: Update, context: CallbackContext) -> str:
    """Get and save passport serial."""
    text = update.message.text

    try:
        validators.passport_serial_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_SERIAL

    context.user_data[PASSPORT_SERIAL] = text

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_NUMBER,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_NUMBER


def passport_number_handler(update: Update, context: CallbackContext) -> str:
    """Get and save passport number."""
    text = update.message.text

    try:
        validators.passport_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_NUMBER

    context.user_data[PASSPORT_NUMBER] = text

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_DATE_OF_ISSUE,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_ISSUED_AT


def passport_issued_at_handler(update: Update,
                               context: CallbackContext) -> str:
    """Get and save when a passport is issued."""
    text = update.message.text

    try:
        validators.date_validate(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_ISSUED_AT

    context.user_data[PASSPORT_ISSUED_AT] = text

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_ISSUED_BY,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_ISSUED_BY


def passport_issued_by_handler(update: Update,
                               context: CallbackContext) -> str:
    """Get and save the passport issued by whom."""
    text = update.message.text

    try:
        validators.passport_issued_by_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_ISSUED_BY

    context.user_data[PASSPORT_ISSUED_BY] = text

    update.message.reply_text(
        text=static_text.ASK_ADDRESS_REGISTRATION,
        parse_mode=ParseMode.HTML,
    )

    return ADDRESS_REGISTRATION


def address_registration_handler(update: Update,
                                 context: CallbackContext) -> str:
    """Receive and save registration address of user."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return ADDRESS_REGISTRATION

    context.user_data[ADDRESS_REGISTRATION] = text

    update.message.reply_text(
        text=static_text.ASK_ADDRESS_RESIDENCE_FIRST,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_keyboard_for_address_similar(),
    )

    return ADDRESS_RESIDENCE


def address_residence_similar_handler(update: Update,
                                      context: CallbackContext) -> str:
    """Address residence similar with address registration."""
    answer = update.callback_query.data
    if answer == 'similar_addr':
        address = context.user_data[ADDRESS_REGISTRATION]
        context.user_data[ADDRESS_RESIDENCE] = address

        update.effective_message.edit_text('Адрес проживания совпадает с '
                                           'адресом прописки.')

        update.effective_message.reply_text(
            text=static_text.ASK_CLOSE_PERSON_NAME,
            parse_mode=ParseMode.HTML,
        )

        return CLOSE_PERSON_NAME

    update.effective_message.edit_text(
        text=static_text.ASK_ADDRESS_RESIDENCE_SECOND,
        parse_mode=ParseMode.HTML,
    )

    return ADDRESS_RESIDENCE


def address_residence_diff_handler(update: Update,
                                   context: CallbackContext) -> str:
    """Address of residence different with address registration."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return ADDRESS_RESIDENCE

    context.user_data[ADDRESS_RESIDENCE] = text

    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_NAME,
        parse_mode=ParseMode.HTML,
    )

    return CLOSE_PERSON_NAME


def close_person_name_handler(update: Update, context: CallbackContext) -> str:
    """Receive and save close person name. E.G. 'Аделина (Жена).'"""
    text = update.message.text

    try:
        validators.close_person_name_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_NAME

    context.user_data[CLOSE_PERSON_NAME] = text

    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_PHONE.format(close_person_name=text),
        parse_mode=ParseMode.HTML
    )

    return CLOSE_PERSON_PHONE


def close_person_phone_handler(update: Update,
                               context: CallbackContext) -> str:
    """Receive and save close person phone."""
    text = update.message.text

    try:
        validators.phone_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_PHONE

    context.user_data[CLOSE_PERSON_PHONE] = text

    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_ADDRESS_FIRST,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_keyboard_for_address_similar(),
    )

    return CLOSE_PERSON_ADDRESS


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


def save_personal_data(user: User, personal_data: dict) -> None:
    """Create and save new object of PersonalData from dict."""
    pd = PersonalData(user=user, **personal_data)
    pd.save()


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
        closed_at=datetime.date.today() + datetime.timedelta(days=10)
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


def close_person_address_similar_handler(update: Update,
                                         context: CallbackContext) -> str:
    """Address of close person similar with user address."""
    answer = update.callback_query.data
    if answer == 'similar_addr':
        address = context.user_data[ADDRESS_RESIDENCE]
        context.user_data[CLOSE_PERSON_ADDRESS] = address

        update.effective_message.edit_text(
            'Адрес проживания близкого человека совпадает с местом проживания '
            'арендатора.'
        )

        # Save Personal Data
        u = User.get_user(update, context)
        save_personal_data(u, context.user_data)

        # Send all Personal Data with keyboard for accepting
        text = get_finish_personal_data(u)
        update.effective_message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_pd_accept_decline_keyboard(),
        )

        return ACCEPT

    update.effective_message.edit_text(
        text=static_text.ASK_CLOSE_PERSON_ADDRESS_SECOND,
        parse_mode=ParseMode.HTML,
    )

    return CLOSE_PERSON_ADDRESS


def close_person_address_diff_handler(update: Update,
                                      context: CallbackContext) -> str:
    """Address residence of close person different with address of user."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_ADDRESS

    context.user_data[CLOSE_PERSON_ADDRESS] = text

    # Save Personal Data
    u = User.get_user(update, context)
    save_personal_data(u, context.user_data)

    # Send all Personal Data with keyboard for accepting
    text = get_finish_personal_data(u)
    update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_pd_accept_decline_keyboard(),
    )

    return ACCEPT


def accept_pd_handler(update: Update, context: CallbackContext) -> str:
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
            LAST_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               last_name_handler, pass_user_data=True)
            ],
            FIRST_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               first_name_handler, pass_user_data=True)
            ],
            MIDDLE_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               middle_name_handler, pass_user_data=True)
            ],
            GENDER: [
                CallbackQueryHandler(gender_handler, pass_user_data=True)
            ],
            BIRTHDAY: [
                MessageHandler(Filters.text & ~Filters.command,
                               birthday_handler, pass_user_data=True)
            ],
            EMAIL: [
                MessageHandler(Filters.text & ~Filters.command,
                               email_handler, pass_user_data=True)
            ],
            PHONE_NUMBER: [
                MessageHandler(Filters.text & ~Filters.command,
                               phone_number_handler, pass_user_data=True)
            ],
            PASSPORT_SERIAL: [
                MessageHandler(Filters.text & ~Filters.command,
                               passport_serial_handler, pass_user_data=True)
            ],
            PASSPORT_NUMBER: [
                MessageHandler(Filters.text & ~Filters.command,
                               passport_number_handler, pass_user_data=True)
            ],
            PASSPORT_ISSUED_AT: [
                MessageHandler(Filters.text & ~Filters.command,
                               passport_issued_at_handler, pass_user_data=True)
            ],
            PASSPORT_ISSUED_BY: [
                MessageHandler(Filters.text & ~Filters.command,
                               passport_issued_by_handler, pass_user_data=True)
            ],
            ADDRESS_REGISTRATION: [
                MessageHandler(Filters.text & ~Filters.command,
                               address_registration_handler,
                               pass_user_data=True)
            ],
            ADDRESS_RESIDENCE: [
                CallbackQueryHandler(address_residence_similar_handler,
                                     pass_user_data=True),
                MessageHandler(Filters.text & ~Filters.command,
                               address_residence_diff_handler,
                               pass_user_data=True)
            ],
            CLOSE_PERSON_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               close_person_name_handler, pass_user_data=True)
            ],
            CLOSE_PERSON_PHONE: [
                MessageHandler(Filters.text & ~Filters.command,
                               close_person_phone_handler, pass_user_data=True)
            ],
            CLOSE_PERSON_ADDRESS: [
                CallbackQueryHandler(close_person_address_similar_handler,
                                     pass_user_data=True),
                MessageHandler(Filters.text & ~Filters.command,
                               close_person_address_diff_handler,
                               pass_user_data=True)
            ],
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
