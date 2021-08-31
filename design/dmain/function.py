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
    f = open("./id_pw.txt", 'r')

    lst_id_pw = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_id_pw.append(line.split('"')[1])
    f.close()
    return lst_id_pw


def db_info() -> list:
    """
    :return: DB_info 접속정보(host, user, dbname, pw)로 구성된 list 반환
    """

    f = open("./DB_info.txt", 'r')
    lst_db_info = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_db_info.append(line.split('\'')[1])
    f.close()

    return lst_db_info


def chrome_option_initate() -> webdriver:
    """
    https://beomi.github.io/2017/09/28/HowToMakeWebCrawler-Headless-Chrome/
    :return: selenium webdriver를 초기 띄우며, crawling detection 가능성을 낮춤
    """

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


def dmain_member_fashion(driver, page, dt_today):
    page_num = page

    # dmain의 회원패션 page 접속
    driver.get(
        """https://cafe.naver.com/ArticleList.nhn?search.clubid=11262350&search.menuid=66&search.boardtype=I&search.totalCount=201&search.page=""" + str(
            page_num))

    # iframe으로 구성되어 있기에 frame으로 driver switch
    driver.switch_to_frame("cafe_main")
    time.sleep(3)

    # 공지 숨기기 click
    if page_num == 1:
        driver.find_element_by_xpath("""//*[@id="main-area"]/div[2]/div[2]/div[1]/label""").click()

    # 페이지 내용을 bs4로 parsing
    html = driver.page_source
    soup = bs(html, 'html.parser')  # .prettify()

    # 각 컨텐츠별 정보
    # 1. 컨텐츠 url
    album_url = soup.find_all("a", {"class": 'album-img'})
    # 2. 컨텐츠 title
    album_title = soup.find_all("span", {"class": 'ellipsis'})
    # 3. 컨텐츠 조회수
    album_search = soup.find_all("span", {"class": 'num'})
    # 4. 컨텐츠 id
    album_member = soup.select('dd.p-nick > div.pers_nick_area > table > tbody > tr > td > a')
    # 5. 컨텐츠 등록시간 : 본 크롤링에서는 당일 업로드 된 사진만을 가져올 예정이라 중요
    album_time = soup.find_all("span", {"class": 'date'})

    # 1-5번 수집 데이터를 list화(search 제외)
    lst_album_url = item_summary(album_url, type='attr', attr='href')
    lst_album_title = item_summary(album_title, type='text')
    lst_album_member = item_summary(album_member, type='text')
    lst_album_time = item_summary(album_time, type='text')

    # 조회수 데이터는 가공이 필요하여, 별도의 과정으로 List화
    lst_album_search = item_summary(album_search, type='text')

    # 댓글 제외
    for item in lst_album_search:
        if '[' in item:
            lst_album_search.remove(item)

    for i in range(len(lst_album_search)):
        lst_album_search[i] = lst_album_search[i].replace("조회 ", "").replace(",", "")

    # 숫자가 아닌 영역, 숫자로 전환
    for i in range(len(lst_album_search)):
        if '만' in lst_album_search[i]:
            try:
                lst_album_search[i] = float(lst_album_search[i][:-1]) * 10000
            except:
                pass

    for i in range(len(lst_album_search)):
        lst_album_search[i] = int(lst_album_search[i])

    for i in range(len(lst_album_url)):
        lst_album_url[i] = lst_album_url[i].replace('/', "")
        lst_album_url[i] = parse.quote(lst_album_url[i].replace("amp;", ""))
        lst_album_url[i] = lst_album_url[i].replace("%3F", "%253F")
        lst_album_url[i] = lst_album_url[i].replace("%26", "%2526")

    # page 내 수집된 게시글을 dataframe으로 구성
    df_result = pd.DataFrame(columns={'get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url'})
    date_today = dt.datetime.strptime(str(dt_today), '%Y-%m-%d')
    str_section = "Dmain_member_fashion"

    for i in range(len(lst_album_url)):
        if len("https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i]) != 218:
            print("https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i])
        row = {'get_date': date_today, 'section': str_section, 'title': lst_album_title[i],
               'member': lst_album_member[i], 'date': lst_album_time[i], 'search_num': lst_album_search[i],
               'article_url': "https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i]}
        df_result = df_result.append(row, ignore_index=True)

    df_result = df_result[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url']]

    for i, row in df_result.iterrows():
        if ':' not in str(row['date']):
            year = int(row['date'].split('.')[0])
            month = int(row['date'].split('.')[1])
            day = int(row['date'].split('.')[2])
            df_result.loc[i, 'date'] = dt.date(year, month, day)

    return df_result


def dmain_member_fashion_get(driver, df, dt_today):
    directory = '//172.0.0.112/mlb/process_team/dmain_crawl/' + str(dt_today) + '_fashion'

    if not os.path.exists(directory):
        os.mkdir(directory)

    df_result = pd.DataFrame(columns ={'get_date', 'section', 'title', 'member', 'date', 'search_num', 'text', 'img_file'})

    for i, row in df.iterrows():
        driver.get(row['article_url'])
        driver.implicitly_wait(10)
        driver.switch_to.frame('cafe_main')

        imgs = driver.find_elements_by_xpath("""//img[@class="article_img ATTACH_IMAGE"]""")
        img_urls = [img.get_attribute('src') for img in imgs]
        print(img_urls)
        texts = driver.find_elements_by_css_selector(
            "#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div")
        lst_text = [text.text.replace("\n", " ") for text in texts]

        lst_text_result = []
        for text in lst_text:
            try:
                text_strip = text.split("""전상품 브랜드명 필수기재. 본인스펙 선택기재.""")[1]
                text_strip = text_strip.strip()
                if len(text_strip) > 1000:
                    text_strip = text_strip[-1000:]
            except:
                try:
                    text_strip = text.split("""https://cafe.naver.com/dieselmania/24239213""")[1]
                    text_strip = text_strip.strip()
                    if len(text_strip) > 1000:
                        text_strip = text_strip[-1000:]
                except :
                    text_strip = text.strip()
                    if len(text_strip) > 1000:
                        text_strip = text_strip[-1000:]

            lst_text_result.append(text_strip)

        text_result = ""
        for item in lst_text_result:
            text_result = text_result + " " + str(item)

        j = 0

        for img in img_urls:
            j += 1
            # source = img.src
            r = requests.get(img)

            temp_title = row['title'].translate(
                {ord('\\'): " ", ord('/'): " ", ord(":"): " ", ord("*"): " ", ord("?"): " ", ord("\""): " ", ord("<"): " ",
                 ord(">"): " ", ord("|"): " ", ord("["): " ", ord("]"): " ", ord("."): " "})
            temp_title = temp_title.strip()

            file_open_path = directory + "/{0}_{1}_{2}_{3}_{4}.jpg".format(temp_title, row['member'], row['search_num'],
                                                                           row['date'], j)
            # print(row['get_date'],  row['section'],  row['title'],  row['member'], row['date'], row['search_num'], row['search_num'])

            add_row = pd.Series({'get_date': row['get_date'], 'section': row['section'], 'title': row['title'], 'member': row['member'], 'date': row['date'], 'search_num': row['search_num'], 'text': lst_text, 'img_file' : file_open_path})
            # print(add_row)

            df_result = df_result.append(add_row, ignore_index=True)
            # print(df_result)

            file = open(file_open_path, "wb")
            file.write(r.content)
            file.close()



    df_result = df_result[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'text', 'img_file']]

    return df_result


def dmain_member_product(driver, page, dt_today):
    page_num = page

    # dmain의 회원패션 page 접속
    driver.get(
        """https://cafe.naver.com/ArticleList.nhn?search.clubid=11262350&search.menuid=65&search.boardtype=I&search.totalCount=201&search.page=""" + str(
            page_num))

    # iframe으로 구성되어 있기에 frame으로 driver switch
    driver.switch_to_frame("cafe_main")
    time.sleep(3)

    # 공지 숨기기 click
    # if page_num == 1:
    #     driver.find_element_by_xpath("""//*[@id="main-area"]/div[2]/div[2]/div[1]/label""").click()

    # 페이지 내용을 bs4로 parsing
    html = driver.page_source
    soup = bs(html, 'html.parser')  # .prettify()

    # 각 컨텐츠별 정보
    # 1. 컨텐츠 url
    album_url = soup.find_all("a", {"class": 'album-img'})
    # 2. 컨텐츠 title
    album_title = soup.find_all("span", {"class": 'ellipsis'})
    # 3. 컨텐츠 조회수
    album_search = soup.find_all("span", {"class": 'num'})
    # 4. 컨텐츠 id
    album_member = soup.select('dd.p-nick > div.pers_nick_area > table > tbody > tr > td > a')
    # 5. 컨텐츠 등록시간 : 본 크롤링에서는 당일 업로드 된 사진만을 가져올 예정이라 중요
    album_time = soup.find_all("span", {"class": 'date'})

    # 1-5번 수집 데이터를 list화(search 제외)
    lst_album_url = item_summary(album_url, type='attr', attr='href')
    lst_album_title = item_summary(album_title, type='text')
    lst_album_member = item_summary(album_member, type='text')
    lst_album_time = item_summary(album_time, type='text')

    # 조회수 데이터는 가공이 필요하여, 별도의 과정으로 List화
    lst_album_search = item_summary(album_search, type='text')

    # 댓글 제외
    for item in lst_album_search:
        if '[' in item:
            lst_album_search.remove(item)

    for i in range(len(lst_album_search)):
        lst_album_search[i] = lst_album_search[i].replace("조회 ", "").replace(",", "")

    # 숫자가 아닌 영역, 숫자로 전환
    for i in range(len(lst_album_search)):
        if '만' in lst_album_search[i]:
            try:
                lst_album_search[i] = float(lst_album_search[i][:-1]) * 10000
            except:
                pass

    for i in range(len(lst_album_search)):
        lst_album_search[i] = int(lst_album_search[i])

    for i in range(len(lst_album_url)):
        lst_album_url[i] = lst_album_url[i].replace('/', "")
        lst_album_url[i] = parse.quote(lst_album_url[i].replace("amp;", ""))
        lst_album_url[i] = lst_album_url[i].replace("%3F", "%253F")
        lst_album_url[i] = lst_album_url[i].replace("%26", "%2526")

    # page 내 수집된 게시글을 dataframe으로 구성
    df_result = pd.DataFrame(columns={'get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url'})
    date_today = dt.datetime.strptime(str(dt_today).split(' ')[0], '%Y-%m-%d')
    str_section = "Dmain_member_product"

    for i in range(len(lst_album_url)):
        if len("https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i]) != 218:
            print("https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i])
        row = {'get_date': date_today, 'section': str_section, 'title': lst_album_title[i],
               'member': lst_album_member[i], 'date': lst_album_time[i], 'search_num': lst_album_search[i],
               'article_url': "https://cafe.naver.com/dieselmania?iframe_url_utf8=%2F" + lst_album_url[i]}
        df_result = df_result.append(row, ignore_index=True)

    df_result = df_result[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url']]

    for i, row in df_result.iterrows():
        if ':' not in str(row['date']):
            year = int(row['date'].split('.')[0])
            month = int(row['date'].split('.')[1])
            day = int(row['date'].split('.')[2])
            df_result.loc[i, 'date'] = dt.date(year, month, day)

    return df_result


def dmain_member_product_get(driver, df, dt_today):
    directory = '//172.0.0.112/mlb/process_team/dmain_crawl/' + str(dt_today) + '_product'

    if not os.path.exists(directory):
        os.mkdir(directory)

    for i, row in df.iterrows():
        driver.get(row['article_url'])
        driver.implicitly_wait(10)
        driver.switch_to.frame('cafe_main')

        imgs = driver.find_elements_by_xpath("""//img[@class="article_img ATTACH_IMAGE"]""")
        img_urls = [img.get_attribute('src') for img in imgs]

        texts = driver.find_elements_by_css_selector(
            "#app > div > div > div.ArticleContentBox > div.article_container > div.article_viewer > div")
        lst_text = [text.text.replace("\n", "") for text in texts]

        lst_text_result = []
        for text in lst_text:
            try:
                text_strip = text.split("""https://cafe.naver.com/dieselmania/22996482""")[1]
                text_strip = text_strip.replace("※ 게시자는'쪽지확인' '좌표요청' 댓글이 도배되지 않고 정보가 잘 전달될 수 있도록 본문내 양식을 준수해주시기 바랍니다.",
                                                "")
                text_strip = text_strip.strip()
                if len(text_strip) > 1000:
                    text_strip = text_strip[-1000:]
            except:
                text_strip = text.strip()
                if len(text_strip) > 1000:
                    text_strip = text_strip[-1000:]
            lst_text_result.append(text_strip)

        df.loc[i, 'text'] = lst_text_result

        j = 0
        # table_donotuse = str.maketrans("\/:*?\"<>|[].", "           ")
        for img in img_urls:
            j += 1
            # source = img.src
            r = requests.get(img)

            temp_title = row['title'].translate(
                {ord('\\'): " ", ord('/'): " ", ord(":"): " ", ord("*"): " ", ord("?"): " ", ord("\""): " ",
                 ord("<"): " ",
                 ord(">"): " ", ord("|"): " ", ord("["): " ", ord("]"): " ", ord("."): " "})
            temp_title= temp_title.strip()

            file_open_path = directory + "/{0}_{1}_{2}_{3}_{4}.jpg".format(temp_title, row['member'], row['search_num'],
                                                                           row['date'], j)
            df.loc[j, 'img_file'] = file_open_path
            file = open(file_open_path, "wb")
            file.write(r.content)
            file.close()

    df.drop('article_url', axis='columns', inplace=True)
    df = df[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'text', 'img_file']]

    return df


def db_insert(lst_db_info, df):
    """
    :param lst_db_info: postgre DB 접속정보(host, user, dbname, pw)
    :param df: DB에 입력할 최종 Dataframe
    """

    # DB Input format 정리
    df.columns = ['get_date', 'section', 'title', 'member', 'date', 'search_num', 'text', 'img_file']

    # Get a database connection
    engine = create_engine(
        "postgresql://" + lst_db_info[2] + ":" + lst_db_info[3] + "@" + lst_db_info[0] + ":5432/" + lst_db_info[1])
    conn = engine.connect()

    df.to_sql(name='db_mkt_naver_cafe_dmain',
              con=engine,
              schema='public',
              if_exists='append',
              index=False,
              dtype={
                  'get_date': sqlalchemy.DateTime(),
                  'section': sqlalchemy.types.VARCHAR(255),
                  'title': sqlalchemy.types.VARCHAR(255),
                  'member': sqlalchemy.types.VARCHAR(255),
                  'date': sqlalchemy.DateTime(),
                  'search_num': sqlalchemy.types.VARCHAR(255),
                  'text': sqlalchemy.types.Text,
                  'img_file': sqlalchemy.types.Text
              }
              )

    conn.close()
