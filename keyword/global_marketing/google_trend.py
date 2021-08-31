import pandas as pd
import datetime as dt
from pytrends.request import TrendReq
from sqlalchemy import create_engine
from datetime import datetime, date, timedelta

# 파라미터 설정
start_dt = '2020-01-01'
today = date.today()
diff = (today.weekday() - 6) % 7
last_mon = today - timedelta(days=diff-1)
period = start_dt + ' '+str(last_mon)
key_keyword = 'Nike'
table_name = 'db_mkt_google_trend'
file_path = "C:/Users/kyujin/PycharmProjects/keyword/global_marketing/global_keyword.xlsx"

# 구글 트렌드 검색량 수집 (5개년 뽑고 싶으면 timeframe = 'today 5-y')
def get_google_searches(keyword_list, geo):
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=keyword_list, cat=0, timeframe=period, geo=geo, gprop='')
    df = pytrend.interest_over_time()
    if not df.empty:
        df = df.drop(labels=['isPartial'], axis='columns')
    return df

# 검색지수 스케일링
def rescale_search_data(df):
    if df.iloc[0][key_keyword] != 0:
        kijun = df.iloc[0][key_keyword]
        scale_df = df*100/kijun
        reset_df = scale_df.reset_index()
        return reset_df
    else:
        print("기준 검색량이 0입니다.")
        return df


# DB 기존 데이터 삭제
def db_reset():
    engine = create_engine('postgresql+psycopg2://process:process@172.0.2.93:5432/postgres')
    conn = engine.connect()
    engine.execute("truncate table public.db_mkt_google_trend; commit;")
    conn.close()


# DB에 데이터프레임 적재
def insert_search_data(scale_df, geo):
    engine = create_engine('postgresql+psycopg2://process:process@172.0.2.93:5432/postgres')
    conn = engine.connect()
    column_lst = scale_df.columns.to_list()
    num = len(column_lst)
    for n in range(num):
        if n+1 < num:
            kwd = column_lst[n+1]
            df = scale_df[['date', kwd]]
            df['Keyword'] = kwd
            df['Region'] = geo
            df.columns = ['end_dt', 'search_index', 'keyword', 'region']
            df.to_sql(name=table_name, con=engine, schema='public', if_exists='append', index=False)
    conn.close()



if __name__ == '__main__':
    df = pd.read_excel("C:/Users/kyujin/PycharmProjects/keyword/global_marketing/global_keyword.xlsx", sheet_name=None)

    for c in df.keys():
        df_sub = df[c][df[c]['Keyword'] != key_keyword]
        kwd_lst = df_sub['Keyword'].to_list()
        q, r = divmod(len(kwd_lst), 4)

        for i in range(q):
            lst = [key_keyword] + kwd_lst[4 * i:4 * i + 4]
            df_search = get_google_searches(lst, c)
            df_scale = rescale_search_data(df_search)
            insert_search_data(df_scale, c)

        if r != 0:
            lst_2 = [key_keyword] + kwd_lst[q * 4:]
            new_df = get_google_searches(lst_2, c)
            df_sc = rescale_search_data(new_df)
            insert_search_data(df_sc, c)
