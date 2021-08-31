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

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/gucci/'
main_url = 'http://gucci.com'

def chrome_option_initiate():
    options = webdriver.ChromeOptions()
    #options.add_argument('headless')
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

def screenshot(url, dir):
    date_dir = mk_date_dir(dir)
    main_dir = date_dir + '/main'
    mk_dir(main_dir)
    driver = chrome_option_initiate()
    driver.get(url)
    driver.implicitly_wait(3)

    ttl_height = driver.execute_script("return document.body.scrollHeight")
    num = ttl_height // 1080 + 1

    for n in range(num):
        time.sleep(rd.randint(1, 3))
        driver.save_screenshot(main_dir + '/'+ str(n) + '.png')
        driver.execute_script("window.scrollTo(0, {})".format((n+1)*1080))
        driver.implicitly_wait(3)

screenshot(main_url, base_dir)

# new arrival의 하위 카테고리에 맞춰 sub dir 생성, 링크 return
def get_new_title_url():
    driver = chrome_option_initiate()
    driver.get('https://www.gucci.com/kr/ko/st/what-new')
    driver.implicitly_wait(3)
    lis = driver.find_elements_by_xpath("""//*[@id="header-nav-child-main"]/ul[1]/li[2]/section/div/ul/li[1]/div/div[2]/ul""")
    link_dict = {}
    if lis:
        print('lis okay')
    for li in lis:
        if li.get_attribute('text'):
            print('li okay')
            text = li.get_attribute('text').strip()
            url = li.get_attribute('href')
            link_dict[text] = url
            print(link_dict)
            time.sleep(1)
    return link_dict


def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    driver.close()

# new arrival sub link >> 아이템별 img, 제품명, 세부정보 페이지 url
def get_items(link):
    driver = chrome_option_initiate()
    driver.get(link)
    driver.implicitly_wait(3)
    item_df = pd.DataFrame(columns=['url', 'prdt_nm', 'prdt_cd', 'price', 'prdt_img_url', 'prdt_img'])
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    driver.implicitly_wait(3)
    time.sleep(3)
    articles = driver.find_elements_by_css_selector(".product-tiles-grid-item-link")
    for i, article in enumerate(articles):
        item_df.loc[i, 'url'] = article.get_attribute('href')
        prdt_nm = article.get_attribute('aria-label')
        item_df.loc[i, 'prdt_nm'] = prdt_nm
        prdt_cd = article.get_attribute('data-style-id')
        item_df.loc[i, 'prdt_cd'] = prdt_cd
        driver.implicitly_wait(3)
        item_df.loc[i, 'price'] = article.find_element_by_css_selector('div.product-tiles-grid-item-detail > div.product-tiles-grid-item-info > p.price > span.sale')
        div = article.find_elements(By.CLASS_NAME, 'product-tiles-grid-item-image-wrapper')[0]
        img = div.find_element_by_css_selector(".product-tiles-grid-item-image .lazy")
        img_url = img.get_attribute("src")
        if img_url:
            print(img_url)
            item_df.loc[i, 'prdt_img_url'] = img_url
            time.sleep(rd.randint(1, 3))
            base_path = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) + '/product'
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            path = base_path + '/'+ str(prdt_nm).strip() + prdt_cd + '.png'
            save_img(img_url, path)
            item_df.loc[i, 'prdt_img'] = path
        else:
            print(img_url, prdt_nm, ' img is not saved')

    path = base_path + '/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) + '.csv'
    if not os.path.exists(path):
        item_df.to_csv(path, index=False, mode='w')
    else:
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for i, row in item_df.iterrows():
                writer.writerow(
                    [item_df.loc[i, 'url'], item_df.loc[i, 'prdt_nm'], item_df.loc[i, 'prdt_img_url'], item_df.loc[i, 'prdt_img'],
                     item_df.loc[i, 'price'], item_df.loc[i, 'prdt_cd'], item_df.loc[i, 'color'], item_df.loc[i, 'description']])
        item_df.to_csv(path, index=False, mode='a', header=False, cols=['url', 'prdt_nm', 'prdt_cd', 'price', 'prdt_img_url', 'prdt_img'], encoding='euc-kr')

    return item_df

get_items('https://www.gucci.com/kr/ko/ca/women/womens-handbags-c-women-handbags')


def get_item_detail(item_df):
    driver = chrome_option_initiate()
    for i in range(len(item_df)):
        driver.get(item_df.loc[i, 'url'])
        driver.implicitly_wait(3)
        item_df.loc[i, 'prdt_cd'] = driver.find_element_by_css_selector(".style-number-title").text
        item_df.loc[i, 'description'] = driver.find_element_by_css_selector("#product-details > div.product-detail > p").text
        product_info = driver.find_elements_by_css_selector("#product-details > div.product-detail > ul > li")
        info_list = []
        for info in product_info:
            info_list.append(info.text)
        item_df.loc[i, 'detail'] = [', '.join(info_list)]
        item_df.loc[i, 'get_date'] = dt.datetime.today()
    print(item_df)


    return item_df

# driver = chrome_option_initiate()
# driver.get('https://www.gucci.com/kr/ko/pr/men/mens-bags/mens-backpacks/gg-embossed-backpack-p-6257701W3BN1000')
# product_info = driver.find_elements_by_css_selector("#product-details > div.product-detail > ul > li")
# info_list = []
# for info in product_info:
#     info = info.text
#     print(info)
#     info_list.append(info)
# print(info_list)

def get_multi_items(link_list):
    for link in link_list:
        get_items(link)

# link = 'https://www.gucci.com/kr/ko/ca/women/womens-handbags-c-women-handbags'
# get_item_detail(get_items(link))

# 신상품 카테고리 링크
 # https://www.gucci.com/kr/ko/ca/whats-new/on-the-runway-c-new-runway
 # https://www.gucci.com/kr/ko/st/capsule/resort
 # https://www.gucci.com/kr/ko/st/capsule/men-gg-embossed
 # https://www.gucci.com/kr/ko/ca/beauty/makeup/lipstick/metallic-lipsticks-c-lips-metallic
 # https://www.gucci.com/kr/ko/st/capsule/circular-line-off-the-grid
 # https://www.gucci.com/kr/ko/st/capsule/gucci-tennis-1977-sneakers

# 여성 핸드백
# https://www.gucci.com/kr/ko/ca/women/womens-handbags-c-women-handbags
# 여성 모자
# https://www.gucci.com/kr/ko/ca/women/womens-accessories/womens-hats-c-women-hats
# 여성 슈즈
# https://www.gucci.com/kr/ko/ca/women/womens-shoes-c-women-shoes

# 남성 가방
# https://www.gucci.com/kr/ko/ca/men/mens-bags-c-men-bags
# 남성 모자
# https://www.gucci.com/kr/ko/ca/men/mens-accessories/mens-hats-c-men-hats
# 남성 슈즈
# https://www.gucci.com/kr/ko/ca/men/mens-shoes-c-men-shoes



