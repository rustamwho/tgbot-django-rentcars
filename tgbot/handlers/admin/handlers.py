from datetime import timedelta
from typing import Callable

from django.utils.timezone import now

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext

from tgbot.handlers.admin import static_text, utils
from tgbot.models import User


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
def admin(update: Update, context) -> None:
    """ Show help info about all secret admins commands """
    update.message.reply_text(static_text.secret_admin_commands)


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
    context.bot.send_document(chat_id=u.user_id, document=csv_users)


@admin_only_handler
def get_all_users_handler(update: Update, context: CallbackContext) -> None:
    text = utils.get_text_all_users()
    update.message.reply_text(
        text=text
    )
