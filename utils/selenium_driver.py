import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def set_driver():
    utils_folder = os.getcwd()

    folder_path = os.path.join(os.getcwd(), 'utils')
    print(folder_path)
    service_chrome = Service(f"{folder_path}\chromedriver.exe")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

    options = webdriver.ChromeOptions()
    options.binary_location = f"{folder_path}\chrome-win64\chrome.exe"
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=service_chrome, options=options)
    return driver