from selenium import webdriver
from bs4 import BeautifulSoup as bs
import random as rd
import datetime as dt
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
from urllib.parse import quote_plus
import os
from selenium.webdriver.support.ui import WebDriverWait


def chrome_option_initate():
    options = webdriver.ChromeOptions()
    #options.add_argument('headless')
    options.add_argument('--start-maximize')
    options.add_argument("disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    options.add_argument("lang=ko_KR")
    driver = webdriver.Chrome('C:/app/chromedriver', options=options)
    driver.get('about:blank')
    driver.set_window_size(1024, 600)
    driver.maximize_window()
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    return driver

directory = '//172.0.0.112/mlb/process_team/luxury_brand/louisvuitton/mainpage/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
if not os.path.exists(directory):
    os.mkdir(directory)

driver = chrome_option_initate()
driver.get('https://kr.louisvuitton.com/kor-kr/homepage')

n = 1
driver.implicitly_wait(1)
driver.save_screenshot(directory + '/' + str(n) + '0.png')
n += 1
wait = WebDriverWait(driver,10)
wait.until(EC.element_to_be_clickable((By.LINK_TEXT, '다음')))
next = driver.find_elements_by_link_text('다음')
next.click()
driver.implicitly_wait(1)
driver.save_screenshot(directory + '/' + str(n) + '0.png')
n += 1
# access denied... 안댜....