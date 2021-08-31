from dataclasses import dataclass
import pandas as pd
import numpy as np
import datetime as dt
from api_con_p import pre_process, datalab_api, json_to_df, divide_df, api_con_exe, df_output



if __name__ == '__main__':

    # 원하는 시작일자를 입력해주세요 (YYYY-MM-DD)
    startDate = '2018-12-31'
    endDate = str(dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d"))

    # 'date'로 바꾸면 일자별 검색량이 추출됩니다.
    period = 'week'

    lst_result = api_con_exe(startDate, endDate, period)
    df_result = df_output(lst_result)

    ratio_sum = 0

    for i, row in df_result.iterrows():
        if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '05') & (row['title'] == 'MLB'):
            ratio_sum += row['ratio']

    df_result['search_qty'] = round((196400 / ratio_sum) * df_result['ratio'], 0)

    df_result = df_result[['title', 'keyword', 'period', 'ratio', 'search_qty']]
    df_result.to_excel('target_result.xlsx')

