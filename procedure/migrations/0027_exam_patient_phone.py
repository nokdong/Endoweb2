# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-05 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0026_auto_20161006_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='patient_phone',
            field=models.CharField(default='010-', max_length=15, verbose_name='전화번호'),
        ),
    ]