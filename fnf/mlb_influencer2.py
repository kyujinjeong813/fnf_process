import pymysql
import pandas as pd
import re
from datetime import datetime


# DB 연결
conn = pymysql.connect(host='fnf.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com', port=3306,
                           user='readonly_prcs_01', password='fnfmysqlprcs@$', db='influencer')
c = conn.cursor()


cols = ['MISSION_SEQ', 'INFL_CHANNEL_NICK', 'LINK', 'UPLOAD_DATE', 'END_DATE',
            'FOLLOWER_CNT', 'follower_score', 'LIKE_CNT', 'REPLY_CNT', 'CONTENT_QLTY', 'HASHTAG_CMPLN',
            'interaction', 'interaction_score', 'due', 'due_score', 'hashtag_score',
            'quality_score', 'ttl_score', 'CLS']

# 쿼리문
def sql(i):
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
        WHERE MISSION_SEQ ='{}'
        ORDER BY MISSION_SEQ
        """.format(i)
    return sql

# 점수화하는 기본 함수
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


def upload_due(x):
    if x.days <= 0 :
        return 1
    elif x.days < 7 :
        return 0.8
    elif x.days < 14 :
        return 0.5
    else:
        return 0


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


def calculate_score(df, cols):
    df.dropna(subset=['UPLOAD_DATE'], inplace=True)
    print(df)
    df_sub = df[df['CONTENT_QLTY']>0]
    print(df_sub)
    df_sub['follower_score'] = df_sub['FOLLOWER_CNT'].apply(follower_cut)
    df_sub['interaction'] = df_sub['LIKE_CNT'] + df_sub['REPLY_CNT']
    df_sub['int_pct'] = df_sub['interaction'].rank(pct=True)
    df_sub['interaction_score'] = df_sub['int_pct'].apply(interaction_cut)
    # df_sub['END_DATE'] = df_sub['END_DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    # df_sub['UPLOAD_DATE'] = df_sub['UPLOAD_DATE'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    df_sub['due'] = df_sub['UPLOAD_DATE'] - df_sub['END_DATE']
    df_sub['due_score'] = df_sub['due'].apply(upload_due)
    df_sub['hashtag_score'] = df_sub['HASHTAG_CMPLN'] * 0.5
    df_sub['quality_score'] = df_sub['CONTENT_QLTY'] * 0.5
    df_sub['ttl_score'] = df_sub['quality_score'] + (df_sub['follower_score'] + df_sub['interaction_score'] + df_sub['hashtag_score']) * df_sub[
        'due_score']
    df_sub['CLS'] = df_sub['ttl_score'].apply(ttl_class)
    df_result = df_sub[cols]
    return df_result


# 미션별로 데이터 받아서 점수평가
mission_list = [212, 200, 199, 196, 191, 183, 182, 177, 176, 142, 140]

df_result = pd.DataFrame(columns=cols)
for i in mission_list:
    Query = sql(i)
    df = pd.read_sql_query(Query, conn)
    df_sub = calculate_score(df, cols)
    df_result = df_sub.append(df_result)

print(df_result)
df_result.to_csv('influencer_score_ttl.csv', index=False)
conn.close()

