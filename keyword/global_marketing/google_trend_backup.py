import pandas as pd
import datetime as dt
from pytrends.request import TrendReq
from sqlalchemy import create_engine

# 파라미터 설정
# country_list = ['India', 'Vietnam', 'Thailand', 'HongKong', 'Macau']
geo_dict = {'India':'IN', 'Vietnam':'VN','Thailand':'TH', 'Taiwan':'TW', 'HongKong':'HK','Macau':'MO'}
period = '2020-01-01 2021-07-27'
key_keyword = 'Nike'

table_name = 'db_mkt_google_trend'



# 구글 트렌드 검색량 수집
def get_google_searches(keyword, country):
    pytrend = TrendReq()
    geo = geo_dict[country]
    pytrend.build_payload(kw_list=keyword, cat=0, timeframe=period, geo=geo, gprop='')
    df = pytrend.interest_over_time()
    if not df.empty:
        df_trim = df.drop(labels=['isPartial'], axis='columns')
        df_trim['Region'] = country
    return df_trim


def db_reset():
    engine = create_engine('postgresql+psycopg2://process:process@172.0.2.93:5432/postgres')
    conn = engine.connect()
    engine.execute("truncate table public.db_mkt_google_trend; commit;")
    conn.close()


# 검색지수 리스케일링
def rescale_search_data(df):
    kijun = df.iloc[0][key_keyword]
    scale_df = df*100/kijun
    reset_df = scale_df.reset_index()
    return reset_df

# 적재위한 형태로 변경
def reform_and_insert_search_data(scale_df):
    engine = create_engine('postgresql+psycopg2://process:process@172.0.2.93:5432/postgres')
    conn = engine.connect()
    column_lst = scale_df.columns.to_list()
    num = len(column_lst)
    for n in range(num):
        if n+2 < num:
            kwd = column_lst[n+2]
            df = scale_df[['date', kwd]]
            df['Keyword'] = kwd
            df.columns = ['end_dt', 'search_index', 'keyword']
            df.to_sql(name=table_name, con=engine, schema='public', if_exists='append', index=False)
    conn.close()



# 키워드리스트 불러오기
def get_insert():
    db_reset()
    df = pd.read_excel('keyword.xlsx')
    df = df[df['Keyword']!='Nike']
    country_list = df['Region'].drop_duplicates().tolist()
    for c in country_list:
        keyword_list = df[df['Region']==c]['Keyword'].tolist()

        q, r = divmod(len(keyword_list), 4)

        for i in range(q + 1):
            if r==0:
                pass
            else:
                if i < q:
                    kwd_4 = keyword_list[4 * i:4 * i + 4]
                    kwd = [key_keyword] + kwd_4
                else:
                    kwd = [key_keyword] + keyword_list[q * 4:]
                df = get_google_searches(kwd,c)
                print(df)
            # scale_df = rescale_search_data(df)
            # print(scale_df)
            # reform_and_insert_search_data(scale_df)


if __name__ == '__main__':
    get_insert()