import os
import datetime

from django.conf import settings
from django.utils.timezone import now
from django.forms.models import model_to_dict
from docxtpl import DocxTemplate

from tgbot.models import User
from rentcars.models import PersonalData, Car
from general_utils.utils import get_verbose_date


def get_pd_string(pd: PersonalData) -> str:
    """Return string with personal data's of user for contract."""
    result = (f'{pd.last_name} {pd.first_name} {pd.middle_name} '
              f'{get_verbose_date(pd.birthday)} года рождения (пол: '
              f'{"муж" if pd.gender == 0 else "жен"}) обладатель '
              f'паспорта гражданина Российской Федерации серия '
              f'{pd.passport_serial} № {pd.passport_number} выданный '
              f'{pd.passport_issued_by} '
              f'{get_verbose_date(pd.passport_date_of_issue)} г., '
              f'зарегистрированный по адресу')
    if pd.address_registration == pd.address_of_residence:
        result += f' постоянного места жительства: {pd.address_registration}'
    else:
        result += (f': {pd.address_registration}, и проживающий по адресу: '
                   f'{pd.address_of_residence}')

    return result


def create_contract(user: User, car: Car) -> DocxTemplate:
    """
    Return new contract with user.
    See python-docx-template documentation for more information about creating
    templates.
    """

    user_pd_string = get_pd_string(user.personal_data)
    owner_pd_string = get_pd_string(car.owner)

    context = model_to_dict(
        user.personal_data,
        fields=['phone_number', 'email', 'close_person_name',
                'close_person_phone', 'close_person_address']
    )
    context['user_pd_string'] = user_pd_string
    context['owner_pd_string'] = owner_pd_string
    context['year'] = now().year
    context['user_id'] = user.user_id
    context['date'] = get_verbose_date(now().replace(year=now().year + 1))

    doc = DocxTemplate(
        os.path.join(settings.DOCX_TEMPLATES_DIR, 'contract_template.docx'))

    doc.render(context)

    return doc
