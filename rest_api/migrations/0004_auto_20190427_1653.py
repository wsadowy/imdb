# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-27 16:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest_api', '0003_auto_20190427_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='birth_year',
            field=models.DateField(null=True, verbose_name=b'Year of birth'),
        ),
        migrations.AlterField(
            model_name='actor',
            name='death_year',
            field=models.DateField(null=True, verbose_name=b'Year of death'),
        ),
    ]
