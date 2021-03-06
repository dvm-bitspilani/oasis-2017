# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-25 22:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_auto_20171026_0356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sale',
            name='colour',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='size',
        ),
        migrations.RemoveField(
            model_name='item',
            name='colour',
        ),
        migrations.AddField(
            model_name='item',
            name='colour',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.Colour'),
        ),
        migrations.RemoveField(
            model_name='item',
            name='size',
        ),
        migrations.AddField(
            model_name='item',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.Size'),
        ),
    ]
