# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-10 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0040_delete_exam'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='address',
            field=models.CharField(blank=True, max_length=30, verbose_name='주소'),
        ),
    ]
