import random as rd
import time
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import pyperclip
from selenium.webdriver.common.keys import Keys
import datetime as dt


from function import chrome_option_initate, log_info, naver_login, dmain_member_fashion, dmain_member_fashion_get, \
    db_info, db_insert, dmain_member_product, dmain_member_product_get

if __name__ == '__main__':

    lst_id_pw = log_info()
    lst_db_info = db_info()

    driver = chrome_option_initate()
    driver = naver_login(driver, lst_id_pw)

    page_num = 1

    dt_index = pd.date_range(start='20200821', end='20200825')
    dt_list = dt_index.tolist()
    dt_list = [dt.date(int(str(item).split(' ')[0].split('-')[0]), int(str(item).split(' ')[0].split('-')[1]), int(str(item).split(' ')[0].split('-')[2])) for item in dt_list]


    today = str(dt.datetime.today() - dt.timedelta(days=1)).split(' ')[0]
    dt_today = dt.date(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2]))

    df_url = pd.DataFrame(columns={'get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url'})
    iteration = True

    while iteration == True :
        # 디매회원패션 접속
        df_new_url = dmain_member_fashion(driver, page_num, dt_today)

        for i, row in df_new_url.iterrows():
            if ":" in str(row['date']) :
                drop_index = df_new_url[df_new_url['date'] == row['date']].index
                df_new_url = df_new_url.drop(drop_index)

        for i, row in df_new_url.iterrows():
            if row['date'] > dt.date(2020, 8, 25) :
                pass

            if (row['date'] >= dt.date(2020, 8, 21)) & (row['date'] <= dt.date(2020, 8, 25)) :
                df_url = df_url.append(row)

            if row['date'] < dt.date(2020, 8, 21) :
                iteration = False

        page_num += 1

    df_url = df_url[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url']]
    df_url.reset_index(drop=True, inplace=True)

    for date_item in dt_list :
        df_url_temp = df_url[df_url['date'] == date_item]
        df_result = dmain_member_fashion_get(driver, df_url_temp, date_item)
        db_insert(lst_db_info, df_result)
        print(df_result)


    page_num = 1
    df_url = pd.DataFrame(columns={'get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url'})
    iteration = True

    while iteration == True :
        # 디매회원소장품 접속
        df_new_url = dmain_member_product(driver, page_num, dt_today)

        for i, row in df_new_url.iterrows():
            if ":" in str(row['date']) :
                drop_index = df_new_url[df_new_url['date'] == row['date']].index
                df_new_url = df_new_url.drop(drop_index)

        for i, row in df_new_url.iterrows():

            if row['date'] > dt.date(2020, 8, 25) :
                pass

            if (row['date'] >= dt.date(2020, 8, 21)) & (row['date'] <= dt.date(2020, 8, 25)) :
                df_url = df_url.append(row)

            if row['date'] < dt.date(2020, 8, 21) :
                iteration = False


        page_num += 1

    df_url = df_url[['get_date', 'section', 'title', 'member', 'date', 'search_num', 'article_url']]
    df_url.reset_index(drop=True, inplace=True)

    for date_item in dt_list :
        df_url_temp = df_url[df_url['date'] == date_item]
        df_result = dmain_member_product_get(driver, df_url_temp, date_item)
        db_insert(lst_db_info, df_result)
        print(df_result)

    driver.quit()


