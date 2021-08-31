
"""
# 크롤링하는 코드를 짭니당
# 게시판에 따라 코드가 달라짐 - 함수를 따로 짜야겠지?
# 클래스를 만들까....
# 카페, 게시판 리스트 / 로그인 정보 등은 별도 파일에 저장하기

# 1단계와 2단계가 있음

1단계 (input : 키워드, 기간) (return : 카페, 게시판, 키워드, 제목, 게시일, 글쓴이, 조회수, 댓글수, url)
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from function import *
from bs4 import BeautifulSoup as bs
import pyperclip
import random as rd
import time

def get_articles(keyword, cafe_id, page_id, start_dt, end_dt):
    driver = chrome_option_initiate()
    base_url = 'https://cafe.naver.com/ArticleList.nhn?search.clubid={}&search.menuid={}&search.boardtype=L'
    url = base_url.format(cafe_id, page_id)
    driver.get(url)
    driver.implicitly_wait(rd.randint(3,5))

    driver = input_parameters(driver, keyword, start_dt, end_dt)
    page_nums = driver.find_elements_by_css_selector('div.prev-next > a')
    if len(page_nums) > 10:
        next_btn = page_nums[-1]
    print(len(page_nums))
    # html = driver.page_source
    # soup = bs(html, 'html.parser')

    # main-area > div.prev-next > a:nth-child(3)


    # 그럼 첫번째 페이지가 나옴 > 한 페이지에서 얻을 수 있는 데이터 긁어오는 함수가 필요함
    # get_article_info()

    # 페이지 숫자 클릭하면서 계속 데이터 수집 >> for 문안에 함수를 넣어야 하나

    # (div class='prev-next' 에서 a 태그 개수를 카운트하면 될 것 같은디!)
    # (아니면 a text 를 다 모아서 )
    # # 다음이 있는지 확인



def get_details():
    pass


# 2단계 (input : url list) (return : url, 내용 - 텍스트, 이미지, 댓글)


# 1단계 결과물, 2단계 결과물을 따로 뽑고 따로 저장
# 필요 시, sql 상에서 조인해서 사용함 (key : url, left join)


# 키워드 리스트 > 전체 카페/게시판 pool에서 검색
# for 문으로 순회해서 함수를 돌리나 그럼?

get_articles('패딩', '19943558','109', '20201001', '20201124')