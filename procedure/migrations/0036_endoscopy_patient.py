# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-11-15 06:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('procedure', '0035_auto_20171115_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='endoscopy',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='procedure.Patient'),
        ),
    ]