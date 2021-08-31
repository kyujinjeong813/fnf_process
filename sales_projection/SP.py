# 학습데이터 만들기
# SP(반바지)

import pandas as pd
import numpy as np

df = pd.read_excel('sales_forecasting.xlsx', sheet_name='DATA_TTL')
df_sp = df[df['item'] == 'SP']
#df_sp
#df_sp.columns

df_sp_kr = df_sp[['season','partcode','subseason_nm', 'start_date', 'week_num', 'sale_amt_kor_retail','sale_tag_kor_retail','sale_qty_kor', 'wh_stock_qty', 'stock_qty']]
df_sp_rf = df_sp[['season','partcode','subseason_nm', 'start_date', 'week_num','sale_amt_kor_rf','sale_tag_kor_rf','sale_qty_rf', 'wh_stock_qty', 'stock_qty']]
df_sp_duty = df_sp[['season','partcode','subseason_nm', 'start_date', 'week_num','sale_amt_kor_duty','sale_tag_kor_duty','sale_qty_duty', 'wh_stock_qty', 'stock_qty']]
df_sp_whole = df_sp[['season','partcode','subseason_nm', 'start_date', 'week_num','sale_amt_wholesale','sale_tag_wholesale','sale_qty_wholesale', 'wh_stock_qty', 'stock_qty']]

df_sp_kr_summer = df_sp_kr[df_sp_kr['subseason_nm']=='Summer']
df_sp_kr_spring = df_sp_kr[df_sp_kr['subseason_nm']=='Spring'

# df_sp_kr_summer 반바지는 모두 여름상품이라 안나눠줘도 됨

# 할인율 계산
df_sp_kr_summer['pct'] = 1
df_sp_kr_summer.loc[(df_sp_kr_summer['sale_tag_kor_retail']!=0), 'pct']  = 1 - df_sp_kr_summer['sale_amt_kor_retail']/df_sp_kr_summer['sale_tag_kor_retail']
df_sp_kr_summer.loc[(df_sp_kr_summer['pct']==1), 'pct'] = 0
#df_sp_kr_summer['pct']

# 재고주수 계산
df_sp_kr_summer['woi'] = 10000
df_sp_kr_summer.loc[(df_sp_kr_summer['sale_qty_kor']>0), 'woi'] = df_sp_kr_summer['stock_qty'] / df_sp_kr_summer['sale_qty_kor']
df_sp_kr_summer.drop(['sale_amt_kor_retail', 'sale_tag_kor_retail'], axis=1, inplace=True)

# datetime index
datetime_series = pd.to_datetime(df_sp_kr_summer['start_date'])
datetime_index = pd.DatetimeIndex(df_sp_kr_summer['start_date'].values)
df_sp_kr_summer = df_sp_kr_summer.set_index(datetime_index)
#df_sp_kr_summer

# 엑셀파일로 저장
df_sp_kr_summer.to_excel('sp_kr_summer.xlsx', sheet_name='Sheet1', header=True)

# 시트별 저장
writer = pd.ExcelWriter('엑셀파일명.xlsx', engine='xlsxwriter')

test1_df.to_excel(writer, sheet_name= '첫번째시트')
test2_df.to_excel(writer, sheet_name= '두번째시트')

writer.save()


df_sp_kr_summer_17 = df_sp_kr_summer[df_sp_kr_summer['season']=='17S']
df_sp_kr_summer_17 = df_sp_kr_summer_17[df_sp_kr_summer_17['start_date']<'2018-01-01']
df_sp_kr_summer_18 = df_sp_kr_summer[df_sp_kr_summer['season']=='18S']
df_sp_kr_summer_18 = df_sp_kr_summer_18[df_sp_kr_summer_18['start_date']<'2019-01-01']
df_sp_kr_summer_19 = df_sp_kr_summer[df_sp_kr_summer['season']=='19S']
df_sp_kr_summer_19 = df_sp_kr_summer_19[df_sp_kr_summer_19['start_date']<'2020-01-01']
df_sp_kr_summer_20 = df_sp_kr_summer[df_sp_kr_summer['season']=='20S']

# 재고주수 문제되는 게 있나 확인
# 겁나 충분했음.. 문제된 적 없음 >>> 컬러별 재고주수를 봐야 할 듯 ㅠㅠㅠㅠㅠ 컹
# 오히려 할인 많이 들어갔던 것 노말이 필요
df_sp_kr_summer.loc[(df_sp_kr_summer2['season']=='17S')&(df_sp_kr_summer2['woi']<5)]
df_sp_kr_summer2[df_sp_kr_summer2['season']=='17S']['woi']

#2가지 방법
# 1.모델 holiday 변수에 할인율 30% 이상인 주 날짜 추가하기
# 2.normal sales qty 계산 (동일 판매액 가정, 수량 노말)
df_sp_kr_summer_19['normal'] = df_sp_kr_summer_19['sale_qty_kor']*(1-df_sp_kr_summer_19['pct'])
