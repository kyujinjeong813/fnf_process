import cx_Oracle as co
import pandas as pd
import os
from sqlalchemy import create_engine
import time
import datetime
import pandas as pd

os.environ["NLS_LANG"] = ".AL32UTF8"

path = 'C://Users/kyujin/Desktop/PROCESS/code_용품팀_200715.xlsx'

ds_index = pd.read_excel(path, sheet_name='index', index_col=None)
ds_index = ds_index[['code', 'category']]
ds_index['code'] = ds_index['code'].apply(str)

def import_data(strSQL):
    from_table_name = 'bi.naver_rank_tb'
    to_table_name = 'db_mkt_naver_shopping_rank'
    print('-----------------------')
    print('start data migrations :   ', from_table_name)
    start_time = time.time()
    print(datetime.datetime.now(), '에 시작')

    #engine connect
    engine2 = create_engine(
        'postgresql://process:process2020#@dev-ffdt-db-instance.cqn2lfalbvwx.ap-northeast-2.rds.amazonaws.com:5432/postgres')
    con2 = engine2.connect()

    #sql
    df = pd.read_sql(strSQL, con2)
    con2.close()

    print("imported completed from aws postgresql, run to start process postgresql")
    print(df.head(5))
    col = ['index', 'start_date', 'end_date', 'rank', 'keyword']
    df.columns = col

    df_final = pd.merge(df, ds_index, left_on='index', right_on='code', how='left', left_index=False,
                        right_index=False, sort=False)
    df_insert = df_final[['index', 'category', 'start_date', 'end_date', 'rank', 'keyword']]
    print(df_insert)
    engine1 = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    engine1.execute("commit;")

    df_insert.to_sql(name=to_table_name, con=engine1, schema='public',
              if_exists='append', index=False)

    del engine1
    del df

    print('finished run time: ', time.time() - start_time, 'second')
    print('-----------------------')

def run():
    print('########  start migration from aws    ########')
    print(datetime.datetime.now(), '에 postgres migration 시작함')
    start_time = time.time()
    from_table_name = 'bi.naver_rank_tb'
    strSQL = "select * from {} where startdate > '2019-12-31'".format(from_table_name)
    # strSQL_2020 = "select * from {} where code in ('50001565','50001566','50002913','50002914','50000797','50002903','50000017','50004156','50004193','50004194','50004177','50004179','50004183','50004186','50004187','50004188','50006910','50006175','50000016','50001673','50001674','50001675','50001676','50001677','50001678','50001683','50001685')".format(from_table_name)
    strSQL_2019 = "select * from {} where startdate between '2019-01-01' and '2019-12-31'".format(from_table_name)
    strSQL_2018 = "select * from {} where startdate between '2018-01-01' and '2018-12-31'".format(from_table_name)
    # strSQL_2017 = "select * from {} where code in ('50004174', '50000796','50001564','50002904') and startdate between '2017-01-01' and '2017-12-31'".format(from_table_name)

    import_data(strSQL)
    import_data(strSQL_2019)
    # import_data(strSQL_2018)
    # import_data(strSQL_2017)

    print('########  end migration    ########')
    print(datetime.datetime.now(), '에 Batch 완료')
    print('run time:', time.time() - start_time, 'second 소요됨')

if __name__ == '__main__':
    run()


# cur = con.cursor()
# strSQL = """
# # select *  from process.db_prdt
# # """
# con.close()



# engine1 = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
# with engine1.connect() as conn:
#     result = conn.execute("truncate table " + 'public.db_mkt_naver_shopping_rank' + ';')
#     print("truncate finished")
# #
# engine2 = create_engine('postgresql://process:process2020#@dev-ffdt-db-instance.cqn2lfalbvwx.ap-northeast-2.rds.amazonaws.com:5432/postgres')
#
# sql_2017 = "select * from bi.naver_rank_tb where startdate between '2017-01-01' and '2017-12-31'"
# sql_2018 = "select * from bi.naver_rank_tb where startdate between '2018-01-01' and '2018-12-31'"
# sql_2019 = "select * from bi.naver_rank_tb where startdate between '2019-01-01' and '2019-12-31'"
# sql_2020 = "select * from bi.naver_rank_tb where startdate > '2019-12-31'"
#
# insert_sql = """
# insert into public.db_mkt_naver_shopping_rank
# """
#
# table = 'public.db_mkt_naver_shopping_rank'
# df = pd.read_sql(sql_2020, engine2)
# # print(df.head())
# # if len(df) > 0:
# #     df_columns = list(df)
# #     columns = ",".join(df_columns)
# #     values = "VALUES({})".format(",".join(['%s' for _ in df_columns]))
#
#     # insert_stmt = "INSERT INTO {} ({}) {}".format(table, columns, values)
#
# # with engine2.connect() as conn2:
# #     result = conn2.execute(insert_stmt)
# #     print("insert finished")
#
#
#
# df.to_sql('public.db_mkt_naver_shopping_rank', engine1, if_exists='append')
# del df