from bs4 import BeautifulSoup
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from utils.selenium_driver import set_driver


def get_shipping_info(driver, product_id):
    # Getting the url page
    print(f"Entering page - {product_id}")

    driver.get(f"https://www.aliexpress.us/item/{product_id}.html?_randl_shipto=US")

    # bs4 soup
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')


    # Getting the shipping info

    shipping_div = soup.find('div', class_='dynamic-shipping')
    print(shipping_div)
    if shipping_div:
        # Extract text from the div
        div_text = shipping_div.get_text()
        print(div_text)
        if 'free shipping' in div_text.lower().strip():
            shipping_fee = 0
        else:
            # Extract shipping fee (Free Shipping or float price)
            shipping_fee_match = re.search(r'(?:Shipping: )([0-9.]+|Free Shipping)', div_text)
            if shipping_fee_match:
                shipping_fee = shipping_fee_match.group(1)
            else:
                shipping_fee = None

        # Extract delivery date (Oct 25 or Oct 29, etc.)
        delivery_date_match = re.search(r'(?:delivery by|delivery on)\s+([A-Za-z]+\s+\d+)', div_text)
        if delivery_date_match:
            delivery_date = delivery_date_match.group(1)
            delivery_days = get_days(delivery_date)
        else:
            delivery_date = None
            delivery_days = None

        print(shipping_fee, delivery_date, delivery_days)
        return shipping_fee, delivery_date, delivery_days
    else:
        return None, None, None


def get_days(date_str: str) -> int:
    try:
        # Get the current year
        current_year = datetime.now().year

        # Combine the current year with the month and day from the future date string
        date_str_with_year = f"{current_year} {date_str}"

        # Convert the combined string to a datetime object
        future_date = datetime.strptime(date_str_with_year, '%Y %b %d')

        # Get the current date as a datetime object
        current_date = datetime.now()

        # Calculate the difference between future date and current date
        time_difference = future_date - current_date

        # Extract the number of days from the difference
        days_until_future = time_difference.days

        return days_until_future
    except ValueError:
        # Handle invalid date format
        return -1
