# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-06 15:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0029_auto_20161006_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='phone_check',
            field=models.CharField(default='.', max_length=50, verbose_name='전화 통화 결과'),
        ),
    ]
