# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-16 20:47
from __future__ import unicode_literals

import ckeditor.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('content', ckeditor.fields.RichTextField()),
                ('appcontent', models.TextField(default='', max_length=3000)),
                ('short_description', models.CharField(blank=True, max_length=140)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_kernel', models.BooleanField(default=False)),
                ('icon', models.ImageField(blank=True, upload_to='icons')),
                ('date', models.CharField(default='TBA', max_length=100)),
                ('time', models.CharField(default='TBA', max_length=100)),
                ('venue', models.CharField(default='TBA', max_length=100)),
                ('min_team_size', models.IntegerField(default=0)),
                ('max_team_size', models.IntegerField(default=0)),
                ('min_teams', models.IntegerField(default=0)),
                ('max_teams', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confirmed', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
            ],
        ),
    ]
