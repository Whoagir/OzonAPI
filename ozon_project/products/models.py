from django.db import models

class Product(models.Model):
    offer_id = models.CharField(max_length=255, unique=True, db_index=True)
    product_id = models.IntegerField(unique=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    sku = models.IntegerField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['offer_id']),
            models.Index(fields=['product_id']),
        ]


class ProductUpdateLog(models.Model):
    updated_at = models.DateTimeField(auto_now_add=True)
    products_updated = models.IntegerField(default=0)

    class Meta:
        get_latest_by = 'updated_at'


# Добавьте это в models.py
class ProductUpdateLog(models.Model):
    updated_at = models.DateTimeField(auto_now_add=True)
    products_updated = models.IntegerField(default=0)

    class Meta:
        get_latest_by = 'updated_at'