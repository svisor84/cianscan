# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-01 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cian', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='offersfilter',
            name='max_auction_bet',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
