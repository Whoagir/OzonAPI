from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('offer_id', 'product_id', 'sku')
    search_fields = ('offer_id', 'product_id')