# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-11 21:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preregistrations', '0002_auto_20170612_0303'),
    ]

    operations = [
        migrations.CreateModel(
            name='RapWars',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(max_length=100)),
                ('phone', models.CharField(default='', max_length=13)),
                ('gender', models.CharField(max_length=6)),
                ('email_address', models.EmailField(max_length=254, unique=True)),
            ],
        ),
    ]
