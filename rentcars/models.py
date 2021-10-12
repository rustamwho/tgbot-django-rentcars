import datetime

from django.db import models
from django.core.validators import EmailValidator

from general_utils.models import CreateUpdateTracker
from general_utils.constants import GENDER_CHOICES
from tgbot.models import User

import rentcars.validators as cstm_validators


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


class Contract(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='contract'
    )

    file = models.FileField(
        verbose_name='Файл договора',
        upload_to='contracts/'
    )

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name='Дата формирования договора'
    )
    closed_at = models.DateField(
        verbose_name='Дата завершения действия договора'
    )

    def __str__(self):
        return self.user.username
