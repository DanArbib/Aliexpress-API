from flask import request, jsonify, send_file, Response
from datetime import datetime, timedelta, timezone
from app import app
from utils.scrape_search import scrape_pages
from utils.product_info import process_product
from utils.woo import upload_product
import json

def paginate_data(data, page, per_page):
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_data = data[start_index:end_index]
    return paginated_data

@app.route("/api/v1/search", methods=['POST'])
def search():

    data = request.json

    category_id = data.get('category_id')
    category_name = data.get('category_name')
    search_text = data.get('search_text')
    max_price = float(data.get('max_price'))
    min_price = float(data.get('min_price'))
    start_page = int(data.get('start_page'))
    end_page = int(data.get('end_page'))

    scrape_pages(search_text, category_id, start_page,end_page , max_price, min_price, category_name)

    return jsonify({'status': 'scrape ended successfully.'}), 200


@app.route("/api/v1/get-search", methods=['GET'])
def get_search():

    # Load your JSON data into a list
    with open('data_search.json', 'r') as json_file:
        data = json.load(json_file)

    # Get query parameters for page and per_page with default values
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    category_id = request.args.get('category_id', None)

    data = data['data']['category_id'][category_id]

    # Paginate the data
    paginated_data = paginate_data(data, page, per_page)

    # Create a response JSON
    response = {
        'page': page,
        'per_page': per_page,
        'total_items': len(data),
        'data': paginated_data
    }

    return jsonify(response)



@app.route("/api/v1/process-products", methods=['POST'])
def process_products():

    data = request.json

    category_id = data.get('category_id')
    sellers_list = data.get('sellers_list')

    process_product(category_id, sellers_list)

    return jsonify({'status': 'Product process ended successfully.'}), 200



@app.route("/api/v1/upload", methods=['POST'])
def upload():

    data = request.json

    website = data.get('website')
    key = data.get('key')
    secret = data.get('secret')
    products_sku_list = data.get('products_sku_list')

    upload_product(website, key, secret, products_sku_list)

    return jsonify({'status': 'Product process ended successfully.'}), 200


