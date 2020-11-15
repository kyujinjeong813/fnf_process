from dataclasses import dataclass
import pandas as pd
import numpy as np
import datetime as dt
from api_con import pre_process, datalab_api, json_to_df, divide_df

#################################################################################
"""화면설정"""
#################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 1000)
# 최대 열 수 설정
pd.set_option('display.max_column', 100)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)

def api_con_exe(startDate, endDate, period):
    '''검색하고자 하는 데이터 upload'''
    df_search = pd.read_excel("target_keyword.xlsx", sheet_name = 'Sheet1')
    df_search['key_nm'] = np.nan

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


if __name__ == '__main__':

    # 시작일자를 입력해주세요 (YYYY-MM-DD 형식)
    startDate = '2016-01-01'
    endDate = str(dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d"))
    period = 'date'


    lst_result = api_con_exe(startDate, endDate, period)
    df_result = df_output(lst_result)

    ratio_sum = 0

    for i, row in df_result.iterrows():
        if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['title'] == '나이키에어맥스97'):
            ratio_sum += row['ratio']

    df_result['search_qty'] = round((633305 / ratio_sum) * df_result['ratio'], 0)

    df_result = df_result[['title', 'keyword', 'period', 'ratio', 'search_qty']]

    df_week = df_result
    df_week['date'] = pd.to_datetime(df_week['period'])
    df_week['year'] = df_week['date'].dt.year
    df_week['month'] = df_week['date'].dt.month
    df_week['weeknum'] = df_week['date'].dt.isocalendar().week
    mask = (df_week['month'] == 12) & (df_week['weeknum'] == 1)
    df_week.loc[mask, 'year'] = df_week.loc[mask, 'year'].apply(lambda x: x + 1)
    df_week.loc[df_week['weeknum'] == 53, 'weeknum'] = 1

    df_qty = df_week.groupby(['title', 'keyword', 'year', 'weeknum'])['search_qty'].sum()
    df_qty = df_qty.reset_index()

    df_dt = df_week.groupby(['year', 'weeknum'])['period'].min()
    df_dt = df_dt.reset_index()

    df_merge = pd.merge(df_qty, df_dt, on=['year', 'weeknum'], how='left')
    
    df_merge.to_excel('target_result.xlsx')
