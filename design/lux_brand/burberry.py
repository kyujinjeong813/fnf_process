from pip._vendor import requests
from selenium import webdriver
import random as rd
import datetime as dt
import pandas as pd
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import requests
import numpy as np
import csv
from sqlalchemy import create_engine

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/burberry/'
#test_url = 'https://kr.burberry.com/tb-summer-monogram-collection-women/'
test_url = 'https://kr.burberry.com/mens-sneakers/'
new_url = 'https://kr.burberry.com/womens-new-arrivals-new-in/'
new_men = 'https://kr.burberry.com/mens-new-arrivals-new-in/'
w_print = 'https://kr.burberry.com/womens-in-print/'
m_mono = 'https://kr.burberry.com/tb-summer-monogram-collection-men/'
m_print = 'https://kr.burberry.com/mens-in-print/'
w_bags = 'https://kr.burberry.com/womens-bags/'
m_acc = 'https://kr.burberry.com/mens-accessories/'
m_bag = 'https://kr.burberry.com/mens-bags/'


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

def mk_date_dir(dir):
    date_dir = dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    if not os.path.exists(date_dir):
        os.mkdir(date_dir)
    return date_dir

def mk_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    driver.close()

def db_insert(df):
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name = 'db_ds_lux_product', con=engine, schema='public',
              if_exists='append', index=False,)
    conn.close()

def product_info(link):
    date_dir = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    mk_dir(date_dir)
    product_dir = date_dir + '/product'
    mk_dir(product_dir)
    driver = chrome_option_initiate()
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    driver.implicitly_wait(rd.randint(5, 8))
    contents = driver.find_elements_by_css_selector("div.col-lg-3.col-md-3")
    driver.implicitly_wait(rd.randint(1, 3))
    df = pd.DataFrame(columns=['domain', 'url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'prdt_cd', 'color', 'price'])

    for i, content in enumerate(contents):
        try:
            a = content.find_element_by_css_selector('div > div.cell-asset.cell-placeholder-3-4 > a')
            url = a.get_attribute('href')
            df.loc[i, 'url'] = url
            product_cd = a.get_attribute('data-product-id')
            df.loc[i, 'prdt_cd'] = product_cd
            product_color = a.get_attribute('aria-label').split('(')[-1].replace(')','')
            df.loc[i, 'color'] = product_color
            time.sleep(rd.randint(1, 3))
            product_nm = a.get_attribute('aria-label').split('(')[0]
            df.loc[i, 'prdt_nm'] = product_nm
            driver.implicitly_wait(1)
            domain_nm = content.find_element_by_css_selector('div > div.cell-text-wrapper > div.product-card-description-wrapper > div.product-card-description > div.product-card-label > p').text
            df.loc[i, 'domain'] = domain_nm
            prdt_price = content.find_element_by_css_selector('div > div.cell-text-wrapper > div.product-card-description-wrapper > div.product-card-price-container > div > p > span').text
            df.loc[i, 'price'] = prdt_price
            time.sleep(rd.randint(1, 3))
            img_url = content.find_element_by_css_selector(
                'div.cell-asset-wrapper.asset-item.js-asset-item.asset-visible.asset-loaded > div > div > img').get_attribute(
                'src')
            df.loc[i, 'prdt_img_url'] = img_url
            product_img = product_dir + '/' + str(product_nm).replace(' ', '').strip() + str(product_cd).replace(' ', '').strip() + '.png'
            save_img(img_url, product_img)
            df.loc[i, 'prdt_img'] = product_img
        except NoSuchElementException:
            print("Unable to locate element")

    print(df)
    path = product_dir + '/' + 'product_detail.csv'
    df.to_csv(path,index=False, mode='a', header=False)
    db_insert(df)

# 왜 아무것도 안뜨지 흑흑 끼루룩
product_info(new_url)
product_info(new_men)

