"""
설치 모듈
awscli
pandas
psycorpg2
sqlalchemy
xlsx2html
"""
import json
from sqlalchemy import create_engine
ENGINE_POSTGRES_AWS = "postgresql+psycopg2://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:35430/postgres"
ENGINE_POSTGRES_REDSHIFT = "postgresql+psycopg2://prcs:Prcs1514@prd-dt-redshift.conhugwtudej.ap-northeast-2.redshift.amazonaws.com:5439/fnf"
ENGINE_POSTGRES_POSTGRES_LOCAL = "postgresql+psycopg2://process:process@172.0.2.93:5432/postgres"

def create_engine_redshift():
    engine = create_engine(ENGINE_POSTGRES_REDSHIFT)
    return engine

def create_engine_aws():
    engine = create_engine(ENGINE_POSTGRES_AWS)
    return engine

def create_engine_postgres_local():
    engine = create_engine(ENGINE_POSTGRES_POSTGRES_LOCAL)
    return engine


import pandas as pd
import openpyxl
import pandasql as ps
# from settings import create_engine_redshift
import datetime
import os

def write_log(message):
    s = str(datetime.datetime.now()) + message
    isfile = os.path.isfile(r'./log.txt')
    if isfile:
        with open(r'./log.txt', 'a') as f:  # 파일이 있으면 마지막 행에 추가
            f.write(str(s) + '\n')
    else:
        with open(r'./log.txt', 'w') as f:  # 파일이 없으면 log.txt 생성하고 입력
            f.write(str(s) + '\n')

engine = create_engine_redshift()
# 엑셀 경로
excel_file_root = './excel/brand_keyword_list.xlsx'
df_mlb = pd.read_excel(excel_file_root, sheet_name='MLB')
df_mk = pd.read_excel(excel_file_root, sheet_name='MK')
df_dx = pd.read_excel(excel_file_root, sheet_name='DX')
df_dk = pd.read_excel(excel_file_root, sheet_name='DK')
df_sa = pd.read_excel(excel_file_root, sheet_name='SA')
df_dv = pd.read_excel(excel_file_root, sheet_name='DV')
df_co = pd.read_excel(excel_file_root, sheet_name='CO')
df = pd.concat([df_mlb, df_mk, df_dx, df_dk, df_sa, df_dv, df_co])
sql = """
select brand as brd_cd,
       adult_kids,
       Category            as cat_nm,
       Sub_Category        as sub_cat_nm,
       Sub_Category_detail as sub_cat_dtl_nm,
       검색어구분               as kwd_type,
       구분                  as comp_type,
       브랜드                 as comp_brd_nm,
       키워드                 as kwd_nm
from df
"""
df = pd.DataFrame(ps.sqldf(sql))
write_log('finish df')
engine.execute("truncate table prcs.db_srch_kwd_naver_mst; commit;")
df.to_sql(name='db_srch_kwd_naver_mst',
          con=engine,
          index=False,
          schema='prcs',
          if_exists='append',
          method='multi',
          chunksize=1000,
          )
write_log('finish  inserting to redshift')
