import requests
import json
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()

HOST = '192.168.1.10'

def search():
    url = f'http://{HOST}:5000/api/v1/search'

    data = {
        "category_id": "200118011",
        "category_name": "Women's Sets",
        "search_text": "",
        "max_price": 100.0,
        "min_price": 0.0,
        "start_page": 1,
        "end_page": 3
    }

    json_data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")
        pprint(response.json())
    else:
        print("Request failed with status code:", response.status_code)


def get_search():
    url = f'http://{HOST}:5000/api/v1/get-search'

    params = {
        'page': 1,
        'per_page': 10,
        'category_id': 200118011
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Request successful!")
        pprint(response.json())
    else:
        print("Request failed with status code:", response.status_code)


def process_products():
    url = f'http://{HOST}:5000/api/v1/process-products'

    data = {
        "category_id": "200118011",
        "sellers_list": ["1101363256"]
    }

    json_data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)


def upload():
    url = f'http://{HOST}:5000/api/v1/upload'

    data = {
        "website": 'garbai.com',
        "key": os.getenv('WEBSITE_KEY'),
        "secret": os.getenv('WEBSITE_SECRET'),
        "products_sku_list": ["987F411CC80B"]
    }

    json_data = json.dumps(data)

    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, data=json_data, headers=headers)

    if response.status_code == 200:
        print("Request successful!")
        print(response.json())
    else:
        print("Request failed with status code:", response.status_code)

# search()
# get_search()
# process_products()
upload()