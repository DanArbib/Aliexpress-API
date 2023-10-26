from utils.process_csv import process_csv
from utils.product_info import process_product
from utils.woo import upload_product
import os
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':

    select = int(input('1. Process csv\n2. Product info\n3. Upload\n'))

    if select == 1:
        process_csv()

    if select == 2:
        sellers_list = ['1101557921']
        process_product(sellers_list)

    if select == 3:

        # Upload
        website = ''
        key = os.getenv('WEBSITE_KEY')
        secret = os.getenv('WEBSITE_SECRET')
        upload_products_id = ['1005003579233360']
        upload_product(website, key, secret, upload_products_id)




