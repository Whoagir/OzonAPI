from django.core.management.base import BaseCommand
from products.api import get_all_products, get_product_description, get_product_sku
from products.models import Product

class Command(BaseCommand):
    help = 'Загружает данные о товарах из API Ozon в базу данных'

    def handle(self, *args, **kwargs):
        products = get_all_products()
        self.stdout.write(f"Всего товаров: {len(products)}")

        for product in products:
            offer_id = product.get('offer_id')
            product_id = product.get('product_id')
            description = get_product_description(offer_id=offer_id, product_id=product_id)
            sku = get_product_sku(offer_id=offer_id, product_id=product_id)

            Product.objects.update_or_create(
                offer_id=offer_id,
                defaults={
                    'product_id': product_id,
                    'description': description,
                    'sku': sku
                }
            )
            self.stdout.write(f"Товар {offer_id} успешно добавлен/обновлен")