import aiohttp
import asyncio
import os
import json
from typing import List, Dict, Any

API_KEYS_FILE = os.path.join(os.path.dirname(__file__), 'api_keys.json')
with open(API_KEYS_FILE, 'r') as f:
    api_keys = json.load(f)
    CLIENT_ID = api_keys['CLIENT_ID']
    API_KEY = api_keys['API_KEY']
BASE_URL = 'https://api-seller.ozon.ru'
HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
    'Content-Type': 'application/json'
}


async def async_post_request(session, endpoint: str, data: dict) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    async with session.post(url, headers=HEADERS, json=data) as response:
        if response.status == 200:
            return await response.json()
        text = await response.text()
        raise Exception(f"Ошибка {response.status}: {text}")


async def get_all_products_async() -> List[Dict[str, Any]]:
    endpoint = "v3/product/list"
    data = {"filter": {}, "last_id": "", "limit": 100}
    all_products = []

    async with aiohttp.ClientSession() as session:
        while True:
            response = await async_post_request(session, endpoint, data)
            result = response.get('result', {})
            items = result.get('items', [])
            all_products.extend(items)
            last_id = result.get('last_id', '')
            if not last_id or len(items) < data['limit']:
                break
            data['last_id'] = last_id

    return all_products


async def get_product_descriptions_async(products: List[Dict[str, Any]]) -> Dict[str, str]:
    endpoint = "v1/product/info/description"
    tasks = []
    descriptions = {}

    async with aiohttp.ClientSession() as session:
        for product in products:
            offer_id = product.get('offer_id')
            data = {'offer_id': offer_id}
            task = asyncio.create_task(async_post_request(session, endpoint, data))
            tasks.append((offer_id, task))

        for offer_id, task in tasks:
            try:
                response = await task
                descriptions[offer_id] = response.get('result', {}).get('description', '')
            except Exception as e:
                print(f"Ошибка при получении описания для {offer_id}: {e}")
                descriptions[offer_id] = ''

    return descriptions


async def get_products_skus_async(products: List[Dict[str, Any]]) -> Dict[str, int]:
    endpoint = "v3/product/info/list"
    batch_size = 100
    all_offer_ids = [p.get('offer_id') for p in products]
    skus = {}

    chunks = [all_offer_ids[i:i + batch_size] for i in range(0, len(all_offer_ids), batch_size)]

    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            data = {'offer_id': chunk}
            try:
                response = await async_post_request(session, endpoint, data)
                items = response.get('items', [])
                for item in items:
                    skus[item.get('offer_id')] = item.get('sku')
            except Exception as e:
                print(f"Ошибка при получении SKU для партии: {e}")

    return skus


# Обертки для совместимости
def get_all_products() -> list:
    return asyncio.run(get_all_products_async())


def get_product_description(offer_id: str = None, product_id: int = None) -> str:
    if not offer_id and not product_id:
        raise ValueError("Укажи offer_id или product_id")

    async def get_single_description():
        async with aiohttp.ClientSession() as session:
            endpoint = "v1/product/info/description"
            data = {'offer_id': offer_id} if offer_id else {'product_id': product_id}
            response = await async_post_request(session, endpoint, data)
            return response.get('result', {}).get('description', '')

    return asyncio.run(get_single_description())


def get_product_sku(offer_id: str = None, product_id: int = None) -> int:
    if not offer_id and not product_id:
        raise ValueError("Укажи offer_id или product_id")

    async def get_single_sku():
        async with aiohttp.ClientSession() as session:
            endpoint = "v3/product/info/list"
            data = {'offer_id': [offer_id]} if offer_id else {'product_id': [str(product_id)]}
            response = await async_post_request(session, endpoint, data)
            items = response.get('items', [])
            return items[0].get('sku') if items else None

    return asyncio.run(get_single_sku())