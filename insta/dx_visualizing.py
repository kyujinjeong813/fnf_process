import numpy as np
import pandas as pd
import os

base_dir = 'C:/Users/kyujin/Documents/Python Scripts/'
ex_file = 'insta_crawling.xlsx'

ex_dir = os.path.join(base_dir, ex_file)

df = pd.read_excel(ex_dir, header=None, dtype={'user_id': str, 'key_url':str, 'init_time':str,'like':np.int64, 'view':np.int64,'hashtag':str},
                     fill_na=0)
df.columns = ['user_id', 'key_url', 'init_time', 'like', 'view', 'hashtag']
df.head()

# NaN -> 0으로 변환
df.fillna(0, inplace=True)
# 좋아요 수가 있는 게시글만 사용 (동영상 제거)
df = df[df.like != 0]

# 사용자 리스트 추출
user_list = df['user_id'].unique().tolist()

# 디스커버리 해시태그 포함 : mkt 컬럼 1(true)로 표기
mask = df.iloc[:, 5].str.contains('디스커버리', na=False, regex=True)
df['mkt'] = 0
df.loc[mask,'mkt'] = 1

# 사용자별 좋아요 수 분포 확인
for user in user_list:
    df_sub = df[df['user_id'] == user]
    like_mean = df_sub['like'].mean()
    like_min = df_sub['like'].min()
    like_max = df_sub['like'].max()
    print(user, like_mean, ' / ',like_min, ' / ', like_max, '/n')

# 시간 -> 일자단위로 변환
df['init_time'] = df['init_time'].apply(lambda x: x.split('T')[0])

# user group 나눠보기 (1~3 tier)
# user id의 평균 좋아요 개수 구하기
user_like_mean = df['like'].groupby(df['user_id']).mean()
user_like_mean = pd.DataFrame(user_like_mean)
user_like_mean = user_like_mean.sort_values(['like'], ascending=[False])
user_like_mean['tier'] = pd.qcut(user_like_mean['like'], 3, labels=['3','2','1'])

user_tier_dict = user_like_mean['tier'].to_dict()
df['tier'] = df['user_id'].apply(lambda x: user_tier_dict[x])

# 시각화
import matplotlib.pyplot as plt
import seaborn as sns

# 박스플롯 그리기 함수 (사용자별 좋아요 수 분포)
def plt_boxplot(dataframe):
    plt.figure(figsize=(20,10))
    sns.boxplot(x=dataframe['user_id'], y=dataframe['like'], data=dataframe)

# 박스플롯 그리기 함수2 (사용자별, 광고유무별 좋아요 수 분포)
def plt_boxplot_mkt(dataframe):
    plt.figure(figsize=(20,10))
    sns.boxplot(x=dataframe['user_id'], y=dataframe['like'], hue=dataframe['mkt'], data=dataframe)

# 히스토그램 그리기
def hist(series):
    series.plot.hist()
    plt.show()

# 커널밀도곡선
def kde(series):
    series.plot.kde()
    plt.show()

# 히스토그램 + 선 같이
def dist(series):
    sns.distplot(series)
    plt.show()

# 히스토그램 + 선 같이 + 러그도
def dist_rug(dataframe):
    sns.distplot(dataframe['like'], rug=True)
    plt.show()

# user별 좋아요 순으로 막대그래프
def bar_like(dataframe):
    sns.barplot(x='like', y='like', hue='mkt', data=dataframe)
    plt.show()

def bar_time(dataframe):
    sns.barplot(x='init_time', y='like', hue='mkt', data=dataframe)

# 시각화는 얼추 된 것 같고, 이제 계산을 해야 한다!
# 끙.. 계산 오또케하지
