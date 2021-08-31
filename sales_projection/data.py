import pandas as pd
import numpy as np

df = pd.read_excel('C:/Users/kyujin/Desktop/PROCESS/sales_forecasting.xlsx', sheet_name='DATA_TTL')

# 날짜 형식으로 변환
def str_to_datetime(x):
    x = pd.to_datetime(x, format='%Y-%m-%d', errors='ignore')
    return x
df['start_dt'] = df['start_dt'].apply(lambda x : str(x))
df['start_dt'] = df['start_dt'].apply(lambda x : str_to_datetime(x))

# rn_type 데이터 프레임 분리
df_n = df[df['rn_type'] == 'N']
df_r = df[df['rn_type'] == 'R']

# n type 정상판매 기간 데이터만 가져오기0
df_n[df_n['start_dt']<'2017-09-30']
#(df_n['season'] == '17S') &

