# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-27 04:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0008_auto_20160927_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='exam_date',
            field=models.DateField(verbose_name='검사 날짜'),
        ),
    ]