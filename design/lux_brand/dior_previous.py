from pip._vendor import requests
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import random as rd
import datetime as dt
import pandas as pd
import time
import urllib.request
from urllib.request import urlopen
from urllib.parse import quote_plus
import os
import io
# from urllib.parse import urlparse
# from urllib import parse
from selenium.webdriver.common.by import By
import requests

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/dior/'
main_url = 'https://www.dior.com/'

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

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    time.sleep(rd.randint(1, 3))
    driver.close()

def get_main_page(url):
    base_path = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    driver = chrome_option_initiate()
    driver.get(url)
    driver.implicitly_wait(3)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    results = soup.find_all("a", {"class" : 'news-item-link'})
    for result in results:
        link = result.get('href')
        subtitle = result.find("div", {"class":'news-item-subtitle'}).text
        item_title = result.find("div", {"class":'news-item-title'}).text
        print(subtitle, item_title, link)
    images = driver.find_elements_by_css_selector(".news-item-visuals .news-item-image-link .image img")
    for image in images:
        img_url = image.get_attribute('src')
        img_title = image.get_attribute('alt')
        print(img_url, img_title)
        path = base_path + '/' + str(img_title).strip() + '.png'
        save_img(img_url, path)

# get_main_page(main_url)

def screenshot(url, directory):
    driver = chrome_option_initiate()
    driver.get(url)
    driver.implicitly_wait(3)

    ttl_height = driver.execute_script("return document.body.scrollHeight")
    num = ttl_height // 1080 + 1
    base_dir = directory + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    for n in range(num):
        time.sleep(rd.randint(1, 3))
        driver.save_screenshot(base_dir + '/main' + str(n) + '.png')
        driver.execute_script("window.scrollTo(0, 1080*{})".format(n+1))
        driver.implicitly_wait(3)

def get_product_img(link):
    driver = chrome_option_initiate()
    driver.get(link)
    driver.implicitly_wait(3)
    product_views = driver.find_elements(By.CLASS_NAME, 'product-link')
    link_list = []
    for product in product_views:
        link = product.get_attribute("href")
        time.sleep(rd.randint(1, 3))
        link_list.append(link)
    print(link_list)
    return link_list

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    time.sleep(rd.randint(1, 3))
    driver.close()

def mk_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)

def get_product_detail(link):
    base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/dior/'
    driver = chrome_option_initiate()
    driver.get(link)
    driver.implicitly_wait(3)
    prdt_nm = driver.find_element_by_css_selector("#main > div > div.top-content-desktop.top-content-desktop--couture > div.top-content-desktop-right > div > div.top-content-desktop-sticky > div.product-titles > h1 > span.multiline-text.product-titles-title").text
    # prdt_sub_nm = driver.find_element_by_css_selector("#main > div > div.top-content-desktop.top-content-desktop--couture > div.top-content-desktop-right > div > div.top-content-desktop-sticky > div.product-titles > h1 > span.multiline-text.product-titles-subtitle.product-titles-subtitle--couture").text
    prdt_cd = driver.find_element_by_css_selector(".product-titles-ref").text
    prdt_cd = str(prdt_cd).split(':')[-1].strip()
    img = driver.find_element_by_css_selector("#main > div > div.top-content-desktop.top-content-desktop--couture > div.top-content-desktop-left > ul > li:nth-child(1) > button > div > img")
    img_url = img.get_attribute('src')
    img_url = str(img_url).split('?')[0]
    time.sleep(rd.randint(1, 3))
    base_path = base_dir + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d")) + '/product'
    mk_dir(base_path)
    prdt_img = base_path + '/' + str(prdt_nm).strip() + prdt_cd + '.png'
    price = driver.find_element_by_xpath("""//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div[3]/div[1]/span[1]""").text
    time.sleep(rd.randint(1, 3))
    description = driver.find_element_by_xpath("""//*[@id="main"]/div/div[1]/div[2]/div/div[2]/div[4]/div/div/div""").text
    infos = driver.find_elements_by_css_selector('#main > div > div.top-content-desktop.top-content-desktop--couture > div.top-content-desktop-right > div > div.top-content-desktop-sticky.is-sticky > div.product-description > div > div > div > ul')
    details = infos.find_elements_by_cass_selector('li')
    detail_list = []
    for detail in details:
        line = detail.text
        detail_list.append(line)
    print(detail_list)
    return {'url': link, 'prdt_nm': prdt_nm, 'prdt_cd': prdt_cd, 'price': price, 'color': 'none', 'description': description,
     'prdt_img_url': img_url, 'prdt_img': prdt_img}



#get_product_detail("https://www.dior.com/ko_kr/products/couture-1ADPO171RAS_H29E-saddle-%ED%8C%8C%EC%9A%B0%EC%B9%98-dior-and-shawn-%EA%BF%80%EB%B2%8C-%ED%8C%A8%EC%B9%98-%EC%9E%90%EC%88%98-%EB%B8%94%EB%9E%99-%EA%B7%B8%EB%A0%88%EC%9D%B8-%EC%86%A1%EC%95%84%EC%A7%80-%EA%B0%80%EC%A3%BD")

#dior_women = "https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1"
#dior_men = "https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EB%82%A8%EC%84%B1"

# get_main_page(dior_women)
# get_main_page(dior_men)

dior_w_bag = "https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1-%EA%B0%80%EB%B0%A9/%EB%AA%A8%EB%93%A0-%EA%B0%80%EC%A3%BD%EC%A0%9C%ED%92%88"
dior_m_bag = "https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EA%B0%80%EC%A3%BD-%EC%A0%9C%ED%92%88/%EC%A0%84%EC%B2%B4-%EA%B0%80%EC%A3%BD-%EC%A0%9C%ED%92%88"
dior_w_sh = "https://www.dior.com/ko_kr/%EC%97%AC%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%97%AC%EC%84%B1-%EC%8A%88%EC%A6%88/%EB%AA%A8%EB%93%A0-%EC%8A%88%EC%A6%88"
dior_m_sh = "https://www.dior.com/ko_kr/%EB%82%A8%EC%84%B1-%ED%8C%A8%EC%85%98/%EC%8A%88%EC%A6%88/%EB%AA%A8%EB%93%A0-%EC%8A%88%EC%A6%88"

# get_product_img(dior_w_sh)

# 되는 건 확인했고 구조화만 시키면 됨