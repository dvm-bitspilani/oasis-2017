# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-22 23:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0004_auto_20170917_1429'),
        ('ems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubDepartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('co_ordinator', models.CharField(max_length=200)),
                ('phone', models.BigIntegerField(default=0)),
                ('email_id', models.EmailField(max_length=254)),
                ('events', models.ManyToManyField(blank=True, null=True, to='events.Event')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Judge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('var1name', models.CharField(blank=True, max_length=20, null=True)),
                ('var1max', models.IntegerField(blank=True, default=10, null=True)),
                ('var2name', models.CharField(blank=True, max_length=20, null=True)),
                ('var2max', models.IntegerField(blank=True, default=10, null=True)),
                ('var3name', models.CharField(blank=True, max_length=20, null=True)),
                ('var3max', models.IntegerField(blank=True, default=10, null=True)),
                ('var4name', models.CharField(blank=True, max_length=20, null=True)),
                ('var4max', models.IntegerField(blank=True, default=10, null=True)),
                ('var5name', models.CharField(blank=True, max_length=20, null=True)),
                ('var5max', models.IntegerField(blank=True, default=10, null=True)),
                ('var6name', models.CharField(blank=True, max_length=20, null=True)),
                ('var6max', models.IntegerField(blank=True, default=10, null=True)),
                ('var7name', models.CharField(blank=True, max_length=20, null=True)),
                ('var7max', models.IntegerField(blank=True, default=10, null=True)),
                ('var8name', models.CharField(blank=True, max_length=20, null=True)),
                ('var8max', models.IntegerField(blank=True, default=10, null=True)),
                ('var9name', models.CharField(blank=True, max_length=20, null=True)),
                ('var9max', models.IntegerField(blank=True, default=10, null=True)),
                ('var10name', models.CharField(blank=True, max_length=20, null=True)),
                ('var10max', models.IntegerField(blank=True, default=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='events.Event')),
                ('judges', models.ManyToManyField(blank=True, null=True, to='ems.Judge')),
                ('teams', models.ManyToManyField(blank=True, related_name='levels', to='ems.Team')),
            ],
        ),
        migrations.AddField(
            model_name='label',
            name='level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ems.Level'),
        ),
    ]
