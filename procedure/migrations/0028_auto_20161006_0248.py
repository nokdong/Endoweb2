# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-05 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0027_exam_patient_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='Bx_result',
            field=models.CharField(default='.', max_length=200, verbose_name='조직검사 결과'),
        ),
    ]
