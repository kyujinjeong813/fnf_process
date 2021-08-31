import pandas as pd
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import os

os.environ["NLS_LANG"] = ".AL32UTF8"

engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
con = engine.connect()

strSQL = """
select brand,
       season,
       partcode,
       prdt_nm,
       prdt_group,
       item,
       --가방
       case when item = 'BG' then 'MLB가방' end                                                                 as bg1,
       case when prdt_nm like '%%백팩%%' then 'MLB백팩' end                                                         as bg2,
       case when prdt_nm like '%%슬링백%%' or prdt_nm like '%%힙색%%' or prdt_nm like '%%웨이스트백%%' then 'MLB힙색' end       as bg3,
       case when prdt_nm like '%%크로스백%%' or prdt_nm like '%%넥파우치%%' or prdt_nm like '%%버킷백%%' then 'MLB크로스백' end    as bg4,

       -- 모자
       case when item = 'CP' then 'MLB모자' end                                                                 as cp0,
       case when item = 'CP' and cap_attr1 = '볼캡' then 'MLB볼캡' end                                            as cp1,
       case when item = 'CP' and season_nonseason = '겨울성' then 'MLB겨울모자' end                                  as cp2,
       case when item = 'CP' and prdt_nm like '%%데님%%' then 'MLB데님모자' end                                       as p3,
       case when item = 'CP' and prdt_nm like '%%모노그램%%' then 'MLB모노그램모자' end                                   as cp4,
       case when item = 'CP' and substr(partcode, 3, 4) = 'CP55' then 'MLB CP55' end                          as cp5,
       case when item = 'CP' and substr(partcode, 3, 4) = 'CP66' then 'MLB CP66' end                          as cp6,
       case when item = 'CP' and substr(partcode, 3, 4) = 'CP77' then 'MLB CP77' end                          as cp7,
       case when item = 'CP' and substr(partcode, 3, 4) = 'CP88' then 'MLB CP88' end                          as cp8,
       case when item = 'CP' and cap_attr1 = '비니' then 'MLB비니' end                                            as cp9,
       case when item = 'CP' and cap_attr1 = '스냅백' then 'MLB스냅백' end                                          as cp10,
       case when item = 'CP' and cap_attr1 = '바이저' then 'MLB바이저' end                                          as cp11,
       case when item = 'CP' and cap_attr1 = '코듀로이' then 'MLB코듀로이' end                                        as cp12,
       case when item = 'CP' and (prdt_nm like '%%햇%%' or prdt_nm like '%%HAT%%') then 'MLB햇' end                 as cp13,
       case
           when item = 'CP' and (prdt_nm like '%%후리스%%' or prdt_nm like '%%뽀글이%%' or cap_attr1 = '후리스')
               then 'MLB후리스모자' end                                                                            as cp14,
       case
           when item = 'CP' and (prdt_nm like '%%후리스%%' or prdt_nm like '%%뽀글이%%' or cap_attr1 = '후리스')
               then 'MLB후리스모자' end                                                                            as cp15,

       --신발
       case when item = 'SH' and prdt_nm like '%%샌들%%' or shape1_user = '샌들' then 'MLB샌들' end                   as sh1,
       case when item = 'SH' and prdt_nm like '%%슬리퍼%%' or shape1_user = '슬리퍼' then 'MLB슬리퍼' end                as sh2,
       case when item = 'SH' and prdt_nm like '%%뮬%%' then 'MLB뮬' end                                           as sh3,
       case when item = 'SH' and prdt_nm like '%%플레이볼%%' and prdt_nm not like '%%뮬%%' then 'MLB스니커즈' end          as sh4,
       case
           when item = 'SH' and prdt_nm like '%%청키%%' and (prdt_nm not like '%%청키 하이%%' and prdt_nm not like '%%플레이볼%%')
               then '빅볼청키' end                                                                                as sh5,
       case when item = 'SH' and prdt_nm like '%%청키 하이%%' then 'MLB 청키하이' end                                   as sh6,
       case when item = 'SH' and shape1_user = '운동화' then 'MLB운동화' end                                        as sh7,

       -- 아우터
       case when prdt_kind_nm = 'OUTER' and prdt_nm like '%%경량%%' then 'MLB경량패딩' end                            as outer1,
       case when prdt_kind_nm = 'OUTER' and item = 'DJ' and prdt_nm like '%%롱%%' then 'MLB롱패딩' end              as outer2,
       case when prdt_kind_nm = 'OUTER' and item = 'DJ' and prdt_nm like '%%숏%%' then 'MLB숏패딩' end              as outer3,
       case when prdt_kind_nm = 'OUTER' and item = 'DV' then 'MLB패딩조끼' end                                    as outer4,
       case when prdt_kind_nm = 'OUTER' and prdt_nm like '%%데님%%' then 'MLB데님자켓' end                            as outer5,
       case when prdt_kind_nm = 'OUTER' and (prdt_nm like '%%바람막이%%' or prdt_nm like '%%윈드%%') then 'MLB바람막이' end as outer6,
       case when prdt_kind_nm = 'OUTER' and (prdt_nm like '%%항공%%') then 'MLB블루종' end                           as outer7,
       case when item = 'JP' and (prdt_nm like '%%베이스볼%%' or prdt_nm like '%%야구%%') then 'MLB야구점퍼' end            as outer8,
       case
           when prdt_kind_nm = 'OUTER' and
                (prdt_nm like '%%후리스%%' or prdt_nm like '%%플리스%%' or prdt_nm like '%%뽀글%%' or prdt_nm like '%%보아%%')
               then 'MLB플리스' end                                                                              as outer9,

       -- 탑
       case when item = 'WS' and prdt_nm like '%%데님%%' then 'MLB데님셔츠' end                                       as top1,
       case when item = 'MT' then 'MLB맨투맨' end                                                                as top2,
       case when item = 'BS' then 'MLB야구져지' end                                                               as top3,
       case when item = 'OP' then 'MLB원피스' end                                                                as top4,
       case when item = 'TS' then 'MLB티셔츠' end                                                                as top5,
       case when item in ('TR', 'ZT') and prdt_nm like '%%후드%%' then 'MLB후드집업' end                              as top6,
       case when item in ('HD') then 'MLB후드티' end                                                             as top7,
       case when item in ('DP') then 'MLB데님바지' end                                                            as top8,
       case when item in ('LG') then 'MLB레깅스' end                                                             as top9,
       case when item in ('DP') and prdt_nm like '%%숏%%' then 'MLB데님반바지' end                                    as top10,
       case when item in ('SM', 'SP') then 'MLB반바지' end                                                       as top11,
       case when item in ('TP', 'PT') then 'MLB트레이닝팬츠' end                                                    as top12,
       case when prdt_kind_nm = 'BOTTOM' and prdt_nm like '%%조거%%' then 'MLB트레이닝팬츠' end                         as top13
from public.di_prdt
where brand = 'M'
  and season
    > '18S';
"""

df = pd.read_sql(strSQL, con)
con.close()

df_item = df[['brand', 'season', 'partcode']]
cols = ['partcode', 'bg1',
       'bg2', 'bg3', 'bg4', 'cp0', 'cp1', 'cp2', 'p3', 'cp4', 'cp5', 'cp6',
       'cp7', 'cp8', 'cp9', 'cp10', 'cp11', 'cp12', 'cp13', 'cp14', 'cp15',
       'sh1', 'sh2', 'sh3', 'sh4', 'sh5', 'sh6', 'sh7', 'outer1', 'outer2',
       'outer3', 'outer4', 'outer5', 'outer6', 'outer7', 'outer8', 'outer9',
       'top1', 'top2', 'top3', 'top4', 'top5', 'top6', 'top7', 'top8', 'top9',
       'top10', 'top11', 'top12', 'top13']


# 품번 - 키워드 데이터 프레임 (품번 중복 허용)
df_sub = df[cols].set_index('partcode')
keyword_list = []
for row in range(len(df_sub)):
    s = df_sub.iloc[row].to_list()
    cleaned_list = [x for x in s if x != None]
    keyword_list.append(cleaned_list)
df_sub = df_sub.assign(keyword = keyword_list)
df_multi = df_sub[['keyword']]
df_multi = df_multi.reset_index()

data = []
for i in df_multi.itertuples():
    lst = i[2]
    for col2 in lst:
        data.append([i[1], col2])

df_output = pd.DataFrame(data=data, columns=df_multi.columns)
df_final = pd.merge(df_item, df_output, how='right', on='partcode')

print(df_final.head())


# 품번 - 해시태그로 연결된 키워드 데이터프레임
df_sub = df[cols].set_index('partcode')
df_sub['keywords'] = ''
keyword_list = []
for row in range(len(df_sub)):
    s = df_sub.iloc[row].to_list()
    cleaned_list = [x for x in s if x != None]
    striped_list = [x.replace(' ', '') for x in cleaned_list if x]
    keywords = '#'.join(striped_list)
    keyword_list.append(keywords)

df = pd.DataFrame(keyword_list, columns=['keywords'])
df_new = pd.concat([df_item, df], axis=1)
## 아래 줄 추가 ##
df_new = df_new[df_new['keywords'] !='']
# print(df_new)

