# 판매 데이터 가져오기 (오라클, fnf scs data join parts)
# http://www.jiniya.net/ng/2017/11/isocalendar/ (날짜를 주차로 변환)
# 검색량도 가져와야겠당

import pandas as pd
import cx_Oracle as co
import os
import platform

file_path = 'C://Users/kyujin/Desktop/PROCESS/MKT/DX/DX마케팅_프로세스팀_5월 정성평가 추가 CONTENTS_LIST_DATA_200622_카라티수정.xlsx'
sheet_name = '인플루언서 별도 시트'
cols = ['중분류', '소분류', '품번']

df = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
df = df.iloc[:, 4:31]
df.dropna(thresh=15, inplace=True)
df.drop(df.tail(1).index, inplace=True)
df = df[cols]
df = df.drop_duplicates(['중분류','소분류','품번'])
items = list(set(df['소분류']))
dict = {}
for i in items:
    partcode = list(df.loc[df['소분류']==i, '품번'])
    dict[i] = partcode

# 소분류(제품)별 품번 리스트
print(dict)

os.environ["NLS_LANG"] = ".AL32UTF8"
dsn_tns = co.makedsn("idb.fnf.co.kr", "1521", service_name="fnf")
con = co.connect(user="process", password="pps$2020", dsn=dsn_tns)
cur = con.cursor()
strSQL = """
select A.brand, A.season, A.wdate, A.partcode, B.line3, sum(A.sale_qty)-sum(A.sale_cqty) as sale_qty,
       sum(A.SALE_AMT)-sum(A.SALE_CAMT) as sale_amt
from fnf.SCSDAY A
left join fnf.parts B
on A.BRAND=B.BRAND and A.SEASON=B.SEASON and A.PARTCODE=B.PARTCODE
where A.BRAND='X' A.WDATE between '2020-01-01' and '2020-06-03' and A.partcode in ('DWTS54031',' DWTS54031','DXRS81031','DXRS85031','DXRS83031','DXRS87031','DWLG92011','DWLG45011','DMPT23011','DMTS53031','DWRS98031','DXSHK2031','DXSHK1031','DXSHF2031','DXSHB6031','DXSHB5031','DXSHB4031','DXSHB3031','DXSHB2031','DXSHB1031','DXSG34011','DXTP23011','DXRS8E031','DXRS8A031','DXRS8C031','DMWJ23011','DWWJ24011','DWLG41011','DWLG42011','DXSHC3031','DXSHC2031','DXSHC1031','DXSHG2031','DXSHG1031','DXSHH1031','DXSHH2031','DXSHH3031','DMPT39011','DMWJA3011','DMWJA1011','DWWJ26011','DMWJ25011','DWSS12011','DMSS11011','DWLG44011','DXSHE4031','DXSHE3031','DXSHE2031','DXSHE1031','DXSFG2031','DXSFG1031','DXSHF6031','DXSHF1031','DXSHF3031','DXSHF5031','DXSHF4031','DXSS37011','DXSHA4011','DXSHA5011','DXSHA3011','DXSHA2011','DXSHA1011','DKBK31011','DXBK31011')
group by A.brand, A.season, A.wdate, A.partcode, B.LINE3
"""
df = pd.read_sql(strSQL, con)
print(df)

con.close()

# partcode 기준으로 분류 (마케팅 여부, 마케팅 키워드 연결)
#df_sale = pd.merge(df, df_match, how='outer', left_on='PARTCODE', right_on='품번')

#df_sale['YEAR'] = df_sale['WDATE'].apply(lambda x: str(x).split('-')[0])

