from dataclasses import dataclass
import pandas as pd
import xlwings as xw
from xlwings.utils import rgb_to_int
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from sqlalchemy import create_engine
import os

os.environ["NLS_LANG"] = ".AL32UTF8"
path = 'C://Users/kyujin/Desktop/PROCESS/code_디자인실_200721.xlsx'
ds_select = pd.read_excel(path, sheet_name='CB', index_col=None, header=None)
path1 = 'C://Users/kyujin/Desktop/PROCESS/code_디자인실_200721.xlsx'
ds_code = pd.read_excel(path1, sheet_name='Sheet2', index_col=None)
ds_sub = ds_code.iloc[1:, 2:4]

engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
con = engine.connect()

# print(ds_select)
category = ''
for i in range(len(ds_select)-1):
    a = int(ds_select.iloc[i,0])
    cat = "'" + str(a) + "',"
    category = category + cat
category = category + "'" + str(int(ds_select.iloc[len(ds_select)-1,0])) + "'"
category = '(' + category + ')'

strSQL = """
    select index, category, start_date, end_date, date_part('year', start_date) as Year,
    date_part('month', start_date) as Month, extract(week from start_date) as Week_Num,
    rank as Rank, keyword as Keyword
    from db_mkt_naver_shopping_rank where category in {} and rank < 21""".format(category)

df = pd.read_sql(strSQL, con)
df['category'] = df['category'].astype('int64')

df_final = pd.merge(df, ds_sub, left_on='category', right_on='code', how='left', left_index=False, right_index=False, sort=False)
cols = ['index', 'name', 'start_date', 'end_date', 'year', 'month', 'week_num', 'rank', 'keyword']
df_final = df_final[cols]
print(df_final)

df_final.to_csv('design_shop_200721.csv', sep=',', na_rep='NaN', index=False)