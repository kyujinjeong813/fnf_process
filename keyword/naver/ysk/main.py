from sqlalchemy.dialects.postgresql import psycopg2
import psycopg2.extras
import pandas as pd
import class_def as cd
import json
import urllib.request
import datetime as dt
import db_update

#################################################################################
"""화면설정"""
#################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 2000)
# 최대 열 수 설정
pd.set_option('display.max_column', 900)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)


def postfetch(sql) -> pd.DataFrame():
    """
    postsql DB에서 fetch해오는 function
    """
    try:
        conn_string = "host='172.0.2.93' dbname ='postgres' user='postgres' password='1111'"
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(sql + ";")
        result = cur.fetchall()

        postfetch_df = pd.DataFrame(result)
        postfetch_df.columns = [desc[0] for desc in cur.description]

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")
        postfetch_df = pd.DataFrame(columns=[desc[0] for desc in cur.description])

    finally:
        cur.close()
        conn.close()

    return postfetch_df


def postfetch_keyword(brand) -> pd.DataFrame():
    """
    postsql DB에서 item 기준으로 qty 정보 fetch 해오는 function
    """
    sql = """select *
             from db_mkt_naver_keyword_master
             where brand = '""" + brand + """'"""

    df = postfetch(sql)

    return df

def db_info() -> list:
    """
    :return: DB_info 접속정보(host, user, dbname, pw)로 구성된 list 반환
    """

    f = open("./DB_info.txt", 'r')
    lst_db_info = []

    while True:
        line = f.readline()
        if not line:
            break
        lst_db_info.append(line.split('\'')[1])
    f.close()

    return lst_db_info

def id_pw():
    lst_id_pw = []
    f = open("./id_pw.txt", 'r')

    while True:
        line = f.readline()
        if not line:
            break
        lst_id_pw.append(line.split('"')[1])
    f.close()
    return lst_id_pw


def data_lab_class(brand) -> dict:
    df = postfetch_keyword(brand)
    df = df.iloc[:, 8:]

    dx = cd.Search(brand)

    for i in range(len(df)):
        dx.add_group_keyword(df.iloc[i, 0])
        for j in range(1, len(df.columns)):
            dx.add_search_keyword(df.iloc[i, 0], df.iloc[i, j])

    return dx


def datalab_api(lst, startDate, endDate, timeUnit) -> dict:
    lst_id_pw = id_pw()

    client_id = lst_id_pw[0]
    client_secret = lst_id_pw[1]

    url = "https://openapi.naver.com/v1/datalab/search";

    group_dict = []
    group_dict.append({"groupName": "나이키에어맥스97", "keywords": ["나이키에어맥스97"]})

    for i in range(len(lst)) :
        group_dict.append(lst[i])

    body = {
        "startDate": startDate,
        "endDate": endDate,
        "timeUnit": timeUnit,
        "keywordGroups": group_dict
    }

    body = json.dumps(body, ensure_ascii=False)

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("Content-Type", "application/json")
    response = urllib.request.urlopen(request, data=body.encode("utf-8"))

    rescode = response.getcode()

    if (rescode == 200):
        response_body = response.read()
        json_obj = json.loads(response_body.decode('utf-8'))

        return json_obj

    else:
        print("Error Code:" + rescode)


def json_to_df(json_obj, brand) -> pd.DataFrame:
    df_json = pd.DataFrame(columns={'brand', 'keyword_repr', 'keyword', 'period', 'ratio'})
    lastrow = 0

    try :
        for i in range(len(json_obj)):
            data = json_obj['results'][i]['data']
            for j in range(len(data)):
                df_json.loc[j + lastrow, 'brand'] = brand
                df_json.loc[j + lastrow, 'keyword_repr'] = json_obj['results'][i]['title']
                df_json.loc[j + lastrow, 'keyword'] = json_obj['results'][i]['keywords']
                df_json.loc[j + lastrow, 'period'] = json_obj['results'][i]['data'][j]['period']
                df_json.loc[j + lastrow, 'ratio'] = json_obj['results'][i]['data'][j]['ratio']
                lastrow += j + 1

        df_json = df_json.reset_index().drop('index', axis='columns')
        df_json = df_json[['brand', 'keyword_repr', 'keyword', 'period', 'ratio']]

        ratio_sum = 0

        for i, row in df_json.iterrows():
            if (str(row['period'])[0:4] == '2020') & (str(row['period'])[5:7] == '01') & (row['keyword_repr'] == '나이키에어맥스97'):
                ratio_sum += row['ratio']

        df_json['search_qty'] = df_json['ratio'].apply(lambda item : int((633308 / ratio_sum) * item))
        df_json['keyword'] = df_json['keyword'].apply(lambda item : str(item))

        'check (removable)'
        print(df_json)
        return df_json

    except :
        pass

def naver_json_result(brand) :

    df_keyword = data_lab_class(brand)

    lst_for_naver = []

    for i, item in enumerate(df_keyword._keyword.keys()):
        lst_for_naver.append({"groupName": item, "keywords": list(filter(None, df_keyword._keyword[item]))})

    lst_result = [lst_for_naver[i * 4:(i + 1) * 4] for i in range((len(lst_for_naver) - 1 + 4) // 4)]

    lst_dfs = []
    for i in range(len(lst_result)):
        json_result = datalab_api(lst_result[i], startDate, endDate, period)
        lst_dfs.append(json_to_df(json_result, brand))

    df_result = pd.DataFrame()
    for i in range(len(lst_dfs)) :
        df_result = pd.concat([df_result, lst_dfs[i]])

    df_result = df_result.drop_duplicates(['keyword_repr', 'keyword', 'period'], keep='first')
    df_result = df_result.reset_index().drop('index', axis='columns')

    return df_result

if __name__ == '__main__':


    ############################################################################################################
    '''naver request basic parameter setting '''
    ############################################################################################################

    startDate = '2016-01-01'
    endDate = str(dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d"))
    period = 'date'

    ############################################################################################################
    '''naver search qty by brand'''
    ############################################################################################################

    df_mlb = naver_json_result('MLB')
    df_mlb_kids = naver_json_result('MLB KIDS')
    df_dx = naver_json_result('DX')
    df_dx_kids =  naver_json_result('DK')

    df_result = pd.concat([df_dx,df_dx_kids,df_mlb,df_mlb_kids])
    df_result = df_result.drop_duplicates(['keyword_repr', 'keyword', 'period'], keep='first')
    df_result = df_result.reset_index().drop('index', axis='columns')

    ############################################################################################################
    '''db update'''
    ############################################################################################################

    lst_db_info = db_info()
    db_update.db_insert(lst_db_info, df_result)
    db_update.keyword_week_update(lst_db_info)