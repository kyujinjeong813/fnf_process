import json
from datetime import datetime, date, timedelta

import pandas as pd
import requests
from sqlalchemy import create_engine


def get_start_date():
    engine = create_engine(
        'postgresql+psycopg2://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:35430/postgres')
    conn = engine.connect()
    strSQL = """
    select max(period)
    from public_data.db_kor_weather_d"""

    df = pd.read_sql(strSQL, conn)
    last_dt = df.iloc[0].to_list()[0]
    start_dt = datetime.strptime(last_dt, '%Y-%m-%d') + timedelta(1)
    startDt = start_dt.strftime("%Y%m%d")

    return startDt


def get_weather_data(initial=False):
    url = 'http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList'
    auth_key = 'u2oi8aG28v7qRUq%2FTmlF%2Fy%2B1gC14gY8Tl5fOho6MSUXO%2FxhBQJk73O%2FpZX%2F0GHpwMH4A8F5UlC43SzNvDnqIpA%3D%3D'
    state_dict = {'108': '서울', '159': '부산'}

    if initial:
        startDt = '20190101'
    else:
        startDt = get_start_date()

    yesterday = date.today() - timedelta(1)
    endDt = yesterday.strftime("%Y%m%d")

    df_result = pd.DataFrame(columns=['state', 'period', 'average_temp', 'min_temp', 'max_temp', 'ttl_rain'])
    for state_code in state_dict.keys():
        queryParams = '?' + \
                  'ServiceKey=' + auth_key + \
                  '&pageNo=1' + \
                  '&numOfRows=999' + \
                  '&dataType=JSON' + \
                  '&dataCd=ASOS' + \
                  '&dateCd=DAY' + \
                  '&startDt=' + startDt + \
                  '&endDt=' + endDt + \
                  '&stnIds=' + state_code

        result = requests.get(url + queryParams)
        js = json.loads(result.content)
        data = pd.DataFrame(js['response']['body']['items']['item'])
        li = ['stnId', 'tm', 'avgTa', 'minTa', 'maxTa', 'sumRn']
        data_sub = data[li]
        data_sub.replace(state_code, state_dict[state_code], inplace=True)
        data_sub.rename(columns={'stnId': 'state', 'tm': 'period',
                             'avgTa': 'average_temp', 'minTa': 'min_temp',
                             'maxTa': 'max_temp', 'sumRn': 'ttl_rain'},
                    inplace=True)
        df = data_sub.replace('', 0)
        df_result = df_result.append(df)
    print(df_result)

    return df_result


def db_insert(df):
    engine = create_engine(
        'postgresql+psycopg2://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:35430/postgres')
    conn = engine.connect()

    df.to_sql(name='db_kor_weather_d', con=engine, schema='public_data',
              if_exists='append', index=False)
    conn.close()
    print('db_update completed')


if __name__ == '__main__':
    df = get_weather_data()
    db_insert(df)