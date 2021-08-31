import os
import time
import pandas as pd
from bs4 import BeautifulSoup as bs
from pip._vendor import requests
from selenium import webdriver
import datetime as dt
import random as rd
from sqlalchemy import create_engine
import pyperclip
from selenium.webdriver.common.keys import Keys

base_dir = 'C:/Users/kyujin/Desktop/PROCESS/MKT/fashion_community'

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

def login(driver):
    driver.get('https://www.naver.com/')
    time.sleep(1)
    login_btn = driver.find_element_by_class_name('link_login')
    login_btn.click()
    time.sleep(1)

    tag_id = driver.find_element_by_name('id')
    tag_pw = driver.find_element_by_name('pw')
    tag_id.clear()
    time.sleep(1)

    tag_id.click()
    pyperclip.copy('nike_program')
    tag_id.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    tag_pw.click()
    pyperclip.copy('djWjfkrh1!')
    tag_pw.send_keys(Keys.CONTROL, 'v')
    time.sleep(1)

    login_btn = driver.find_element_by_id('log.login')
    login_btn.click()
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
            item = item.replace('&referrerAllArticles=false','')
            lst_result.append(item)

    return lst_result

def str_to_int(str):
    num = 0
    if '만' in str:
        str = str.replace('만','')
        if '.' in str:
            str = str.replace('.','')
            num = int(str) * 1000
        else:
            num = int(str) * 10000
    elif ',' in str:
        str = str.replace(',','')
        num = int(str)
    else:
        num = int(str)
    return num

# 자유게시판 : page 75 (20년 1월 말) ~ 145 (19년 8월)
'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=109&userDisplay=50&search.boardtype=L&search.specialmenutype=&search.page='

# qna : page 311 (20년 1월 말) ~ 535 (19년 9월)
"https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page="

def get_gocd_qna_path(num=100):
    base_path = "https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page="
    path_list = []
    for i in range(num):
        path = base_path + str(i+1)
        path_list.append(path)
    return path_list

def get_gocd_qna_path_period():
    base_path = "https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page="
    path_list = []
    for i in range(311, 536):
        path = base_path + str(i)
        path_list.append(path)
    return path_list

def get_articles(path) :
    driver = chrome_option_initiate()
    driver.get(path)
    time.sleep(2)
    driver.switch_to.frame("cafe_main")
    time.sleep(1)
    html = driver.page_source
    soup = bs(html, 'html.parser')

    article_num = soup.findAll("div", {"class":'inner_number'})
    url_and_title = soup.findAll("a", {"class":'article'})
    time.sleep(0.5)
    author = soup.select('tr > td.p-nick > a.m-tcol-c')
    issue_date = soup.findAll("td", {"class":'td_date'})
    view_count = soup.findAll("td", {"class":'td_view'})
    time.sleep(0.5)
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
        row = {'get_date': date_today, 'article_num': lst_article_num[i], 'url':lst_url[i],
               'title':lst_title[i], 'author':lst_author[i], 'issue_date':lst_issue_date[i],
               'view_count':lst_view_count[i]}
        df_result = df_result.append(row, ignore_index=True)

    today = dt.datetime.now()
    df_result.loc[df_result['issue_date'].str.contains(':', na=False), 'issue_date'] = today.strftime("%Y.%m.%d")
    df_result['view_count'] = df_result['view_count'].apply(lambda x: str_to_int(x))
    return df_result


def get_dailylook_details(link):
    base_url = 'https://cafe.naver.com'
    url = base_url + str(link)
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1,3))
    driver.switch_to.frame("cafe_main")
    html = driver.page_source
    soup = bs(html, 'html.parser')

    contents_lst = []
    comment_lst = []
    img_lst = []

    contents = soup.select('.ContentRenderer div > div')
    for content in contents:
        text = content.text
        if text:
            contents_lst.append(text)

    img = soup.select('.ContentRenderer div > img')
    if img:
        for i in img:
            img_url = i.get('src')
            img_lst.append(img_url)

    comments = soup.select('ul.comment_list > li')
    for comment in comments:
        comm = comment.select_one('.comment_text_box > p > span').text.strip()
        author = comment.select_one('.comment_nick_box > div > a').text.strip()
        comment_obj = {'author' : author, 'comment' : comm}
        comment_lst.append(comment_obj)

    row = {'url': link, 'body_contents' : contents_lst, 'body_imgs': img_lst, 'comment' : comment_lst}
    print(row)
    return row

# url = '/ArticleRead.nhn?referrerAllArticles=false&menuid=26&page=480&boardtype=I&specialmenutype=&clubid=19943558&articleid=195399'
#
# row = get_dailylook_details(url)
# print(row)

# def get_article_details(df, driver):
#     df = df[['get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count']]
#
#     link_list = df['url'].to_list()
#     base_url = 'https://cafe.naver.com'
#     i = 0
#
#     for link in link_list:
#         if i == 2:
#             time.sleep(10)
#         url = base_url + str(link)
#         driver.get(url)
#         time.sleep(3)
#         driver.switch_to.frame("cafe_main")
#         html = driver.page_source
#         soup = bs(html, 'html.parser')
#
#         contents_lst = []
#         comment_lst = []
#
#         contents = soup.findAll('p', {"class":'se-text-paragraph'})
#         if contents:
#             for content in contents:
#                 content_lst = item_summary(content, type='text')
#                 contents_lst.extend(content_lst)
#         body_content = ' '.join(content_lst)
#         df[df['url'] == link]['contents'] = body_content
#
#         comments = soup.findAll('ul', {"class" : 'comment_list'})
#         for comment in comments:
#             lis = comment.findAll('li')
#             for li in lis:
#                 nickname = li.find('a', {"class": 'comment_nickname'}).text
#                 comm = li.find('span', {"class":'text_comment'}).text
#                 comm_obj = {'nickname: ', nickname, 'comm: ', comm}
#             comment_lst.append(comm_obj)
#         df[df['url'] == link]['comments'] = comment_lst
#         i += 1
#     print(df['comments'])
#
#     return df


def get_qna_data(path_list):
    df = pd.DataFrame(columns={'get_date', 'article_num', 'url', 'title', 'author', 'issue_date', 'view_count'})
    for path in path_list:
        time.sleep(0.5)
        df_result = get_articles(path)
        df = pd.concat([df, df_result])
        print(df)
    df.to_csv('gocd_qna_19fw.csv', index=False)
    return df
# detail도 가쥬와야 하는데.. 로그인문제가 발생해버림

# df = get_qna_data(get_gocd_qna_path_period())
# print(df)

# path_list = get_gocd_qna_path_period()
# print(path_list)
# path_list = ['https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=311', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=312', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=313', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=314', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=315', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=316', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=317', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=318', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=319', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=320', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=321', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=322', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=323', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=324', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=325', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=326', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=327', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=328', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=329', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=330', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=331', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=332', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=333', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=334', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=335', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=336', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=337', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=338', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=339', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=340', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=341', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=342', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=343', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=344', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=345', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=346', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=347', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=348', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=349', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=350', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=351', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=352', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=353', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=354', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=355', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=356', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=357', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=358', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=359', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=360', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=361', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=362', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=363', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=364', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=365', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=366', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=367', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=368', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=369', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=370', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=371', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=372', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=373', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=374', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=375', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=376', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=377', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=378', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=379', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=380', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=381', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=382', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=383', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=384', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=385', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=386', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=387', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=388', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=389', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=390', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=391', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=392', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=393', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=394', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=395', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=396', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=397', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=398', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=399', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=400', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=401', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=402', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=403', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=404', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=405', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=406', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=407', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=408', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=409', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=410', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=411', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=412', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=413', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=414', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=415', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=416', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=417', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=418', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=419', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=420', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=421', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=422', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=423', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=424', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=425', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=426', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=427', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=428', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=429', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=430', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=431', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=432', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=433', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=434', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=435', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=436', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=437', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=438', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=439', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=440', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=441', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=442', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=443', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=444', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=445', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=446', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=447', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=448', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=449', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=450', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=451', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=452', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=453', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=454', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=455', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=456', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=457', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=458', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=459', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=460', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=461', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=462', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=463', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=464', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=465', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=466', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=467', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=468', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=469', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=470', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=471', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=472', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=473', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=474', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=475', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=476', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=477', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=478', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=479', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=480', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=481', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=482', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=483', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=484', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=485', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=486', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=487', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=488', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=489', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=490', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=491', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=492', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=493', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=494', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=495', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=496', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=497', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=498', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=499', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=500', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=501', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=502', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=503', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=504', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=505', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=506', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=507', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=508', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=509', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=510', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=511', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=512', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=513', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=514', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=515', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=516', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=517', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=518', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=519', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=520', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=521', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=522', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=523', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=524', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=525', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=526', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=527', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=528', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=529', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=530', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=531', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=532', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=533', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=534', 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=64&search.boardtype=L&userDisplay=50&search.page=535']
#
# df = get_qna_data(path_list)
# print(df)


# 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=26&search.boardtype=I&search.page=481'

path = 'https://cafeptthumb-phinf.pstatic.net/MjAyMDA0MjRfMjEx/MDAxNTg3NzI1NTYxMDQ2.DilrUbPfM6sjmZDdYH6jrbWNbBlYisSIe8dXCag5tiEg.atpECfwqj6KZAovL1QwTz0mYWyCqQoPeF6C5hiCCBjIg.JPEG/IMG_E8308.JPG?type=w740'
img = requests.get(path)
if img:
    print('오잉')
else:
    print('패슈')