# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-19 12:14
from __future__ import unicode_literals

from django.db import migrations, models
import registrations.models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0009_auto_20170919_0338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='verify_docs',
            field=models.ImageField(default=None, null=True, upload_to=registrations.models.user_directory_path),
        ),
    ]
