from sqlalchemy import create_engine
import pandas as pd
import json
import urllib.request
import datetime
import sqlalchemy


def get_keywords_from_db(brand):

    try:
        engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
        conn = engine.connect()

        sql = """select *
                 from public.db_mkt_naver_keyword_master
                 where brand = '""" + brand + """'"""

        df = pd.read_sql(sql, conn)
        df = df.apply(lambda x: x.str.strip(), axis=1)
        conn.close()
        df_sub = df.iloc[:,8:].drop_duplicates()
        return df_sub

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")
        return



def make_keyword_list(df):
    columns = df.columns.tolist()
    start_index = columns.index('keyword_repr')

    df_keywords = df.iloc[:, start_index:]
    df_keyword_set = pd.DataFrame(columns=['groupName', 'keywords'])
    for i in range(len(df_keywords)):
        keyword_list = df_keywords.iloc[i, 0:len(df_keywords.columns)].tolist()
        keyword_list = [keyword.replace(' ', '') for keyword in keyword_list if keyword]
        keyword_list = list(set(keyword_list))
        df_keyword_set.loc[i] = {'groupName': df_keywords.iloc[i, 0], 'keywords': keyword_list}

    return df_keyword_set


def get_iteration_number(df):
    num = len(df) // 4
    rem = len(df) % 4
    return num, rem


def df_to_dict(df_keyword_set, last_row=False,  i=0):
    if last_row:
        df_keyword_4 = df_keyword_set.iloc[-last_row:, :]
    else:
        df_keyword_4 = df_keyword_set.iloc[i*4:(i+1)*4, :]
    df_keyword_set = df_keyword_4.transpose()
    keyword_dict = df_keyword_set.to_dict()
    keyword_list = list(keyword_dict.values())
    keyword_list.extend([{"groupName": "나이키에어맥스97", "keywords": ["나이키에어맥스97"]}])
    return keyword_list


def api_con(keyword_list, startDate, endDate, timeUnit):

    #client_id = "HIhP5fvdbNMnigiPHXJd"
    #client_secret = "BxJ5nWPc0a"
    client_id = "0SD5AerrdptgLB2lnoBG"
    client_secret = "AXO5zr9o8k"
    # client_id = "HoTafla2tj4KNdVeZeLH"
    # client_secret = "SQJ9JlxYdJ"
    url = "https://openapi.naver.com/v1/datalab/search"

    body = {
        "startDate": startDate,
        "endDate": endDate,
        "timeUnit": timeUnit,
        "keywordGroups": keyword_list
    }

    body = json.dumps(body, ensure_ascii=False)

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))

    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        json_obj = json.loads(response_body.decode('utf-8'))

        return json_obj

    else:
        print("Error Code:" + rescode)


def json_to_df(json_obj, brand):

    df_json = pd.DataFrame(columns={'brand', 'keyword_repr', 'keyword', 'period', 'ratio'})
    lastrow = 0

    try:
        for i in range(len(json_obj['results'])):
            data = json_obj['results'][i]['data']
            for j in range(len(data)):
                df_json.loc[j + lastrow, 'brand'] = brand
                df_json.loc[j + lastrow, 'keyword_repr'] = json_obj['results'][i]['title']
                df_json.loc[j + lastrow, 'keyword'] = json_obj['results'][i]['keywords']
                df_json.loc[j + lastrow, 'period'] = json_obj['results'][i]['data'][j]['period']
                df_json.loc[j + lastrow, 'ratio'] = json_obj['results'][i]['data'][j]['ratio']
                lastrow += j + 1

        df_json = df_json.reset_index().drop('index', axis='columns')
        df_json = df_json[['brand', 'keyword_repr', 'keyword', 'period', 'ratio']]

        ratio_sum = 0

        for i, row in df_json.iterrows():
            if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['keyword_repr'] == '나이키에어맥스97'):
                ratio_sum += row['ratio']

        df_json['search_qty'] = df_json['ratio'].apply(lambda item : int((633308 / ratio_sum) * item))
        df_json['keyword'] = df_json['keyword'].apply(lambda item : str(item))

        print(df_json)
        return df_json

    except:
        pass

def db_refresh(brand):
    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()

    sql = """delete
                from public.db_mkt_naver_keyword_trend
                where brand='{}';
                """.format(brand)

    conn.execute(sql)
    conn.execute("commit;")
    conn.close()


def db_insert(df, brand):

    df['brand'] = brand
    df.columns = ['brand', 'keyword_repr', 'keyword', 'period', 'ratio', 'search_qty']
    df.dropna(inplace=True)

    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()

    df.to_sql(name = 'db_mkt_naver_keyword_trend',
                  con = engine,
                  schema ='public',
                  if_exists= 'append',
                  index = False,
                  dtype = {
                      'title' : sqlalchemy.types.VARCHAR(255),
                      'keyword_repr': sqlalchemy.types.VARCHAR(1000),
                      'period' : sqlalchemy.types.TIMESTAMP,
                      'ratio' : sqlalchemy.types.Float(precision=5),
                      'search_qty' : sqlalchemy.types.Float(precision=5),
                      'brand' : sqlalchemy.types.VARCHAR(50)
                  }
                 )

    conn.close()


def db_week_update(brand):

    engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
    conn = engine.connect()

    sql ="""delete
                from public.db_mkt_naver_keyword_trend_w
                where brand='{}';
    insert into public.db_mkt_naver_keyword_trend_w
    with summary as (
    select date(date_trunc('week', period::timestamp))                      as period,
           brand,
           keyword_repr,
           keyword,
           ratio,
           search_qty
    from public.db_mkt_naver_keyword_trend
    where brand='{}'
)
select to_char(period, 'YYYYMMDD') as period,
       brand,
       keyword_repr,
       keyword,
       sum(ratio) as ratio,
       sum(search_qty) as search_qty
from summary
where brand='{}'
group by period, brand, keyword_repr, keyword;""".format(brand, brand, brand)

    conn.execute(sql)
    conn.execute("commit;")
    conn.close()
    print("===========weekly_update_complete===========")


