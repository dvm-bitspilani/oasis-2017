# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-26 10:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_auto_20171026_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartbill',
            name='created_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
