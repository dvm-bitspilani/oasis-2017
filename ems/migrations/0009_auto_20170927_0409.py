# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-26 22:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ems', '0008_auto_20170927_0408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bitsian',
            name='name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
