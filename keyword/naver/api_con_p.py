import json
import urllib.request
import pandas as pd
import numpy as np
import datetime as dt


df_search = pd.read_excel("target_keyword.xlsx", sheet_name='Sheet1')
df = df_search.dropna(thresh=1).iloc[:, 0:21]
# print(df.index)



# def make_keyword_list(row):
#     row_new = row.dropna().values
#     list = ', '.join(row_new.astype(str))
#     print(list)


def pre_process(df):
    df_temp = pd.DataFrame(columns={'gp_nm', 'key_nm'})

    for i in range(len(df)):
        df_temp.loc[i] = {'gp_nm': df.iloc[i, 0], 'key_nm': list(set(df.iloc[i, 0:len(df.columns) - 1].tolist()))}

    for i in range(len(df_temp)):
        df_temp.loc[i, 'key_nm'] = [x for x in df_temp.loc[i, 'key_nm'] if str(x) != 'nan']

    df = df_temp
    return df

d = pre_process(df)
print(d)

def divide_df(df, sep) -> list:
    lst = []

    for i in range(divmod(len(df), sep)[0] + [1 if divmod(len(df), sep)[1] > 0 else 0][0]):
        df_temp = df.head(1)

        if i < (divmod(len(df), sep)[0]):
            df_temp = df_temp.append(df.loc[i * sep: (i + 1) * sep - 1])

        else:
            df_temp = df_temp.append(df[-sep:])

        df_temp = df_temp.reset_index().drop('index', axis='columns')
        lst.append(df_temp)

    return lst

def datalab_api(df, startDate, endDate, timeUnit):
    client_id = "0SD5AerrdptgLB2lnoBG"
    client_secret = "AXO5zr9o8k"
    # client_id = "EkChJKTPR6ZvGVCd_NmW"
    # client_secret = "ioJVmM1nRW"

    url = "https://openapi.naver.com/v1/datalab/search"
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

def api_con_exe(startDate, endDate, period):

    df_search = pd.read_excel("target_keyword.xlsx", sheet_name = 'Sheet1')
    df_search['key_nm'] = np.nan

    df = pre_process(df_search)
    lst = divide_df(df, 4)

    lst_result = []

    for df_item in lst :
        fetchall = datalab_api(df_item, startDate, endDate, period)
        df_result = json_to_df(fetchall)
        lst_result.append(df_result)

    return lst_result

def df_output(lst_result) :

    lst_mutiple = []

    for i in range(len(lst_result)) :
        df_temp = lst_result[i]
        multiple = df_temp.loc[0, 'ratio'] / lst_result[0].loc[0, 'ratio']
        lst_mutiple.append(multiple)

    for i in range(len(lst_result)) :
        lst_result[i]['ratio'] = lst_result[i]['ratio'].apply(lambda item : item / lst_mutiple[i])

    for i in range(len(lst_result)) :
        df = lst_result[i]
        df.loc[:len(df['period'].unique())-1] = lst_result[0].loc[:len(df['period'].unique())-1]

    df_result = pd.DataFrame(columns={'title', 'keyword', 'period', 'ratio'})

    for df in lst_result :
        df_result = df_result.append(df)

    df_result['keyword'] = df_result['keyword'].apply(lambda item : str(item))
    df_result = df_result.drop_duplicates(['title', 'keyword', 'period'], keep='first')

    return df_result
