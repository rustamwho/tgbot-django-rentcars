from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from general_utils.constants import GENDER_CHOICES_DICT
from tgbot.models import User
from tgbot.handlers.personal_data import (static_text, keyboard_utils,
                                          manage_data)
from general_utils.utils import get_finish_personal_data

from rentcars.models import PersonalData
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


def start_initialization_pd(update: Update, context: CallbackContext) -> str:
    """When touch "Заполнить данные"."""
    u = User.get_user(update, context)

    current_text = update.effective_message.text
    update.effective_message.edit_text(
        text=current_text
    )

    context.bot.send_message(
        chat_id=u.user_id,
        text=static_text.ABOUT_FILLING_PERSONAL_DATA
    )

    update.effective_message.reply_text(
        text=static_text.ASK_LAST_NAME,
        parse_mode=ParseMode.HTML
    )
    return LAST_NAME


def validate_and_save_text(validator: callable, state: str):
    """Decorator for validate input text and saving to context."""
    def decorator(func: callable):
        def wrapper(update: Update, context: CallbackContext):
            text = update.message.text

            try:
                validator(text)
            except ValidationError as e:
                update.message.reply_text(e.message + '\n\nПовторите ввод.')
                return state

            context.user_data[state] = text

            return func(update, context)

        return wrapper

    return decorator


@validate_and_save_text(validator=validators.ru_eng_letters_validator,
                        state=LAST_NAME)
def last_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save last name of user."""
    update.message.reply_text(
        text=static_text.ASK_FIRST_NAME,
        parse_mode=ParseMode.HTML
    )
    return FIRST_NAME


@validate_and_save_text(validator=validators.ru_eng_letters_validator,
                        state=FIRST_NAME)
def first_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save first name of user."""
    update.message.reply_text(
        text=static_text.ASK_MIDDLE_NAME,
        parse_mode=ParseMode.HTML
    )
    return MIDDLE_NAME


@validate_and_save_text(validator=validators.ru_eng_letters_validator,
                        state=MIDDLE_NAME)
def middle_name_handler(update: Update, context: CallbackContext) -> str:
    """Get and save patronymic of user. Send hello with full name."""

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

    update.effective_message.edit_text(f'Ваш пол: '
                                       f'{GENDER_CHOICES_DICT[gender]}')

    update.effective_message.reply_text(
        text=static_text.ASK_BIRTHDAY,
        parse_mode=ParseMode.HTML,
    )
    return BIRTHDAY


@validate_and_save_text(validator=validators.birthday_date_validate,
                        state=BIRTHDAY)
def birthday_handler(update: Update, context: CallbackContext) -> str:
    """Get and save birthday date of user."""
    update.message.reply_text(
        text=static_text.ASK_EMAIL,
        parse_mode=ParseMode.HTML,
    )

    return EMAIL


@validate_and_save_text(
    validator=EmailValidator(
        message='Адрес электронной почты должен быть правильным. '
                'Например, rustamwho@mail.com'),
    state=EMAIL)
def email_handler(update: Update, context: CallbackContext) -> str:
    """Get and save email of user."""

    update.message.reply_text(
        text=static_text.ASK_PHONE_NUMBER,
        parse_mode=ParseMode.HTML,
    )

    return PHONE_NUMBER


@validate_and_save_text(validator=validators.phone_number_validator,
                        state=PHONE_NUMBER)
def phone_number_handler(update: Update, context: CallbackContext) -> str:
    """Get and save phone number of user."""

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_SERIAL,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_SERIAL


@validate_and_save_text(validator=validators.passport_serial_validator,
                        state=PASSPORT_SERIAL)
def passport_serial_handler(update: Update, context: CallbackContext) -> str:
    """Get and save passport serial."""

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_NUMBER,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_NUMBER


@validate_and_save_text(validator=validators.passport_number_validator,
                        state=PASSPORT_NUMBER)
def passport_number_handler(update: Update, context: CallbackContext) -> str:
    """Get and save passport number."""

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_DATE_OF_ISSUE,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_ISSUED_AT


@validate_and_save_text(validator=validators.date_validate,
                        state=PASSPORT_ISSUED_AT)
def passport_issued_at_handler(update: Update,
                               context: CallbackContext) -> str:
    """Get and save when a passport is issued."""

    update.message.reply_text(
        text=static_text.ASK_PASSPORT_ISSUED_BY,
        parse_mode=ParseMode.HTML,
    )

    return PASSPORT_ISSUED_BY


@validate_and_save_text(validator=validators.passport_issued_by_validator,
                        state=PASSPORT_ISSUED_BY)
def passport_issued_by_handler(update: Update,
                               context: CallbackContext) -> str:
    """Get and save the passport issued by whom."""

    update.message.reply_text(
        text=static_text.ASK_ADDRESS_REGISTRATION,
        parse_mode=ParseMode.HTML,
    )

    return ADDRESS_REGISTRATION


@validate_and_save_text(validator=validators.address_validator,
                        state=ADDRESS_REGISTRATION)
def address_registration_handler(update: Update,
                                 context: CallbackContext) -> str:
    """Receive and save registration address of user."""

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


@validate_and_save_text(validator=validators.address_validator,
                        state=ADDRESS_RESIDENCE)
def address_residence_diff_handler(update: Update,
                                   context: CallbackContext) -> str:
    """Address of residence different with address registration."""

    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_NAME,
        parse_mode=ParseMode.HTML,
    )

    return CLOSE_PERSON_NAME


@validate_and_save_text(validator=validators.close_person_name_validator,
                        state=CLOSE_PERSON_NAME)
def close_person_name_handler(update: Update, context: CallbackContext) -> str:
    """Receive and save close person name. E.G. 'Аделина (Жена).'"""
    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_PHONE.format(
            close_person_name=context.user_data[CLOSE_PERSON_NAME]),
        parse_mode=ParseMode.HTML
    )

    return CLOSE_PERSON_PHONE


@validate_and_save_text(validator=validators.phone_number_validator,
                        state=CLOSE_PERSON_PHONE)
def close_person_phone_handler(update: Update,
                               context: CallbackContext) -> str:
    """Receive and save close person phone."""

    update.message.reply_text(
        text=static_text.ASK_CLOSE_PERSON_ADDRESS_FIRST,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_keyboard_for_address_similar(),
    )

    return CLOSE_PERSON_ADDRESS


def save_personal_data(user: User, personal_data: dict) -> None:
    """Create and save new object of PersonalData from dict."""
    pd = PersonalData(user=user, **personal_data)
    pd.save()


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


@validate_and_save_text(validator=validators.address_validator,
                        state=CLOSE_PERSON_ADDRESS)
def close_person_address_diff_handler(update: Update,
                                      context: CallbackContext) -> str:
    """Address residence of close person different with address of user."""

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
    """After touch accept or decline buttons of pd."""
    query = update.callback_query
    data = query.data

    if data == manage_data.CORRECT:
        query.edit_message_text(
            query.message.text
        )

        query.bot.send_message(
            chat_id=query.message.chat_id,
            text=static_text.PERSONAL_DATA_FINISHED,
            parse_mode=ParseMode.HTML,
        )

        return ConversationHandler.END

    elif data == manage_data.WRONG:
        query.edit_message_text(
            text=static_text.PERSONAL_DATA_WRONG,
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext) -> int:
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text('Отмена. Для начала с нуля нажмите '
                              '/personal_data')
    return ConversationHandler.END


def get_conversation_handler_for_init_pd():
    """Return Conversation handler for /contract"""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                start_initialization_pd,
                pattern=f'^{manage_data.START_INITIALIZATION_PD}$')
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
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )
    return conv_handler
