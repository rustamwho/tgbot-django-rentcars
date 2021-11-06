import datetime

from rentcars.models import Car


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
