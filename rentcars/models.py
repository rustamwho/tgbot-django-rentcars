from django.db import models
from django.core.validators import EmailValidator

from utils.models import CreateUpdateTracker
from tgbot.models import User

import rentcars.validators as cstm_validators


class PersonalData(CreateUpdateTracker):
    """
    Personal data of user in Russian language.
    """
    GENDER_CHOICES = ((0, 'Мужской'), (1, 'Женский'))
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

    class Meta:
        verbose_name = 'Персональные данные'
        verbose_name_plural = 'Персональные данные'

    def save(self, *args, **kwargs):
        if self.phone_number.startswith('8'):
            self.phone_number = '+7' + self.phone_number[1:]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.last_name
