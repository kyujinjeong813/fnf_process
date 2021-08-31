from sqlalchemy import create_engine
import pandas as pd
from datetime import datetime, timedelta

def get_start_date():

    engine = create_engine('postgresql+psycopg2://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:35430/postgres')
    conn = engine.connect()
    strSQL = """
    select max(period)
    from public_data.db_kor_weather_d"""

    df = pd.read_sql(strSQL, conn)
    last_dt = df.iloc[0].to_list()[0]
    start_dt = datetime.strptime(last_dt, '%Y-%m-%d') + timedelta(1)
    print(start_dt)
    startDt = start_dt.strftime("%Y%m%d")
    print(startDt)

    return startDt

get_start_date()