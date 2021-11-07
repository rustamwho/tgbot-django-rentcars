from rentcars.models import Fine


def get_text_with_fines(fines: list[Fine]) -> str:
    """Return text with short info for all received fines."""
    text = ''
    for i, fine in enumerate(fines, 1):
        text += f'{i}. {fine.get_short_info()}\n'

    return text
