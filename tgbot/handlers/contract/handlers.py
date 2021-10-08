import datetime
import io

from telegram import ParseMode, Update
from telegram.ext.callbackcontext import CallbackContext
from django.core.files import File

from general_utils.utils import get_verbose_date
from tgbot.models import User

from rentcars.utils.contracts import create_contract
from rentcars.models import Contract


def start_contract(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)

    new_contract = create_contract(u)
    new_contract_io = io.BytesIO()
    new_contract.save(new_contract_io)
    new_contract_io.seek(0)
    contr = Contract(
        user=u,
        file=File(new_contract_io, name=u.username + '.docx'),
        closed_at=datetime.date.today()
    )
    contr.save()
    context.bot.send_document(
        chat_id=u.user_id,
        document=contr.file,
        filename=(u.last_name + ' ' + u.first_name + ' ' +
                  get_verbose_date(contr.created_at) + '.docx')
    )
