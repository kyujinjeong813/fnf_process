import os
import time
import pandas as pd
import pyperclip
from bs4 import BeautifulSoup as bs
from pip._vendor import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime as dt
from urllib import parse
import sqlalchemy
from sqlalchemy import create_engine
import xlrd
import psycopg2
from selenium.webdriver.common.action_chains import ActionChains
import random

#################################################################################
"""화면설정"""
#################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 1000)
# 최대 열 수 설정
pd.set_option('display.max_column', 100)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)


def log_info() -> list:
    """
    :return: Instagram MLB Korea(ID, PW) 접속정보
    """
    f = open("id_pw.txt", 'r')
    print(f)

    lst_id_pw = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_id_pw.append(line.split('"')[1])
    f.close()
    # print(lst_id_pw)
    return lst_id_pw

def db_info() -> list:
    """
    :return: DB_info 접속정보(host, user, dbname, pw)로 구성된 list 반환
    """

    f = open("DB_info.txt", 'r')
    lst_db_info = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_db_info.append(line.split('\'')[1])
    f.close()

    return lst_db_info


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

def naver_login(driver, lst_id_pw) -> webdriver:
    """
    네이버 로그인은 sendkey를 막고 있기에, pyperclip 모듈을 통해 clipboard를 통해 붙여넣기 기능으로 구현
    sendkey를 막고 있다함은 sendkey로 ID/PW 전송 시, 자동입력방지 캡차로 인하여 로그인 불가
    :param driver: Chrome initiate
    :param lst_id_pw: Naver ID/PW
    :return : Naver Login webdriver
    """
    driver.get("https://www.naver.com/")
    driver.implicitly_wait(10)

    driver.find_element_by_xpath("""//*[@id="account"]/a""").click()
    driver.implicitly_wait(10)

    driver.find_element_by_xpath("""//*[@id="id"]""").click()
    pyperclip.copy(lst_id_pw[0])
    driver.find_element_by_xpath("""//*[@id="id"]""").send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    driver.find_element_by_xpath("""//*[@id="pw"]""").click()
    pyperclip.copy(lst_id_pw[1])
    driver.find_element_by_xpath("""//*[@id="pw"]""").send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    driver.find_element_by_xpath("""//*[@id="log.login"]""").click()
    time.sleep(3)

    return driver



def item_summary(lst_item, type='attr', attr=None) -> list:
    lst_result = []
    if type == 'text':
        for item in lst_item:
            item = item.get_text()
            lst_result.append(item)

    if type == 'attr':
        for item in lst_item:
            item = item['href']
            lst_result.append(item)

    return lst_result


# def dmain_member_fashion(driver, dt_today):

def dmain_member_fashion(driver):

    # dmain의 게시판 page 접속 -> menu id
    패션문답 = '171'
    패션토크 = '161'
    쇼핑후기 = '69'

    driver.get(
        """https://cafe.naver.com/dieselmania?iframe_url=/ArticleList.nhn%3Fsearch.clubid=11262350%26search.menuid=""" + 패션문답 + """%26search.boardtype=L%26search.totalCount=151%26search.page=""")

    # iframe으로 구성되어 있기에 frame으로 driver switch
    driver.switch_to.frame("cafe_main")

    time.sleep(3)
    driver.find_element_by_xpath("""//*[@id="currentSearchDate"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_1"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_1"]""").send_keys("20190801") #시작일 지정
    time.sleep(1)
    driver.find_element_by_xpath("""//*[@id="input_2"]""").click()
    driver.find_element_by_xpath("""//*[@id="input_2"]""").send_keys("20201104") #종료일 지정
    time.sleep(1)

    driver.find_element_by_xpath("""//*[@id="btn_set"]""").click()

    # webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
    # webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()


    # 검색어 입력 - 검색어가 변하는 편
    pyperclip.copy('숏패딩')
    driver.find_element_by_xpath("""//*[@id="query"]""").send_keys(Keys.CONTROL, 'v')
    action = webdriver.ActionChains(driver).send_keys(Keys.TAB).send_keys(Keys.ENTER)
    action.perform()

    lst_url = []
    #검색결과 페이지는 넉넉히 30으로 설정
    #페이지 클릭
    try:
        for i in range(0,1):
            time.sleep(3)
            y = str(i+1)
            driver.find_element_by_xpath("""// *[ @ id = "main-area"] / div[7] / a["""+y+"""]""").click()
            html1 = driver.page_source
            soup1 = bs(html1, 'html.parser')  # .prettify()
            url = soup1.find_all("a", {"class": 'article'})
            lst_url1 = item_summary(url, type='attr', attr= 'href')
            for x in range(len(lst_url1)):
                lst_url1[x] = str(lst_url1[x])
                lst_url.append(lst_url1[x])
            time.sleep(5)
            print(lst_url)
    except Exception:
        pass

    return lst_url

def crawler(driver,lst_url):
    df_result = pd.DataFrame(columns={'get_date', 'board', 'title', 'user', 'post_date', 'view_count', 'comment', 'content', 'url'})
    for i in range(len(lst_url)):
        print('------------------------------------------------------')
        driver.get("https://cafe.naver.com" + lst_url[i])
        driver.switch_to.frame("cafe_main")
        html = driver.page_source
        soup = bs(html, 'html.parser')
        time.sleep(random.randint(3,5))
        title = soup.select('h3.title_text')
        print(title)
        post_date = soup.select('span.date')
        print(post_date)
        user = soup.select('div.nick_box')
        print(user)
        content = soup.select('div.se-main-container')
        print(content)
        comment_all = soup.select('span.text_comment')
        print(comment_all)
        view_count = soup.select('span.count')
        print(view_count)
        time.sleep(random.randint(3,5))
        if '만' in view_count:
            try:
                view_count = float(view_count[:-1]) * 10000
            except:
                pass
        if ',' in view_count:
            try:
                view_count = int(view_count.replace(',','').strip())
            except:
                pass
            else:
                view_count = int(view_count)

        date_today = dt.datetime.strptime(str(dt_today), '%Y-%m-%d')
        board = "패션문답" #바꿔주기

    #     row = {'get_date': date_today,
    #            'board': board,
    #            'title': title,
    #            'user': user,
    #            'post_date': post_date,
    #            'view_count': view_count,
    #            'comment': comment_all,
    #            'content': content,
    #            'url': "https://cafe.naver.com" + lst_url[i]}
    #     df_result = df_result.append(row, ignore_index=True)
    #     df_result = df_result[['get_date', 'board', 'title', 'user', 'post_date', 'view_count', 'comment', 'content', 'url']]
    # return df_result

def csv(df_result):
    df_result.to_csv('C:/Users/mkjung/Desktop/MKJ/naver_cafe_crawler/패션문답.csv', encoding='utf-8-sig')


#############코드실행

driver = chrome_option_initiate()
naver_login(driver,log_info())
today = str(dt.datetime.today()).split(' ')[0]
dt_today = dt.date(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2]))

# url_list = dmain_member_fashion(driver)
url_list = ['/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32932406&referrerAllArticles=false', '/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32928238&referrerAllArticles=false', '/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32928172&referrerAllArticles=false',
'/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32926139&referrerAllArticles=false', '/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32926138&referrerAllArticles=false', '/ca-fe/ArticleRead.nhn?clubid=11262350&page=1&menuid=171&inCafeSearch=true&searchBy=0&query=%EC%88%8F%ED%8C%A8%EB%94%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012020-11-04&media=0&sortBy=date&articleid=32912421&referrerAllArticles=false']
df = crawler(driver, url_list)