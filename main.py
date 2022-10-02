from unicodedata import name
import requests
import cloudscraper


import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import datetime

def get_price():
    URL = "https://www.futbin.com/23/player/26281/erling-haaland"
    options = FirefoxOptions()
    options.add_argument('--headless' )
    driver = webdriver.Firefox(options=options)
    driver.get(URL)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # # find span id "pc-lowest-1" and get the text
    # price = soup.find("span", {"id": "pc-lowest-1"}).text
    # print("PC:", price)
    # price = soup.find("span", {"id": "ps-lowest-1"}).text  
    # print("PS:", price)

    # find div id "pr_pc" and get the text
    price = soup.find("div", {"id": "pr_pc"}).text
    print("PC:", price)
    # price = soup.find("div", {"id": "pr_ps"}).text
    # print("PS:", price)
    driver.quit()


def main():
    print("Starting...")
    #inifi loop
    while True:
        get_price()
        time.sleep(60)

if __name__ == '__main__':
    main()