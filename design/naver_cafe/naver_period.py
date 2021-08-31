import re
import time
import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
import sqlalchemy
from sqlalchemy import create_engine

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

def get_page_num(driver, channel, num=None):
    if num:
        page_num = num
    else:
        if channel == 'cafe':
            xpath = """//*[@id="_cafe_section"]/div/span"""
            counts = driver.find_element_by_xpath(xpath).text
            count = int((counts.split('/')[1]).split('건')[0].replace(',', ""))
            page_num = count // 10 + 1
        elif channel == 'blog':
            xpath = """//*[@id="main_pack"]/div[2]/div/span"""
            counts = driver.find_element_by_xpath(xpath).text
            count = int((counts.split('/')[1]).split('건')[0].replace(',', ""))
            page_num = count // 10 + 1
        elif channel == 'news':
            xpath = """//*[@id="main_pack"]/div[1]/div[1]/div[1]/span"""
            counts = driver.find_element_by_xpath(xpath).text
            count = int((counts.split('/')[1]).split('건')[0].replace(',', ""))
            page_num = count // 10 + 1
        else:
            page_num = 10
    return page_num

def get_blog_contents(keyword, start_dt, end_dt, num=None):
    path = 'https://search.naver.com/search.naver?query={}&date_from={}&date_to={}&where=post&date_option=8&start='.format(keyword, start_dt, end_dt)
    driver = chrome_option_initiate()
    driver.get(path)
    df_blog = pd.DataFrame(columns={'title', 'date', 'contents', 'author', 'url'})
    page_num = get_page_num(driver, channel='blog', num=num)
    lastrow = 0
    for i in range(page_num):
        page_path = path + str(i * 10 + 1)
        driver.get(page_path)
        lis = driver.find_elements_by_class_name("sh_blog_top")
        for i, li in enumerate(lis):
            df_blog.loc[i + lastrow, 'title'] = li.find_element_by_class_name("sh_blog_title").get_attribute("title")
            date = li.find_element_by_class_name("txt_inline").text
            date = str(date).replace(' ', '')
            df_blog.loc[i + lastrow, 'issue_date'] = text_to_date(date)
            df_blog.loc[i + lastrow, 'body'] = li.find_element_by_class_name("sh_blog_passage").text
            df_blog.loc[i + lastrow, 'author'] = li.find_element_by_css_selector(
                "dd.txt_block > span > a:nth-child(1)").text
            df_blog.loc[i + lastrow, 'url'] = li.find_element_by_css_selector(
                "dd.txt_block > span > a.url").get_attribute("href")
            lastrow += 1
            print(lastrow)
    df_blog['view_count'] = 0
    df_blog['date'] = str(datetime.now().date())
    df_to_csv(df_blog, keyword, 'blog')
    return df_blog

def get_cafe_contents(keyword, start_dt, end_dt, num=None):
    path = 'https://search.naver.com/search.naver?where=articleg&ie=utf8&query={}&prdtype=0&date_option=6&date_from={}&date_to={}&start='.format(keyword, start_dt, end_dt)
    driver = chrome_option_initiate()
    driver.get(path)
    df_cafe = pd.DataFrame(columns={'title', 'date', 'contents', 'author', 'url'})
    page_num = get_page_num(driver, channel='cafe', num=num)
    lastrow = 0
    for i in range(page_num):
        page_path = path + str(i * 10 + 1)
        driver.get(page_path)
        lis = driver.find_elements_by_class_name("sh_cafe_top")
        for i, li in enumerate(lis):
            contents = li.find_element_by_class_name("sh_cafe_passage").text
            if '키즈' in contents:
                pass
            elif '야구' in contents:
                pass
            else:
                df_cafe.loc[i + lastrow, 'title'] = li.find_element_by_class_name("sh_cafe_title").text
                date = li.find_element_by_class_name("txt_inline").text
                date = str(date).replace(' ', '')
                df_cafe.loc[i + lastrow, 'issue_date'] = text_to_date(date)
                df_cafe.loc[i + lastrow, 'contents'] = li.find_element_by_class_name("sh_cafe_passage").text
                df_cafe.loc[i + lastrow, 'author'] = li.find_element_by_css_selector(
                    "dd.txt_block > span > a:nth-child(1)").text
                # df_cafe.loc[i + lastrow, 'url'] = li.find_element_by_css_selector("dd.txt_block > span > a:nth-child(2)").get_attribute("href")
                df_cafe.loc[i + lastrow, 'url'] = li.find_element_by_css_selector(
                    "dd.txt_block > span > a.url").get_attribute("href")
                lastrow += 1
            print(lastrow)
    df_cafe['view_count'] = 0
    df_cafe['date'] = str(datetime.now().date())
    df_to_csv(df_cafe, keyword, 'cafe')
    return df_cafe

def get_news_contents(keyword, start_dt, end_dt):
    path = 'https://search.naver.com/search.naver?query={}&pd=3&ds={}&de={}&where=news&pd=1&start='.format(keyword, start_dt, end_dt)
    driver = chrome_option_initiate()
    driver.get(path)
    df_news = pd.DataFrame(columns={'title', 'date', 'contents', 'author', 'url'})
    page_num = get_page_num(driver, channel='news')
    lastrow = 0
    for i in range(page_num):
        page_path = path + str(i * 10 + 1)
        driver.get(page_path)
        lis = driver.find_elements_by_css_selector('ul.type01 > li')
        for i, li in enumerate(lis):
            df_news.loc[i + lastrow, 'title'] = li.find_element_by_css_selector("dl > dt > a").text
            text = li.find_element_by_css_selector("dd.txt_inline").text
            issue_date = text_to_date(text)
            df_news.loc[i + lastrow, 'issue_date'] = issue_date
            df_news.loc[i + lastrow, 'contents'] = li.find_element_by_css_selector("dl > dd:nth-child(3)").text
            df_news.loc[i + lastrow, 'author'] = li.find_element_by_css_selector("dd.txt_inline > span._sp_each_source").text
            df_news.loc[i + lastrow, 'url'] = li.find_element_by_css_selector("dl > dt > a").get_attribute("href")
            lastrow += 1
    df_news['view_count'] = 0
    df_news['date'] = str(datetime.now().date())
    df_to_csv(df_news, keyword, 'news')
    return df_news

def get_post_contents(keyword, start_dt, end_dt):
    path = 'https://m.post.naver.com/search/post.nhn?keyword={}&sortType=rel.dsc&range={}:{}&term=custom'.format(keyword, start_dt, end_dt)
    print(path)
    driver = chrome_option_initiate()
    driver.get(path)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    driver.implicitly_wait(3)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(3)

    df_post = pd.DataFrame(columns={'author', 'issue_date', 'view_count', 'title', 'contents', 'url'})
    lastrow = 0
    lis = driver.find_elements_by_css_selector('li._cds')
    for i, li in enumerate(lis):
        url = li.find_element_by_css_selector('div > div.feed_body > div.text_area > a.link_end').get_attribute('href')
        author = li.find_element_by_css_selector('div > div.feed_head > div > div.writer_area > p > span > a > span').text
        upload_date = li.find_element_by_css_selector('div > div.feed_head > div > div.info_post > time').text
        view_count = li.find_element_by_css_selector('div.feed_head > div > div.info_post > span').text
        view_count_num = int(view_count.split(' ')[0].replace(',', ''))
        title = li.find_element_by_css_selector('div > div.feed_body > div.text_area > a.link_end > strong').text
        contents = li.find_element_by_css_selector('div > div.feed_body > div.text_area > a.link_end > p').text
        df_post.loc[i + lastrow, 'url'] = url
        df_post.loc[i + lastrow, 'author'] = author
        df_post.loc[i + lastrow, 'issue_date'] = upload_date
        df_post.loc[i + lastrow, 'view_count'] = view_count_num
        df_post.loc[i + lastrow, 'title'] = title
        df_post.loc[i + lastrow, 'contents'] = contents
        lastrow += 1
        driver.implicitly_wait(3)
    df_post['date'] = str(datetime.now().date())
    df_to_csv(df_post, keyword, 'post')
    return df_post

def db_insert(df, channel, keyword):
    df_insert = df[['date', 'url', 'author', 'issue_date', 'view_count', 'title', 'contents']]
    df_insert['keyword'] = keyword
    df_insert['channel'] = channel
    df_insert.columns = ['date', 'url', 'author', 'issue_date', 'view_count', 'title', 'contents','keyword', 'channel']

    print(df_insert)
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()
    df_insert.to_sql(name = 'db_mkt_naver_viral_data', con=engine, schema='public',
              if_exists='append', index=False,
                     )
    conn.close()

def get_naver_contents(keyword, start_dt, end_dt):
    df_blog = get_blog_contents(keyword, start_dt, end_dt)
    db_insert(df_blog, 'blog', keyword)
    df_cafe = get_cafe_contents(keyword, start_dt, end_dt)
    db_insert(df_cafe, 'cafe', keyword)
    df_news = get_news_contents(keyword, start_dt, end_dt)
    db_insert(df_news, 'news', keyword)
    df_post = get_post_contents(keyword, start_dt, end_dt)
    db_insert(df_post, 'post', keyword)


# get_naver_contents('청키하이', '20180101', '20200814')
# get_naver_contents('mlb청키하이', '20180101', '20200814')
get_naver_contents('아크메드라비', '20190101', '20200814')
# get_naver_contents('마스크스트랩', '20180101', '20200814')
# get_naver_contents('뉴발란스327', '20170101', '20200814')