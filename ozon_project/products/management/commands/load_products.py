from django.core.management.base import BaseCommand
import asyncio
import datetime
from asgiref.sync import sync_to_async
from products.api import (
    get_all_products_async,
    get_product_descriptions_async,
    get_products_skus_async
)
from products.models import Product, ProductUpdateLog
from django.db import transaction


class Command(BaseCommand):
    help = 'Загружает данные о товарах из API Ozon в базу данных с инкрементальными обновлениями'

    async def async_handle(self, *args, **kwargs):
        # Получаем время последнего обновления с использованием sync_to_async
        try:
            last_update = await sync_to_async(self.get_last_update)()
            self.stdout.write(f"Последнее обновление: {last_update}")
        except ProductUpdateLog.DoesNotExist:
            last_update = None
            self.stdout.write("Первое обновление, загружаем все товары")

        self.stdout.write("Получение списка товаров...")
        products = await get_all_products_async()
        self.stdout.write(f"Всего товаров: {len(products)}")

        # Если есть предыдущее обновление, определяем изменившиеся товары
        if last_update:
            # Получаем существующие товары из БД с использованием sync_to_async
            existing_products = await sync_to_async(self.get_existing_products)()

            # Идентификаторы новых товаров (которых нет в БД)
            new_offer_ids = [p['offer_id'] for p in products if p['offer_id'] not in existing_products]

            if new_offer_ids:
                self.stdout.write(f"Обнаружено {len(new_offer_ids)} новых товаров для обновления")
                # Фильтруем только новые товары
                products_to_update = [p for p in products if p['offer_id'] in new_offer_ids]
            else:
                self.stdout.write("Новых товаров не обнаружено")
                products_to_update = []
        else:
            # Первый запуск - обновляем все товары
            products_to_update = products

        if not products_to_update:
            self.stdout.write("Нет товаров для обновления")
            # Записываем информацию о текущем обновлении с использованием sync_to_async
            await sync_to_async(self.create_update_log)(0)
            return

        # Получаем описания и SKU только для товаров, которые нужно обновить
        self.stdout.write("Получение информации о товарах...")
        descriptions_task = asyncio.create_task(get_product_descriptions_async(products_to_update))
        skus_task = asyncio.create_task(get_products_skus_async(products_to_update))

        descriptions = await descriptions_task
        skus = await skus_task

        # Формируем список объектов для обновления
        product_data = []
        for product in products_to_update:
            offer_id = product.get('offer_id')
            product_id = product.get('product_id')

            product_data.append({
                'offer_id': offer_id,
                'product_id': product_id,
                'description': descriptions.get(offer_id, ''),
                'sku': skus.get(offer_id)
            })

        # Оптимизированное обновление БД с использованием sync_to_async
        self.stdout.write("Обновление базы данных...")

        created, updated = await sync_to_async(self.update_db)(product_data)

        self.stdout.write(f"Создано {created} новых товаров")
        self.stdout.write(f"Обновлено {updated} существующих товаров")

        # Записываем информацию о текущем обновлении
        await sync_to_async(self.create_update_log)(len(product_data))

    def get_last_update(self):
        return ProductUpdateLog.objects.latest('updated_at').updated_at

    def get_existing_products(self):
        return {p.offer_id: p for p in Product.objects.all()}

    def update_db(self, product_data):
        with transaction.atomic():
            # Сначала получаем существующие товары
            existing_offer_ids = set(Product.objects.values_list('offer_id', flat=True))

            # Разделяем на новые и обновляемые
            to_create = []
            to_update = []

            for data in product_data:
                if data['offer_id'] in existing_offer_ids:
                    to_update.append(data)
                else:
                    to_create.append(Product(**data))

            # Массовое создание новых
            created_count = 0
            if to_create:
                Product.objects.bulk_create(to_create)
                created_count = len(to_create)

            # Обновление существующих
            updated_count = 0
            for data in to_update:
                Product.objects.filter(offer_id=data['offer_id']).update(
                    product_id=data['product_id'],
                    description=data['description'],
                    sku=data['sku']
                )
                updated_count += 1

            return created_count, updated_count

    def create_update_log(self, products_updated):
        ProductUpdateLog.objects.create(
            updated_at=datetime.datetime.now(),
            products_updated=products_updated
        )

    def handle(self, *args, **kwargs):
        asyncio.run(self.async_handle(*args, **kwargs))