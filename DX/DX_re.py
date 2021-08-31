# 코드 구조화
import pandas as pd

# 마케팅 데이터 가공
file_path = 'C://Users/kyujin/Desktop/PROCESS/MKT/DX/6월_DX마케팅_프로세스팀_인플루언서_CONTENTS LIST_DATA_200702.xlsx'
sheet_name = '인플루언서 별도 시트'
cols = ['중분류', '소분류', '품번', '플랫폼', '진행업체', '진행비용(\)','제품비용(\)',
        'ID/이름/채널명','업로드 날짜', '주차', '업로드 URL', '팔로워/구독자 수', '좋아요', '댓글', '업로드일정','해시태그','퀄리티']

df_mkt = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
df_mkt = df_mkt.iloc[:, 4:31]
df_mkt.dropna(thresh=15, inplace=True)
df_mkt.drop(df_mkt.tail(1).index, inplace=True)
df_mkt = df_mkt[cols]

df_insta = df_mkt[df_mkt['플랫폼']=='인스타그램']
df_insta['인터랙션총량'] = df_insta['좋아요'] + df_insta['댓글']*5
df_insta.dropna(subset=['해시태그','퀄리티'], inplace=True)

df_insta['인터랙션비중'] = df_insta['인터랙션총량']/df_insta['팔로워/구독자 수']
df_insta['정성평가'] = (df_insta['업로드일정']*2 + df_insta['해시태그']*10 + df_insta['퀄리티']*10)/20
columns = list(df_insta.columns)
columns = ['중분류', '소분류', '품번', '플랫폼', '진행업체', '진행비용(\)','제품비용(\)',
           'ID/이름/채널명', '업로드 날짜', '주차', '업로드 URL',
       '팔로워/구독자 수', '좋아요', '댓글', '업로드일정', '해시태그', '퀄리티', '인터랙션총량', '인터랙션비중',
       '정성평가', '인터랙션총량_2.5', '인터랙션비중_2.5', '정량평가rank', '정성평가rank']

df_ttl = pd.DataFrame(columns=columns)

item_list = list(set(df_insta['소분류']))

for i in range(len(item_list)):
    df_sub = df_insta[df_insta['소분류']==item_list[i]]
    df_sub['인터랙션총량_2.5'] = df_sub['인터랙션총량'].rank(pct=True)*2.5
    df_sub['인터랙션비중_2.5'] = df_sub['인터랙션비중'].rank(pct=True)*2.5
    df_sub['정량평가'] = df_sub['인터랙션총량_2.5'] + df_sub['인터랙션비중_2.5']
    df_sub['정량평가rank'] = 1 - (df_sub['인터랙션비중_2.5'] + df_sub['인터랙션총량_2.5']).rank(pct=True)
    df_sub['정성평가rank'] = 1 - df_sub['정성평가'].rank(pct=True)
    df_ttl = df_ttl.append(df_sub)

df_ttl.loc[df_ttl['정량평가rank'] <=0.1, '정량등급'] = 'S'
df_ttl.loc[(df_ttl['정량평가rank'] <=0.3)&(df_ttl['정량평가rank'] >0.1), '정량등급'] = 'A'
df_ttl.loc[(df_ttl['정량평가rank'] <=0.7)&(df_ttl['정량평가rank'] >0.3), '정량등급'] = 'B'
df_ttl.loc[df_ttl['정량평가rank'] >0.7, '정량등급'] = 'C'
df_ttl.loc[df_ttl['정성평가rank'] <=0.1, '정성등급'] = 'S'
df_ttl.loc[(df_ttl['정성평가rank'] <=0.3)&(df_ttl['정성평가rank'] >0.1), '정성등급'] = 'A'
df_ttl.loc[(df_ttl['정성평가rank'] <=0.7)&(df_ttl['정성평가rank'] >0.3), '정성등급'] = 'B'
df_ttl.loc[df_ttl['정성평가rank'] >0.7, '정성등급'] = 'C'
df_ttl = df_ttl.rename({'소분류':'제품'}, axis='columns')

file_path = 'C://Users/kyujin/Desktop/PROCESS/MKT/DX/6월_DX마케팅_프로세스팀_인플루언서_CONTENTS LIST_DATA_200702.xlsx'
sheet_name = '인플루언서 별도 시트'
cols = ['중분류', '소분류', '품번', '플랫폼', '진행업체', '진행비용(\)','제품비용(\)',
        'ID/이름/채널명','업로드 날짜', '주차', '업로드 URL', '팔로워/구독자 수', '좋아요', '댓글', '공유,저장']
df_cpi = pd.read_excel(file_path, sheet_name=sheet_name, header=2)
df_cpi = df_cpi.iloc[:, 4:31]
df_cpi.dropna(thresh=5, inplace=True)
df_cpi.drop(df_cpi.tail(1).index, inplace=True)
df_cpi = df_cpi[cols]
df_cpi['총비용'] = df_cpi['진행비용(\)']+df_cpi['제품비용(\)']
df_cpi['댓글'] = df_cpi['댓글'].fillna(0)
df_cpi['좋아요'] = df_cpi['좋아요'].fillna(0)
df_cpi['공유,저장'] = df_cpi['공유,저장'].fillna(0)
df_cpi = df_cpi.replace({'댓글': '-'}, {'댓글': 0})

df_cpi['좋아요'] = pd.to_numeric(df_cpi['좋아요'])
df_cpi['댓글'] = pd.to_numeric(df_cpi['댓글'])
df_cpi['공유,저장'] = pd.to_numeric(df_cpi['공유,저장'])

df_cpi['인터랙션'] = df_cpi['좋아요'] + df_cpi['댓글']*5 + df_cpi['공유,저장']

with pd.ExcelWriter('DX_influence.xlsx') as writer:
    df_ttl.to_excel(writer, sheet_name='INSTA')
    df_cpi.to_excel(writer, sheet_name='CPI')