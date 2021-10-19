from datetime import timedelta
from typing import Callable

from django.utils.timezone import now

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext

from general_utils.utils import get_verbose_date

from tgbot.handlers.admin import (static_text, utils, keyboard_utils,
                                  manage_data)
from tgbot.models import User

from rentcars.models import Contract, PersonalData


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
        keyboard = keyboard_utils.get_approve_contract_keyboard(
            unapproved_contract.id
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

        context.bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )


@admin_only_handler
def admin_commands_handler(update: Update, context) -> None:
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
        # else edit message about
        if unapproved:
            query.edit_message_text(
                text=static_text.NOW_SEND_UNAPPROVED_CONTRACTS
            )
            send_unapproved_contracts(chat_id, context)
        else:
            if current_text != static_text.UNAPPROVED_CONTACTS_NOT_EXISTS:
                query.edit_message_text(
                    text=static_text.UNAPPROVED_CONTACTS_NOT_EXISTS,
                    reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
                )
            else:
                query.edit_message_text(
                    text=static_text.UNAPPROVED_CONTACTS_NOT_EXISTS2,
                    reply_markup=keyboard_utils.get_admin_main_menu_keyboard()
                )
    # Approving contract
    elif data.startswith(manage_data.BASE_FOR_APPROVE_CONTRACT):
        contract_id = int(data.split('_')[-1])
        current_contract = Contract.objects.get(id=contract_id)
        current_contract.is_approved = True
        current_contract.save()

        query.edit_message_text(
            text=current_text + static_text.CONTRACT_IS_APPROVED
        )
