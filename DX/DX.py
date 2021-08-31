# 코드 구조화
import pandas as pd

# 인스타그램 주차별 소분류별 인터랙션 정량
file_path = 'C://Users/kyujin/Desktop/PROCESS/MKT/DX/DX마케팅_프로세스팀_5월 정성평가 추가 CONTENTS_LIST_DATA_200622_카라티수정.xlsx'
sheet_name = '인플루언서 별도 시트'
cols = ['중분류', '소분류', '품번', '플랫폼', 'ID/이름/채널명','업로드 날짜', '주차', '업로드 URL', '팔로워/구독자 수', '좋아요', '댓글']

df_mkt = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
df_mkt = df_mkt.iloc[:, 4:31]
df_mkt.dropna(thresh=5, inplace=True)
df_mkt.drop(df_mkt.tail(1).index, inplace=True)
df_mkt = df_mkt[cols]
df_mkt.dropna(subset=['업로드 날짜'], inplace=True)
df_mkt.dropna(subset=['주차'], inplace=True)

df_mkt['댓글'] = df_mkt['댓글'].fillna(0)
df_mkt['좋아요'] = df_mkt['좋아요'].fillna(0)
df_mkt = df_mkt.replace({'댓글': '-'}, {'댓글': 0})

df_mkt['댓글'] = pd.to_numeric(df_mkt['댓글'])
df_mkt['좋아요'] = pd.to_numeric(df_mkt['좋아요'])
df_mkt['인터랙션정량'] = df_mkt['좋아요'] + df_mkt['댓글']*5
df_insta = df_mkt[df_mkt['플랫폼']=='인스타그램']

insta_post_inter = df_insta.groupby(['소분류', '주차']).sum()['인터랙션정량'].to_frame()
insta_post_inter = insta_post_inter.reset_index()
insta_post_inter.columns = ['소분류', '주차', '인터랙션정량']

insta_post_count = df_insta.groupby(['소분류', '주차']).count()['업로드 URL'].to_frame()
insta_post_count = insta_post_count.reset_index()
insta_post_count.columns = ['소분류', '주차', '업로드 URL']

df_count = pd.merge(insta_post_inter, insta_post_count, on=['소분류','주차'], how='outer')
df_count.to_excel('DX_insta_interaction.xlsx', sheet_name = 'Sheet1')
