# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-25 08:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='cart',
        ),
        migrations.AddField(
            model_name='item',
            name='cart',
            field=models.ManyToManyField(to='store.Cart'),
        ),
    ]
