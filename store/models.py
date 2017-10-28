from __future__ import unicode_literals

from django.db import models
from registrations.models import *
from ems.models import Bitsian

class Cart(models.Model):
    buyer_id = models.CharField(max_length=20)
    is_bitsian = models.BooleanField(default=False)
    participant = models.ForeignKey('registrations.Participant', on_delete=models.CASCADE, null=True)
    bitsian = models.ForeignKey('ems.Bitsian', on_delete=models.CASCADE, null=True)
    paid = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now=True)
    amount = models.IntegerField(default=0)
    email = models.EmailField()
    cart_token = models.CharField(max_length=32, null=True, blank=True)
    maincombos = models.ManyToManyField('MainCombo')

    def __unicode__(self):
        return str(self.buyer_id) + '-' + str(self.amount)

class Sale(models.Model):
    item = models.ForeignKey('MainItem', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

class Item(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(default=0)
    front_pic = models.ImageField(upload_to="store/front_pics/", null=True)
    back_pic = models.ImageField(upload_to="store/back_pics/", null=True)
    colour = models.ForeignKey('Colour', null=True, blank=True)

    def __unicode__(self):
        return self.name + '-' + str(self.colour.name)

class MainItem(models.Model):
    size = models.ForeignKey('Size', null=True, blank=True)
    quantity_left = models.IntegerField(default=0)
    cart = models.ManyToManyField(Cart, through=Sale)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)

    def __unicode__(self):
        return str(self.item.name) + '-' + str(self.size.name) + '-' + str(self.item.colour.name)

class Colour(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return self.name

class CartBill(models.Model):

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_time = models.DateTimeField(auto_now=True)
    time_paid = models.DateTimeField(auto_now=True)
    two_thousands = models.IntegerField(null=True, blank=True, default=0)
    five_hundreds = models.IntegerField(null=True, blank=True, default=0)
    two_hundreds = models.IntegerField(null=True, blank=True, default=0)
    hundreds = models.IntegerField(null=True, blank=True, default=0)
    fifties = models.IntegerField(null=True, blank=True, default=0)
    twenties = models.IntegerField(null=True, blank=True, default=0)
    tens = models.IntegerField(null=True, blank=True, default=0)
    draft_number = models.CharField(max_length=100, null=True, blank=True, default=None)
    draft_amount = models.IntegerField(null=True, blank=True, default=0)
    two_thousands_returned = models.IntegerField(null=True, blank=True, default=0)
    five_hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
    two_hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
    hundreds_returned = models.IntegerField(null=True, blank=True, default=0)
    fifties_returned = models.IntegerField(null=True, blank=True, default=0)
    twenties_returned = models.IntegerField(null=True, blank=True, default=0)
    tens_returned = models.IntegerField(null=True, blank=True, default=0)

class Combo(models.Model):
    items = models.ManyToManyField('Item')
    price = models.IntegerField(default=0)

class MainCombo(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE)
    mainitems = models.ManyToManyField('MainItem')
