import datetime

from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from general_utils.constants import GENDER_CHOICES

from rentcars import validators

from tgbot.models import User
from tgbot.handlers.personal_data import (static_text, keyboard_utils,
                                          manage_data)

(LAST_NAME, FIRST_NAME, MIDDLE_NAME, GENDER, BIRTHDAY, EMAIL, PHONE_NUMBER,
 PASSPORT_SERIAL, PASSPORT_NUMBER, PASSPORT_ISSUED_AT, PASSPORT_ISSUED_BY,
 ADDRESS_REGISTRATION, ADDRESS_RESIDENCE, CLOSE_PERSON_NAME,
 CLOSE_PERSON_PHONE, CLOSE_PERSON_ADDRESS) = range(16)


def get_my_personal_data_handler(update: Update,
                                 context: CallbackContext) -> None:
    u = User.get_user(update, context)

    if not hasattr(u, 'personal_data'):
        update.message.reply_text(
            text=static_text.PERSONAL_DATA_NOT_EXISTS
        )
        return

    pd = model_to_dict(u.personal_data, exclude='user')

    pd['gender'] = GENDER_CHOICES[pd['gender']][1]
    pd['birthday'] = datetime.date.strftime(pd['birthday'], '%d.%m.%Y')
    pd['passport_date_of_issue'] = datetime.date.strftime(
        pd['passport_date_of_issue'], '%d.%m.%Y'
    )

    text = static_text.PERSONAL_DATA.format(**pd)

    context.bot.send_message(
        chat_id=u.user_id,
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_personal_data_edit_keyboard(),
    )


def main_menu_edit_pd_handler(update: Update, context: CallbackContext):
    """Handler for MENU callbacks."""
    current_text = update.effective_message.text
    query = update.callback_query
    data = query.data
    if data in (manage_data.MENU_EDIT_PD_MAIN, manage_data.BACK):
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_all_types_pd_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == manage_data.MENU_EDIT_PD_PD:
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_pd_pd_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == manage_data.MENU_EDIT_CONTACTS:
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_pd_contacts_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == manage_data.MENU_EDIT_PASSPORT:
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_pd_passport_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == manage_data.MENU_EDIT_CLOSE_PERSON:
        query.edit_message_text(
            text=current_text,
            reply_markup=keyboard_utils.get_pd_close_person_keyboard(),
            parse_mode=ParseMode.HTML
        )
    elif data == manage_data.REMOVE_KEYBOARD:
        query.edit_message_text(text=current_text, parse_mode=ParseMode.HTML)


def editing_pd_start_handler(update: Update, context: CallbackContext):
    """Handling EDIT PERSONAL DATA commands."""
    current_text = update.effective_message.text
    query = update.callback_query
    data = query.data

    if data == manage_data.EDIT_PD_LAST_NAME:
        query.edit_message_text(
            text=static_text.ASK_LAST_NAME, parse_mode=ParseMode.HTML
        )
        return LAST_NAME
    elif data == manage_data.EDIT_PD_FIRST_NAME:
        query.edit_message_text(
            text=static_text.ASK_FIRST_NAME, parse_mode=ParseMode.HTML
        )
        return FIRST_NAME
    elif data == manage_data.EDIT_PD_MIDDLE_NAME:
        query.edit_message_text(
            text=static_text.ASK_MIDDLE_NAME, parse_mode=ParseMode.HTML
        )
        return MIDDLE_NAME
    elif data == manage_data.EDIT_PD_GENDER:
        query.edit_message_text(
            text=static_text.ASK_GENDER,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_utils.get_keyboard_for_gender()
        )
        return GENDER
    elif data == manage_data.EDIT_PD_BIRTHDAY:
        query.edit_message_text(
            text=static_text.ASK_BIRTHDAY, parse_mode=ParseMode.HTML
        )
        return BIRTHDAY
    elif data == manage_data.EDIT_PD_PHONE_NUMBER:
        query.edit_message_text(
            text=static_text.ASK_PHONE_NUMBER, parse_mode=ParseMode.HTML
        )
        return PHONE_NUMBER
    elif data == manage_data.EDIT_PD_EMAIL:
        query.edit_message_text(
            text=static_text.ASK_EMAIL, parse_mode=ParseMode.HTML
        )
        return EMAIL
    elif data == manage_data.EDIT_PD_ADDRESS_REGISTRATION:
        query.edit_message_text(
            text=static_text.ASK_ADDRESS_REGISTRATION,
            parse_mode=ParseMode.HTML
        )
        return ADDRESS_REGISTRATION
    elif data == manage_data.EDIT_PD_ADDRESS_RESIDENCE:
        query.edit_message_text(
            text=static_text.ASK_ADDRESS_RESIDENCE,
            parse_mode=ParseMode.HTML
        )
        return ADDRESS_RESIDENCE
    elif data == manage_data.EDIT_PD_PASSPORT_SERIAL:
        query.edit_message_text(
            text=static_text.ASK_PASSPORT_SERIAL,
            parse_mode=ParseMode.HTML
        )
        return PASSPORT_SERIAL
    elif data == manage_data.EDIT_PD_PASSPORT_NUMBER:
        query.edit_message_text(
            text=static_text.ASK_PASSPORT_NUMBER,
            parse_mode=ParseMode.HTML
        )
        return PASSPORT_NUMBER
    elif data == manage_data.EDIT_PD_PASSPORT_ISSUED_BY:
        query.edit_message_text(
            text=static_text.ASK_PASSPORT_ISSUED_BY,
            parse_mode=ParseMode.HTML
        )
        return PASSPORT_ISSUED_BY
    elif data == manage_data.EDIT_PD_PASSPORT_ISSUED_AT:
        query.edit_message_text(
            text=static_text.ASK_PASSPORT_DATE_OF_ISSUE,
            parse_mode=ParseMode.HTML
        )
        return PASSPORT_ISSUED_AT
    elif data == manage_data.EDIT_PD_CLOSE_PERSON_NAME:
        query.edit_message_text(
            text=static_text.ASK_CLOSE_PERSON_NAME,
            parse_mode=ParseMode.HTML
        )
        return CLOSE_PERSON_NAME
    elif data == manage_data.EDIT_PD_CLOSE_PERSON_PHONE:
        u = User.get_user(update, context)
        close_person_name = u.personal_data.close_person_name
        query.edit_message_text(
            text=static_text.ASK_CLOSE_PERSON_PHONE.format(
                close_person_name=close_person_name
            ),
            parse_mode=ParseMode.HTML
        )
        return CLOSE_PERSON_PHONE
    elif data == manage_data.EDIT_PD_CLOSE_PERSON_ADDRESS:
        query.edit_message_text(
            text=static_text.ASK_CLOSE_PERSON_ADDRESS,
            parse_mode=ParseMode.HTML
        )
        return CLOSE_PERSON_ADDRESS


"""
Handlers for editing Personal Data
"""


def editing_last_name_handler(update: Update, context: CallbackContext):
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return LAST_NAME

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.last_name = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_first_name_handler(update: Update,
                               context: CallbackContext) -> int:
    """Get and save first name of user."""
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return FIRST_NAME
    u = User.get_user(update, context)
    pd = u.personal_data
    pd.first_name = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_middle_name_handler(update: Update,
                                context: CallbackContext) -> int:
    """Get and save patronymic of user. Send hello with full name."""
    text = update.message.text

    try:
        validators.russian_letters_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return MIDDLE_NAME

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.middle_name = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_gender_handler(update: Update, context: CallbackContext) -> int:
    """Get and save gender of user."""
    gender = int(update.callback_query.data)
    update.callback_query.edit_message_text(
        text=f'Вы выбрали <b>ПОЛ</b> - {GENDER_CHOICES[gender][1]}',
        parse_mode=ParseMode.HTML
    )

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.gender = gender
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_birthday_handler(update: Update, context: CallbackContext) -> int:
    """Get and save birthday date of user."""
    text = update.message.text

    try:
        validators.birthday_date_validate(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return BIRTHDAY
    u = User.get_user(update, context)
    pd = u.personal_data
    pd.birthday = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_phone_number_handler(update: Update,
                                 context: CallbackContext) -> int:
    """Get and save phone number of user."""
    text = update.message.text

    try:
        validators.phone_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PHONE_NUMBER

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.phone_number = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_email_handler(update: Update, context: CallbackContext) -> int:
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

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.email = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_address_registration_handler(update: Update,
                                         context: CallbackContext) -> int:
    """Receive and save registration address of user."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return ADDRESS_REGISTRATION

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.address_registration = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_address_residence_handler(update: Update,
                                      context: CallbackContext) -> int:
    """Receive and save registration address of user."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return ADDRESS_REGISTRATION

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.address_of_residence = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_passport_serial_handler(update: Update,
                                    context: CallbackContext) -> int:
    """Get and save passport serial."""
    text = update.message.text

    try:
        validators.passport_serial_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_SERIAL
    u = User.get_user(update, context)
    pd = u.personal_data
    pd.passport_serial = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_passport_number_handler(update: Update,
                                    context: CallbackContext) -> int:
    """Get and save passport number."""
    text = update.message.text

    try:
        validators.passport_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_NUMBER

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.passport_number = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_passport_issued_by_handler(update: Update,
                                       context: CallbackContext) -> int:
    """Get and save the passport issued by whom."""
    text = update.message.text

    try:
        validators.passport_issued_by_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_ISSUED_BY

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.passport_issued_by = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_passport_issued_at_handler(update: Update,
                                       context: CallbackContext) -> int:
    """Get and save when a passport is issued."""
    text = update.message.text

    try:
        validators.date_validate(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return PASSPORT_ISSUED_AT

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.passport_date_of_issue = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_close_person_name_handler(update: Update,
                                      context: CallbackContext) -> int:
    """Receive and save close person name. E.G. 'Аделина (Жена).'"""
    text = update.message.text

    try:
        validators.close_person_name_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_NAME

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.close_person_name = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_close_person_phone_handler(update: Update,
                                       context: CallbackContext) -> int:
    """Receive and save close person phone."""
    text = update.message.text

    try:
        validators.phone_number_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_PHONE

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.close_person_phone = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def editing_close_person_address_handler(update: Update,
                                         context: CallbackContext) -> int:
    """Address residence of close person different with address of user."""
    text = update.message.text

    try:
        validators.address_validator(text)
    except ValidationError as e:
        update.message.reply_text(e.message + '\n\nПовторите ввод.')
        return CLOSE_PERSON_ADDRESS

    u = User.get_user(update, context)
    pd = u.personal_data
    pd.close_person_address = text
    pd.save()
    get_my_personal_data_handler(update, context)

    return ConversationHandler.END


def cancel_handler(update: Update, context: CallbackContext):
    """Отменить весь процесс диалога. Данные будут утеряны."""
    update.message.reply_text(
        'Отмена. Для начала с нуля нажмите /personal_data')
    return ConversationHandler.END


def get_pd_edit_conversation_handler():
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(editing_pd_start_handler,
                                 pattern=f'^{manage_data.BASE_FOR_EDITING}')
        ],
        states={
            LAST_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_last_name_handler)
            ],
            FIRST_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_first_name_handler)
            ],
            MIDDLE_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_middle_name_handler)
            ],
            GENDER: [
                CallbackQueryHandler(editing_gender_handler)
            ],
            BIRTHDAY: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_birthday_handler)
            ],
            PHONE_NUMBER: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_phone_number_handler)
            ],
            EMAIL: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_email_handler)
            ],
            ADDRESS_REGISTRATION: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_address_registration_handler)
            ],
            ADDRESS_RESIDENCE: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_address_residence_handler)
            ],
            PASSPORT_SERIAL: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_passport_serial_handler)
            ],
            PASSPORT_NUMBER: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_passport_number_handler)
            ],
            PASSPORT_ISSUED_BY: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_passport_issued_by_handler)
            ],
            PASSPORT_ISSUED_AT: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_passport_issued_at_handler)
            ],
            CLOSE_PERSON_NAME: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_close_person_name_handler)
            ],
            CLOSE_PERSON_PHONE: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_close_person_phone_handler)
            ],
            CLOSE_PERSON_ADDRESS: [
                MessageHandler(Filters.text & ~Filters.command,
                               editing_close_person_address_handler)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
        ]
    )

    return conv_handler
