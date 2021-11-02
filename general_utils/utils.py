import datetime

from general_utils.constants import trans_dict_eng_rus


def get_verbose_date(date: datetime.date) -> str:
    """Return date in string 'dd.mm.yyyy' format."""
    return datetime.date.strftime(date, '%d.%m.%Y')


def transliterate_license_plate(license_plate: str) -> str:
    """Return License plate in russian language."""
    for symbol in license_plate:
        if symbol.isalpha():
            print('ras')
            license_plate = license_plate.replace(symbol,
                                                  trans_dict_eng_rus[symbol])
    return license_plate
