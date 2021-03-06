# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-27 12:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0013_cartbill_created_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='item',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='item',
            name='quantity_left',
        ),
        migrations.RemoveField(
            model_name='item',
            name='size',
        ),
        migrations.AlterField(
            model_name='sale',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.MainItem'),
        ),
        migrations.AddField(
            model_name='mainitem',
            name='cart',
            field=models.ManyToManyField(through='store.Sale', to='store.Cart'),
        ),
        migrations.AddField(
            model_name='mainitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Item'),
        ),
        migrations.AddField(
            model_name='mainitem',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.Size'),
        ),
    ]
