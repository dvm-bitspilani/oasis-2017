# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-01 14:44
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0010_attendance_bitsian'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registrations', '0026_bitsian'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_bitsian', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.IntegerField(default=0)),
                ('is_complete', models.BooleanField(default=False)),
                ('bitsian', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carts', to='registrations.Bitsian')),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carts', to='registrations.Participant')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Colour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='PCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='a', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('if_veg', models.NullBooleanField(default=None)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.PCategory')),
                ('colour', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Colour')),
            ],
        ),
        migrations.CreateModel(
            name='ProductMain',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('quantity', models.IntegerField(default=500)),
                ('discount', models.IntegerField(default=0)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mainproducts', to='shop.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('paid', models.BooleanField(default=False)),
                ('received', models.BooleanField(default=True)),
                ('uid', models.UUIDField(default=uuid.uuid4)),
                ('cancelled', models.BooleanField(default=True)),
                ('confirmed', models.BooleanField(default=False)),
                ('cart', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='shop.Cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to='shop.ProductMain')),
            ],
        ),
        migrations.CreateModel(
            name='SaleGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_bitsian', models.BooleanField(default=False)),
                ('amount', models.IntegerField(default=0)),
                ('bitsian', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='salegroup', to='registrations.Bitsian')),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='registrations.Participant')),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Stall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StallGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_bitsian', models.BooleanField(default=False)),
                ('amount', models.IntegerField(default=0)),
                ('order_complete', models.BooleanField(default=False)),
                ('group_paid', models.BooleanField(default=False)),
                ('unique_code', models.CharField(default='', max_length=200, null=True)),
                ('cancelled', models.BooleanField(default=False)),
                ('code_requested', models.BooleanField(default=False)),
                ('orderid', models.CharField(default='', max_length=200)),
                ('order_ready', models.BooleanField(default=False)),
                ('previous', models.BooleanField(default=False)),
                ('order_no', models.IntegerField(default=0)),
                ('bitsian', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stallgroup', to='registrations.Bitsian')),
                ('participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='registrations.Participant')),
                ('sale_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.SaleGroup')),
                ('stall', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.Stall')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('value', models.IntegerField(default=0)),
                ('payment_refund_id', models.CharField(default='', max_length=30)),
                ('t_type', models.CharField(choices=[('buy', 'buy'), ('add', 'add'), ('transfer', 'transfer'), ('swd', 'swd'), ('recieve', 'recieve')], default='buy', max_length=100)),
                ('from_controls', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('curr_balance', models.PositiveIntegerField(default=0)),
                ('uid', models.UUIDField(default=uuid.uuid4)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_bitsian', models.BooleanField(default=False)),
                ('phone', models.BigIntegerField(default=0)),
                ('userid', models.CharField(default='', max_length=20)),
                ('bitsian', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.Bitsian')),
                ('participant', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='registrations.Participant')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='transfer_to_from',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='shop.Wallet'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='wallet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to='shop.Wallet'),
        ),
        migrations.AddField(
            model_name='stallgroup',
            name='transaction',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stallgroup', to='shop.Transaction'),
        ),
        migrations.AddField(
            model_name='stallgroup',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salegroup',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.Transaction'),
        ),
        migrations.AddField(
            model_name='salegroup',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sale',
            name='sale_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.SaleGroup'),
        ),
        migrations.AddField(
            model_name='sale',
            name='stall_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sales', to='shop.StallGroup'),
        ),
        migrations.AddField(
            model_name='productmain',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Size'),
        ),
        migrations.AddField(
            model_name='product',
            name='p_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.Type'),
        ),
        migrations.AddField(
            model_name='product',
            name='prof_show',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='events.ProfShow'),
        ),
        migrations.AddField(
            model_name='product',
            name='stall',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='menu', to='shop.Stall'),
        ),
    ]
