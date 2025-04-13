import requests

CLIENT_ID = '214467'
API_KEY = 'a9bf1891-090c-42ee-a0eb-b5027556c5b9'
BASE_URL = 'https://api-seller.ozon.ru'
HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY,
    'Content-Type': 'application/json'
}


def make_post_request(endpoint: str, data: dict) -> dict:
    url = f"{BASE_URL}/{endpoint}"
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        return response.json()
    raise Exception(f"Ошибка {response.status_code}: {response.text}")


def get_all_products() -> list:
    endpoint = "v3/product/list"
    data = {"filter": {}, "last_id": "", "limit": 100}
    all_products = []

    while True:
        result = make_post_request(endpoint, data).get('result', {})
        items = result.get('items', [])
        all_products.extend(items)
        last_id = result.get('last_id', '')
        if not last_id or len(items) < data['limit']:
            break
        data['last_id'] = last_id

    return all_products


def get_product_description(offer_id: str = None, product_id: int = None) -> str:
    if not offer_id and not product_id:
        raise ValueError("Укажи offer_id или product_id")

    endpoint = "v1/product/info/description"
    data = {'offer_id': offer_id} if offer_id else {'product_id': product_id}
    result = make_post_request(endpoint, data).get('result', {})
    return result.get('description', '')


def get_product_sku(offer_id: str = None, product_id: int = None) -> int:
    if not offer_id and not product_id:
        raise ValueError("Укажи offer_id или product_id")

    endpoint = "v3/product/info/list"
    data = {'offer_id': [offer_id]} if offer_id else {'product_id': [str(product_id)]}
    result = make_post_request(endpoint, data).get('items', [])
    return result[0].get('sku') if result else None


if __name__ == "__main__":
    products = get_all_products()

    print(f"Всего товаров: {len(products)}")

    first_three_products = products[:3]

    for product in first_three_products:
        offer_id = product.get('offer_id')
        product_id = product.get('product_id')

        description = get_product_description(offer_id=offer_id, product_id=product_id)

        sku = get_product_sku(offer_id=offer_id, product_id=product_id)

        print(f"Товар: {product}")
        print(f"Описание: {description}")
        print(f"SKU: {sku}")
        print("-" * 50)