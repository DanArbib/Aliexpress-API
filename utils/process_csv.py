import os, csv, re, json
from ali_sdk import iop
from ali_sdk.iop import IopClient

def ali_client() -> IopClient:
    """
    Setting the API client for Aliexpress
    :return: ali client
    """

    url = 'https://api-sg.aliexpress.com/sync'
    app_key = os.getenv('APP_KEY_ALI')
    app_secret = os.getenv('APP_SECRET_ALI')
    client = iop.IopClient(url, app_key, app_secret)

    return client


def extract_id(url: str) -> str:
    """
    Extract the id from the aliexpress url
    :param url:
    :return: id
    """

    # Define a regular expression pattern to match the ID in the URL
    pattern = r'/(\d+)\.html'

    # Use re.search to find the first match in the URL
    match = re.search(pattern, url)

    if match:
        # The group(1) will contain the matched ID
        item_id = match.group(1)
        return item_id
    else:
        return None


def get_seller_information(product_id: str) -> dict:
    """
    Get the seller information from Aliexpress API to init new seller in db
    :param product_id:
    :return: dict
    """

    client = ali_client()

    request = iop.IopRequest('aliexpress.ds.product.get')
    request.add_api_param('ship_to_country', 'US')
    request.add_api_param('product_id', product_id)
    request.add_api_param('target_currency', 'USD')
    request.add_api_param('target_language', 'en')

    response = client.execute(request)
    data = response.body

    seller_info = data['aliexpress_ds_product_get_response']['result']['ae_store_info']

    store_id = seller_info['store_id']
    store_name = seller_info['store_name']


    res_data = {
        "store_id": store_id,
        "store_name": store_name.strip()
    }

    return res_data

def process_csv() -> bool:
    """
    Get the last saved csv file in csv folder and extract the product ids.
    Save in JSON file with the seller's information
    :return: bool
    """

    seller_information = {}

    with open('data_search.json', 'r') as json_file:
        data_search = json.load(json_file)

    # Backup data
    with open('./backup/data_search.json', 'w') as json_file:
        json.dump(data_search, json_file, indent=4)

    # Initiate sellers in JSON file
    if 'sku' not in data_search['data']:
        data_search['data']['sellers'] = {}

    # Get a list of all CSV files in the directory
    csv_files = [f for f in os.listdir('csv') if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the directory.")
        return False

    # Sort the list of CSV files by modification time (most recent first)
    csv_files.sort(key=lambda x: os.path.getmtime(os.path.join('csv', x)), reverse=True)

    # Get the path to the last modified CSV file
    last_saved_csv = os.path.join('csv', csv_files[0])

    # Open and read the last saved CSV file
    with open(last_saved_csv, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)

        for row in csv_reader:

            # Extract the product id for row
            product_id = extract_id(row[1])

            if product_id:
                if not seller_information:

                    # Extract seller information from Aliexpress API
                    seller_information = get_seller_information(product_id)

                    # Check if seller already exists or not
                    store_id = seller_information['store_id']
                    if store_id not in data_search['data']['sellers']:

                        data_search['data']['sellers'][store_id] = seller_information
                        data_search['data']['sellers'][store_id]['products'] = []

                # Adding the products id from the seller
                if product_id not in data_search['data']['sellers'][store_id]['products']:
                    data_search['data']['sellers'][store_id]['products'].append(product_id)

    # Update json with new data
    with open('data_search.json', 'w') as json_file:
        json.dump(data_search, json_file, indent=4)

    return True









