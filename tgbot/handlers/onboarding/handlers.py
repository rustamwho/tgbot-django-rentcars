from telegram import Update
from telegram.ext.callbackcontext import CallbackContext

from tgbot.handlers.onboarding import static_text

from tgbot.models import User


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    update.message.reply_text(text=text)
    context.bot.send_message(
        chat_id=u.user_id,
        text=static_text.ANSWER_TO_UNKNOWN
    )


def answer_to_unknown(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text=static_text.ANSWER_TO_UNKNOWN
    )
