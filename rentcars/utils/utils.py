from rentcars.utils.constants import trans_dict_eng_rus


def transliterate_license_plate(license_plate: str) -> str:
    """Return License plate in russian language."""
    for symbol in license_plate:
        if symbol.isalpha():
            license_plate = license_plate.replace(symbol,
                                                  trans_dict_eng_rus[symbol])
    return license_plate
