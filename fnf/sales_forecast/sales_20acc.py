import pandas as pd
import psycopg2

conn_string = "host='172.0.2.93' dbname ='postgres' user='postgres' password='1111'"
conn = psycopg2.connect(conn_string)
cur = conn.cursor()
query = """
select A.start_dt, A.partcode, A.season, B.item, A.sale_qty_kor_retail, A.sale_amt_kor_retail, A.sale_qty_kor_rfdutywhole, A.sale_amt_kor_rfdutywhole
from db_prdt_sale_kor_w_agg A
left join db_prdt B on A.brand=B.brand and A.season=B.season and A.partcode=B.partcode
where A.brand='M' and A.start_dt > '20161229' and (A.sale_amt_kor_retail > 0 or A.sale_amt_kor_rfdutywhole > 0);"""
cur.execute(query)
result = cur.fetchall()
df = pd.DataFrame(result)

df.columns = ['start_dt', 'partcode', 'season', 'item', 'kor_qty', 'kor_amt', 'rfdutywh_qty', 'rfdutywh_amt']

