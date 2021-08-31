from selenium import webdriver
from bs4 import BeautifulSoup as bs
import random as rd
import datetime as dt
import pandas as pd
import time
import urllib.request
from urllib.parse import quote_plus
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/louisvuitton/'
main_url = 'https://kr.louisvuitton.com/'

def chrome_option_initiate():
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
        driver.implicitly_wait(3)
        driver.save_screenshot(main_dir + '/' + str(n) + '.png')
        driver.execute_script("window.scrollTo(0, {})".format((n+1)*1080))
        time.sleep(rd.randint(1, 3))
        # 맨 하단 이미지 로딩이 안되넹 ㅠ 흑흑 막는거뉘...

def get_main_page():
    driver = chrome_option_initiate()
    driver.get('https://kr.louisvuitton.com/kor-kr/homepage')
    driver.implicitly_wait(1)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    sections = soup.select('div .lv-slider__container > ul > li')
    n=1
    for section in sections:
        contents = section.select('div > div > div > picture > source')
        for content in contents:
            img_urls = content.get('srcset')
            img = img_urls.split(',')[0].split('?')[0]
            driver = chrome_option_initiate()
            driver.get(img)
            directory = mk_date_dir(dir) + '/main/'
            driver.save_screenshot(directory + str(n)+'.png')
            driver.close()
            n += 1
            time.sleep(rd.randint(1, 3))

# 루이비통 강적이당
# 걍 매주 들어가서 링크 리스트를 업데이트 해야 할...까...봐.....뀨륵

lv_new1 = 'https://kr.louisvuitton.com/kor-kr/new/for-women/latest-must-haves-for-women/_/N-17t28nm'
lv_new2 = 'https://kr.louisvuitton.com/kor-kr/new/for-women/lv-pont-9/_/N-1ih516e'


def get_products(url):
    driver = chrome_option_initiate()
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'lv-smart-picture')))
    lis = driver.find_elements_by_css_selector('div.lv-paginated-list.lv-category__grid > ul > li')
    for li in lis:
        if li:
            link = li.get_attribute('href')
            print(link)
            img = li.find_element_by_css_selector('div.lv-product-card__media-wrap > div > div > picture > img')
            print(img)

get_products(lv_new1)

# 루이비통 포기!!!!!!!
