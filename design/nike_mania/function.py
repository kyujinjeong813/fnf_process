import os
import time
import pandas as pd
# import pyperclip
from bs4 import BeautifulSoup as bs
from pip._vendor import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import datetime as dt
import random as rd
from urllib import parse
import sqlalchemy
from sqlalchemy import create_engine
import xlrd
import psycopg2
from selenium.common.exceptions import NoSuchElementException

base_dir = '//172.0.0.112/mlb/process_team/nmania_crawl/'


def chrome_option_initiate():
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


def get_page_path(num=2):
    # nike mania / 기간 : 2019-08-01 ~ 2019-12-31 / 게시판 : 나매인 착용샷 / 검색어 : 룩
    base_path = "https://cafe.naver.com/ArticleSearchList.nhn?search.clubid=10625158&search.menuid=374&search.media=0&search.searchdate=2019-08-012019-12-31&search.defaultValue=1&search.exact=&search.include=&userDisplay=15&search.exclude=&search.option=0&search.sortBy=date&search.searchBy=0&search.includeAll=&search.query=%B7%E8&search.viewtype=title&search.page="
    path_list = []
    for i in range(num):
        path = base_path + str(i + 10)
        path_list.append(path)
    return path_list


def nike_mania_fashion(path):
    driver = chrome_option_initiate()
    driver.get(path)
    driver.switch_to.frame("cafe_main")
    time.sleep(3)
    html = driver.page_source
    soup = bs(html, 'html.parser')

    article_num = soup.findAll("div", {"class": 'inner_number'})
    url_and_title = soup.findAll("a", {"class": 'article'})
    time.sleep(3)
    author = soup.select('tr > td.p-nick > a.m-tcol-c')
    issue_date = soup.findAll("td", {"class": 'td_date'})
    view_count = soup.findAll("td", {"class": 'td_view'})
    time.sleep(3)

    lst_article_num = item_summary(article_num, type='text')
    lst_url = item_summary(url_and_title, type='attr')
    lst_title = item_summary(url_and_title, type='text')
    lst_author = item_summary(author, type='text')
    lst_issue_date = item_summary(issue_date, type='text')
    lst_view_count = item_summary(view_count, type='text')

    for i in lst_article_num:
        i = str(i).replace('\n', '').strip()

    date_today = str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))
    df_result = pd.DataFrame(columns={'get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count'})

    for i in range(len(lst_article_num)):
        row = {'get_date': date_today, 'article_num': lst_article_num[i], 'url': lst_url[i],
               'title': lst_title[i], 'author': lst_author[i], 'issue_date': lst_issue_date[i],
               'view_count': lst_view_count[i]}
        df_result = df_result.append(row, ignore_index=True)

    print(df_result)
    df_result.to_csv('nike_mania.csv')
    return df_result


def get_data(path_list):
    df = pd.DataFrame(columns={'get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count'})
    for path in path_list:
        time.sleep(3)
        df_result = nike_mania_fashion(path)
        df = pd.concat([df, df_result])
    print(df)
    df.to_csv('nike_mania.csv', index=False)
    return df


# get_data(get_page_path(num=40))

def mk_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    with open(path, 'wb') as file:
        file.write(img.content)
    driver.close()


def db_insert(df):
    df = df[['article_num', 'url', 'title', 'author', 'issue_date', 'get_date', 'view_count',
             'like', 'comment', 'contents', 'img_url', 'img']]
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name='db_ds_nike_mania', con=engine, schema='public',
              if_exists='append', index=False, )
    conn.close()


def get_article_details(df):
    df = df[['get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count']]
    df['like'] = ''
    df['comment'] = ''
    df['contents'] = ''
    df['img_url'] = ''
    df['img'] = ''

    link_list = df['url'].to_list()

    for link in link_list:
        driver = chrome_option_initiate()
        driver.get(link)
        time.sleep(3)
        driver.switch_to.frame("cafe_main")
        html = driver.page_source
        soup = bs(html, 'html.parser')

        img_lst = []
        contents_lst = []

        base = soup.select('div.ContentRenderer > div > img')
        if base:
            for img in base:
                img_src = img.get('src')
                img_lst.append(img_src)
            print(img_lst)

        base_i = soup.select('div.NHN_Writeform_Main > div > img')
        if base_i:
            print(base_i)
            for i in base_i:
                img_src = i.get('src')
                img_lst.append(img_src)
            print(img_lst)

        base_p = soup.select('div.ContentRenderer > div > div.NHN_Writeform_Main > p')
        if base_p:
            for p in base_p:
                ps = p.string
                if ps:
                    contents_lst.append(ps)
            # if len(contents_lst) > 1:
            #     del contents_lst[0]

            img_p = p.select('img')
            if img_p:
                for i in img_p:
                    img_url = i.get('src')
                    img_lst.append(img_url)
                # if len(img_lst) > 1:
                #     del img_lst[0]

        time.sleep(rd.randint(3, 5))

        contents = soup.select('div.article_viewer > div.ContentRenderer > div > p')
        if contents:
            contents_lst = item_summary(contents, type='text')

        try:
            like_num = \
            soup.select('div.article_container > div.ReplyBox > div.box_left > div > div > a > em.u_cnt._count')[0].text
            if like_num:
                df.loc[df['url'] == link, 'like'] = like_num
        except:
            pass
        try:
            comment_num = \
            soup.select('div.ArticleContentBox > div.article_container > div.ReplyBox > div.box_left > a > strong')[
                0].text
            if comment_num:
                df.loc[df['url'] == link, 'comment'] = comment_num
        except:
            pass
        img_name1 = df.loc[df['url'] == link, 'issue_date'].to_string().replace('.', '_').strip()
        img_name2 = df.loc[df['url'] == link, 'article_num'].to_string().strip()
        mk_dir(base_dir)
        path = base_dir + img_name1 + img_name2
        for i, src in enumerate(img_lst):
            img_path = path + str(i) + '.jpg'
            save_img(src, img_path)

        df.loc[df['url'] == link, 'contents'] = ' '.join(contents_lst)
        df.loc[df['url'] == link, 'img_url'] = ', '.join(img_lst)
        df.loc[df['url'] == link, 'img'] = path + '1.jpg'

    db_insert(df)

    return df


# df = pd.read_excel('C:/Users/kyujin/PycharmProjects/design/nike_mania/re_crawl.xlsx')
# get_article_details(df)

link = 'https://cafe.naver.com/ArticleRead.nhn?clubid=10625158&page=24&menuid=374&inCafeSearch=true&searchBy=1&query=%EB%A3%A9&includeAll=&exclude=&include=&exact=&searchdate=2019-08-012019-12-31&media=0&sortBy=date&articleid=8780353'
driver = chrome_option_initiate()
driver.get(link)
time.sleep(3)
driver.switch_to.frame("cafe_main")
html = driver.page_source
soup = bs(html, 'html.parser')

# img_lst = []
# contents_lst = []

# base = soup.select('div.ContentRenderer > div > img')
# print(base)
base_i = soup.select('div.ContentRenderer > div')
print(base_i)
# for i in base_i:
#     print(i)
#     im = i.select('div > img')
#     print(im)
# if base:
#     for img in base:
#         img_src = img.get('src')
#         img_lst.append(img_src)
#     print(img_lst)
#
# base_i = soup.select('div.NHN_Writeform_Main > div > img')
# if base_i:
#     print(base_i)
#     for i in base_i:
#         img_src = i.get('src')
#         img_lst.append(img_src)
#     print(img_lst)
#
# base_p = soup.select('div.ContentRenderer > div > div.NHN_Writeform_Main > p')
# if base_p:
#     for p in base_p:
#         ps = p.string
#         if ps:
#             contents_lst.append(ps)
#             # if len(contents_lst) > 1:
#             #     del contents_lst[0]
#
#     img_p = p.select('img')
#     if img_p:
#         for i in img_p:
#             img_url = i.get('src')
#             img_lst.append(img_url)
# if len(img_lst) > 1:
#     del img_lst[0]
