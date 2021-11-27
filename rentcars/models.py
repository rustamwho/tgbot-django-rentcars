import datetime

from django.db import models
from django.utils.timezone import now, localtime
from django.utils import timezone
from django.core.validators import EmailValidator

from general_utils.models import CreateUpdateTracker
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User

import rentcars.validators as cstm_validators
from rentcars.utils.paths import (car_photos_path, contract_photos_path,
                                  fine_screens_path)
from rentcars.utils.utils import transliterate_license_plate


class PersonalData(CreateUpdateTracker):
    """
    Personal data of user in Russian language.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='personal_data',
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        validators=[cstm_validators.russian_letters_validator]
    )
    middle_name = models.CharField(
        max_length=100,
        verbose_name='Отчество',
        validators=[cstm_validators.russian_letters_validator]
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
        validators=[cstm_validators.russian_letters_validator]
    )

    gender = models.IntegerField(choices=GENDER_CHOICES, verbose_name='Пол')

    birthday = models.DateField(
        auto_now=False,
        verbose_name='Дата рождения',
        validators=[cstm_validators.birthday_date_validate]
    )

    email = models.EmailField(
        max_length=70,
        validators=[EmailValidator(
            message='Адрес электронной почты должен быть правильным. '
                    'Например, rustamwho@mail.com')],
        verbose_name='Почта'
    )

    phone_number = models.CharField(
        max_length=12,
        validators=[cstm_validators.phone_number_validator],
        verbose_name='Номер телефона'
    )

    passport_serial = models.CharField(
        max_length=4,
        verbose_name='Серия паспорта',
        validators=[cstm_validators.passport_serial_validator]
    )
    passport_number = models.CharField(
        max_length=6,
        verbose_name='Номер паспорта',
        validators=[cstm_validators.passport_number_validator]
    )
    passport_date_of_issue = models.DateField(
        auto_now=False,
        verbose_name='Дата выдачи паспорта'
    )
    passport_issued_by = models.CharField(
        max_length=255,
        verbose_name='Кем выдан паспорт',
        validators=[cstm_validators.passport_issued_by_validator]
    )

    address_registration = models.CharField(
        max_length=256,
        verbose_name='Адрес прописки',
        validators=[cstm_validators.address_validator]
    )
    address_of_residence = models.CharField(
        max_length=256,
        verbose_name='Адрес места жительства',
        validators=[cstm_validators.address_validator]
    )

    close_person_name = models.CharField(
        max_length=50,
        verbose_name='Близкий человек',
        validators=[cstm_validators.close_person_name_validator],
        null=True,
        blank=True,
        help_text=('Должен быть в формате "ИМЯ (КЕМ ПРИХОДИТСЯ)", '
                   'например Юля (Жена)')
    )
    close_person_phone = models.CharField(
        max_length=12,
        validators=[cstm_validators.phone_number_validator],
        verbose_name='Номер близкого человека',
        null=True,
        blank=True,

    )
    close_person_address = models.CharField(
        max_length=256,
        verbose_name='Адрес места жительства близкого человека',
        validators=[cstm_validators.address_validator],
        null=True,
        blank=True,
        help_text='Адрес обязательно должен содержать "ул." и "д."'
    )

    class Meta:
        verbose_name = 'Персональные данные'
        verbose_name_plural = 'Персональные данные'

    def save(self, *args, **kwargs):
        # All numbers in database saved as starts with '+7'
        if self.phone_number.startswith('8'):
            self.phone_number = '+7' + self.phone_number[1:]
        if self.close_person_phone and self.close_person_phone.startswith('8'):
            self.close_person_phone = '+7' + self.close_person_phone[1:]

        # For dates from bot (received in str)
        if isinstance(self.birthday, str):
            self.birthday = datetime.datetime.strptime(self.birthday,
                                                       '%d.%m.%Y')
        if isinstance(self.passport_date_of_issue, str):
            self.passport_date_of_issue = datetime.datetime.strptime(
                self.passport_date_of_issue, '%d.%m.%Y'
            )

        # Capitalize all names
        self.last_name = self.last_name.capitalize()
        self.first_name = self.first_name.capitalize()
        self.middle_name = self.middle_name.capitalize()
        if self.close_person_name:
            self.close_person_name = self.close_person_name.title()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.last_name} {self.first_name} {self.middle_name}'


class Car(models.Model):
    """Data of car."""
    license_plate = models.CharField(
        max_length=9,
        validators=[cstm_validators.license_plate_validator],
        verbose_name='Регистрационный знак',
        help_text='Регистрационный знак автомобиля должен быть в формате '
                  '"X999XX999" (В базу сохраняется на русском языке)',
    )
    vin = models.CharField(
        max_length=17,
        validators=[cstm_validators.vin_validator],
        verbose_name='VIN',
        help_text='VIN-номер автомобиля, состоящий из 17 символов',
    )
    model = models.CharField(
        max_length=50,
        verbose_name='Марка, модель',
        help_text='Полное название машины, например, "Toyota Camry"',
    )
    type = models.CharField(
        max_length=50,
        verbose_name='Тип ТС',
        help_text='Например, "Легковой"',
    )
    category = models.CharField(
        max_length=1,
        validators=[cstm_validators.vehicle_category_validator],
        verbose_name='Категория ТС',
        help_text='Одна английская буква из ABCD',
    )
    year_manufacture = models.CharField(
        max_length=4,
        validators=[cstm_validators.vehicle_manufactured_year_validator],
        verbose_name='Год выпуска',
    )
    color = models.CharField(
        max_length=50,
        verbose_name='Цвет ТС',
    )
    power = models.IntegerField(
        verbose_name='Мощность двигателя, л.с.'
    )
    ecological_class = models.CharField(
        max_length=20,
        verbose_name='Экологический класс',
        help_text='Цифра или слово, например, "ПЯТЫЙ"',
    )
    vehicle_passport_serial = models.CharField(
        max_length=4,
        validators=[cstm_validators.vehicle_passport_serial_validator],
        verbose_name='Серия ПТС',
        help_text='Серия паспорта ТС должна быть в формате 00АА',
    )
    vehicle_passport_number = models.CharField(
        max_length=6,
        validators=[cstm_validators.passport_number_validator],
        verbose_name='Номер ПТС',
        help_text='6 цифр',
    )
    max_mass = models.IntegerField(
        verbose_name='Разрешенная max масса, кг',
    )
    sts_serial = models.CharField(
        max_length=4,
        validators=[cstm_validators.sts_serial_validator],
        verbose_name='Серия СТС',
        help_text='Серия свидетельства о регистрации ТС (4 цифры)'
    )
    sts_number = models.CharField(
        max_length=6,
        validators=[cstm_validators.sts_number_validator],
        verbose_name='Номер СТС',
        help_text='Номер свидетельства о регистрации ТС (6 цифр)'
    )
    owner = models.ForeignKey(
        PersonalData,
        on_delete=models.PROTECT,
        related_name='cars',
        verbose_name='Владелец авто',
        help_text='Выберите из списка владельца авто'
    )

    def save(self, *args, **kwargs):
        self.license_plate = transliterate_license_plate(self.license_plate)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'
        ordering = ['license_plate']

    def __str__(self):
        return self.license_plate

    @property
    def is_busy(self):
        return self.contracts.filter(closed_at__gte=now()).exists()

    @classmethod
    def get_busy_cars(cls):
        return cls.objects.filter(contracts__closed_at__gte=now().date())

    def get_short_info(self):
        """Return info 'LICENSE_PLATE - MODEL' for current car."""
        return f'{self.license_plate} - {self.model}'


class PhotoCar(models.Model):
    """Model for saving of car photos."""
    image = models.ImageField(
        verbose_name='Фотографии машины',
        upload_to=car_photos_path,
    )
    file_id = models.CharField(
        verbose_name='ID фотографии на серверах Telegram',
        max_length=250,
        blank=True,
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='images'
    )

    class Meta:
        verbose_name = 'Фотография машины'
        verbose_name_plural = 'Фотографии машины'


class Contract(models.Model):
    """Contract with user."""
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='contracts',
        verbose_name='Арендатор',
        help_text='Пользователь телеграма6 нужно выбрать из списка',
    )

    file = models.FileField(
        verbose_name='Файл договора',
        upload_to='contracts/files/',
        help_text='.docx файл'
    )

    is_approved = models.BooleanField(
        verbose_name='Подтвержден',
        default=False,
        help_text='Подтвержден ли договор администратором '
                  '(После подтверждения машина считается арендованной)',
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='contracts',
        blank=True,
        null=True,
        verbose_name='Машина',
        help_text='Арендуемая машина (Выбрать из списка)',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время формирования договора'
    )
    approved_at = models.DateTimeField(
        verbose_name='Дата и время подтверждения договора',
        blank=True,
        null=True,
        help_text='Дата и время, с которого договор начинает действовать'
    )
    closed_at = models.DateTimeField(
        verbose_name='Дата и время завершения действия договора',
        null=True
    )

    def __str__(self):
        return f'№{self.id} от {self.get_created_at_in_str()}'

    @property
    def is_active(self):
        return self.closed_at >= now() if self.closed_at else True

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'

    def get_created_at_in_str(self):
        return localtime(self.created_at).strftime('%d.%m.%Y %H:%M')

    def get_approved_at_in_str(self):
        if self.approved_at:
            return localtime(self.approved_at).strftime('%d.%m.%Y %H:%M')
        return None

    def get_closed_at_in_str(self):
        if self.closed_at:
            return localtime(self.closed_at).strftime('%d.%m.%Y %H:%M')
        return None

    def get_short_info(self):
        pd = self.user.personal_data
        return (f'{pd.last_name} {pd.first_name[0]}.{pd.middle_name[0]}. '
                f'от {self.get_approved_at_in_str()} '
                f'({self.car.license_plate[:-3]})')

    def get_full_name_user(self):
        pd = self.user.personal_data
        return f'{pd.last_name} {pd.first_name[0]}.{pd.middle_name[0]}.'

    @classmethod
    def get_active_contracts(cls):
        return cls.objects.filter(closed_at__gte=now())


class PhotoCarContract(models.Model):
    """ Model for saving car's photos of contract. """
    image = models.ImageField(
        verbose_name='Фотографии машины',
        upload_to=contract_photos_path,
    )
    file_id = models.CharField(
        verbose_name='ID фотографии на серверах Telegram',
        max_length=250,
        blank=True,
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='car_photos'
    )

    class Meta:
        verbose_name = 'Фотография машины во время заключения договора'
        verbose_name_plural = 'Фотографии машины во время заключения договора'


class Fine(models.Model):
    """ Fine model. """
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='fines',
        verbose_name='Машина',
        help_text='Оштрафованная машина (выбрать из списка)',
    )
    datetime = models.DateTimeField(
        verbose_name='Дата и время штрафа',
        null=True,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма штрафа, руб.',
    )
    screenshot = models.ImageField(
        verbose_name='Скриншот штрафа',
        upload_to=fine_screens_path,
        blank=True,
        null=True,
    )
    screenshot_id = models.CharField(
        verbose_name='ID скриншота на серверах Telegram',
        max_length=250,
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='fines',
        blank=True,
        null=True,
        verbose_name='Водитель',
        help_text='Заполнится автоматически после сохранения!',
    )
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='fines',
        blank=True,
        null=True,
        verbose_name='Договор',
        help_text='Заполнится автоматически после сохранения!',
    )
    is_paid = models.BooleanField(
        verbose_name='Штраф оплачен',
        default=False,
    )

    class Meta:
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'
        ordering = ['is_paid', '-datetime']

    def __str__(self):
        return f'{self.amount} - {self.car} - {self.get_datetime_in_str()}'

    def save(self, *args, **kwargs):
        if isinstance(self.datetime, str):
            self.datetime = datetime.datetime.strptime(
                self.datetime,
                '%d.%m.%Y %H:%M').astimezone(
                tz=timezone.get_current_timezone()
            )
        if not self.contract:
            valid_contr = Contract.objects.filter(
                approved_at__lte=self.datetime,
                closed_at__gte=self.datetime,
                car=self.car)
            if valid_contr.exists():
                self.contract = Contract.objects.get(
                    approved_at__lte=self.datetime,
                    closed_at__gte=self.datetime,
                    car=self.car,
                )
                self.user = self.contract.user
        super().save(*args, *kwargs)

    def get_date_in_str(self):
        """Return date of fine in str 'dd.mm.yyyy' format."""
        return self.datetime.strftime('%d.%m.%Y')

    def get_datetime_in_str(self):
        return localtime(self.datetime).strftime('%d.%m.%Y %H:%M')

    def get_short_info(self):
        text = f'{self.get_datetime_in_str()} - {self.amount} руб. '
        if self.car:
            text += str(self.car.license_plate[:-3])
        return text
