import datetime
import io

from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import MessageHandler, ConversationHandler, Filters, \
    CommandHandler, CallbackQueryHandler
from django.core.files import File
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.timezone import now

from general_utils.utils import get_verbose_date
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User
from tgbot.handlers.contract import static_text, keyboard_utils

from rentcars.utils.contracts import create_contract
from rentcars.models import PersonalData, Contract
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


def start_contract(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)

    if u.contract.exists():
        valid_contracts = u.contract.filter(closed_at__gte=now().date())
        if valid_contracts.exists():
            valid_contract = valid_contracts.order_by('closed_at').last()
            days = (valid_contract.closed_at - now().date()).days
            update.message.reply_text(f'До конца действия договора осталось '
                                      f'{days} дней.')
            return ConversationHandler.END

    if u.personal_data is not None:
        update.message.reply_text(text='Ваши персональные данные известны. '
                                       'Формирую договор.')

        create_save_send_contract(u, context)

        return ConversationHandler.END

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


def last_name_handler(update: Update, context: CallbackContext) -> int:
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


def first_name_handler(update: Update, context: CallbackContext) -> int:
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


def middle_name_handler(update: Update, context: CallbackContext) -> int:
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


def gender_handler(update: Update, context: CallbackContext) -> int:
    gender = int(update.callback_query.data)
    context.user_data[GENDER] = gender

    update.effective_message.edit_text(f'Ваш пол: {GENDER_CHOICES[gender][1]}')

    update.effective_message.reply_text(
        text=static_text.ASK_BIRTHDAY,
        parse_mode=ParseMode.HTML,
    )
    return BIRTHDAY


def birthday_handler(update: Update, context: CallbackContext) -> int:
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


def email_handler(update: Update, context: CallbackContext) -> int:
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


def phone_number_handler(update: Update, context: CallbackContext) -> int:
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


def passport_serial_handler(update: Update, context: CallbackContext) -> int:
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


def passport_number_handler(update: Update, context: CallbackContext) -> int:
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
                               context: CallbackContext) -> int:
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
                               context: CallbackContext) -> int:
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
                                 context: CallbackContext) -> int:
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
                                      context: CallbackContext) -> int:
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
                                   context: CallbackContext) -> int:
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


def close_person_name_handler(update: Update, context: CallbackContext) -> int:
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
                               context: CallbackContext) -> int:
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


def get_finish_personal_data(context: CallbackContext) -> str:
    text = static_text.END_PERSONAL_DATA.format(
        name=(f'{context.user_data[LAST_NAME]} '
              f'{context.user_data[FIRST_NAME]} '
              f'{context.user_data[MIDDLE_NAME]}'),
        gender=GENDER_CHOICES[context.user_data[GENDER]][1],
        birthday=context.user_data[BIRTHDAY],
        email=context.user_data[EMAIL],
        phone_number=context.user_data[PHONE_NUMBER],
        passport=(context.user_data[PASSPORT_SERIAL] + ' №' +
                  context.user_data[PASSPORT_NUMBER]),
        passport_issued=(context.user_data[PASSPORT_ISSUED_BY] + ' ' +
                         context.user_data[PASSPORT_ISSUED_AT]),
        address_registration=context.user_data[ADDRESS_REGISTRATION],
        address_residence=context.user_data[ADDRESS_RESIDENCE],
        close_person=(context.user_data[CLOSE_PERSON_PHONE] + ' ' +
                      context.user_data[CLOSE_PERSON_NAME]),
        close_person_address=context.user_data[CLOSE_PERSON_ADDRESS]
    )

    return text


def save_personal_data(user: User, personal_data: dict) -> None:
    pd = PersonalData(user=user, **personal_data)
    pd.save()


def create_save_send_contract(u: User,
                              context: CallbackContext) -> None:
    new_contract = create_contract(u)
    new_contract_io = io.BytesIO()
    new_contract.save(new_contract_io)
    new_contract_io.seek(0)
    contr = Contract(
        user=u,
        file=File(new_contract_io,
                  name=u.username + str(now().date()) + '.docx'),
        closed_at=datetime.date.today() + datetime.timedelta(days=10)
    )
    contr.save()

    context.bot.send_message(
        chat_id=u.user_id,
        text='Сейчас пришлю договор. Его надо будет распечатать и подписать.'
    )

    context.bot.send_document(
        chat_id=u.user_id,
        document=contr.file,
        filename=(u.last_name + ' ' + u.first_name + ' ' +
                  get_verbose_date(contr.created_at) + '.docx')
    )


def close_person_address_similar_handler(update: Update,
                                         context: CallbackContext) -> int:
    answer = update.callback_query.data
    if answer == 'similar_addr':
        address = context.user_data[ADDRESS_RESIDENCE]
        context.user_data[CLOSE_PERSON_ADDRESS] = address

        update.effective_message.edit_text(
            'Адрес проживания близкого человека совпадает с местом проживания '
            'арендатора.'
        )
        text = get_finish_personal_data(context)
        update.effective_message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
        )
        u = User.get_user(update, context)

        save_personal_data(u, context.user_data)

        create_save_send_contract(u, context)

        return ConversationHandler.END

    update.effective_message.edit_text(
        text=static_text.ASK_CLOSE_PERSON_ADDRESS_SECOND,
        parse_mode=ParseMode.HTML,
    )

    return CLOSE_PERSON_ADDRESS


def close_person_address_diff_handler(update: Update,
                                      context: CallbackContext) -> int:
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_ADDRESS

    context.user_data[CLOSE_PERSON_ADDRESS] = text

    text = get_finish_personal_data(context)
    update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
    )
    u = User.get_user(update, context)

    save_personal_data(u, context.user_data)

    create_save_send_contract(u, context)

    # TODO: Расписать докстринги для функций

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext):
    """ Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите /contract')
    return ConversationHandler.END


def get_conversation_handler_for_contract():
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('contract', start_contract),
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
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
