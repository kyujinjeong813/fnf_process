import json
import urllib.request
import pandas as pd
import numpy as np


def pre_process(df) -> pd.DataFrame:
    df_temp = pd.DataFrame(columns={'gp_nm', 'key_nm'})

    for i in range(len(df)):
        df_temp.loc[i] = {'gp_nm': df.iloc[i, 0], 'key_nm': list(set(df.iloc[i, 0:len(df.columns) - 1].tolist()))}

    for i in range(len(df_temp)):
        df_temp.loc[i, 'key_nm'] = [x for x in df_temp.loc[i, 'key_nm'] if str(x) != 'nan']

    for i in range(len(df_temp)):
        df_temp.loc[i, 'key_nm'] = list(filter(None, df_temp.loc[i, 'key_nm']))
        if df_temp.loc[i, 'gp_nm'] == np.nan :
            df_temp = df_temp.drop(i)

    for i in range(len(df_temp)):
        if len(df_temp.loc[i, 'key_nm']) == 0 :
            df_temp.loc[i, 'key_nm'] = [df_temp.loc[i, 'gp_nm']]

    df = df_temp

    return df


"""
    input : preprocessing된 df를 네이버 키워드 검색이 가능한 5개로 분절
    output : 5개씩 분절된 dataframe을 포함하는 List
"""


def divide_df(df, sep) -> list:
    lst = []

    for i in range(divmod(len(df), sep)[0] + [1 if divmod(len(df), sep)[1] > 0 else 0][0]):
        df_temp = df.head(1)

        if i < (divmod(len(df), sep)[0]):
            df_temp = df_temp.append(df.loc[i * sep: (i + 1) * sep - 1])

        else:
            df_temp = df_temp.append(df[-sep:])

        df_temp = df_temp.reset_index().drop('index', axis = 'columns')
        lst.append(df_temp)

    return lst


"""
    참고) http://blog.daum.net/geoscience/1405
"""

def datalab_api(df, startDate, endDate, timeUnit) -> dict:
    client_id = "0SD5AerrdptgLB2lnoBG"
    client_secret = "AXO5zr9o8k"
    # client_id = "EkChJKTPR6ZvGVCd_NmW"
    # client_secret = "ioJVmM1nRW"

    url = "https://openapi.naver.com/v1/datalab/search";
    print(df)
    body = {
        "startDate": startDate,
        "endDate": endDate,
        "timeUnit": timeUnit,
        "keywordGroups":
            [{"groupName": df.loc[0, 'gp_nm'], "keywords": df.loc[0, 'key_nm']},
             {"groupName": df.loc[1, 'gp_nm'], "keywords": df.loc[1, 'key_nm']},
             {"groupName": df.loc[2, 'gp_nm'], "keywords": df.loc[2, 'key_nm']},
             {"groupName": df.loc[3, 'gp_nm'], "keywords": df.loc[3, 'key_nm']},
             {"groupName": df.loc[4, 'gp_nm'], "keywords": df.loc[4, 'key_nm']},
             ],
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

    else:
        print("Error Code:" + rescode)

    return json_obj


def json_to_df(json_obj) -> pd.DataFrame:
    df_json = pd.DataFrame(columns={'title', 'keyword', 'period', 'ratio'})
    lastrow = 0

    for i in range(len(json_obj)+1):
        data = json_obj['results'][i]['data']
        for j in range(len(data)):
            df_json.loc[j + lastrow, 'title'] = json_obj['results'][i]['title']
            df_json.loc[j + lastrow, 'keyword'] = json_obj['results'][i]['keywords']
            df_json.loc[j + lastrow, 'period'] = json_obj['results'][i]['data'][j]['period']
            df_json.loc[j + lastrow, 'ratio'] = json_obj['results'][i]['data'][j]['ratio']
            lastrow += j + 1

    df_json = df_json.reset_index().drop('index', axis='columns')
    df_json = df_json[['title', 'keyword', 'period', 'ratio']]

    return df_json