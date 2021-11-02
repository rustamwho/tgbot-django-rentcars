# Generated by Django 3.2.7 on 2021-11-01 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_delete_location'),
        ('rentcars', '0011_auto_20211023_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='car', to='rentcars.car', verbose_name='Машина'),
        ),
        migrations.CreateModel(
            name='Fine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата штрафа')),
                ('amount', models.PositiveIntegerField(verbose_name='Сумма штрафа')),
                ('car', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fines', to='rentcars.car', verbose_name='Машина')),
                ('contract', models.ForeignKey(blank=True, help_text='Заполнится автоматически после сохранения!', on_delete=django.db.models.deletion.CASCADE, to='rentcars.contract', verbose_name='Договор')),
                ('user', models.ForeignKey(blank=True, help_text='Заполнится автоматически после сохранения!', on_delete=django.db.models.deletion.CASCADE, to='tgbot.user', verbose_name='Водитель')),
            ],
            options={
                'verbose_name': 'Штраф',
                'verbose_name_plural': 'Штрафы',
            },
        ),
    ]
