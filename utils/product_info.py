import json
from ali_sdk import iop
import os
from dotenv import load_dotenv
from ali_sdk.iop import IopClient
from utils.shipping_fee import get_shipping_info
from utils.selenium_driver import set_driver
import datetime
from conf import MAX_VARIATIONS, PROFIT, MIN_PROFIT, MIN_SELL_PRICE, MAX_ATTRIBUTES
import math
import secrets
load_dotenv()


def ali_client() -> IopClient:

    url = 'https://api-sg.aliexpress.com/sync'
    app_key = os.getenv('APP_KEY_ALI')
    app_secret = os.getenv('APP_SECRET_ALI')
    client = iop.IopClient(url, app_key, app_secret)

    return client


def get_category_name(category_id: str) -> str:

    category_name = ''
    return category_name


def generate_sku(data: str) -> str:
    sku = secrets.token_hex(nbytes=6).upper()
    while sku in data:
        sku = secrets.token_hex(nbytes=6).upper()
    return sku

def get_product_info(product_id: str) -> tuple:

    client = ali_client()

    request = iop.IopRequest('aliexpress.ds.product.get')
    request.add_api_param('ship_to_country', 'US')
    request.add_api_param('product_id', product_id)
    request.add_api_param('target_currency', 'USD')
    request.add_api_param('target_language', 'en')

    response = client.execute(request)
    data = response.body
    variants = data['aliexpress_ds_product_get_response']['result']['ae_item_sku_info_dtos']['ae_item_sku_info_d_t_o']

    product_info = data['aliexpress_ds_product_get_response']['result']['ae_item_base_info_dto']
    category_id = product_info['category_id']
    sales_count = product_info['sales_count']
    title = product_info['subject']
    avg_evaluation_rating = product_info['avg_evaluation_rating']
    images = data['aliexpress_ds_product_get_response']['result']['ae_multimedia_info_dto']['image_urls']
    images_list = images.split(';')

    #
    mobile_detail_string = product_info['mobile_detail']
    mobile_detail_data = json.loads(mobile_detail_string)
    mobile_detail_list = mobile_detail_data['mobileDetail']
    text_list = [item['content'] for item in mobile_detail_list if 'content' in item]
    details = ' '.join(text_list)

    return sales_count, title, avg_evaluation_rating, variants, images_list, details.strip(), category_id


def process_variants(variants: dict, shipping_fee: float) -> tuple:

    attributes_dict = {}
    variation_batch = []

    for variant in variants:
        offer_sale_price = variant['offer_sale_price']
        sku_available_stock = variant['sku_available_stock']
        sku_id = variant['sku_id']
        options = variant['ae_sku_property_dtos']['ae_sku_property_d_t_o']

        # Change price with shipping fee and profit
        profit = float(offer_sale_price) * PROFIT
        if profit < MIN_PROFIT:
            profit = MIN_PROFIT

        sell_price = float(offer_sale_price) + profit + float(shipping_fee)
        rounded_sell_price = math.floor(sell_price) + 0.99
        rounded_sell_price = rounded_sell_price if rounded_sell_price > MIN_SELL_PRICE else MIN_SELL_PRICE
        print(offer_sale_price, rounded_sell_price)

        img = ''
        attributes = []
        for option in options:
            name = option['sku_property_name']
            value = option.get('property_value_definition_name', '')
            if not value:
                value = option['sku_property_value']

            img = option.get('sku_image', None) if option.get('sku_image', None) is not None else img

            # Attributes dict
            if name in attributes_dict:
                key = attributes_dict[name]
                if value not in key:
                    key.append(value)
            else:
                attributes_dict[name] = [value]

            # Batch format part
            property = {"id": '',
                        "name": name,
                        "option": value}

            attributes.append(property)

        # Woo batch format
        new_option = {"regular_price": rounded_sell_price,
                      'manage_stock': True,
                      "stock_quantity": sku_available_stock,
                      "attributes": attributes,
                      "meta_data": [
                          {
                              "key": "ali_variant_id",
                              "value": sku_id
                          }
                      ]
                      }
        if img is not None:
            new_option["image"] = {"src": img}

        variation_batch.append(new_option)

    # process attributes to woo format
    attributes_list = []
    i = 1
    for key, values in attributes_dict.items():
        option_names = [value for value in values]
        new_variant = {
            "id": '',
            "name": key,
            "options": option_names,
            "position": 0,
            "variation": True,
            "visible": True}
        i += 1

        attributes_list.append(new_variant)

    return variation_batch, attributes_list


def process_product(sellers_to_upload: list) -> bool:

    driver = set_driver()

    with open('data_search.json', 'r') as json_file:
        data_search = json.load(json_file)

    with open('data_variants.json', 'r') as json_file:
        data_variants = json.load(json_file)

    # Backup json data
    with open('./backup/backup_search.json', 'w') as json_file:
        json.dump(data_search, json_file, indent=4)

    with open('./backup/backup_variants.json', 'w') as json_file:
        json.dump(data_variants, json_file, indent=4)

    # Initiate product_id in JSON file
    if 'product_id' not in data_variants['data']:
        data_variants['data']['product_id'] = {}

    # Convert the JSON data to a string to check SKUs
    json_string = json.dumps(data_variants)


    for seller in sellers_to_upload:
        product_ids = data_search['data']['sellers'][seller]['products']
        store_id = data_search['data']['sellers'][seller]['store_id']

        for product_id in product_ids:

            # Get product info from Ali API
            sales_count, title, avg_evaluation_rating, variants, images_list, details, category_id  = get_product_info(product_id)

            # Get shipping info with selenium
            shipping_fee, delivery_date, delivery_days = get_shipping_info(driver, product_id)

            # Woo format for attributes list and variants
            processed_variants, processed_attributes = process_variants(variants, shipping_fee)

            # Skip products with many attributes and variations
            if len(processed_attributes) > MAX_ATTRIBUTES:
                continue

            for attribute in processed_attributes:
                options = attribute['options']
                if len(options) >= MAX_VARIATIONS:
                    continue

            ali_product_url = f'https://www.aliexpress.us/item/{product_id}.html'
            category_name = get_category_name(category_id)

            new_data = {'sku': generate_sku(json_string),
                        'site': [],
                        'last_scrape': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'title': title,
                        'sales_count': sales_count,
                        'delivery_days': delivery_days if delivery_days else '',
                        'avg_evaluation_rating': avg_evaluation_rating,
                        'ali_seller_id': store_id,
                        'ali_product_id': product_id,
                        'ali_product_url': ali_product_url,
                        'category': category_name,
                        'images_list': images_list,
                        'details': details,
                        'variants': processed_variants,
                        'attributes': processed_attributes,
                        }

            data_variants['data']['product_id'][product_id] = new_data


    with open('data_variants.json', 'w') as json_file:
        json.dump(data_variants, json_file, indent=4)

    return True
