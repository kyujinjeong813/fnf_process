from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NaverArticleScrapper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5)

    # 카페id, 게시판id 받아서 페이지 접근


    def get_links(self):

    # 검색어, 기간 입력하여 get url
    def get_search_page(self):
        pass

    # 검색 결과로 나온 페이지 수 확인 >> 페이지 돌면서 내용 가져올 수 있게 리턴값으로 받음
    def get_search_page_num(self):
        pass

    # 검색결과로 나온 한 페이지의 내용 divs로 긁어오기
    def get_article_lists(self):
        pass

    # div 하나에 대해 글번호, 제목, 등등 받아오기
    def get_article_contents(self):
        pass

    # 게시글 링크 입력받으면 > 본문, 댓글, 이미지 등 받아오기
    def get_content_detail(self):
        pass

    # 앨범 형태의 페이지 내용 lis 긁어오기
    def get_album_lists(self):
        pass

    def get_last_line_number(self):
        """Get the line number of last company loaded into the list of companies."""
        return int(self.driver.find_element_by_css_selector("ul.company-list > li:last-child > a > span:first-child").text)


from browser import Browser
from naver_function import *

# class NaverCafe:
#
#     def __init__(self, has_screen=False):
#         self.browser = Browser(has_screen)
#

# def get_articles(browser, url):
#     iframe_to_driver(browser, url)
#     get_html_soup(browser)


# div들 얻는 것 / 각 div 에서
def get_articles(soup):
    div_class = 'article-board m-tcol-c'
    div = soup.find_all('div', class_=div_class)[1]
    trs = div.find_all('tr')
    for tr in trs:
        number = tr.find('div', class_='inner_number').text
        title = tr.find('a', class_='article').text.strip()
        url = tr.find('a', class_='article').attrs['href']
        #댓글 = tr.find('a', class_='cmt').text