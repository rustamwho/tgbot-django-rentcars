import io
import csv

from datetime import datetime
from django.db.models import QuerySet
from django.utils.timezone import now
from typing import Dict

from tgbot.models import User

from rentcars.models import Contract


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
    arendators = User.objects.filter(contracts__closed_at__gte=now().date())

    text = 'Действующие договоры:\n'
    for i, u in enumerate(arendators, 1):
        name = (u.personal_data.last_name + ' ' +
                u.personal_data.first_name[0] + '. ' +
                u.personal_data.middle_name[0] + '.')
        valid_contract: Contract = u.get_active_contract()
        days = (valid_contract.closed_at - now().date()).days
        if valid_contract.car:
            text += (f'{i}. {name} ({valid_contract.car.license_plate} - '
                     f'осталось {days} дней)\n')
        else:
            text += (f'{i}. {name} (Машина не назначена - '
                     f'осталось {days} дней)\n')

    return text
