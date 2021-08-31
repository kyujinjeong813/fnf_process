import json
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
ENGINE_POSTGRES_POSTGRES_LOCAL = "postgresql+psycopg2://process:process@172.0.2.93:5432/postgres"

def create_engine_postgres_local():
    engine = create_engine(ENGINE_POSTGRES_POSTGRES_LOCAL)
    return engine

def get_china_sales_from_db():

    try:
        engine = create_engine_postgres_local()
        conn = engine.connect()

        sql = """
        select to_date(a.start_dt, 'YYYYMMDD') as start_dt, c.cat_nm, c.sub_cat_nm,
        sum(a.sale_qty) as cy_sale_qty
        from chn_ys.ys_dw_chn_ttl_w a, fnf_oracle.di_barcode b, dw.db_prdt c
        where a.barcode=b.barcode and b.partcode=c.part_cd and b.brand='M' and a.start_dt > '20200801'
        group by to_date(a.start_dt, 'YYYYMMDD'), c.cat_nm, c.sub_cat_nm
        """

        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")
        return


def get_korea_sales_from_db():

    try:
        engine = create_engine_postgres_local()
        conn = engine.connect()

        sql = """
        select a.start_dt, b.cat_nm, b.sub_cat_nm,
        sum(a.sale_nml_qty_rtl+a.sale_ret_qty_rtl) as sale_qty_rtl,
        sum(a.sale_nml_qty_notax+a.sale_ret_qty_notax) as sale_qty_duty,
        sum(a.sale_nml_qty_rf+a.sale_ret_qty_rf) as sale_qty_rf
        from dw.db_scs_w a left join dw.db_prdt b
        on a.prdt_cd=b.prdt_cd
        where a.brd_cd='M' and a.start_dt > '20200801'
        group by a.start_dt, b.cat_nm, b.sub_cat_nm
        """

        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")
        return


df_china = get_china_sales_from_db()
df_korea = get_korea_sales_from_db()

df = pd.merge(df_china, df_korea, how='outer', on=['start_dt', 'sub_cat_nm'])
df_sub = df[['start_dt', 'cat_nm_x', 'sub_cat_nm', 'cy_sale_qty', 'sale_qty_rtl', 'sale_qty_duty', 'sale_qty_rf']]

sub_cat = df_sub.sub_cat_nm.unique().tolist()
sub_cat.remove('TBA')
sub_cat.remove(None)

def get_distance(df):
    x = mns.fit_transform(df.cy_sale_qty.values.reshape(-1,1))
    y = mns.fit_transform(df.sale_qty_rtl.values.reshape(-1,1))
    dist = np.sqrt(np.sum([(a - b) * (a - b) for a, b in zip(x, y)]))
    return dist

sub_dist = dict()

for i in sub_cat:
    df_sub_cat = df_sub[df_sub['sub_cat_nm'] == i]
    dist = get_distance(df_sub_cat)
    sub_dist[i] = dist

print(sub_dist)



from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

mns = MinMaxScaler()

df_bag1['ch_sale'] = mns.fit_transform(df_bag1.cy_sale_qty.values.reshape(-1,1))
df_bag1['kr_rtl_sale'] = mns.fit_transform(df_bag1.sale_qty_rtl.values.reshape(-1,1))

from fastdtw import fastdtw

distance, path = fastdtw(df_bag1['ch_sale'], df_bag1['kr_rtl_sale'])
fig, ax = plt.subplots(figsize=(12,6))

ax.plot([df_bag1.ch_sale.iloc[v] for v in [p[0] for p in path]], color='b', label='China', alpha=0.75)

ax.plot([df_bag1.kr_rtl_sale.iloc[v] for v in [p[1] for p in path]], color='r', label='Korea Retail', alpha=0.75)

ax.legend()
ax.set_title("China vs Korea retail sales | distance: {}".format(round(distance, 3)), fontsize=15)
ax.set_xlabel("time steps")
ax.set_ylabel("normalized price")

plt.show()