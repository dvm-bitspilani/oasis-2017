# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-14 21:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wordwars', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_no', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.BigIntegerField()),
                ('score', models.IntegerField(default=0)),
                ('day1', models.IntegerField(default=0)),
                ('day2', models.IntegerField(default=0)),
                ('day3', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='Participant',
        ),
        migrations.AlterField(
            model_name='question',
            name='day',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wordwars.Day'),
        ),
    ]
