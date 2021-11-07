# Generated by Django 3.2.9 on 2021-11-06 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0002_delete_location'),
        ('rentcars', '0015_auto_20211102_1258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='car',
            options={'ordering': ['license_plate'], 'verbose_name': 'Автомобиль', 'verbose_name_plural': 'Автомобили'},
        ),
        migrations.AlterModelOptions(
            name='fine',
            options={'ordering': ['is_paid', '-datetime'], 'verbose_name': 'Штраф', 'verbose_name_plural': 'Штрафы'},
        ),
        migrations.RemoveField(
            model_name='fine',
            name='date',
        ),
        migrations.AddField(
            model_name='fine',
            name='datetime',
            field=models.DateTimeField(null=True, verbose_name='Дата и время штрафа'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='approved_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата подтверждения договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='car',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='rentcars.car', verbose_name='Машина'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='closed_at',
            field=models.DateTimeField(verbose_name='Дата завершения действия договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата формирования договора'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='tgbot.user'),
        ),
        migrations.AlterField(
            model_name='fine',
            name='contract',
            field=models.ForeignKey(blank=True, help_text='Заполнится автоматически после сохранения!', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fines', to='rentcars.contract', verbose_name='Договор'),
        ),
        migrations.AlterField(
            model_name='fine',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Заполнится автоматически после сохранения!', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fines', to='tgbot.user', verbose_name='Водитель'),
        ),
    ]