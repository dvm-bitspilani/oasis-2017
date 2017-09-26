# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-26 15:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ems', '0006_auto_20170924_2037'),
    ]

    operations = [
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_frozen', models.BooleanField(default=False)),
                ('score', models.CharField(default='{}', max_length=500)),
                ('total_score', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='label',
            name='level',
        ),
        migrations.RemoveField(
            model_name='level',
            name='judges',
        ),
        migrations.RemoveField(
            model_name='parameter',
            name='label',
        ),
        migrations.AddField(
            model_name='parameter',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ems.Level'),
        ),
        migrations.AddField(
            model_name='team',
            name='is_bitsian',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='team',
            name='leader_bitsian',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bitsian_leader', to='ems.Bitsian'),
        ),
        migrations.AddField(
            model_name='team',
            name='level',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='team',
            name='members_bitsian',
            field=models.ManyToManyField(to='ems.Bitsian'),
        ),
        migrations.AlterField(
            model_name='judge',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='level',
            name='name',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='level',
            name='position',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='parameter',
            name='name',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='team',
            name='leader',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team_leader', to='registrations.Participant'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.DeleteModel(
            name='Label',
        ),
        migrations.AddField(
            model_name='score',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ems.Level'),
        ),
        migrations.AddField(
            model_name='score',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='ems.Team'),
        ),
    ]
