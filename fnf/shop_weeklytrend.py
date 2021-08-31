import pandas as pd
from sqlalchemy import create_engine
import os
import operator
import re
import nltk
# nltk.download('punkt')
from nltk import word_tokenize

engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
con = engine.connect()
strSQL = """
select *
from di_shop_weeklytrend
where brand='I' and yyyyww between '2019-32' and '2020-02'
order by yyyyww
"""

df = pd.read_sql(strSQL, con)

# ours_sale : 필수 입력 필드 / 정보는 많은데 제대로 추출이 될 지 모르겠윰 ㅠ
# req_md : 반응 좋은 제품 품번/제품명 많이 언급됨
# style_best
# style_worst
# style_reorder

# 1. FW 기간 다 합쳐서 style_best 모아서 빈도수 확인
# df['style_best'].to_csv('style_best_test.txt', index=False, header=None, sep='\t')

values = "".join(str(i) for i in df['style_best'])
values = values.replace('-', '')
values = values.replace('None', ' ')
# print(values)

# 영문 데이터 빈도수 체커
# https://velog.io/@bong2030/nltk%EB%A1%9C-%EC%98%81%EB%AC%B8-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EB%B9%88%EB%8F%84%EC%88%98-%EC%B2%B4%EC%BB%A4%EB%A5%BC-%EB%A7%8C%EB%93%A4%EC%96%B4%EB%B3%B4%EC%9E%90-%EA%B5%AD%EB%AC%B8-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EB%B9%88%EB%8F%84-%EC%B6%94%EA%B0%80

r_values = "".join(str(i) for i in df['style_reorder'])
r_values = r_values.replace('-', '')
r_values = r_values.replace('None', ' ')
# print(r_values)


# 정규표현식 통해 품번 골라내기
def get_lst(value):
    regex1 = re.compile('[a-zA-Z]+[a-zA-Z]+[0-9]+[0-9]')
    regex2 = re.compile('[a-zA-Z]+[a-zA-Z]+[a-zA-Z]+[0-9]')
    code_lst1 = regex1.findall(value)
    code_lst2 = regex2.findall(value)
    code_lst1.extend(code_lst2)
    w_count = {}
    for code in code_lst1:
        try:
            w_count[code] += 1
        except:
            w_count[code] = 1
    s_count = sorted(w_count.items(), key=operator.itemgetter(1), reverse=True)
    return s_count

s_count = get_lst(values)

item_lst = ['MT', 'TR', 'JP', 'DV', 'HD', 'TP', 'DJ', 'TS', 'SH', 'CP', 'BG']
ttl_lst = []

best_prdt_lst = []
for t in item_lst:
    lst = []
    for i in s_count:
        if t == 'TR':
            if 'TR' in i[0]:
                if 'MTR' in i[0]:
                    pass
                else:
                    lst.append(i)
        elif t == 'MT':
            if 'MT' in i[0]:
                if 'CP' in i[0]:
                    pass
                else:
                    lst.append(i)
        else:
            if t in i[0]:
                lst.append(i)
    ttl_lst.append(lst)


# 아이템별 언급 횟수 구하는 함수
def get_item_frequency(lst):
    frequency = {}
    for i in range(len(item_lst)):
        sum = 0
        for j in range(len(lst[i])):
            sum += lst[i][j][1]
        frequency[item_lst[i]] = sum
    return frequency
