from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

driver = chrome_option_initiate()
driver.get("https://www.youtube.com/results?search_query=%EC%BD%94%EB%93%80%EB%A1%9C%EC%9D%B4")
# import time
# SCROLL_PAUSE_TIME = 0.5
# body = driver.find_element_by_tag_name('body')
#
# while True:
#     last_height = driver.execute_script('return document.documentElement.scrollHeight')
#     for i in range(10):
#         body.send_keys(Keys.END)
#         time.sleep(SCROLL_PAUSE_TIME)
#     new_height = driver.execute_script('return document.documentElement.scrollHeight')
#     if new_height == last_height:
#         break;

df = pd.DataFrame(columns = ['title', 'view_count', 'user', 'post_ago','links'])
contents = driver.find_elements_by_xpath('//*[@id="video-title"]')

n = 1
for content in contents:
    if content:
        links = content.get_attribute('href')
        print(links)
        info = content.get_attribute('aria-label')
        if info:
            title = info.split('게시자:')[0]
            rest = info.split('게시자:')[-1]
            view_count = int(rest.split('조회수 ')[-1].replace('회', '').replace(',',''))
            user = rest.strip().split(' ')[0]
            post_ago = rest.split('전')[0].strip().split(' ')[-1]
            df.loc[n, 'title'] = title
            df.loc[n, 'view_count'] = view_count
            df.loc[n, 'user'] = user
            df.loc[n, 'post_ago'] = post_ago
            df.loc[n, 'links'] = links
            n += 1

print(df)

# 추가로 할 것
# 데이터프레임을 csv 파일로 저장

# none 으로 최대한 안나오도록
# time sleep, wait 등 해보기