# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-26 22:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ems', '0007_auto_20170926_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bitsian',
            name='college',
        ),
        migrations.RemoveField(
            model_name='bitsian',
            name='email',
        ),
        migrations.RemoveField(
            model_name='bitsian',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='bitsian',
            name='short_id',
        ),
        migrations.AlterField(
            model_name='bitsian',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
