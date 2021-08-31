import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine


def db_insert(lst_db_info, df):
    """
    :param lst_db_info: postgre DB 접속정보(host, user, dbname, pw)
    :param df: DB에 입력할 최종 Dataframe
    "https://www.fun-coding.org/mysql_advanced2.html"
    """

    # DB Input format 정리
    df.columns = ['brand', 'keyword_repr', 'keyword', 'period', 'ratio', 'search_qty']
    df.dropna(inplace=True)

    # Get a database connection
    engine = create_engine("postgresql://"+lst_db_info[2]+":"+lst_db_info[3]+"@"+lst_db_info[0]+":5432/"+lst_db_info[1])
    conn = engine.connect()

    df.to_sql(name = 'db_mkt_naver_keyword_trend',
                  con = engine,
                  schema ='public',
                  if_exists= 'replace',
                  index = False,
                  dtype = {
                      'brand': sqlalchemy.types.VARCHAR(50),
                      'keyword_repr' : sqlalchemy.types.VARCHAR(255),
                      'keyword': sqlalchemy.types.VARCHAR(1000),
                      'period' : sqlalchemy.types.TIMESTAMP,
                      'ratio' : sqlalchemy.types.Float(precision=5),
                      'search_qty' : sqlalchemy.types.Float(precision=5)
                  }
                 )

    conn.close()


def db_weekly_insert(lst_db_info, sql):
    """
    :param lst_db_info: postgre DB 접속정보(host, user, dbname, pw)
    :param df: DB에 입력할 최종 Dataframe
    :param table: DB 입력할 table
    :param dict_table_info: DB 입력 table 구성
    """

    # Get a database connection
    engine = create_engine(
        "postgresql://" + lst_db_info[2] + ":" + lst_db_info[3] + "@" + lst_db_info[0] + ":5432/" + lst_db_info[1])
    conn = engine.connect()

    conn.execute(sql)
    conn.execute("commit;")
    conn.close()


def keyword_week_update(lst_db_info):

    tot_sql ="""truncate table public.db_mkt_naver_keyword_trend_w;
insert into public.db_mkt_naver_keyword_trend_w
with summary as (
    select date(date_trunc('week', period::timestamp))                      as period,
           brand,
           keyword_repr,
           keyword,
           ratio,
           search_qty
    from public.db_mkt_naver_keyword_trend
)
select to_char(period, 'YYYYMMDD') as period,
       brand,
       keyword_repr,
       keyword,
       sum(ratio) as ratio,
       sum(search_qty) as search_qty
from summary
group by period, brand, keyword_repr, keyword;"""

    db_weekly_insert(lst_db_info, tot_sql)

    print("===========weekly_update_complete===========")