import pymysql
import pandas as pd
import re


# DB에서 데이터 가져오기
conn=pymysql.connect(host='fnf.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com',port=3306,
                     user='readonly_prcs_01',password='fnfmysqlprcs@$',db='influencer')
c=conn.cursor()

sql = """SELECT A.MISSION_SEQ,
           A.INFL_CHANNEL_SEQ,
           B.INFL_CHANNEL_NICK,
           A.ACCEPT_FLAG,
           A.OPTION_SEQ,
           (SELECT PRODUCT
                  FROM (SELECT A.MISSION_SEQ, A.INFL_CHANNEL_SEQ, GROUP_CONCAT(B.PRODUCT_CODE SEPARATOR ',') AS PRODUCT
    FROM MISSION_DELIVERY A
    LEFT JOIN MISSION_PROD B
    ON A.MISSION_PROD_SEQ=B.MISSION_PROD_SEQ AND A.MISSION_SEQ=B.MISSION_SEQ
    WHERE A.DELIVERY_REQUEST IS NOT NULL
    GROUP BY A.MISSION_SEQ, A.INFL_CHANNEL_SEQ) AS PROD
               WHERE PROD.MISSION_SEQ=A.MISSION_SEQ AND PROD.INFL_CHANNEL_SEQ=A.INFL_CHANNEL_SEQ) AS PRODUCT,
           A.LINK,
           A.UPLOAD_DATE,
           (SELECT END_DATE FROM MISSION WHERE MISSION_SEQ=A.MISSION_SEQ) AS END_DATE,
           A.FOLLOWER_CNT,
           A.LIKE_CNT,
           A.REPLY_CNT,
           A.VIEW_CNT,
           A.CREATE_DATE,
           A.FULFILL,
           A.CONTENT_QLTY,
           A.HASHTAG_CMPLN,
           A.OPEN_GRAPH_IMG
    FROM MISSION_INFL A
             LEFT JOIN INFLUENCER_CHANNEL B
                       ON A.INFL_CHANNEL_SEQ = B.INFL_CHANNEL_SEQ
    WHERE MISSION_SEQ in ('196', '199')
    ORDER BY MISSION_SEQ
    """


result = pd.read_sql_query(sql, conn)
print(result)
result.to_csv('influencer.csv', index=False)
conn.close()

# pandas에서 점수화/등급 매기기

df = pd.read_csv('influencer.csv')
df.dropna(subset=['UPLOAD_DATE'], inplace=True)

# 1. 팔로워 수 기준 점수
def follower_cut(x):
    if x > 2000000 :
        return 50
    elif x > 1000000 :
        return 45
    elif x > 700000 :
        return 40
    elif x > 500000 :
        return 35
    elif x > 300000 :
        return 30
    elif x > 100000 :
        return 25
    elif x > 50000 :
        return 20
    elif x > 30000 :
        return 15
    elif x > 10000 :
        return 10
    else:
        return 5

df['follower_score'] = df['FOLLOWER_CNT'].apply(follower_cut)
df['interaction'] = df['LIKE_CNT'] + df['REPLY_CNT']
df['int_pct'] = df['interaction'].rank(pct=True)

def interaction_cut(x):
    if x > 0.8:
        return 20
    elif x > 0.6 :
        return 15
    elif x > 0.4 :
        return 10
    elif x > 0.2 :
        return 5
    else :
        return 1

df['interaction_score'] = df['int_pct'].apply(interaction_cut)

from datetime import datetime

df['END_DATE'] = df['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
df['UPLOAD_DATE'] = df['UPLOAD_DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))

df['due'] = df['UPLOAD_DATE']-df['END_DATE']

def upload_due(x):
    if x.days <= 0 :
        return 1
    elif x.days < 7 :
        return 0.8
    elif x.days < 14 :
        return 0.5
    else:
        return 0

df['due_score'] = df['due'].apply(upload_due)
df['hashtag_score'] = df['HASHTAG_CMPLN']*0.5
df['quality_score'] = df['CONTENT_QLTY']*0.5
df['ttl_score'] = df['quality_score'] + (df['follower_score'] + df['interaction_score'] + df['hashtag_score'])*df['due_score']

# 최종 등급 부여하는 코드
def ttl_class(x):
    if x > 90:
        return 'S'
    elif x > 80:
        return 'A'
    elif x > 50:
        return 'B'
    elif x > 20:
        return 'C'
    else:
        return 'D'

df['CLS'] = df['ttl_score'].apply(ttl_class)

df.to_csv('influencer_score.csv')
