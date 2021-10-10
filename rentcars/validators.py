import datetime

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def russian_letters_validator(value: str) -> None:
    """Checking that the string consists only of Russian letters"""
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Я]+$',
        message='Разрешаются только русские буквы.'
    )
    reg_validator(value)


def phone_number_validator(value: str) -> None:
    """Phone number must start with +7 or 8 and contains 11 digits."""
    if not value.startswith('+7') and not value.startswith('8'):
        raise ValidationError('Номер телефона должен начинаться с +7 или с 8.')
    reg_validator = RegexValidator(
        regex=r'(\+7|8)\d{10}',
        message='Номер телефона должен состоять из 11 цифр. '
                'Например, +79999999999')
    reg_validator(value)


def date_validate(value: str) -> None:
    """Date must be in format <dd.mm.yyyy>."""
    reg_validator = RegexValidator(
        regex=r'^(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>\d{4})$',
        message='Дата должна быть в формате ДД.ММ.ГГГГ. Например, 31.12.2021.')
    reg_validator(value)
    day, month, year = (int(x) for x in value.split('.'))
    if day > 31 or month > 12 or year > datetime.date.today().year:
        raise ValidationError(message=('Дата должна быть в формате ДД.ММ.ГГГГ.'
                                       ' Например, 31.12.2021.')
                              )


def birthday_date_validate(born: str) -> None:
    """Person must be of legal age and under 80 years of age."""
    # Validate format of input date string
    if type(born) is not datetime.date:
        date_validate(born)
        born = datetime.datetime.strptime(born, '%d.%m.%Y').date()

    today = datetime.date.today()

    age = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day))

    if age < 18:
        raise ValidationError('Арендатор должен быть совершеннолетним.')
    if age > 80:
        raise ValidationError('Арендатор должен быть младше 80 лет.')


def passport_serial_validator(value: str) -> None:
    """The passport series consists of 4 digits."""
    if not value.isdigit() or len(value) != 4:
        raise ValidationError('Серия паспорта должна состоять из 4 цифр.')


def passport_number_validator(value: str) -> None:
    """The passport number consists of 6 digits."""
    if not value.isdigit() or len(value) != 6:
        raise ValidationError('Номер паспорта должен состоять из 6 цифр.')


def passport_issued_by_validator(value: str):
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Я\s0-9-№]+$',
        message='В строке КЕМ ВЫДАН могут быть только русские буквы, пробелы '
                'и цифры.'
    )
    reg_validator(value)


def address_validator(value: str) -> None:
    """Address contains 'г.', 'ул.', 'д.'."""
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Я.,\s0-9-]+$',
        message='Адрес должен состоять только из русских букв, пробелов, точек'
                ', запятых и тире.'
    )
    reg_validator(value)
    if not all(x in value for x in ('г.', 'ул.', 'д.')):
        raise ValidationError('Требуется полный адрес. Например, Республика '
                              'Татарстан, г. Казань, ул. Баумана, д. 1')


def close_person_name_validator(value: str):
    """
    Close Person name must contains Name and who is he e.g. 'Анна (Жена)'.
    Only Russian letters and brackets.
    """
    reg_validator = RegexValidator(
        regex=r'^([а-яА-Я]+)\s\([а-яА-Я]+\)$',
        message='Имя близкого человека должно быть написано в формате '
                'ИМЯ (КЕМ ПРИХОДИТСЯ). Например, "Юля (Жена)".')
    reg_validator(value)
