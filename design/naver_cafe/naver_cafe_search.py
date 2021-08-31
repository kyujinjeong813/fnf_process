import re
import time
import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
import sqlalchemy
from selenium.webdriver.common.keys import Keys
from sqlalchemy import create_engine
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.alert import Alert
#################################################################################
"""화면설정"""
#################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 1000)
# 최대 열 수 설정
pd.set_option('display.max_column', 100)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)


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


def df_to_csv(df, keyword, channel):
    file_path = 'C:/Users/kyujin/Desktop/PROCESS/MKT/viral_data/'
    today = datetime.now()
    csv_path = file_path + str(keyword) + '_' + str(channel) + '_' + today.strftime("%Y_%m_%d") + '.csv'
    df.to_csv(csv_path)


def text_to_date(text):
    today = datetime.now()
    regex1 = re.compile(r'\d+일')
    regex2 = re.compile(r'\d\d\d\d.\d\d.\d\d')
    matchobj1 = regex1.search(text)
    matchobj2 = regex2.search(text)
    if '시간' in text:
        release_date = today.strftime("%Y.%m.%d")
    elif '어제' in text:
        release_date = (today - timedelta(days=1)).strftime("%Y.%m.%d")
    elif matchobj1:
        day_delta = int(matchobj1.group(0).split('일')[0])
        release_date = (today - timedelta(days=day_delta)).strftime("%Y.%m.%d")
    elif matchobj2:
        release_date = matchobj2.group(0)
    else:
        release_date = today.strftime("%Y.%m.%d")
    return release_date


def get_cafe_contents(keyword, start_dt, end_dt):
    path = 'https://search.naver.com/search.naver?where=articleg&ie=utf8&query={}&prdtype=0&date_option=6&date_from={}&date_to={}&start='.format(
        keyword, start_dt, end_dt)
    driver = chrome_option_initiate()
    driver.get(path)
    driver.implicitly_wait(5)

    # 일반글만 노출되는 것으로 변환
    driver.find_element_by_xpath("""//*[@id="main_pack"]/div[2]/ul/li[3]/a""").click()
    time.sleep(1)

    # 전체 게시글 수 확인
    content_num = driver.find_element_by_xpath("""/html/body/div[3]/div[2]/div/div[1]/div[3]/div/span""").text
    content_num = content_num.split(' / ')[1].replace("건", "")
    if ',' in content_num:
        content_num = content_num.replace(",", "")

    iteration_num = divmod(int(content_num), 10)[0]
    last_iteration_num = divmod(int(content_num), 10)[1]

    iter = 0
    df_compare = pd.DataFrame(columns={'gn_keyword', 'title', 'user_id', 'date', 'search_num', 'review_text'})

    if iteration_num > 100 :
        iteration_num = 100
        last_iteration_num =10

    while (iter <= iteration_num):

        inner_iteration_num = last_iteration_num if iter == iteration_num else 10

        for i in range(inner_iteration_num):
            window_before = driver.window_handles[0]
            row = get_cafe_contents_detail(driver, i, window_before, keyword)

            # 출력대상이 되는 dataframe 구성
            df = pd.DataFrame(columns={'gn_keyword', 'title', 'user_id', 'date', 'search_num', 'review_text'})
            df = df.append(row, ignore_index=True)

            before_len = len(df_compare)
            df_compare = df_compare.append(row, ignore_index=True)
            df_compare = df_compare.drop_duplicates(subset=['title', 'user_id', 'date'], keep='last')
            after_len = len(df_compare)
            if before_len != after_len :
                df = df[['gn_keyword', 'title', 'user_id', 'date', 'search_num', 'review_text']]
                db_insert(df)
        iter += 1
        try :
            driver.find_element_by_xpath("""//a[contains(@class, 'next')]""").click()
        except :
            try :
                time.sleep(3)
                driver.find_element_by_xpath("""//a[contains(@class, 'next')]""").click()
            except :
                break
        time.sleep(3)

    driver.close()
    df_to_csv(df, keyword, 'cafedetail')


def get_cafe_contents_detail(driver, num, window_before, keyword):
    # 각 컨텐츠별 클릭

    driver.find_element_by_xpath(
        """/html/body/div[3]/div[2]/div/div[1]/div[3]/ul/li[""" + str(num + 1) + """]/dl/dt/a""").click()
    time.sleep(2)

    # 현재의 창을 저장 -- for 추후 closing
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_name=window_after)
    time.sleep(1)

    # iframe으로 구성되어 있기에 frame으로 driver switch
    try :
        driver.switch_to.frame("cafe_main")
    except :
        da = Alert(driver)
        da.accept()

        window_after = driver.window_handles[1]
        driver.switch_to.window(window_name=window_after)
        time.sleep(1)
        driver.switch_to.frame("cafe_main")

    html = driver.page_source
    soup = bs(html, 'html.parser')

    # 각 컨텐츠별 정보
    # 1. 컨텐츠 title --> string
    title = soup.find("h3", {"class": 'title_text'})
    try :
        title = str(title.get_text()).strip()
    except :
        print("title error")
        title = ""

    # 2. user id --> string
    user = soup.find("a", {"class": 'nickname'})
    try :
        user = str(user.get_text()).strip()
    except :
        print("user id error")
        user = ""

    # 3. upload date --> datetime date
    date = soup.find("span", {"class": 'date'})
    try :
        date = str(date.get_text()).split(' ')[0]
        date = dt.date(int(date.split('.')[0]), int(date.split('.')[1]), int(date.split('.')[2]))
    except :
        print("date error")
        date = dt.date(2020, 1, 1)

    # 4. 조회수 --> int
    search_num = soup.find("span", {"class": 'count'})
    try :
        search_num = str(search_num.get_text()).split(' ')[1]
        if ',' in search_num:
            search_num = search_num.replace(',', '')

        if '만' in search_num:
            try:
                search_num = float(search_num[:-1]) * 10000
            except:
                print('search_num error')
                pass

        search_num = int(search_num)
    except :
        search_num = 0

    # 5. 댓글 --> list
    try :
        review_text = soup.find_all("span", {"class": 'text_comment'})
        lst_review = []
        for item in review_text:
            item = str(item.get_text()).strip()
            if '\n' in item:
                item = item.replace('\n', ' ')
            lst_review.append(item)
    except :
        print('review error')
        lst_review =[]

    # return 할 row 생성
    row = {'gn_keyword': keyword, 'title': title, 'user_id': user, 'date': date, 'search_num': search_num, 'review_text': lst_review}

    # 현재 tab close 후, 최초 검색페이지로 이동
    driver.close()
    driver.switch_to.window(window_name=window_before)
    time.sleep(1)
    print(row)

    return row


def db_insert(df):
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df.to_sql(name='db_mkt_naver_cafe_review', con=engine, schema='public',
                     if_exists='append', index=False)
    conn.close()


if __name__ == '__main__':
    get_cafe_contents('아크메드라비 후드티', '201900101', '20200921')
    # get_cafe_contents('캉골 버킷백', '20190901', '20200229')

