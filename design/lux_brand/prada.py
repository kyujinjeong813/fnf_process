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

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/prada/'
main_url = 'https://www.prada.com/kr/ko.html'
date_dir = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))

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

def mk_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

w_bags = 'https://www.prada.com/kr/en/women/bags.html?page='
w_new_bags = 'https://www.prada.com/kr/ko/women/new_in/bags.html'
m_new_bags = 'https://www.prada.com/kr/ko/men/new_in/bags.html'
w_new = 'https://www.prada.com/kr/ko/women/new_in.html'
m_new = 'https://www.prada.com/kr/ko/men/new_in.html?page='
m_bags = 'https://www.prada.com/kr/ko/men/bags.html?page='
m_acc = 'https://www.prada.com/kr/en/men/accessories.html?page='
# https://www.prada.com/kr/en/women/bags.html?page=2# (이런 식으로 페이지 # 지정해서 긁어오면 됨)

w_bucket = 'https://www.prada.com/kr/en/women/essentials/prada_duet.html'
w_linea_rossa = 'https://www.prada.com/kr/en/collection-hub/women_prada_linea_rossa.html?page=3&category=all'

def page_links(base_url, num):
    url_list = []
    for i in range(num):
        url = base_url + str(i+1)
        url_list.append(url)
    return url_list

def get_links(base_url, num=1):
    prada = 'https://www.prada.com/'
    url_list = page_links(base_url, num)
    link_list = []
    for url in url_list:
        driver = chrome_option_initiate()
        driver.get(url)
        html = driver.page_source
        soup = bs(html, 'html.parser')
        contents = soup.findAll('div', {'class': 'gridCategory__item'})
        for content in contents:
            item = content.select('div > div.productQB__wrapperOut > a:nth-of-type(1)')
            for i in item:
                url = prada + i.get('href')
                link_list.append(url)
    print(link_list)
    return link_list

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    driver.close()

def get_product_detail(url):
    mk_dir(date_dir)
    driver = chrome_option_initiate()
    driver.get(url)
    try:
        prdt_nm = driver.find_element_by_css_selector('div#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > h1').text
        prdt_cd = driver.find_element_by_css_selector(
            'section#pdp_details > div > article.tab__item.js-tab.tab__item--visible.js-tab-visible > div > div > b').text
        price = driver.find_element_by_css_selector(
            'div#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > div.pDetails__price.price.js-product-details-price > div > span').text
        color = driver.find_element_by_css_selector(
            'div#mainPdpContent > section.pDetails > div > div.pDetails__wrapper > div > div.pDetails__conf > div.pDetails__color > div > div > div.customSelect__select.hidePlaceholder > div > a.customSelect__input.customSelect__selected > span').text
        description = driver.find_element_by_css_selector(
            'section#pdp_details > div > article.tab__item.js-tab.tab__item--visible.js-tab-visible > div > div > p').text
        prdt_img_url = driver.find_element_by_css_selector(
            'div#mainPdpContent > section.pDetails > div > div.pDetails__wrapperImg > div > div > div.pDetails__slider.js-slider.js-scrollImage.slick-initialized.slick-slider.slick-dotted > div > div > div.pDetails__slide.js-imgProduct.slick-slide.slick-current.slick-active > a > picture > img').get_attribute(
            'src')
        base_path = date_dir + '/product'
        mk_dir(base_path)
        prdt_img = base_path + '/' + str(prdt_nm).strip() + prdt_cd + '.png'
        save_img(prdt_img_url, prdt_img)
    except NoSuchElementException:
        print("Unable to locate element")

    return {'url':url, 'prdt_nm':prdt_nm, 'prdt_cd':prdt_cd, 'price':price, 'color':color, 'description':description, 'prdt_img_url':prdt_img_url, 'prdt_img':prdt_img}

def db_insert(df):
    df = df[['domain', 'url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'prdt_cd', 'color', 'price']]
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name = 'db_ds_lux_product', con=engine, schema='public',
              if_exists='append', index=False,)
    conn.close()

def get_multi_items(link_list, domain):
    df = pd.DataFrame(
        columns={'url', 'prdt_nm', 'prdt_img_url', 'prdt_img', 'prdt_cd', 'color', 'price', 'description'}) #description 제외
    for link in link_list:
        result = get_product_detail(link)
        result_df = pd.DataFrame([result])
        df = df.append(result_df)
        time.sleep(rd.randint(1, 3))
    df['domain'] = 'prada' + str(domain)
    db_insert(df)
    path = date_dir+'/product/product_detail.csv'
    if not os.path.exists(path):
        df.to_csv(path, index=False, mode='w')
    else:
        with open(path, 'a') as f:
            writer = csv.writer(f)
            for i, row in df.iterrows():
                writer.writerow([df.loc[i, 'domain'],df.loc[i, 'url'],df.loc[i, 'prdt_nm'],df.loc[i, 'prdt_img_url'],df.loc[i, 'prdt_img'],df.loc[i, 'prdt_cd'],df.loc[i, 'color'],df.loc[i, 'price'],df.loc[i, 'description']])
        df.to_csv(path, index=False, mode='a', header=False)
    print(df)
    return df

# link_list_w_bucket = get_links(w_bucket)
# print(link_list_w_bucket)
# link_list_w_bags = get_links(w_bags, 2)
# link_list_m_bags = get_links(m_bags, 2)
# link_list_m_acc = get_links(m_acc, 2)
# print(link_list_w_bags)
# print(link_list_m_bags)
# print(link_list_m_acc)

# list = ['https://www.prada.com//kr/en/women/bags/totes/products.leather_handbag.1BG335_2BBE_F0NV1_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.leather_handbag.1BG335_2BBE_F0LK0_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.leather_handbag.1BG335_2BBE_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.leather_handbag.1BG335_2BBE_F0WA1_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.saffiano_leather_handbag.1BA269_2ERX_F0770_V_OO7.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_re-edition_2005_saffiano_leather_bag.1BH204_NZV_F0632_V_V4L.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_duet_nylon_shoulder_bag_with_braided_trim.1BH038_2A6S_F0002_V_MOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_duet_leather_shoulder_bag.1BH038_2CCC_F0002_V_OOM.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.nylon_prada_duet_shoulder_bag.1BH038_V44_F0571_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.nylon_prada_duet_shoulder_bag.1BH038_V44_F0008_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.re-edition_2000_nylon_mini_bag.1NE515_2DH0_F0002.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.re-edition_2000_nylon_mini_bag.1NE515_2DH0_F0237.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.re-edition_2000_nylon_mini_bag.1NE515_2DH0_F0637.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.re-edition_2000_nylon_mini_bag.1NE515_2DH0_F0638.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.re-edition_nylon_mini_shoulder_bag.1TT122_064_F0770.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.medium_saffiano_leather_prada_matinee_bag.1BA282_2ERX_F068Z_V_MOE.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.saffiano_leather_mini_bag.1BP020_2EEP_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.saffiano_leather_mini_bag.1BP020_2EEP_F0637_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/mini_bags/products.nappa_leather_mini_shoulder_bag.1DH010_2CET_F0002.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.medium_saffiano_leather_prada_galleria_bag.1BA274_NZV_F098L_V_DOO.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.small_saffiano_leather_prada_panier_bag.1BA217_2ERX_F0LJ4_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_spectrum_shoulder_bag.1BH141_WDF0_F0ZYY_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_spectrum_shoulder_bag.1BH141_WDF0_F0ES9_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.nylon_tote_bag.1BG308_2E0W_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/bucket_bags/products.leather_bucket_bag.1BE018_2BBE_F0002_V_NOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.medium_nylon_shoulder_bag.1BD671_V44_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_shoulder_bag.1BH130_2BBE_F0002_V_NOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_cross-body_bag.1BH082_2BBE_F0002_V_NOM.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_shoulder_bag.1BH050_2BBE_F0002_V_NOM.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.prada_re-edition_2005_nylon_bag.1BH204_064_F0002_V_V1L.html', 'https://www.prada.com//kr/en/women/bags/totes/products.prada_double_nylon_and_saffiano_leather_bag.1BG775_2DLN_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.prada_matinee_micro_saffiano_leather_bag.1BA286_2ERX_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/top_handles/products.medium_saffiano_leather_prada_matinee_bag.1BA282_2ERX_F0009_V_MOE.html', 'https://www.prada.com//kr/en/women/bags/bucket_bags/products.leather_prada_tress_bucket_bag.1BE049_2DI4_F0XKV_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_bag_with_cord_details.1BC131_2DJ4_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_bag_with_cord_details.1BC131_2DJ4_F0XKV_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.leather_bag_with_cord_details.1BC131_2DJ4_F0G3Z_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/bucket_bags/products.leather_prada_tambour_bucket_bag.1BE050_2AIX_F0002_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/bucket_bags/products.leather_prada_tambour_bucket_bag.1BE050_2AIX_F0XKV_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/bucket_bags/products.leather_prada_tambour_bucket_bag.1BE050_2AIX_F0G3Z_V_OOO.html', 'https://www.prada.com//kr/en/women/prada_hyper_leaves/bags/products.leather_prada_tambour_bucket_bag.1BE048_2AIX_F0XKV_V_5OL.html', 'https://www.prada.com//kr/en/women/prada_hyper_leaves/bags/products.leather_prada_tambour_bucket_bag.1BE048_2AIX_F0002_V_5OL.html', 'https://www.prada.com//kr/en/women/bags/shoulder_bags/products.raffia_and_leather_bag.1BC126_2DJS_F0A5T_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.corn_husk_and_leather_tote.1BG325_2DJD_F0A5T_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.corn_husk_and_leather_tote.1BG336_2DJD_F0A5T_V_ZOO.html', 'https://www.prada.com//kr/en/women/summer_stories/bags/products.wicker_and_canvas_bucket_bag.1BE039_2E28_F0B67_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.woven_palm_and_leather_tote.1BG314_2DIJ_F0A5T_V_OOO.html', 'https://www.prada.com//kr/en/women/bags/totes/products.straw_and_leather_tote.1BG312_2DIF_F0ZI8_V_IOO.html']
# list_2 = list[41:50]
# get_multi_items(list_2)

get_multi_items(get_links(w_bags,2), 'w_bags')
# get_multi_items(get_links(m_bags,3), 'm_bags')
# get_multi_items(get_links(w_bucket), 'w_bucket')
# w_linea_rossa
