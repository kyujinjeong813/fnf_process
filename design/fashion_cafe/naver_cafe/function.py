"""
공통으로 사용하는 함수 모음
1. chrome initiater
2. login
3. db_insert
4. data reprocessing <- 이건 다 받은 다음에 판다스 형태에서 db insert 하기 전에 넣는 게 더 효율적이려낭!!!
"""

import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs
import random as rd
import pyperclip
import datetime as dt

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
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: function() {return[1, 2, 3, 4, 5];},});")
    return driver


def naver_login(driver, ID, PW) -> webdriver:
    driver.get("https://www.naver.com/")
    driver.implicitly_wait(rd.randint(3,5))

    driver.find_element_by_xpath("""//*[@id="account"]/a""").click()
    driver.implicitly_wait(rd.randint(2,4))

    driver.find_element_by_xpath("""//*[@id="id"]""").click()
    pyperclip.copy(ID)
    driver.find_element_by_xpath("""//*[@id="id"]""").send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    driver.find_element_by_xpath("""//*[@id="pw"]""").click()
    pyperclip.copy(PW)
    driver.find_element_by_xpath("""//*[@id="pw"]""").send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    driver.find_element_by_xpath("""//*[@id="log.login"]""").click()
    time.sleep(rd.randint(3,5))

    return driver

def search(driver, keyword, start_dt, end_dt):
    """
    카페 페이지에서 키워드, 시작일, 종료일 입력 / 별도 리턴은 받지 않음, 실행만 시킴
    :param driver:
    :param keyword:
    :param start_dt:
    :param end_dt:
    :return:
    """
    driver.switch_to.frame("cafe_main")
    time.sleep(rd.randint(1,3))
    driver.find_element_by_xpath("""//*[@id="currentSearchDate"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_1"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_1"]""").send_keys(start_dt)
    driver.find_element_by_xpath("""//*[@id="input_2"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_2"]""").send_keys(end_dt)

    driver.find_element_by_xpath("""//*[@id="btn_set"]""").click()

    pyperclip.copy(keyword)
    driver.find_element_by_xpath("""//*[@id="query"]""").send_keys(Keys.CONTROL, 'v')
    action = webdriver.ActionChains(driver).send_keys(Keys.TAB).send_keys(Keys.ENTER)
    action.perform()

    return driver

def get_page_num(driver):
    a_tags = driver.find_elements_by_css_selector('div.prev-next > a')
    page_num = len(a_tags)
    return page_num

def get_page_by_click(driver, num):
    driver.find_element_by_xpath("""//*[@id="main-area"]/div[7]/a[{}]""".format(num)).click()
    return driver


def item_summary(lst_item, type='attr'):
    lst_result = []
    if type == 'text':
        for item in lst_item:
            item = item.get_text()
            item = item.rstrip('\n').lstrip('\n').strip()
            lst_result.append(item)

    if type == 'attr':
        for item in lst_item:
            item = item['href']
            item = str(item).replace('/ca-fe/', 'https://cafe.naver.com/')
            item = item.replace('&referrerAllArticles=false', '')
            lst_result.append(item)

    return lst_result

def get_html_source(driver):
    html = driver.page_source
    soup = bs(html, 'html.parser')
    return soup

# soup = get_html_source(driver)

def get_page_contents(soup):

    article_num = soup.findAll("div", {"class": 'inner_number'})
    url_and_title = soup.findAll("a", {"class": 'article'})
    time.sleep(rd.randint(1,3))
    author = soup.select('tr > td.p-nick > a.m-tcol-c')
    issue_date = soup.findAll("td", {"class": 'td_date'})
    view_count = soup.findAll("td", {"class": 'td_view'})
    reply_count = soup.findAll("a", {"class": 'cmt'})
    time.sleep(rd.randint(1,3))

    lst_article_num = item_summary(article_num, type='text')
    lst_url = item_summary(url_and_title, type='attr')
    lst_title = item_summary(url_and_title, type='text')
    lst_author = item_summary(author, type='text')
    lst_issue_date = item_summary(issue_date, type='text')
    lst_view_count = item_summary(view_count, type='text')
    lst_reply_count = item_summary(reply_count, type='text')

    date_today = str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    df_result = pd.DataFrame(
            columns={'get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count', 'reply_count'})

    for i in range(len(lst_article_num)):
        row = {'get_date': date_today, 'article_num': lst_article_num[i], 'url': lst_url[i],
                   'title': lst_title[i], 'author': lst_author[i], 'issue_date': lst_issue_date[i],
                   'view_count': lst_view_count[i], 'reply_count':lst_reply_count[i]}
        print(row)
        df_result = df_result.append(row, ignore_index=True)

    return df_result


cafe_id = '19943558'
page_id = '109'
start_dt = '20201001'
end_dt = '20201124'
keyword = '패딩'

driver = chrome_option_initiate()
base_url = 'https://cafe.naver.com/ArticleList.nhn?search.clubid={}&search.menuid={}&search.boardtype=L'
url = base_url.format(cafe_id, page_id)
driver.get(url)
driver.implicitly_wait(rd.randint(3,5))
driver.switch_to.frame("cafe_main")
page_num = get_page_num(driver)

if page_num < 10:
    for i in range(1, page_num+1):
        driver.find_element_by_xpath("""// *[ @ id = "main-area"] / div[7] / a[""" + i + """]""").click()
        soup = get_html_source(driver)
        df = get_page_contents(soup)

# driver = search(driver, keyword, start_dt, end_dt)
# df = get_page_contents(get_html_source(driver))
