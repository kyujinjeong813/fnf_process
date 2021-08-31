import pandas as pd
from sqlalchemy import create_engine
import os

engine_info = 'postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres'

# 일단 한 대표품번에 대해서만 했습니당
prdt_cd = '31TSM1131'

def read_db_contents(engine_info, sql):
    engine = create_engine(engine_info)
    conn = engine.connect()
    strSQL = sql
    df = pd.read_sql(strSQL, conn)
    return df


# 제품정보 및 주간 판매액 데이터 프레임화
sql_week ="""
select B.prdt_cd, B.prdt_nm, sum(A.sale_amt_kor_ttl) as sale_amt
from fnf_oracle.db_prdt_sale_kor_w A
left join fnf_oracle.di_prdt B
on A.brand=B.brand and A.season=B.season and A.partcode=B.partcode
where A.brand='M' and
      (to_date(A.start_dt, 'YYYYMMDD') > current_date - interval '14days'
and to_date(A.start_dt, 'YYYYMMDD') < current_date - interval '6days')
and prdt_cd = '{}'
group by B.prdt_cd, B.prdt_nm
""".format(prdt_cd)

df_week = read_db_contents(engine_info, sql_week)



# 최근 16주 판매
sql_16 ="""
select B.prdt_cd, A.start_dt, sum(A.sale_amt_kor_ttl) as sale_amt
from fnf_oracle.db_prdt_sale_kor_w A
left join fnf_oracle.di_prdt B
on A.brand=B.brand and A.season=B.season and A.partcode=B.partcode
where A.brand='M' and (to_date(A.start_dt, 'YYYYMMDD') < current_date - interval '6days' and to_date(A.start_dt, 'YYYYMMDD') > current_date - interval '118days')
and B.prdt_cd ='{}'
group by B.prdt_cd,  A.start_dt
order by B.prdt_cd, A.start_dt
""".format(prdt_cd)

df_16 = read_db_contents(engine_info, sql_16)



# 기준주차 추출
sql_date = """
select distinct start_dt
from fnf_oracle.db_prdt_sale_kor_w
where to_date(start_dt, 'YYYYMMDD') < current_date - interval '6days' and to_date(start_dt, 'YYYYMMDD') > current_date - interval '118days'
order by start_dt
"""

# 제품, 주차 데이터 프레임 생성
df_date = read_db_contents(engine_info, sql_date)
df_date['prdt_cd'] = prdt_cd

# 빈 주차 판매 0으로 만들기
df_merge = pd.merge(df_date, df_16, how='left', on=['prdt_cd', 'start_dt'])
df_sale16 = df_merge.fillna(0)

lst = df_sale16['sale_amt'].tolist()
df_week['sale_16'] = [lst]

dict = df_week.T.to_dict().values()
print(dict)

# row = {'prdt_cd': prdt_cd, 'prdt_nm': prdt_nm, 'body_imgs': img_lst, 'comment': comment_lst}