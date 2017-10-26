from django import template
from store.models import *
from functools import reduce
from django.db.models import Q
register = template.Library()

@register.inclusion_tag('store/show_tags.html')
def show_tags():
    carts = Cart.objects.all().count()
    paid_carts = Cart.objects.filter(paid=True).count()
    return {'carts':carts, 'paid_carts':paid_carts}