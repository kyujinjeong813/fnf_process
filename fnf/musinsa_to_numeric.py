import pandas as pd
from sqlalchemy import create_engine
import os

os.environ["NLS_LANG"] = ".AL32UTF8"

engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
con = engine.connect()

strSQL = """
        select * from db_mkt_musinsa_top20
"""

df = pd.read_sql(strSQL, con)
con.close()

def char_to_int(x):
    x = str(x)
    y = x
    try:
        if '천' in x:
            if '.' in x:
                y = int(str(x.replace('.', '')).replace('천', '')) * 100
            else:
                y = int(x.replace('천', '')) * 1000
        elif '만' in x:
            if '.' in x:
                y = int(str(x.replace('.', '')).replace('만', '')) * 1000
            else:
                y = int(x.replace('만', '')) * 10000
        elif ',' in x:
            y = int(x.replace(',',''))
        elif 'None' in x:
            y = 0
        else:
            pass
    except:
        pass
    return y

df['pg_view'] = df['pg_view'].map(lambda item : char_to_int(item))
df['pg_view'] = pd.to_numeric(df['pg_view'])

df['acum_sales'] = df['acum_sales'].map(lambda item : char_to_int(item))
df['acum_sales'] = pd.to_numeric(df['acum_sales'])

to_table_name = 'db_mkt_musinsa_top20'
engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
engine.execute("truncate table " + to_table_name + ';')
engine.execute("commit;")
print('truncate finished, insert start')

df.to_sql(name=to_table_name, con=engine, schema='public',
          if_exists='append', index=False)

del engine
del df