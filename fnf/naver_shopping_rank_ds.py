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

ds_select = pd.read_excel(path, sheet_name='CB', index_col=None)


engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
con = engine.connect()

# for i in range(8):
#     df_sub = list(ds_select.iloc[:, i].dropna())
#     result = list(map(lambda x : ''+str(x).split('.')[0]+'', df_sub))
#     df_result = []
#     print('------------------------------------------------')
#     for j in range(len(result)):
#         cat = "'" + result[j] + "'"
#         strSQL = """
#         select index, category, start_date, end_date, date_part('year', start_date) as Year,
#         date_part('month', start_date) as Month, extract(week from start_date) as Week_Num,
#         rank as Rank, keyword as Keyword
#         from db_mkt_naver_shopping_rank where index = {} and rank < 21""".format(cat)
#         df = pd.read_sql(strSQL, con)
#         df_result = df.append(df_result)
#     print(df_result)
#     df_result['index'] = df_result['index'].astype('int64')
#     # df_final = pd.merge(df_result, ds_code, left_on='category', right_on='code', how='left', sort=False)
#     # cols = ['index', 'name', 'start_date', 'end_date', 'year', 'month', 'week_num', 'rank', 'keyword']
#     # df_final = df_final[cols]
#     print(df_result)
#
#     df_result.to_csv('design_shop{}.csv'.format(i), sep=',', na_rep='NaN', index=False)


df_sub = list(ds_select.iloc[:, 8].dropna())
result = list(map(lambda x : ''+str(x).split('.')[0]+'', df_sub))
df_result = []
for j in range(len(result)):
    cat = "'" + result[j] + "'"
    strSQL = """
    select index, category, start_date, end_date, date_part('year', start_date) as year,
    date_part('month', start_date) as month, extract(week from start_date) as week_num,
    rank, keyword
    from db_mkt_naver_shopping_rank where index = {} and rank < 21""".format(cat)
    print(strSQL)
    df = pd.read_sql(strSQL, con)
    df_result = df.append(df_result)
    print(df_result)
df_result['index'] = df_result['index'].astype('int64')
df_result.to_csv('design_shop_0828.csv', sep=',', na_rep='NaN', index=False)
#
#     df_final = pd.merge(df_result, ds_code, left_on='category', right_on='code', how='left', sort=False)
#     df_final.to_csv('design_shop.csv', sep=',', na_rep='NaN', index=False)
    # with pd.ExcelWriter('design_shop.xlsx') as writer:
    #     df_result.to_excel(writer, sheet_name="Sheet{}".format(i))

# i=0
# df_sub = list(df.iloc[:, i+1].dropna())
# result = list(map(lambda x : ''+str(x).split('.')[0]+'', df_sub))
# df_result = []
# for j in range(len(result)):
#     cat = "'" + result[j] + "'"
#     strSQL = "select * from db_mkt_naver_shopping_rank where category = {}".format(cat)
#     print(strSQL)
#     df = pd.read_sql(strSQL, con)
#     df_result = df.append(df_result)
# print(df_result)
# df_result.to_csv('design_shop_1.csv', sep=',', na_rep='NaN', index=False)

# con.close()

