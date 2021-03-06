import datetime

from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def ru_eng_letters_validator(value: str) -> None:
    """Checking that the string consists only of Russian letters."""
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-Z-]+$',
        message='Разрешаются только русские/английские буквы и -.'
    )
    reg_validator(value)


def phone_number_validator(value: str) -> None:
    """Phone number must start with +7 or 8 and contains 11 digits."""
    if not value.startswith('+7') and not value.startswith('8'):
        raise ValidationError('Номер телефона должен начинаться с +7 или с 8.')
    reg_validator = RegexValidator(
        regex=r'^(\+7|8)\d{10}$',
        message='Номер телефона должен состоять из 11 цифр. '
                'Например, +79999999999')
    reg_validator(value)


def date_validate(value: str) -> None:
    """Date must be in format <dd.mm.yyyy>."""
    reg_validator = RegexValidator(
        regex=r'^\d{1,2}\.\d{1,2}\.\d{4}$',
        message='Дата должна быть в формате ДД.ММ.ГГГГ. Например, 31.12.2021.')
    reg_validator(value)
    day, month, year = (int(x) for x in value.split('.'))
    if day > 31 or month > 12 or year > datetime.date.today().year:
        raise ValidationError(message=('Дата должна быть в формате ДД.ММ.ГГГГ.'
                                       ' Например, 31.12.2021.')
                              )


def time_validate(value: str) -> None:
    reg_validator = RegexValidator(
        regex=r'^[0-2]?[0-9]?:[0-5]?[0-9]?$',
        message='Время должно быть в формате ЧЧ:ММ. Например, 14:35.'
    )
    reg_validator(value)


def birthday_date_validate(born: str) -> None:
    """Person must be of legal age and under 80 years of age."""
    # Validate format of input date string
    if type(born) is not datetime.date:
        date_validate(born)
        born = datetime.datetime.strptime(born, '%d.%m.%Y').date()

    today = datetime.date.today()

    age = today.year - born.year - (
            (today.month, today.day) < (born.month, born.day))

    if age < 21:
        raise ValidationError('Арендатор должен быть старше 21 года.')
    if age > 80:
        raise ValidationError('Арендатор должен быть младше 80 лет.')


def passport_serial_validator(value: str) -> None:
    """The passport series consists of 4 digits."""
    if not value.isdigit() or len(value) != 4:
        raise ValidationError('Серия паспорта должна состоять из 4 цифр.')


def passport_number_validator(value: str) -> None:
    """The passport number consists of 6 digits."""
    reg_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9]+$',
        message='Номер паспорта может содержать только английские буквы и '
                'цифры.'
    )
    reg_validator(value)


def passport_issued_by_validator(value: str):
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Яa-zA-Z\s0-9-№.]+$',
        message='В строке КЕМ ВЫДАН могут быть только русские/английские'
                'буквы, пробелы и цифры.'
    )
    reg_validator(value)


def address_validator(value: str) -> None:
    """Address contains 'ул.', 'д.'."""
    reg_validator = RegexValidator(
        regex=r'^[а-яА-Я.,\s0-9-/№]+$',
        message='Адрес должен состоять только из русских букв, пробелов, точек'
                ', запятых и тире.'
    )
    reg_validator(value)
    if not all(x in value for x in ('ул.', 'д.')):
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


"""
Validators for Car
"""


def license_plate_validator(value: str):
    """
    License plate must must be in allowed formats. For more:
    https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Russia
    """
    reg_validator = RegexValidator(
        regex=r'^[АВЕКМНОРСТУХавекмнорстухABEKMHOPCTYXabekmhopcty]{1}'
              r'\d{3}(?<!000)'
              r'[АВЕКМНОРСТУХавекмнорстухABEKMHOPCTYXabekmhopcty]{2}\d{2,3}$'
              r'|'
              r'^[АВЕКМНОРСТУХавекмнорстухABEKMHOPCTYXabekmhopcty]{2}'
              r'\d{3}(?<!000)'
              r'\d{2,3}$',
        message='Регистрационный знак автомобиля должен быть в одном из '
                'следующих форматов:\n'
                '- X999XX999 или X999XX99 для обычных машин\n'
                '- XX999999 для такси\n\nПо ГОСТ номер может содержать '
                'только буквы АВЕКМНОРСТУХ и цифры.'
    )
    reg_validator(value)


def vin_validator(value: str):
    """Validator for Vehicle identification number."""
    reg_validator = RegexValidator(
        regex=r'^[0-9ABCDEFGHJKLMNPRSTUVWXYZ]{17}$',
        message='Идентификационный номер (VIN) автомобиля по ГОСТ состоит из '
                '17 символов. Разрешаются английские буквы и цифры.'
    )
    reg_validator(value)


def vehicle_category_validator(value: str):
    """Validator for the category of vehicle"""
    reg_validator = RegexValidator(
        regex=r'^[ABCDabcd]{1}$',
        message='Категория автомобиля обозначается одной английской буквой '
                'ABCD.'
    )
    reg_validator(value)


def vehicle_manufactured_year_validator(value: str):
    """Validator for the year of manufacture of vehicle."""
    now_year = datetime.date.today().year
    if (not value.isdigit() or
            len(value) != 4 or
            not 1900 < int(value) <= now_year):
        raise ValidationError('Год выпуска должен быть правильным.')


def vehicle_passport_serial_validator(value: str):
    """Validator for the serial of vehicle passport."""
    reg_validator = RegexValidator(
        regex=r'^[0-9]{2}[А-ЯA-Z]{2}',
        message='Серия паспорта ТС должна быть в формате 00АА.'
    )
    reg_validator(value)


def sts_serial_validator(value: str) -> None:
    """The passport series consists of 4 digits."""
    if not value.isdigit() or len(value) != 4:
        raise ValidationError('Серия СТС должна состоять из 4 цифр.')


def sts_number_validator(value: str) -> None:
    """The passport number consists of 6 digits."""
    if not value.isdigit() or len(value) != 6:
        raise ValidationError('Номер СТС должен состоять из 6 цифр.')
