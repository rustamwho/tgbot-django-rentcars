# Generated by Django 3.2.7 on 2021-11-02 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentcars', '0013_fine_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='approved_at',
            field=models.DateField(blank=True, null=True, verbose_name='Дата подтверждения договора'),
        ),
    ]
