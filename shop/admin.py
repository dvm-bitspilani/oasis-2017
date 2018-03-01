from django.contrib import admin
from .models import *
class ItemInLine(admin.TabularInline):
    model = ProductMain
    fields = ('size', 'price', 'is_available')
    extra = 2

class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemInLine]
    fields = ('name','stall', 'colour', 'p_type', 'category')
# Register your models here.
admin.site.register(Wallet)
admin.site.register(Product, ItemAdmin)
admin.site.register(ProductMain)
admin.site.register(Cart)
admin.site.register(Transaction)
admin.site.register(Sale)
admin.site.register(SaleGroup)
admin.site.register(Stall)
admin.site.register(StallGroup)
admin.site.register(Type)
admin.site.register(Colour)
admin.site.register(Size)
admin.site.register(PCategory)