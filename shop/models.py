from __future__ import unicode_literals
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class Stall(models.Model):
	name = models.CharField(max_length=200, blank=True)
	description = models.TextField(default='', blank=True)
	user = models.OneToOneField(User)

	def __unicode__(self):
		return self.name

class Colour(models.Model):                ########## Implement as a choice field
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Size(models.Model):                  ########### Implement as a choice field
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Type(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
		return self.name

class PCategory(models.Model):
	name = models.CharField(max_length=20, default='a')
	def __unicode__(self):
		return self.name


class Product(models.Model):
	p_type = models.ForeignKey('Type', null=True, blank=True)
	name = models.CharField(max_length=200, blank=True)
	description = models.TextField(default='', blank=True)
	if_veg = models.NullBooleanField(default=None)
	stall = models.ForeignKey('Stall', related_name="menu", null=True)
	colour = models.ForeignKey('Colour', null=True, blank=True)
	prof_show = models.ForeignKey('events.ProfShow', null=True)
	category = models.ForeignKey(PCategory, null=True)

	def __unicode__(self):
		return self.name + '-' + str(self.colour) + '-' + str(self.p_type)

class ProductMain(models.Model):
	size = models.ForeignKey('Size', null=True, blank=True)
	product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True,  related_name="mainproducts")
	price = models.IntegerField(default=0)
	is_available = models.BooleanField(default=True)
	quantity = models.IntegerField(default=500)
	discount = models.IntegerField(default=0)
	orderno = models.IntegerField(default=0)
	
	def __unicode__(self):
		return str(self.product) + ' ' + self.size.name

class SaleGroup(models.Model): # for group of items
	created_at = models.DateTimeField(default=timezone.now)
	is_bitsian = models.BooleanField(default=False)
	bitsian = models.ForeignKey('registrations.Bitsian', on_delete=models.SET_NULL, null=True, related_name="salegroup")
	participant = models.ForeignKey('registrations.Participant', on_delete=models.SET_NULL, null=True)
	amount = models.IntegerField(default=0)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True)

class Sale(models.Model): # for single item
	product = models.ForeignKey('ProductMain', related_name="sales")
	quantity = models.IntegerField(default=0)
	cart = models.ForeignKey('Cart', null=True, on_delete=models.SET_NULL, related_name="sales")
	paid = models.BooleanField(default=False)
	received = models.BooleanField(default=True)
	sale_group = models.ForeignKey('SaleGroup', on_delete=models.SET_NULL, null=True)
	uid = models.UUIDField(default=uuid.uuid4)
	cancelled = models.BooleanField(default=True)
	confirmed = models.BooleanField(default=False)
	stall_group = models.ForeignKey('StallGroup', null=True, on_delete=models.SET_NULL, related_name="sales")

	def __unicode__(self):
		return self.product.product.name + ' ' + str(self.quantity)

class StallGroup(models.Model): # This model is redundant but was necessary to handle the system change decided in the end
	created_at = models.DateTimeField(default=timezone.now)
	is_bitsian = models.BooleanField(default=False)
	bitsian = models.ForeignKey('registrations.Bitsian', on_delete=models.SET_NULL, null=True, related_name="stallgroup")
	stall = models.ForeignKey(Stall, null=True, on_delete=models.SET_NULL)
	sale_group = models.ForeignKey(SaleGroup, null=True, on_delete=models.SET_NULL)
	participant = models.ForeignKey('registrations.Participant', on_delete=models.SET_NULL, null=True)
	amount = models.IntegerField(default=0)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	order_complete = models.BooleanField(default=False)
	group_paid = models.BooleanField(default=False)
	unique_code = models.CharField(max_length=200, default='', null=True)
	transaction = models.OneToOneField('Transaction', null=True, default=None, related_name='stallgroup')
	cancelled = models.BooleanField(default=False)
	code_requested = models.BooleanField(default=False)
	orderid = models.CharField(max_length=200, default='')
	order_ready = models.BooleanField(default=False)
	previous = models.BooleanField(default=False)
	order_no = models.IntegerField(default=0)

class Cart(models.Model):
	is_bitsian = models.BooleanField(default=False)
	bitsian = models.ForeignKey('registrations.Bitsian', on_delete=models.SET_NULL, null=True, related_name="carts")
	participant = models.ForeignKey('registrations.Participant', related_name="carts", on_delete=models.SET_NULL, null=True)
	created_at = models.DateTimeField(default=timezone.now)
	amount = models.IntegerField(default=0)
	is_complete = models.BooleanField(default=False)
	user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)

	def __unicode__(self):
		return str(self.amount) + ' ' + str(self.created_at)

class Transaction(models.Model):
	transaction_coices = (
		('buy', 'buy'),
		('add', 'add'),
		('transfer','transfer'),
		('swd', 'swd'),
		('recieve','recieve') 
	)
	created_at = models.DateTimeField(default=timezone.now)
	value = models.IntegerField(default=0)
	wallet = models.ForeignKey('Wallet', related_name='transactions', on_delete=models.SET_NULL, null=True)
	payment_refund_id = models.CharField(default='', max_length=30)
	transfer_to_from = models.ForeignKey('Wallet', related_name="transfers", null=True)
	t_type = models.CharField(max_length=100, default='buy', choices=transaction_coices)
	from_controls = models.BooleanField(default=False)

	def __unicode__(self):
		return self.wallet.__unicode__() + ' ' + str(self.value)


class Wallet(models.Model):
	user = models.OneToOneField(User)
	curr_balance = models.PositiveIntegerField(default=0)
	uid = models.UUIDField(default=uuid.uuid4)
	created_at = models.DateTimeField(default=timezone.now)
	is_bitsian = models.BooleanField(default=False)
	bitsian = models.OneToOneField('registrations.Bitsian', null=True)
	participant = models.OneToOneField('registrations.Participant', null=True)
	phone = models.BigIntegerField(default=0)
	userid = models.CharField(max_length=20, default='')

	def __unicode__(self):
		return self.user.username