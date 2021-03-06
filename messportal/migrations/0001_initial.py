# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-18 21:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0009_auto_20171016_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('price', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MessBill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('buyer_id', models.CharField(max_length=10)),
                ('quantity', models.IntegerField(default=0)),
                ('mess', models.CharField(max_length=10)),
                ('n2000', models.IntegerField(default=0)),
                ('n500', models.IntegerField(default=0)),
                ('n200', models.IntegerField(default=0)),
                ('n100', models.IntegerField(default=0)),
                ('n50', models.IntegerField(default=0)),
                ('n20', models.IntegerField(default=0)),
                ('n10', models.IntegerField(default=0)),
                ('amount', models.IntegerField(default=0)),
                ('intake', models.IntegerField(default=0)),
                ('outtake', models.IntegerField(default=0)),
                ('created_by', models.CharField(max_length=50)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='messportal.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ProfShowBill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now=True)),
                ('buyer_id', models.CharField(max_length=10)),
                ('quantity', models.IntegerField(default=0)),
                ('n2000', models.IntegerField(default=0)),
                ('n500', models.IntegerField(default=0)),
                ('n200', models.IntegerField(default=0)),
                ('n100', models.IntegerField(default=0)),
                ('n50', models.IntegerField(default=0)),
                ('n20', models.IntegerField(default=0)),
                ('n10', models.IntegerField(default=0)),
                ('amount', models.IntegerField(default=0)),
                ('intake', models.IntegerField(default=0)),
                ('outtake', models.IntegerField(default=0)),
                ('created_by', models.CharField(max_length=50)),
                ('prof_show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.ProfShow')),
            ],
        ),
    ]
