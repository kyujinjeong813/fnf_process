import pandas as pd
import numpy as np

df = pd.read_excel('C:/Users/kyujin/Desktop/PROCESS/duty.xlsx', sheet_name='duty')

group = ['week_num', 'sale_year', 'item']
cal = ['sale_qty_duty']

df_sub = df.groupby(group)[cal].sum()
df_sub = df_sub.reset_index()


duty_20 = df_sub[df_sub['sale_year']==2020]
duty_20.columns = ['week_num', 'sale_year', 'item', '20duty']
duty_20.drop('sale_year', axis=1, inplace=True)
duty_17 = df_sub[df_sub['sale_year']==2017]
duty_17.columns = ['week_num', 'sale_year', 'item', '17duty']
duty_17.drop('sale_year', axis=1, inplace=True)
duty_18 = df_sub[df_sub['sale_year']==2018]
duty_18.columns = ['week_num', 'sale_year', 'item', '18duty']
duty_18.drop('sale_year', axis=1, inplace=True)
duty_19 = df_sub[df_sub['sale_year']==2019]
duty_19.columns = ['week_num', 'sale_year', 'item', '19duty']
duty_19.drop('sale_year', axis=1, inplace=True)

all_df = pd.merge(duty_17, duty_18, how='left', on=['week_num','item'])
all_df = pd.merge(all_df, duty_19, how='left', on=['week_num','item'])
all_df = pd.merge(all_df, duty_20, how='left', on=['week_num','item'])
all_df = all_df.fillna(0)

all_df['vs17'] = all_df['20duty']/all_df['17duty']
all_df['vs18'] = all_df['20duty']/all_df['18duty']
all_df['vs19'] = all_df['20duty']/all_df['19duty']

all_df = all_df.replace([np.inf, -np.inf], 0)
all_df = all_df.fillna(0)
all_df

item = {'TK', 'TP', 'TR', 'TS', 'VT', 'WP','WS','SH', 'SK', 'SM', 'SO', 'SP','BG', 'BS', 'CP', 'DP', 'DT', 'JP', 'LG', 'MT', 'OP', 'PT'}

def replace_outliers(list):
    outlier_indices = []
    Q1 = np.percentile(list,25)
    Q3 = np.percentile(list,75)
    IQR = Q3 - Q1
    if IQR > 10:
        outlier_step = IQR * 0.25
    elif IQR > 5:
        outlier_step = IQR * 0.7
    else:
        outlier_step = IQR
    outlier_indices = []
    for i in list:
        if i < Q1 - outlier_step or i > Q3 + outlier_step:
            outlier_indices.append(list.index(i))
    for j in outlier_indices:
        list[j] = np.percentile(list, 50)
    return list

def calculate_w_average(list, wt):
    products = [a * b for a, b in zip(list, wt)]
    return np.sum(products)

recent_week_num = 7
wt = [0.35, 0.24, 0.16, 0.1, 0.07, 0.05, 0.03]
this_week = 21
end_week = 36
cols = ['vs17', 'vs18', 'vs19']

for it in item:
    for col in cols:
        value_list = []
        for i in range(recent_week_num):
            value = all_df[(all_df['item'] == it) & (all_df['week_num'] == this_week - i)][col].values
            value_list.append(value)
        value_list = replace_outliers(value_list)
        all_df.loc[(all_df['item'] == it) & (all_df['week_num'] > this_week), col] = calculate_w_average(value_list, wt)

all_df['est17'] = all_df['17duty']*all_df['vs17']
all_df['est18'] = all_df['18duty']*all_df['vs18']
all_df['est19'] = all_df['19duty']*all_df['vs19']
all_df['est_duty'] = all_df['est17']*0.2 + all_df['est18']*0.3 + all_df['est19']*0.5

all_df.to_excel('20s_duty.xlsx', sheet_name='duty')

###################################################################
# ACC

import pandas as pd
import numpy as np

df = pd.read_excel('C:/Users/kyujin/Desktop/PROCESS/sales_forecasting.xlsx', sheet_name='DATA_TTL')

# 날짜 형식 변환
def str_to_datetime(x):
    x = pd.to_datetime(x, format='%Y-%m-%d', errors='ignore')
    return x
df['start_dt'] = df['start_dt'].apply(lambda x : str(x))
df['start_dt'] = df['start_dt'].apply(lambda x : str_to_datetime(x))
df['sale_year'] = df['start_dt'].apply(lambda x : str(x).split('-')[0])

item = ['CP', 'SH', 'BG', 'SO', 'MT']
df_sub = df[df['item'].isin(item)]
cols = ['week_num', 'sale_year', 'partcode', 'season', 'item', 'sale_qty_kor', 'sale_qty_rf', 'sale_qty_duty', 'sale_qty_wholesale']
df_sub = df_sub[cols]

# 아이템, start_dt로 그룹
group = ['week_num', 'sale_year', 'season', 'item']
cal = ['sale_qty_kor', 'sale_qty_rf', 'sale_qty_duty', 'sale_qty_wholesale']

df_sub = df_sub.groupby(group)[cal].sum()
df_sub = df_sub.reset_index()

df_17_1 = df_sub.loc[(df_sub['season']=='17S') & (df_sub['sale_year']=='2017'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_17_2 = df_sub.loc[(df_sub['season']=='17F') & (df_sub['sale_year']=='2017'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_17 = pd.concat([df_17_1,df_17_2])
df_17.columns = ['week_num', 'item', '17kr', '17rf', '17ws']
df_17 = df_17.groupby(['week_num', 'item'])['17kr', '17rf', '17ws'].sum()
df_17 = df_17.reset_index()

df_18_1 = df_sub.loc[(df_sub['season']=='18S') & (df_sub['sale_year']=='2018'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_18_2 = df_sub.loc[(df_sub['season']=='18F') & (df_sub['sale_year']=='2018'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_18 = pd.concat([df_18_1,df_18_2])
df_18.columns = ['week_num', 'item', '18kr', '18rf', '18ws']
df_18 = df_18.groupby(['week_num', 'item'])['18kr', '18rf', '18ws'].sum()
df_18 = df_18.reset_index()

df_19_1 = df_sub.loc[(df_sub['season']=='19S') & (df_sub['sale_year']=='2019'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_19_2 = df_sub.loc[(df_sub['season']=='19F') & (df_sub['sale_year']=='2019'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_19 = pd.concat([df_19_1,df_19_2])
df_19.columns = ['week_num', 'item', '19kr', '19rf', '19ws']
df_19 = df_19.groupby(['week_num', 'item'])['19kr', '19rf', '19ws'].sum()
df_19 = df_19.reset_index()

df_20_1 = df_sub.loc[(df_sub['season']=='20S') & (df_sub['sale_year']=='2020'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_20_2 = df_sub.loc[(df_sub['season']=='19F') & (df_sub['sale_year']=='2020'), ['week_num', 'item','sale_qty_kor', 'sale_qty_rf', 'sale_qty_wholesale']]
df_20 = pd.concat([df_20_1,df_20_2])
df_20.columns = ['week_num', 'item', '20kr', '20rf', '20ws']
df_20 = df_20.groupby(['week_num', 'item'])['20kr', '20rf', '20ws'].sum()
df_20 = df_20.reset_index()

all_df = pd.merge(df_17, df_18, how='left', on=['week_num', 'item'])
all_df = pd.merge(all_df, df_19, how='left', on=['week_num', 'item'])
all_df = pd.merge(all_df, df_20, how='left', on=['week_num', 'item'])
all_df = all_df.fillna(0)
all_df = pd.concat([all_df.iloc[:,:2], all_df.iloc[:, 2:].clip(lower=0)], axis=1)
all_df = all_df.replace([np.inf, -np.inf], 0)

all_df['vs17_kr'] = all_df['20kr']/all_df['17kr']
all_df['vs18_kr'] = all_df['20kr']/all_df['18kr']
all_df['vs19_kr'] = all_df['20kr']/all_df['19kr']

all_df['vs17_rf'] = all_df['20rf']/all_df['17rf']
all_df['vs18_rf'] = all_df['20rf']/all_df['18rf']
all_df['vs19_rf'] = all_df['20rf']/all_df['19rf']

all_df['vs17_ws'] = all_df['20ws']/all_df['17ws']
all_df['vs18_ws'] = all_df['20ws']/all_df['18ws']
all_df['vs19_ws'] = all_df['20ws']/all_df['19ws']

all_df = all_df.fillna(0)
all_df = all_df.replace([np.inf, -np.inf], 0)
# week_num, item, 17kr, 18kr, 19kr, 20kr


wt_7 = [0.35, 0.24, 0.16, 0.1, 0.07, 0.05, 0.03]
wt_4 = [0.53, 0.27, 0.13, 0.07]
this_week = 21
end_week = 52
recent_week_num = 7

cols = ['vs17_kr','vs18_kr','vs19_kr','vs17_rf','vs18_rf','vs19_rf','vs17_ws','vs18_ws','vs19_ws']

if recent_week_num == 7:
    wt = wt_7
else:
    wt = wt_4

def replace_outliers(list):
    outlier_indices = []
    Q1 = np.percentile(list,25)
    Q3 = np.percentile(list,75)
    IQR = Q3 - Q1
    if IQR > 10:
        outlier_step = IQR * 0.25
    elif IQR > 5:
        outlier_step = IQR * 0.7
    else:
        outlier_step = IQR
    outlier_indices = []
    for i in list:
        if i < Q1 - outlier_step or i > Q3 + outlier_step:
            outlier_indices.append(list.index(i))
    for j in outlier_indices:
        list[j] = np.percentile(list, 50)
    return list

def calculate_w_average(list, wt):
    products = [a * b for a, b in zip(list, wt)]
    return np.sum(products)

# DP는 19년 기획이 없었음 / 가중치 다르게 적용해야 함

for it in item:
    for col in cols:
        value_list = []
        for i in range(recent_week_num):
            value = all_df[(all_df['item'] == it) & (all_df['week_num'] == this_week - i)][col].values
            value_list.append(value)
        value_list = replace_outliers(value_list)
        all_df.loc[(all_df['item'] == it) & (all_df['week_num'] > this_week) & (
                    all_df['week_num'] < end_week), col] = calculate_w_average(value_list, wt)
        all_df.loc[(all_df['item'] == it) & (all_df['week_num'] > end_week), col] = 0

all_df['est17kr'] = all_df['17kr'] * all_df['vs17_kr']
all_df['est18kr'] = all_df['18kr'] * all_df['vs18_kr']
all_df['est19kr'] = all_df['19kr'] * all_df['vs19_kr']

all_df['est17rf'] = all_df['17rf'] * all_df['vs17_rf']
all_df['est18rf'] = all_df['18rf'] * all_df['vs18_rf']
all_df['est19rf'] = all_df['19rf'] * all_df['vs19_rf']

all_df['est17ws'] = all_df['17ws'] * all_df['vs17_ws']
all_df['est18ws'] = all_df['18ws'] * all_df['vs18_ws']
all_df['est19ws'] = all_df['19ws'] * all_df['vs19_ws']

# 최종 예측치
all_df['est_kr'] = all_df['est17kr']*0.2 + all_df['est18kr']*0.3 + all_df['est19kr']*0.5
all_df['est_rf'] = all_df['est17rf']*0.2 + all_df['est18rf']*0.3 + all_df['est19rf']*0.5
all_df['est_ws'] = all_df['est17ws']*0.2 + all_df['est18ws']*0.3 + all_df['est19ws']*0.5

all_df.to_excel('sales_20acc.xlsx', sheet_name = 'acc')
