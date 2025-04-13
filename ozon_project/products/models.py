from django.db import models

class Product(models.Model):
    offer_id = models.CharField(max_length=255, unique=True)
    product_id = models.IntegerField(unique=True)
    description = models.TextField(blank=True, null=True)
    sku = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.offer_id