# Generated by Django 3.2.9 on 2021-11-07 16:08

from django.db import migrations, models
import rentcars.validators


class Migration(migrations.Migration):

    dependencies = [
        ('rentcars', '0016_auto_20211106_1328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='sts_number',
            field=models.CharField(help_text='Номер свидетельства о регистрации ТС', max_length=6, validators=[rentcars.validators.sts_number_validator], verbose_name='Номер СТС'),
        ),
        migrations.AlterField(
            model_name='car',
            name='sts_serial',
            field=models.CharField(help_text='Серия свидетельства о регистрации ТС', max_length=4, validators=[rentcars.validators.sts_serial_validator], verbose_name='Серия СТС'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='closed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения действия договора'),
        ),
    ]
