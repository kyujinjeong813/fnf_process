import pandas as pd

base_path = 'C:/Users/kyujin/Desktop/PROCESS/MKT/viral_data/'

# NAVER : blog, cafe, news

def csv_to_df(file_name): #file_name = 'mlb모노그램_blog_2020_08_12.csv'
    file_path = base_path + file_name
    df = pd.read_csv(file_path)
    return df

def get_keyword_chnl(file_name):
    keyword = str(file_name).split('_')[0]
    chnl = str(file_name).split('_')[1]
    return keyword, chnl

def get_columns(chnl):
    if chnl == 'blog':
        cols = ['author', 'title', 'url', 'date', 'issue_date', 'body']
    elif chnl == 'cafe':
        cols = ['author', 'title', 'url', 'date', 'issue_date', 'contents']
    elif chnl == 'news':
        cols = ['author', 'title', 'url', 'date', 'issue_date', 'contents']
    elif chnl == 'post':
        cols = ['author', 'title', 'url', 'date', 'issue_date', 'contents', 'view_count']
    return cols

def str_to_datetime(df, chnl):
    if chnl == 'post':
        df['issue_date'] = df['issue_date'].apply(lambda x : x[:-1])
        df['issue_date'] = pd.to_datetime(df['issue_date'], format='%Y-%m-%d', errors='ignore')
    else:
        df['issue_date'] = pd.to_datetime(df['issue_date'], format='%Y-%m-%d', errors='ignore')
    return df

def get_year_and_week(df):
    df['year'] = df['issue_date'].dt.year
    df['month'] = df['issue_date'].dt.month
    df['week_num'] = df['issue_date'].dt.weekofyear
    df.loc[(df['week_num'] == 1) & (df['month'] == 12), 'year'] = df['year'] + 1
    df['key'] = df[['year', 'week_num']].astype(str).apply(lambda x: '_'.join(x), axis=1)
    return df

# key값을 기준으로 group count [url]
def get_week_url_count(df, chnl):
    df_count = df.groupby(df['key']).count()['url'].to_frame()
    df_count = df_count.reset_index()
    df_count.columns = ['key', chnl+'_cnt']
    return df_count

# key값을 기준으로 group sum [view_count]
def get_week_view_count(df, chnl='post'):
    df_sum = df.groupby(df['key']).sum()['view_count'].to_frame()
    df_sum = df_sum.reset_index()
    df_sum.columns = ['key', chnl+'_sum']
    return df_sum

# Youtube >> 저장형식 csv로 바꿔서 필요 없을 듯
# def excel_to_df(file_name):
#     file_path = base_path + file_name
#     df = pd.read_excel(file_path)
#     df = df.iloc[:, 1:-1]
#     df.rename(columns={'title':'title', 'post_date':'issue_date', 'view':'view_count', 'user':'author', 'follower':'follower', 'url':'url'}, inplace=True)
#     return df

# ----------------------------------- 네이버 ------------------------------------

file_name = 'mlb모노그램_blog_2020_08_12.csv'

def preprocessing(file_name):
    keyword, chnl = get_keyword_chnl(file_name)
    cols = get_columns(chnl)
    df = csv_to_df(file_name)
    df = df[cols]
    str_to_datetime(df, chnl)
    get_year_and_week(df)
    df_count = get_week_url_count(df, chnl)
    if chnl == 'post':
        df_sum = get_week_view_count(df)
        df_count = df_count.merge(df_sum, on='key')
    return df, df_count

# 이런 식으로 실행!
df, df_count = preprocessing(file_name)

# 음.. 한단계 더 나아가서
# 키워드가 같고 채널이 다른 파일들 가쥬와서 하나로 합치기
# 검색량도 합치기
# 매출도 합치기
# 그래프를 소ㅑ아

