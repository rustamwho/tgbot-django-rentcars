import logging
import traceback
import html

import telegram
from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

from dtb.settings import TELEGRAM_LOGS_CHAT_ID
from tgbot.models import User


def send_stacktrace_to_tg_chat(update: Update,
                               context: CallbackContext) -> None:
    u = User.get_user(update, context)

    logging.error("Exception while handling an update:",
                  exc_info=context.error)

    # If user blocked that bot
    if 'bot was blocked by the user' in context.error.__str__():
        u.is_blocked_bot = True
        u.save()
        return

    tb_list = traceback.format_exception(None, context.error,
                                         context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    user_message = ('😔 Прошу прощения, с ботом что-то не так. '
                    'Автору уже отправлена информация об ошибке. '
                    'Устраним проблему в кратчайшие сроки.\n')
    context.bot.send_message(
        chat_id=u.user_id,
        text=user_message,
    )

    admin_message = f"⚠️⚠️⚠️ for {u.tg_str}:\n{message}"[:4090]
    if TELEGRAM_LOGS_CHAT_ID:
        context.bot.send_message(
            chat_id=TELEGRAM_LOGS_CHAT_ID,
            text=admin_message,
            parse_mode=telegram.ParseMode.HTML,
        )
    else:
        logging.error(admin_message)
