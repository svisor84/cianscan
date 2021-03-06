# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-10-07 00:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cian', '0002_offersfilter_max_auction_bet'),
    ]

    operations = [
        migrations.AddField(
            model_name='offersfilter',
            name='auction_step',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offersfilter',
            name='our_max_auction_bet',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offersfilter',
            name='watch_top3',
            field=models.BooleanField(default=False),
        ),
    ]
