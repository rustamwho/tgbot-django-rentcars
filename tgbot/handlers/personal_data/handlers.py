import datetime
import io

from django.forms.models import model_to_dict

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (MessageHandler, ConversationHandler, Filters,
                          CommandHandler, CallbackQueryHandler)

from general_utils.constants import GENDER_CHOICES

from tgbot.models import User
from tgbot.handlers.personal_data import static_text
from tgbot.handlers.personal_data import keyboard_utils


def get_my_personal_data_handler(update: Update,
                                 context: CallbackContext) -> None:
    u = User.get_user(update, context)
    pd = model_to_dict(u.personal_data, exclude='user')

    pd['gender'] = GENDER_CHOICES[pd['gender']][1]
    pd['birthday'] = datetime.date.strftime(pd['birthday'], '%d.%m.%Y')
    pd['passport_date_of_issue'] = datetime.date.strftime(
        pd['passport_date_of_issue'], '%d.%m.%Y'
    )

    text = static_text.PERSONAL_DATA.format(**pd)

    update.message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_utils.get_personal_data_edit_keyboard(),
    )
