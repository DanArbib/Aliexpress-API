from woocommerce import API
import requests
import time
import re
from conf import MAX_IMG
import json
import os
from io import BytesIO
from pprint import pprint


def get_wcapi(website: str, key: str, secret: str) -> API:

    # Init API
    wcapi = API(
        url=f'https://{website}//',
        consumer_key=key,
        consumer_secret=secret,
        version="wc/v3",
        timeout=60
    )
    return wcapi

def get_access_token(domain_name):
    auth_url = f'https://{domain_name}/wp-json/jwt-auth/v1/token'
    data = {
        'username': 'app_user',
        'password': os.environ.get('JWT_PASSWORD')
    }
    response = requests.post(auth_url, data=data)
    jwt = response.json().get('token')
    return jwt

def get_all_categories(wcapi: API) -> dict:

    dict = {}
    page = 1

    while True:
        # Retrieve categories from the current page
        response = wcapi.get('products/categories', params={'per_page': 100, 'page': page})
        if response.status_code == 200:
            categories = response.json()
            if not categories:
                break

            for category in categories:
                dict[category['name']] = category['id']

            page += 1
        else:
            print(f"Failed to fetch categories from page {page}. Error code: {response.status_code}")
            break

    return dict


def get_all_attributes(wcapi: API) -> dict:

    dict = {}
    per_page = 100
    page = 1

    while True:
        # Retrieve attributes from the current page
        response = wcapi.get('products/attributes', params={'per_page': per_page, 'page': page})
        if response.status_code == 200:
            attributes = response.json()
            total_attributes = len(attributes)

            if total_attributes == 0:
                break

            for attribute in attributes:
                dict[attribute['name']] = attribute['id']
                dict[attribute['slug']] = attribute['id']

            if total_attributes < per_page:
                break

            page += 1
        else:
            print(f"Failed to fetch attributes from page {page}. Error code: {response.status_code}")
            break

    return dict


def check_name_in_dict(categories: dict, search_name: str) -> str:

    slug_search = search_name.strip().lower()
    slug_search = re.sub(r'[^a-zA-Z0-9\s]', '', slug_search)
    slug_search = slug_search.replace(' ', '-')

    if slug_search in categories:
        return categories[slug_search]

    if search_name in categories:
        return categories[search_name]


def add_new_category(wcapi: API, category_name: str) -> str:

    # Create a new category
    new_category_data = {
        'name': category_name,
    }

    # Send request with new category data
    response = wcapi.post('products/categories', new_category_data)

    # Get the category ID from response
    if response.status_code == 201:
        category_id = response.json().get('id')
        return category_id


def add_new_attribute(wcapi: API, variant_name: str) -> str:

    # Create a new attribute
    new_attribute_data = {
        'name': variant_name,
        'slug': variant_name.lower(),
        'type': 'select',
        'order_by': 'menu_order',
        'has_archives': True
    }

    # Send request with new attribute data
    response = wcapi.post('products/attributes', new_attribute_data)

    # Get the attribute ID from response
    if response.status_code == 201:
        new_attribute_id = response.json().get('id')
        # Category with the search name already exists
        return new_attribute_id


def delete_woocommerce_product(website: str, website_product_id: str) -> bool:

    # Woocommerce API
    wcapi = get_wcapi(website)

    # Send request to delete the product
    response = wcapi.delete(f"products/{website_product_id}", params={"force": True})
    if response.status_code == 200:
        return True
    return False


def upload_image(image_list: list, jwt: str, base_url: str) -> dict:

    media_url = base_url + 'media'
    headers = {
        'Authorization': 'Bearer ' + jwt
    }

    images_dict = {}

    for image_url in image_list:
        print(image_url)
        image_content = requests.get(image_url).content
        image_extension = os.path.splitext(image_url)[1]  # Extract the file extension from the URL
        image_file = BytesIO(image_content)
        files = {
            'file': (f'image{image_extension}', image_file)  # Include the filename and extension
        }
        response = requests.post(media_url, headers=headers, files=files)
        if response.status_code == 201:
            image_id = response.json().get('id')
            images_dict[image_url] = image_id
        else:
            images_dict[image_url] = ''
            print('Failed to upload the image. Error:', response.json())

    return images_dict


def upload_request(website: str, wcapi: API, category_id: str, title: str, weight: str, tags_list_woo: list,
                   image_list: list, sku: str, description: str,ul: str, attributes: list, variants: list,
                   ali_seller_id: str, ali_product_id: str, ali_product_url: str, seo_text: str) -> tuple:

    product_id = ''
    product_url = ''

    # Data structure
    data = {
        "sku": f"{sku}",
        "status": "publish", # draft
        "name": f"{title}",
        "tags": tags_list_woo,
        "slug": f"{title}",
        'price': '9.99',
        "on_sale": False,
        "sale_price": "",
        "weight": f"{weight}",
        "dimensions": {
            "length": "10",
            "width": "45",
            "height": "45"
        },
        "description": f"<center><p>{description}</p></center>",
        "short_description": f"<ul>{ul}</ul>",
        "categories": [{"id": f"{category_id}"}],
        "images": image_list,
        "has_options": True,
        "stock_quantity": None,
        "stock_status": "instock",
        "low_stock_amount": None,
        "manage_stock": False,
        "purchasable": True,
        "shipping_class_id": 0,
        "shipping_required": True,
        "catalog_visibility": "visible",
        "type": "variable",
        "attributes": attributes,
        "meta_data": [{"key": "seller_id",
                       "value": ali_seller_id},
                      {"key": "product_id",
                       "value": ali_product_id},
                      {"key": "product_url",
                       "value": ali_product_url},
                      {'key': 'metadesc',
                       'value': seo_text},
                      ],
    }

    # Send request with the new product data
    try:
        print('Creating product')
        response = wcapi.post("products", data)
        res = response.json()
        if response.status_code == 400:
            if res['code'] == 'product_invalid_sku':
                product_to_delete = res['data']['resource_id']
                response = wcapi.delete(f"products/{product_to_delete}", params={"force": True})
                print('deleted')
                time.sleep(20)
                if response.status_code == 200:
                    print('upload_again')
                    upload_request(website, wcapi, category_id, title, weight, tags_list_woo, image_list, sku,
                                   description, ul, attributes, variants, ali_seller_id, ali_product_id,
                                   ali_product_url, seo_text)

    except:
        print('Error while uploading the product')
        return product_id, product_url

    product_id = res.get('id', '')
    product_url = res.get('permalink', '')
    # images = res.get('images', '')
    # main_image_id = images[0]['id']

    if product_id:
        # Create variant data
        print('Creating variants')

        try:
            # Send request with the new variants data
            variants_data = {"create": variants}
            response = wcapi.post(f'products/{product_id}/variations/batch', variants_data)
            print(response.status_code)

        except:
            print('Product without variation, rollback deleting product')

        return product_id, product_url

    return product_id, product_url


def upload_product(website: str, key: str, secret: str, upload_products_id: list) -> bool:

    # Open variants data json
    with open('data_variants.json', 'r') as json_file:
        data = json.load(json_file)

    with open('./backup/backup_variants.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Woocommerce API setup
    print('Getting Woo api client')
    wcapi = get_wcapi(website, key, secret)

    # WordPress API setup
    jwt = get_access_token(website)
    base_url = f'https://{website}/wp-json/wp/v2/'

    # Get all categories from site
    print('Getting all site categories')
    categories_dict = get_all_categories(wcapi)

    # Get all attributes from site
    print('Getting all site attributes')
    attributes_dict_woo = get_all_attributes(wcapi)

    for upload_product_id in upload_products_id:

        # Check if the sku exists in variation file
        if upload_product_id not in data['data']['product_id']:
            continue

        # Check if the item already in website
        in_list = False
        for site in data['data']['product_id'][upload_product_id]['site']:
            if site['site'] == website:
                print(f'Item {upload_product_id} is already exists in {website}')
                in_list = True
                break

        if in_list:
            continue


        product = data['data']['product_id'][upload_product_id]
        title = product['title']
        print(f'-{title}')
        variants = product['variants']
        attributes = product['attributes']
        sku = product['sku']
        category = product['category']
        ali_seller_id = product['ali_seller_id']
        ali_product_id = product['ali_product_id']
        ali_product_url = product['ali_product_url']
        images = product['images_list']
        tag_list = []
        weight = ''
        description = product['details']
        ul = """<ul><li>High quality products.</li><li>Durable materials and designed to last.</li>
                <li>Unique and stylish designs.</li><li>Trendy and distinctive home décor.</li>
                <li>Carefully packed.</li></ul>"""
        seo_text = f'High quality {title}, Unique and stylish design, Durable materials Trendy and distinctive home décor.'

        # Checks if the category already exists in Woo. if not, creating
        category_id = check_name_in_dict(categories_dict, category)

        if not category_id:

            # Adding new category
            category_id = add_new_category(wcapi, category)
            if category_id != 0:
                categories_dict[category] = category_id


        # Checks if attribute already exists in Woo. if not, creating
        variant_ids = {}
        for attribute in attributes:
            name = attribute['name']
            var_id = check_name_in_dict(attributes_dict_woo, name)
            if not var_id:
                var_id = add_new_attribute(wcapi, name)
                attributes_dict_woo[name] = var_id
            variant_ids[name] = var_id


        # Add ids to variants list and attributes list
        for variant in variants:
            for attribute in variant['attributes']:
                name = attribute['name']
                attribute['id'] = variant_ids[name]

        for attribute in attributes:
            name = attribute['name']
            attribute['id'] = variant_ids[name]


        # Uploading images for variations
        unique_urls = []
        [unique_urls.append(item['image']['src']) for item in variants if item['image']['src'] not in unique_urls]

        images_dict = upload_image(unique_urls, jwt, base_url)


        for variant in variants:
            url = variant['image']['src']
            id = images_dict[url]
            if id:
                variant['image']['id'] = id
                # variant['image']['src'] = ''
                # del variant['image']['src']

        # images
        image_list = []
        for i, image in enumerate(images):
            if image in images_dict:
                image = {"image_id": images_dict[image],
                         "alt": f"{title}"}
            else:
                image = {"src": f"{image}",
                         "alt": f"{title}"}

            image_list.append(image)
            if i > MAX_IMG:
                break


        # Tags
        tags_list_woo = []
        for tag in tag_list:
            tags_list_woo.append({'name': tag})

        product_id, product_url = upload_request(website, wcapi, category_id, title, weight, tags_list_woo, image_list,
                                                 sku, description, ul, attributes, variants, ali_seller_id,
                                                 ali_product_id, ali_product_url, seo_text)

        new_data = {
            "site": website,
            "product_id": product_id,
            "product_url": product_url,
        }

        data['data']['product_id'][upload_product_id]['site'].append(new_data)

        print(product_id, product_url)

        with open('data_variants.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)



