import pandas as pd
import numpy as np
import datetime

df = pd.read_excel('DX_MKT_2020.xlsx', sheet_name='KEYWORD_DATA')
keywords = set(df['KEYWORD'])

df_list = []
for word in keywords:
    df_word = df[df['KEYWORD'] == word]
    df_list.append(df_word)

new_df_list = []
for i in range(len(df_list)):
    datetime_series = pd.to_datetime(df_list[i]['SEARCHDATE'])
    datetime_index = pd.DatetimeIndex(datetime_series.values)
    new_df = df_list[i].set_index(datetime_index)
    new_df.drop('SEARCHDATE', axis=1, inplace=True)
    new_df_daily = new_df.asfreq('D')
    new_df_daily = new_df_daily.fillna(method='ffill')
    new_df_list.append(new_df_daily)

# 주간단위로 변경
keyword_df = pd.concat(new_df_list)
keyword_df = keyword_df.groupby('KEYWORD').resample('W-Sun').sum()
keyword_df = keyword_df.reset_index()
keyword_df.columns = ['KEYWORD', 'WDATE', 'SEARCHCOUNT']
# 기준일자 일->월로 변경
w_series = pd.to_datetime(keyword_df['WDATE'])
w_series = w_series.apply(lambda x: x + datetime.timedelta(days=1))
keyword_df['WDATE'] = w_series

keyword_df.to_excel('dx_keyword.xlsx', index=False)