# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-16 11:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0019_auto_20171016_1444'),
        ('events', '0007_auto_20171006_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paid', models.BooleanField(default=False)),
                ('attended', models.BooleanField(default=False)),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='ProfShow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('appcontent', models.TextField(default='', max_length=3000)),
                ('short_description', models.CharField(blank=True, max_length=140)),
                ('date', models.CharField(default='TBA', max_length=100)),
                ('time', models.CharField(default='TBA', max_length=100)),
                ('venue', models.CharField(default='TBA', max_length=100)),
                ('contact', models.CharField(default='', max_length=140)),
                ('price', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='attendance',
            name='prof_show',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.ProfShow'),
        ),
    ]
