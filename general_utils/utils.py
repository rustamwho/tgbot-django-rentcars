import datetime

from django.forms.models import model_to_dict

from rentcars.models import Car, User
from general_utils.constants import GENDER_CHOICES_DICT
from general_utils.static_text import PERSONAL_DATA


def get_verbose_date(date: datetime.date) -> str:
    """Return date in string 'dd.mm.yyyy' format."""
    return datetime.date.strftime(date, '%d.%m.%Y')


def get_text_about_car(car: Car) -> str:
    text = ''
    for field in car._meta.concrete_fields:
        if field.name == 'id':
            continue
        text += (f'📍<b>{field.verbose_name}:</b> '
                 f'{car.__getattribute__(field.name)}\n')
    return text


def get_finish_personal_data(user: User) -> str:
    """Beautiful formatting text with personal data's."""

    pd = model_to_dict(user.personal_data, exclude='user')

    pd['gender'] = GENDER_CHOICES_DICT[pd['gender']]
    pd['birthday'] = datetime.date.strftime(pd['birthday'], '%d.%m.%Y')
    pd['passport_date_of_issue'] = datetime.date.strftime(
        pd['passport_date_of_issue'], '%d.%m.%Y'
    )

    text = PERSONAL_DATA.format(**pd)

    return text
