import datetime

from django.db import models
from django.utils.timezone import now
from django.core.validators import EmailValidator

from general_utils.models import CreateUpdateTracker
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User

import rentcars.validators as cstm_validators
from rentcars.utils.paths import car_photos_path, contract_photos_path


class PersonalData(CreateUpdateTracker):
    """
    Personal data of user in Russian language.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        primary_key=True,
        related_name='personal_data'
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
        validators=[cstm_validators.phone_number_validator]
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
        validators=[cstm_validators.close_person_name_validator]
    )
    close_person_phone = models.CharField(
        max_length=12,
        validators=[cstm_validators.phone_number_validator],
        verbose_name='Номер близкого человека'
    )
    close_person_address = models.CharField(
        max_length=256,
        verbose_name='Адрес места жительства',
        validators=[cstm_validators.address_validator]
    )

    class Meta:
        verbose_name = 'Персональные данные'
        verbose_name_plural = 'Персональные данные'

    def save(self, *args, **kwargs):
        if self.phone_number.startswith('8'):
            self.phone_number = '+7' + self.phone_number[1:]
        if self.close_person_phone.startswith('8'):
            self.close_person_phone = '+7' + self.close_person_phone[1:]
        if isinstance(self.birthday, str):
            self.birthday = datetime.datetime.strptime(self.birthday,
                                                       '%d.%m.%Y')
        if isinstance(self.passport_date_of_issue, str):
            self.passport_date_of_issue = datetime.datetime.strptime(
                self.passport_date_of_issue, '%d.%m.%Y'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.last_name


class Car(models.Model):
    license_plate = models.CharField(
        max_length=9,
        validators=[cstm_validators.license_plate_validator],
        verbose_name='Регистрационный знак',
    )
    vin = models.CharField(
        max_length=17,
        validators=[cstm_validators.vin_validator],
        verbose_name='VIN',
    )
    model = models.CharField(
        max_length=50,
        verbose_name='Марка, модель',
    )
    type = models.CharField(
        max_length=50,
        verbose_name='Тип ТС',
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
        verbose_name='Экологический класс'
    )
    vehicle_passport_serial = models.CharField(
        max_length=4,
        validators=[cstm_validators.vehicle_passport_serial_validator],
        verbose_name='Серия ПТС',
    )
    vehicle_passport_number = models.CharField(
        max_length=6,
        validators=[cstm_validators.passport_number_validator],
        verbose_name='Номер ПТС'
    )
    max_mass = models.IntegerField(
        verbose_name='Разрешенная max масса, кг'
    )
    sts_serial = models.CharField(
        max_length=4,
        validators=[cstm_validators.sts_serial_validator],
        verbose_name='Серия свидетельства о регистрации ТС'
    )
    sts_number = models.CharField(
        max_length=6,
        validators=[cstm_validators.sts_number_validator],
        verbose_name='Номер свидетельства о регистрации ТС'
    )

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'

    def __str__(self):
        return self.license_plate

    @property
    def is_busy(self):
        rented = Contract.objects.filter(closed_at__gte=now().date(),
                                         car=self).exists()
        return rented


class PhotoCar(models.Model):
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
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='contract'
    )

    file = models.FileField(
        verbose_name='Файл договора',
        upload_to='contracts/files/'
    )

    is_approved = models.BooleanField(
        verbose_name='Подтвержден',
        default=False
    )

    car = models.ForeignKey(
        Car,
        on_delete=models.PROTECT,
        related_name='car',
        blank=True,
        null=True,
        verbose_name='Машина',
    )

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name='Дата формирования договора'
    )
    closed_at = models.DateField(
        verbose_name='Дата завершения действия договора'
    )

    def __str__(self):
        return self.user.username if self.user.username else str(
            self.user.user_id)

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договоры'


class PhotoCarContract(models.Model):
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
