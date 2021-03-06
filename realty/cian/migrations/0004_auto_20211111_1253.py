# Generated by Django 3.2.9 on 2021-11-11 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cian', '0003_auto_20191007_0014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='is_moulage',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='offer',
            name='is_paid',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='offer',
            name='is_premium',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='offer',
            name='is_top',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='offersfilter',
            name='is_updating',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AlterField(
            model_name='offersfilter',
            name='watch_top3',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='offersupdate',
            name='status',
            field=models.CharField(blank=True, choices=[('waiting', 'Ожидание'), ('processing', 'Обновляется'), ('success', 'Обновлено успешно'), ('retry', 'cian не даёт'), ('error', 'Произошла ошибка')], default='waiting', max_length=16),
        ),
        migrations.AlterField(
            model_name='retailer',
            name='is_agent',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
