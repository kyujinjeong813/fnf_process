from dataclasses import dataclass
from sqlalchemy.dialects.postgresql import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import datetime as dt
from api_con import pre_process, datalab_api, json_to_df, divide_df, db_insert
# import weekly_update as week_update

#################################################################################
"""화면설정"""
#################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 1000)
# 최대 열 수 설정
pd.set_option('display.max_column', 100)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)


def postfetch(sql) -> pd.DataFrame():
    """
    postsql DB에서 fetch해오는 function
    """
    try:
        conn_string = "host='172.0.2.93' dbname ='postgres' user='postgres' password='1111'"
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(sql + ";")
        result = cur.fetchall()

        postfetch_df = pd.DataFrame(result)
        postfetch_df.columns = [desc[0] for desc in cur.description]

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")

    finally:
        cur.close()
        conn.close()

    return postfetch_df



def postfetch_keyword() -> pd.DataFrame():
    """
    postsql DB에서 item 기준으로 qty 정보 fetch 해오는 function
    """
    sql = """select *
             from db_mkt_naver_keyword_master"""

    df = postfetch(sql)

    return df


def db_info() -> list:
    """
    :return: DB_info 접속정보(host, user, dbname, pw)로 구성된 list 반환
    """

    f = open("C:/Users/kyujin/PycharmProjects/keyword/naver/ysk/DB_info.txt", 'r')
    lst_db_info = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_db_info.append(line.split('\'')[1])
    f.close()

    return lst_db_info


def api_con_exe(brand, startDate, endDate, period):
    '''검색하고자 하는 데이터 upload'''
    df_search = postfetch_keyword()
    df_search = df_search[df_search['brand'] == brand]
    df_search = df_search.iloc[:, 8:]
    df_search.rename(columns={'keyword_repr': 'gp_nm'}, inplace=True)
    df_search.loc[-1] = ['나이키에어맥스97', '나이키에어맥스97', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    df_search['key_nm'] = np.nan
    df_search.index = df_search.index + 1
    df_search = df_search.sort_index()

    print(df_search)

    df = pre_process(df_search)

    lst = divide_df(df, 4)

    lst_result = []

    for df_item in lst:
        fetchall = datalab_api(df_item, startDate, endDate, period)
        df_result = json_to_df(fetchall)
        lst_result.append(df_result)

    return lst_result

def df_output(lst_result):
    lst_mutiple = []

    for i in range(len(lst_result)):
        df_temp = lst_result[i]
        multiple = df_temp.loc[0, 'ratio'] / lst_result[0].loc[0, 'ratio']
        lst_mutiple.append(multiple)

    for i in range(len(lst_result)):
        lst_result[i]['ratio'] = lst_result[i]['ratio'].apply(lambda item: item / lst_mutiple[i])

    for i in range(len(lst_result)):
        df = lst_result[i]
        df.loc[:len(df['period'].unique()) - 1] = lst_result[0].loc[:len(df['period'].unique()) - 1]

    df_result = pd.DataFrame(columns={'title', 'keyword', 'period', 'ratio'})

    for df in lst_result:
        df_result = df_result.append(df)

    df_result['keyword'] = df_result['keyword'].apply(lambda item: str(item))
    df_result = df_result.drop_duplicates(['title', 'keyword', 'period'], keep='first')

    return df_result


# if __name__ == '__main__':
#     """
#         Input 파일명은 target.xlsx이고, 첫줄은 제거
#         Output 파일명은 target_result.xlsx
#         같은 폴더 두 파일이 있어야 함.
#     """
#
#     startDate = '2016-01-01'
#     endDate = str(dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d"))
#     period = 'date'
#
#     """MLB"""
#     lst_result_MLB = api_con_exe('MLB', startDate, endDate, period)
#     df_result_MLB = df_output(lst_result_MLB)
#     df_result_MLB['brand'] = 'MLB'
#
#     ratio_sum = 0
#
#     for i, row in df_result_MLB.iterrows():
#         if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['title'] == '나이키에어맥스97'):
#             ratio_sum += row['ratio']
#
#     df_result_MLB['search_qty'] = round((633305 / ratio_sum) * df_result_MLB['ratio'], 0)
#
#     """MLB KIDS"""
#     lst_result_MLB_KIDS = api_con_exe('MLB KIDS', startDate, endDate, period)
#     df_result_MLB_KIDS = df_output(lst_result_MLB_KIDS)
#     df_result_MLB_KIDS['brand'] = 'MLB KIDS'
#
#     ratio_sum = 0
#
#     for i, row in df_result_MLB_KIDS.iterrows():
#         if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['title'] == '나이키에어맥스97'):
#             ratio_sum += row['ratio']
#
#     df_result_MLB_KIDS['search_qty'] = round((633305 / ratio_sum) * df_result_MLB_KIDS['ratio'], 0)
#
#     """DX"""
#     lst_result_DX = api_con_exe('DX', startDate, endDate, period)
#     df_result_DX = df_output(lst_result_DX)
#     df_result_DX['brand'] = 'DX'
#
#     ratio_sum = 0
#
#     for i, row in df_result_DX.iterrows():
#         if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['title'] == '나이키에어맥스97'):
#             ratio_sum += row['ratio']
#
#     df_result_DX['search_qty'] = round((633305 / ratio_sum) * df_result_DX['ratio'], 0)
#
#     """DK"""
#     lst_result_DK = api_con_exe('DK', startDate, endDate, period)
#     df_result_DK = df_output(lst_result_DK)
#     df_result_DK['brand'] = 'DK'
#
#     ratio_sum = 0
#
#     for i, row in df_result_DK.iterrows():
#         if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['title'] == '나이키에어맥스97'):
#             ratio_sum += row['ratio']
#
#     df_result_DK['search_qty'] = round((633305 / ratio_sum) * df_result_DK['ratio'], 0)
#
#     df_result = pd.concat([df_result_MLB, df_result_MLB_KIDS, df_result_DX, df_result_DK])
#
#     df_result = df_result.drop_duplicates(keep='first')
#
#     df_result = df_result[['title', 'keyword', 'period', 'ratio', 'search_qty', 'brand']]
#     # df_result.to_excel('target_result.xlsx')
#     lst_db_info = db_info()
#     db_insert(lst_db_info, df_result)
#     week_update.keyword_week_update()
