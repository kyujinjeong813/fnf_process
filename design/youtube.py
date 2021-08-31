from bs4 import BeautifulSoup as bs
import time
import pandas as pd
import datetime as dt
import random as rd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def chrome_option_initate() -> webdriver:
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
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

# 유튜브 연관검색어 저장
def youtube_wp_auto(keyword):
    driver = chrome_option_initate()
    driver.get("https://www.youtube.com/")
    driver.implicitly_wait(1)

    for i in range(len(keyword)):
        driver.find_element_by_xpath("//input[@id='search']").send_keys(keyword[i])
        time.sleep(0.3)

    time.sleep(2)

    html = driver.page_source
    soup = bs(html, 'html.parser')
    result = soup.find_all("div", {"class":"sbqs_c"})

    lst_result = []
    for i in range(len(result)-1) :
        lst_result.append(result[i].get_text())

    driver.quit()
    return lst_result

# 유튜브 검색결과 저장 (썸네일, 제목, 사용자, 조회수, 일자)
def youtube_contents(keyword):
    driver = chrome_option_initate()
    driver.get("https://www.youtube.com/results?search_query=%EC%BD%94%EB%93%80%EB%A1%9C%EC%9D%B4+%ED%8C%AC%EC%B8%A0")
    # driver.find_element_by_xpath("//input[@id='search']").send_keys(keyword)
    # driver.find_element_by_xpath("""// *[ @ id = "search-icon-legacy"]""").send_keys(Keys.ENTER)
    driver.implicitly_wait(3)
    driver.execute_script("arguments[0].scrollIntoView();")
    driver.execute_script("arguments[0].click();")

    previous_count = 0
    contents = driver.find_elements_by_css_selector('.style-scope.ytd-item-section-renderer')
    current_count = len(contents)
    while previous_count != current_count:
        try:
            previous_count = current_count
            driver.execute_script("arguments[0].scrollIntoView();", contents[-1])
            print("Number of total Elements fount: {}".format(len(contents)))
        finally:
            time.sleep(2)
            contents = driver.find_elements_by_css_selector('.style-scope.ytd-item-section-renderer')
            current_count = len(contents)

    for content in contents:
        if content:
            print('success')
            #https://stackoverflow.com/questions/55124462/cant-scroll-down-in-youtube-my-code-can-run-some-website-but-not-with-youtube
        info = content.find_elements_by_css_selector('#meta #title-wrapper h3 a')
        title = info.get_attribute("title")
        print(title)
        link = info.get_attribute("href")
        print(link)
        detail = info.get_attribute("aria-label")
        print(detail)
        print('-----------------')

    # for i in range(len(counts)):
    #     content = driver.find_element_by_css_selector("# contents > ytd-video-renderer:nth-child({})".format(i))
    #     contents = content.find_element_by_xpath("""//*[@id ="dismissable"]""")
    #     info = contents.find_element_by_xpath("""//*[@id="video-title"]""")
    #     title = info.get_attribute("title")
    #     link = info.get_attribute("href")
    #     detail = info.get_attribute("aria-label")
    #     print(link, title, detail)
    #     print('-----------------')

    # driver.execute_script("window.scrollTo(0, 1080)")
    #height = driver.execute_script("return document.body.scrollHeight")
    #print(height)
    # while True:
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    #     time.sleep(1)
    #     new_height = driver.execute_script("return document.body.scrollHeight")
    #     if new_height == height:
    #         break
    #     height = new_height
        # for re in result:

    # for re in results:
    #     link = re.get('href')
    #     img = re.find_element_by_css_selector('.style-scope yt-img-shadow').get('src')
    #     print(link, img)

youtube_contents('코듀로이 팬츠')