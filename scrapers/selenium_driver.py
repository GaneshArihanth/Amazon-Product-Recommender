from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")

    # For Selenium 4+, the recommended initialisation is to pass options only.
    # This assumes a compatible ChromeDriver is available on PATH.
    driver = webdriver.Chrome(options=chrome_options)
    return driver
