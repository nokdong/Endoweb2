# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-05 06:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0021_auto_20161005_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='patient_sex',
            field=models.CharField(choices=[('남자', '남자'), ('여자', '여자')], default='m', max_length=10, verbose_name='성별'),
        ),
    ]
