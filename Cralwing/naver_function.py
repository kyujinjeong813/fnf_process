import pyperclip
from browser import Browser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from utils import randomized_sleep
from bs4 import BeautifulSoup as bs

naver_login = {
    'id' : 'kazmin84',
    'pw' :'Kazmin0982!'
}

def naver_login(browser):
    browser.find_element_by_xpath("""//*[@id="account"]/a""").click()
    randomized_sleep()

    copy_input(browser, '//*[@id="id"]', naver_login['id'])
    copy_input(browser, '//*[@id="pw"]', naver_login['pw'])

    browser.find_element_by_xpath("""//*[@id="log.login"]""").click()
    randomized_sleep(2)

def copy_input(browser, xpath, input):
    browser.find_element_by_xpath(xpath).click()
    pyperclip.copy(input)
    browser.find_element_by_xpath(xpath).send_keys(Keys.CONTROL, 'v')
    randomized_sleep()

def click_and_input(browser, xpath, input):
    browser.find_element_by_xpath(xpath).click()
    browser.find_element_by_xpath(xpath).send_keys(input)
    randomized_sleep()

def input_period(browser, start_dt, end_dt):
    browser.find_element_by_xpath("""//*[@id="currentSearchDate"]""").click()
    click_and_input(browser, '//*[@id="input_1"]', start_dt)
    click_and_input(browser, '//*[@id="input_2"]', end_dt)
    browser.find_element_by_xpath("""//*[@id="btn_set"]""").click()

def iframe_to_driver(browser, url):
    browser.get(url)
    browser.driver.switch_to.frame("cafe_main")
    randomized_sleep()

def get_html_soup(browser):
    html = browser.page_source
    soup = bs(html, 'html.parser')
    return soup

def db_insert(db_info, df):
    pass

# 게시판 페이지가 몇개나 있는지 구하기
# 1. pgR 이 있는지 확인 (div class "prev-next" > a class "pgR")
# 있으면 기본 10 / 없으면 a 개수 통해서 last_num 구하기
# ㄴ10까지 돌고, pgG

def page_click(browser, num):
    browser.driver.find_element_by_xpath('// *[ @ id = "main-area"] / div[7] / a['+str(num)+']').click()

def get_article_lists(browser):
    pass

def get_album_lists(browser):
    pass


# 으어.. 맘에는 안들지만 돌아는 간다
# 이제 데이터를 어떻게 다룰지를 고민하쟈아
# csv로 ? 그담 통째로 db_insert!
def get_page_num(browser, album=False):
    n = 1
    ele_nums = browser.find('.prev-next > a')
    next_btn = browser.find_one('.pgR')
    if next_btn:
        while n < 11:
            # get_article_lists(browser)  # 또는 get_album_lists()
            # db_insert()
            n += 1
            page_click(browser, n)
            print(n)
        get_next_page_num(browser)
    else:
        end_num = int(ele_nums[-1].text) % 10
        for i in range(end_num+1):
            page_click(browser, i)
            # get_article_lists(browser)  # 또는 get_album_lists()
            # db_insert()
        print('end')

다 필요없엌ㅋㅋㅋ ㅠㅠ 맨 마지막 숫자 알아내기 하쟈아
# def get_next_page_num(browser):
#     print("start")
#     n = 2
#     ele_nums = browser.find('.prev-next > a')
#     next_btn = browser.find_one('.pgR')
#     if next_btn:
#         while n < 12:
#             # get_article_lists(browser)  # 또는 get_album_lists()
#             # db_insert()
#             print(n)
#             n += 1
#             page_click(browser, n)
#         print("next step")
#         get_next_page_num(browser)
#     else:
#         end_num = int(ele_nums[-1].text) % 10 + 1
#         for i in range(2, end_num+1):
#             page_click(browser, i)
#             print(i)
#             # get_article_lists(browser)  # 또는 get_album_lists()
#             # db_insert()
#         print('end')

browser = Browser(True)
url = 'https://cafe.naver.com/ArticleSearchList.nhn?search.clubid=10625158&search.searchdate=6m&search.searchBy=&search.query=%BD%C5%B9%DF&search.defaultValue=1&search.sortBy=date&userDisplay=15&search.media=0&search.option=0&search.menuid=374'
iframe_to_driver(browser, url)
get_page_num(browser)

