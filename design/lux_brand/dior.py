from selenium import webdriver
from bs4 import BeautifulSoup as bs
import random as rd
import datetime as dt
import os
import time
import pandas as pd
import requests
import csv
from sqlalchemy import create_engine
from selenium.common.exceptions import NoSuchElementException

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/dior/'
main_url = 'https://www.dior.com/ko_kr'
date_dir = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))

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
        driver.implicitly_wait(3)
        driver.execute_script("window.scrollTo(0, {})".format((n+1)*1080))

# screenshot(main_url, base_dir)

w_bags = 'https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1-%EA%B0%80%EB%B0%A9/%EB%AA%A8%EB%93%A0-%EA%B0%80%EC%A3%BD%EC%A0%9C%ED%92%88'
m_bags = 'https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EA%B0%80%EC%A3%BD-%EC%A0%9C%ED%92%88/%EC%A0%84%EC%B2%B4-%EA%B0%80%EC%A3%BD-%EC%A0%9C%ED%92%88'
w_shoes = 'https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1-%EC%8A%88%EC%A6%88/%EB%AA%A8%EB%93%A0-%EC%8A%88%EC%A6%88'
m_shoes = 'https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%8A%88%EC%A6%88/%EB%AA%A8%EB%93%A0-%EC%8A%88%EC%A6%88'
w_fall = 'https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/2020-%EA%B0%80%EC%9D%84-%EC%BB%AC%EB%A0%89%EC%85%98'

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    driver.close()

def db_insert(df):
    df = df[['domain', 'url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'prdt_cd', 'color', 'price']]
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name = 'db_ds_lux_product', con=engine, schema='public',
              if_exists='append', index=False,)
    conn.close()

def product_info(link, domain):
    date_dir = mk_date_dir(base_dir)
    mk_dir(date_dir + '/product')
    driver = chrome_option_initiate()
    driver.get(link)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    driver.implicitly_wait(3)
    contents = driver.find_elements_by_css_selector("a.product-link")
    df = pd.DataFrame(
        columns=['url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'price', 'prdt_cd', 'color', 'description'])
    #6개 제한인거같음...
    for i, content in enumerate(contents):
        try:
            df.loc[i, 'url'] = content.get_attribute('href')
            prdt_nm = content.find_element_by_css_selector(
                "div.product-legend > span.title-with-level > span.multiline-text").text
            df.loc[i, 'prdt_nm'] = prdt_nm
            description = content.find_element_by_css_selector("div.product-legend > p.product-subtitle").text
            df.loc[i, 'description'] = description
            time.sleep(rd.randint(1, 3))
            prdt_img_url = content.find_element_by_css_selector("div.product-image > div.image > img").get_attribute(
                'src')
            df.loc[i, 'prdt_img_url'] = prdt_img_url
            prdt_img = date_dir + '/product/' + str(prdt_nm).replace(' ', '').strip() + str(description).replace(' ',
                                                                                                                 '').strip() + '.png'
            time.sleep(rd.randint(1, 3))
            save_img(prdt_img_url, prdt_img)
            df.loc[i, 'prdt_img'] = prdt_img
            df.loc[i, 'price'] = content.find_element_by_css_selector("div.product-legend > span.price-line").text
            df.loc[i, 'color'] = ''
        except NoSuchElementException:
            print("Unable to locate element")

    path = date_dir + '/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) + '.csv'
    if not os.path.exists(path):
        df.to_csv(path, index=False, mode='w')
    else:
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for i, row in df.iterrows():
                writer.writerow(
                    [df.loc[i, 'url'], df.loc[i, 'prdt_nm'], df.loc[i, 'prdt_img_url'], df.loc[i, 'prdt_img'],
                     df.loc[i, 'price'], df.loc[i, 'prdt_cd'], df.loc[i, 'color'], df.loc[i, 'description']])
        df.to_csv(path, index=False, mode='a', header=False, cols=['url', 'prdt_nm','prdt_img_url', 'prdt_img','prdt_cd','color', 'price', 'description'])
    df['domain'] = domain
    df = df[['domain','url', 'prdt_nm','prdt_img_url', 'prdt_img','prdt_cd','color', 'price']]
    db_insert(df)
    return df

product_info(w_fall, 'w_fall')

# def get_product_detail(url):
#     base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/prada/'
#     driver = chrome_option_initiate()
#     driver.get(url)
#     html = driver.page_source
#     soup = bs(html, 'html.parser')
#     prdt_nm = soup.select_one('#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > h1').text
#     prdt_cd = soup.select_one('#pdp_details > div > article.tab__item.js-tab.tab__item--visible.js-tab-visible > div > div > b').text
#     price = soup.select_one('#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > div.pDetails__price.price.js-product-details-price > div > span').text
#     color = soup.select_one('#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > div.pDetails__conf > div.pDetails__color > div > div > div.customSelect__select.hidePlaceholder > div > a.customSelect__input.customSelect__selected > span').text
#     description = soup.select_one('#pdp_details > div > article.tab__item.js-tab.tab__item--visible.js-tab-visible > div > div > p').text
#     prdt_img_url = soup.select_one('#mainPdpContent > section.pDetails > div > div.pDetails__wrapperImg > div > div > div.pDetails__slider.js-slider.js-scrollImage.slick-initialized.slick-slider.slick-dotted > div > div > div.pDetails__slide.js-imgProduct.slick-slide.slick-current.slick-active > a > picture > img').get('src')
#     base_path = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) + '/product'
#     mk_dir(base_path)
#     prdt_img = base_path + '/' + str(prdt_nm).strip() + prdt_cd + '.png'
#     save_img(prdt_img_url, prdt_img)
#
#     return {'url':url, 'prdt_nm':prdt_nm, 'prdt_cd':prdt_cd, 'price':price, 'color':color, 'description':description, 'prdt_img_url':prdt_img_url, 'prdt_img':prdt_img}
#
# def get_multi_items(link_list):
#     df = pd.DataFrame(
#         columns={'url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'url', 'price', 'prdt_cd', 'color', 'description',
#                  'prdt_img_url', 'prdt_img'})
#     for link in link_list:
#         result = get_product_detail(link)
#         result_df = pd.DataFrame([result])
#         final_df = df.append(result_df)
#         time.sleep(rd.randint(1, 3))
#     path = date_dir+'/product-' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) +'.csv'
#     final_df.to_csv(path, mode='a', index=False)
