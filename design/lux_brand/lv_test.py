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

def chrome_option_initate():

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36")
    options.add_argument("lang=ko_KR")

    driver = webdriver.Chrome('C:/app/chromedriver', options=options)

    driver.get('about:blank')
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")

    return driver

def get_img_url(section):
    contents = section.select('div > div > div > picture > source')
    url_list = []
    for content in contents:
        img_urls = content.get('srcset')
        img_url = img_urls.split(',')[0].split('?')[0]
        url_list.append(img_url)
    return url_list

def get_main_content(section):
    try:
        content_a = section.select('a > div:nth-child(2)')
        if content_a:
            print(content_a)
            text_1 = content_a.select('h2')
            text_2 = content_a.select('p')
    except:
        try:
            content_div = section.select('div > div:nth-child(2)')
            if content_div:
                print(content_div)
                text_11 = content_a.select('h2')
                text_22 = content_a.select('p')
        except:
            print("싸우자")


def get_main_page():
    driver = chrome_option_initate()
    driver.get('https://kr.louisvuitton.com/kor-kr/homepage')
    driver.implicitly_wait(1)

    # directory = '//172.0.0.112/mlb/process_team/luxury_brand/louisvuitton/mainpage/' + str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    # if not os.path.exists(directory):
    #     os.mkdir(directory)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    main_1 = soup.select('div .lv-slider__container > ul > li')

    url_ttl = []
    contents = []
    for section in main_1:
        url_list_main_1 = get_img_url(section)
        url_ttl.append(url_list_main_1)
        txt_list_main_1 = get_main_content(section)
        contents.append(txt_list_main_1)
    print(contents)
    # main_2 = soup.select('div .lv-homepage__line2 > a')
    # for section in main_2:
    #     url_list_main_2 = get_img_url(section)
    #     url_list_main_2.append(url_ttl)
    #     txt_list_main_2 = get_contents(section)
    #     txt_list_main_2.append(contents)
    # main_3 = soup.select('div .lv-homepage__line3 > a')
    # for section in main_3:
    #     url_list_main_3 = get_img_url(section)
    #     url_list_main_3.append(url_ttl)
    #     txt_list_main_3 = get_contents(section)
    #     txt_list_main_3.append(contents)

    print(url_ttl)
    print('-----------------------')
    # print(contents)

    # requests는 막혀서, 다른 방법을 찾아야 함
    # url 저장 > 셀레늄으로 url 접속 > 우측 버튼클릭 > 이미지 저장 >> webp to png 변환 -_- 아옼


get_main_page()

