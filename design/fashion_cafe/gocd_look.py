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
import re
import xlrd
import psycopg2

base_dir = '//172.0.0.112/mlb/process_team/고아캐드_crawl/'
dt_today = dt.datetime.today()

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

def str_to_int(str):
    num = 0
    str = str.replace('조회', '').strip()
    if '만' in str:
        str = str.replace('만', '')
        if '.' in str:
            str = str.replace('.', '')
            num = int(str) * 1000
        else:
            num = int(str) * 10000
    if ',' in str:
        str = str.replace(',','')
        num = int(str)
    else:
        num = int(str)

    return num

def no_space(text):
    text1 = re.sub('&nbsp; | &nbsp;', '', text)
    text2 = re.sub('\n', '', text1)
    return text2

def save_img(url, path):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    img = requests.get(url)
    if img:
        with open(path, 'wb') as file:
            file.write(img.content)
    driver.close()

def db_insert(df, db_name):
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name = db_name, con=engine, schema='public',
              if_exists='append', index=False,)
    conn.close()

def get_dailylook_details(url):
    driver = chrome_option_initiate()
    driver.get(url)
    driver.implicitly_wait(rd.randint(3,5))
    driver.switch_to.frame("cafe_main")
    html = driver.page_source
    soup = bs(html, 'html.parser')
    time.sleep(rd.uniform(3, 5))

    img_lst = []
    body_content = ''

    comment_dict = {}
    # 댓글 해결이 안되어서.. 이미지만 일단 받아놓을까ㅠ
    # comments = soup.select('.comment_list > li')
    # time.sleep(rd.uniform(0,2))
    # print(comments)
    # for c in comments:
    #     nickname = c.select_one('.comment_nick_box > .comment_nick_info > a').text
    #     nickname = no_space(nickname).strip()
    #     comm = c.select_one('.text_comment').text
    #     comm = no_space(comm).strip()
    #     comment_dict[nickname] = comm
    #     time.sleep(rd.uniform(0, 1))
    # print(comment_dict)

    contents = soup.select('.ContentRenderer > div')
    time.sleep(rd.uniform(1, 3))
    if contents:
        for content in contents:
            imgs = content.findAll('img')
            for img in imgs:
                img_url = img['src']
                img_lst.append(img_url)

            texts = content.findAll('div')
            text = []
            for ts in texts:
                t = ts.text
                t = no_space(t)
                text.append(t)
            body_content = ' '.join(text)

    else:
        contents = soup.select('.inbox > .tbody')
        if contents:
            for content in contents:
                ps = content.findAll('p')
                text = []
                for p in ps:
                    p_text = p.text
                    p_text = no_space(p_text)
                    text.append(p_text)
                body_content = ' '.join(text)

                imgs = content.findAll('img')
                for img in imgs:
                    img_url = img['src']
                    img_lst.append(img_url)

        else:
            contents = soup.select('.se-main-container')
            if contents:
                for content in contents:
                    ps = content.findAll('p')
                    text = []
                    for p in ps:
                        p_text = p.text
                        p_text = no_space(p_text)
                        text.append(p_text)
                    body_content = ' '.join(text)

                    imgs = content.findAll('img')
                    for img in imgs:
                        img_url = img['src']
                        img_lst.append(img_url)
    # comment dict를 못끌고옴 ㅠ 일단 빼고 합시댜~
    return body_content, img_lst

# path = 'https://cafe.naver.com/casuallydressed?iframe_url_utf8=%2FArticleRead.nhn%253Fclubid%3D19943558%2526menuid%3D26%2526boardtype%3DI%2526page%3D12%2526specialmenutype%3D%2526articleid%3D260805%2526referrerAllArticles%3Dfalse'
# body_content, img_lst, comment_dict = get_dailylook_details(path)
# print(comment_dict)

def get_dailylook(url, dir):
    driver = chrome_option_initiate()
    driver.get(url)
    time.sleep(rd.randint(1, 3))
    driver.switch_to.frame("cafe_main")
    time.sleep(rd.randint(1, 3))
    html = driver.page_source
    soup = bs(html, 'html.parser')

    df_result = pd.DataFrame(columns={'section', 'url', 'title', 'author', 'issue_date',
                                      'get_date', 'view_cnt', 'comment_num'})
    get_date = str(dt.datetime.strftime(dt.datetime.today(), "%Y-%m-%d"))

    base_url = 'https://cafe.naver.com/casuallydressed'
    article_lst = soup.select('.article-album-sub > li')
    for article in article_lst:
        link = article.find('a').attrs['href']
        link_url = base_url + link
        title = article.select_one('.ellipsis').text
        date = article.select_one('.date_num > .date').text
        issue_date = date[:-1]
        issue_date = issue_date.replace('.', '-')
        author = article.select_one('.p-nick > a').text
        read_num = article.select_one('.date_num > .num').text
        read_num = read_num.replace('조회수', '')
        read_cnt = str_to_int(read_num)
        comment_num = article.select_one('.m-tcol-p > .num')
        if comment_num:
            comment_cnt = int(comment_num.text.replace('[', '').replace(']',''))
        else:
            comment_cnt = 0

        row = {'section' : 'gocd_dailylook', 'url' : link_url, 'title' : title, 'author' : author,
               'issue_date' : issue_date, 'get_date' : get_date, 'view_cnt' : read_cnt, 'comment_num' : comment_cnt}
        df_result = df_result.append(row, ignore_index=True)
    df_result = df_result[['section', 'url', 'title', 'author', 'issue_date', 'get_date', 'view_cnt', 'comment_num']]
    df_result['content'] = ''
    df_result['comment'] = ''

    df_img = pd.DataFrame(columns={'url', 'seq', 'img_url', 'img_file'})
    for i, row in df_result.iterrows():
        body_content, img_lst = get_dailylook_details(row['url'])
        row['content'] = body_content
        for i, img in enumerate(img_lst):
            path = "{0}_{1}_{2}_{3}_{4}.jpg".format(row['title'], row['author'], row['view_cnt'], row['issue_date'], i)
            path = re.sub("[\/:*?\"<>|]", "", path)
            path = dir + '/' + path
            save_img(img, path)
            time.sleep(rd.uniform(1,2))
            new_row = {'url':row['url'], 'seq':i, 'img_url':img, 'img_file':path}
            df_img = df_img.append(new_row, ignore_index=True)

    print(df_result.head())
    print('------------------')
    print(df_img.head())
    # 디비 저장하고, 엑셀 또는 csv 파일로 저장하는 것까지
    db_insert(df_img, 'db_mkt_naver_cafe_gocd_img')
    db_insert(df_result, 'db_mkt_naver_cafe_gocd')

    return df_result, df_img

# 테스트
# url = 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=26&search.boardtype=I&search.totalCount=801&search.page=31'
# get_dailylook(url)
#
# # 12~31 페이지 (19.9~20.4)
# 12페이지 하다가 뻑났숑
base_url = 'https://cafe.naver.com/ArticleList.nhn?search.clubid=19943558&search.menuid=26&search.boardtype=I&search.page='
for i in range(22,31):
    url = base_url + str(i)
    dir = base_dir + str(i)
    if not os.path.exists(dir):
        os.mkdir(dir)
    df_result, df_img = get_dailylook(url, dir)

    csv_img_path = base_dir + str(i) + '_img.csv'
    df_img.to_csv(csv_img_path, index=False, mode='a', header=True)
    csv_result_path = base_dir + str(i) + '_article.csv'
    df_result.to_csv(csv_result_path, index=False, mode='a', header=True)

    time.sleep(rd.uniform(5,10))