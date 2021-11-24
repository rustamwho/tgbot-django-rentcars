import io
import csv

from pytils.translit import slugify

from telegram.ext.callbackcontext import CallbackContext
from datetime import datetime
from django.db.models import QuerySet
from django.utils.timezone import now
from django.core.files import File
from typing import Dict

from tgbot.models import User

from rentcars.models import Contract, Fine, PersonalData, Car
from rentcars.utils.contracts import create_contract


def _get_csv_from_qs_values(queryset: QuerySet[Dict], filename: str = 'users'):
    keys = queryset[0].keys()

    # csv module can write data in io.StringIO buffer only
    s = io.StringIO()
    dict_writer = csv.DictWriter(s, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(queryset)
    s.seek(0)

    # python-telegram-bot library can send files only from io.BytesIO buffer
    # we need to convert StringIO to BytesIO
    buf = io.BytesIO()

    # extract csv-string, convert it to bytes and write to buffer
    buf.write(s.getvalue().encode())
    buf.seek(0)

    # set a filename with file's extension
    buf.name = f"{filename}__{datetime.now().strftime('%Y.%m.%d.%H.%M')}.csv"

    return buf


def get_text_all_users():
    """Return text with ALL users."""
    users_list = User.objects.all()

    text = ''
    users_without_pd = []
    i = 1

    for u in users_list:
        if hasattr(u, 'personal_data'):
            user_t = (u.personal_data.last_name + ' ' +
                      u.personal_data.first_name + ' ' +
                      u.personal_data.middle_name)
            text += f'{i}. {user_t}. @{u.username}\n'
            i += 1
        else:
            users_without_pd.append(u)

    if not users_without_pd:
        return text

    text += '\nПользователи без персональных данных:\n'

    users_without_username = []

    for u in users_without_pd:
        if u.username is not None:
            text += f'{i}. @{u.username}\n'
        else:
            users_without_username.append(u)
        i += 1

    if not users_without_username:
        return text

    text += '\nПользователи без никнейма в телеграме:\n'

    for u in users_without_username:
        text += f'{i}. Telegram ID - {u.user_id}'
        i += 1

    return text


def get_text_all_arendators():
    """
    Return text with arendators and the remaining days of the contract with
    them.
    """
    arendators = User.objects.filter(contracts__closed_at__gte=now())

    text = 'Действующие договоры:\n'
    for i, u in enumerate(arendators, 1):
        name = (u.personal_data.last_name + ' ' +
                u.personal_data.first_name[0] + '. ' +
                u.personal_data.middle_name[0] + '.')
        valid_contract: Contract = u.get_active_contract()
        days = (valid_contract.closed_at - now()).days
        if valid_contract.car:
            text += (
                f'{i}. {name} ({valid_contract.car.license_plate} - '
                f'осталось {days} дней)\n'
                f'Начало аренды: {valid_contract.get_approved_at_in_str()}\n'
                f'Конец аренды: {valid_contract.get_closed_at_in_str()}\n\n')
        else:
            text += (f'{i}. {name} (Машина не назначена - '
                     f'осталось {days} дней)\n\n')

    return text


def get_text_all_fines():
    """Return text for all fines with license plate of car, date and user."""
    if not Fine.objects.exists():
        return 'Штрафов нет'
    text = 'Все штрафы:\n'
    for i, fine in enumerate(Fine.objects.all().order_by('-datetime'), 1):
        if fine.user:
            pd: PersonalData = fine.user.personal_data
            row = (f'{fine.car.license_plate[:-3]} - {fine.amount} руб. '
                   f'{fine.get_datetime_in_str()} - '
                   f'{pd.last_name} {pd.first_name[0]}.'
                   f'{pd.middle_name[0]}.\n')
            text += f'{i}. {row}'
        else:
            text += (
                f'{i}. {fine.car.license_plate[:-3]} - {fine.amount} руб. '
                f'{fine.get_datetime_in_str()}\n')

    return text


def get_text_paid_fines():
    """Return text for paid fines with license plate of car, date and user."""
    paid_fines = Fine.objects.filter(is_paid=True).order_by('-datetime')
    if not paid_fines.exists():
        return 'Оплаченных штрафов нет'
    text = 'Оплаченные штрафы:\n'
    for i, fine in enumerate(paid_fines, 1):
        if fine.user:
            pd: PersonalData = fine.user.personal_data
            row = (f'{fine.car.license_plate[:-3]} - {fine.amount} руб. '
                   f'{fine.get_datetime_in_str()} - '
                   f'{pd.last_name} {pd.first_name[0]}.'
                   f'{pd.middle_name[0]}.\n')
            text += f'{i}. {row}'
        else:
            text += (
                f'{i}. {fine.car.license_plate[:-3]} - {fine.amount} руб. '
                f'{fine.get_datetime_in_str()}\n')

    return text


def get_text_unpaid_fines():
    """Return text for unpaid fines with license plate of car, date, user."""
    unpaid_fines = Fine.objects.filter(is_paid=False).order_by('-datetime')
    if not unpaid_fines.exists():
        return 'Неоплаченных штрафов нет'
    text = 'Неоплаченные штрафы:\n'
    for i, fine in enumerate(unpaid_fines, 1):
        if fine.user:
            pd: PersonalData = fine.user.personal_data
            row = (f'{fine.car.license_plate[:-3]} - {fine.amount} руб. '
                   f'{fine.get_datetime_in_str()} - '
                   f'{pd.last_name} {pd.first_name[0]}.'
                   f'{pd.middle_name[0]}.\n')
            text += f'{i}. {row}'
        else:
            text += (
                f'{i}. {fine.car.license_plate[:-3]} - {fine.amount} руб. '
                f'{fine.get_datetime_in_str()}\n')

    return text


def create_and_save_contract_file(contract: Contract, admin_id: int,
                                  context: CallbackContext) -> None:
    """Create contract .docx with user and save Contract object."""
    u = contract.user
    # Create new contract file
    new_contract = create_contract(contract.user, contract.car)

    # Create Contract object with new contract file
    contract_file_io = io.BytesIO()
    new_contract.save(contract_file_io)
    contract_file_io.seek(0)
    contract.file = File(contract_file_io,
                         name=(slugify(contract.user.personal_data.last_name) +
                               str(now().date()) + '.docx'))

    contract.save()

    context.bot.send_document(
        chat_id=u.user_id,
        document=contract.file,
        filename=contract.file.name,
        caption=('❗ Сформирован договор. Его надо будет распечатать '
                 'и подписать.')
    )

    pd = contract.user.personal_data
    user_name = f'{pd.last_name} {pd.first_name[0]}.{pd.middle_name[0]}.'
    contract_closed_at = contract.get_closed_at_in_str()
    text_for_admin = (
        f'❗ Сформирован новый договор с {user_name}\n'
        f'📍 Срок действия договора - до {contract_closed_at}.'
    )
    contract = u.get_active_contract()
    context.bot.send_document(
        chat_id=admin_id,
        document=contract.file,
        filename=contract.file.name,
        caption=text_for_admin
    )
