from pip._vendor import requests
from selenium import webdriver
import random as rd
import datetime as dt
import pandas as pd
import time
import os
from selenium.webdriver.common.by import By
import requests
import numpy as np
import csv

def chrome_option_initiate():
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
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


base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/'
url_dict = {'gucci':'http://gucci.com', 'prada':'https://www.prada.com/kr/ko.html',
        'dior':'https://www.dior.com/ko_kr', 'louisvuitton':'https://kr.louisvuitton.com/',
        'burberry':'https://kr.burberry.com/'}

def mk_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory

def screenshot(driver, main_dir):
    ttl_height = driver.execute_script("return document.body.scrollHeight")
    num = ttl_height // 1080 + 1
    for n in range(num):
        time.sleep(rd.randint(1, 3))
        driver.save_screenshot(main_dir + '/main_'+ str(n) + '.png')
        driver.execute_script("window.scrollTo(0, {})".format((n+1)*1080))
        driver.implicitly_wait(3)

def get_main_page(url_dict):
    for brand, url in url_dict.items():
        dir = base_dir + str(brand) + '/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
        mk_dir(dir)
        main_dir = dir + '/main'
        mk_dir(main_dir)
        driver = chrome_option_initiate()
        driver.get(url)
        screenshot(driver, main_dir)


get_main_page(url_dict)


def get_comm_page(url_dict):
    for brand, url in url_dict.items():
        dir = base_dir + str(brand) + '/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
        mk_dir(dir)
        main_dir = dir + '/main_m'
        mk_dir(main_dir)
        driver = chrome_option_initiate()
        driver.get(url)
        screenshot(driver, main_dir)

# url_dict2 = {'gucci': 'https://www.gucci.com/kr/ko/st/stories'}
# url_dict2 = {'prada': 'https://www.prada.com/kr/ko/women/re-nylon.html'}

# url_dict2 = {'dior':'https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1'} 디올여성패션
# url_dict2 = {'dior':'https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EB%82%A8%EC%84%B1'} 디올남성패션
# get_comm_page(url_dict2)