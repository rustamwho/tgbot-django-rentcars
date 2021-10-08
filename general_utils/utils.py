import datetime


def get_verbose_date(date: datetime.date) -> str:
    """Return date in string 'dd.mm.yyyy' format"""
    return datetime.date.strftime(date, '%d.%m.%Y')
