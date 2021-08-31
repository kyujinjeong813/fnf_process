import pandas as pd
from sqlalchemy import create_engine
import os

engine_info = 'postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres'

def read_db_contents(engine_info, sql):
    engine = create_engine(engine_info)
    conn = engine.connect()
    strSQL = sql
    df = pd.read_sql(strSQL, conn)
    return df

# 제품정보 및 주간 판매액 데이터 프레임화 (상위 5개만 가져옴)
sql_week ="""
select B.prdt_cd, B.prdt_nm, A.start_dt, sum(A.sale_amt_kor_ttl) as sale_amt
from fnf_oracle.db_prdt_sale_kor_w A
left join fnf_oracle.di_prdt B
on A.brand=B.brand and A.season=B.season and A.partcode=B.partcode
where A.brand='M' and
      (to_date(A.start_dt, 'YYYYMMDD') > current_date - interval '14days'
and to_date(A.start_dt, 'YYYYMMDD') < current_date - interval '6days')
group by B.prdt_cd, B.prdt_nm,  A.start_dt
order by sum(A.sale_amt_kor_ttl) desc
limit 5
"""

df_week = read_db_contents(engine_info, sql_week)


# 대표품번 리스트 및 tuple 생성
prdt_cd_lst = df_week['prdt_cd'].tolist()
prdt_cd_tuple = tuple(prdt_cd_lst)

# 대표품번 별 최근 16주 판매 (대표품번 전체 데이터 추출)
sql_16 ="""
select B.prdt_cd, A.start_dt, sum(A.sale_amt_kor_ttl) as sale_amt
from fnf_oracle.db_prdt_sale_kor_w A
left join fnf_oracle.di_prdt B
on A.brand=B.brand and A.season=B.season and A.partcode=B.partcode
where A.brand='M' and (to_date(A.start_dt, 'YYYYMMDD') < current_date - interval '6days' and to_date(A.start_dt, 'YYYYMMDD') > current_date - interval '118days')
and B.prdt_cd in {}
group by B.prdt_cd,  A.start_dt
order by B.prdt_cd, A.start_dt
""".format(prdt_cd_tuple)

# 기준주차 추출
sql_date = """
select distinct start_dt
from fnf_oracle.db_prdt_sale_kor_w
where to_date(start_dt, 'YYYYMMDD') < current_date - interval '6days' and to_date(start_dt, 'YYYYMMDD') > current_date - interval '118days'
order by start_dt
"""

# 품번별 16주차 판매
df_16 = read_db_contents(engine_info, sql_16)

df_date = read_db_contents(engine_info, sql_date)
# print(df_date)
# print(df_16)

df_merge = df_date.combine_first(df_16)
print(df_merge)

#
# monday = sorted(list(set(df_16['start_dt'].tolist())))
# print(monday)
#
# df_sale16 = pd.DataFrame(columns=['prdt_cd', 'sale_amt_16'])
# for i in prdt_cd_lst:
#     sale_lst = df_16[df_16['prdt_cd'] == i]['sale_amt'].tolist()
#     print(len(sale_lst))
#     row = {'prdt_cd' : i, 'sale_amt_16' : sale_lst}
#     df_sale16 = df_sale16.append(row, ignore_index=True)

# print(df_sale16)
