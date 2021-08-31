import pandas as pd
import numpy as np
import datetime as dt
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import os
import platform

#############################################################################################################
'''matplotlib 한글깨짐 현상 해결'''
#############################################################################################################
if platform.system() == 'Windows':
    # 윈도우인 경우
    font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
    rc('font', family=font_name)
else:
    # Mac 인 경우
    rc('font', family='AppleGothic')

plt.rcParams['axes.unicode_minus'] = False

##############################################################################################################
'''
    [가져오는 df의 table 정보]     
    brand 
    season 
    item   
    partcode 
    chnl_nm   
    make_dt    
    yymm  
    start_dt  
    sale_amt  
    sale_qty  
    sale_tag
'''
##############################################################################################################

# (1차분리) 시즌별(SS/FW Lev.) / 채널별 dataframe 분리하는 함수

def div_group(df, ssfw, *args):
    # 기본변수 선언
    str_temp = ''
    lst_chnl = []
    for item in args:
        lst_chnl.append(item)
    df_temp = pd.DataFrame()


    # 시즌 분리작업
    df['ssfw'] = df['season'].apply(lambda item: item[-1])
    df = df[df['ssfw'] == ssfw]
    df = df.drop('ssfw', axis='columns')

    # 채널 분리작업
    for item in lst_chnl:
        df_temp = df_temp.append(df[df['chnl_nm'] == item])

    if len(lst_chnl) > 1:
        for item in lst_chnl:
            str_temp = str_temp + item
        df_temp['chnl_nm'] = str_temp

    df_temp = df_temp.groupby(list(df_temp)[:5] + ['yymm', 'start_dt']).sum()[
        ['sale_amt', 'sale_qty', 'sale_tag']].reset_index()
    df = df_temp.copy()

    return df


#  아이템별 당해년도 해당 아이템 내 매출액 Percentile, Rolling 여부를 확인하는 함수
def div_yr_item(df, item):
    df['yr'] = df['season'].apply(lambda x: x[:2]) ##K## item->x
    df = df[df['item'] == item]
    df_temp_com = df[['prdt_cd', 'yr', 'partcode']].drop_duplicates()
    df_temp_com = df_temp_com.groupby(['prdt_cd', 'yr']).count().groupby(level=[0]).cumsum().reset_index()
    df_temp_com.columns = ['prdt_cd', 'yr', 'rolling']
    df_temp_com.drop('yr', axis='columns', inplace=True)

    df_temp = df.groupby(['yr', 'partcode', 'prdt_cd']).sum()['sale_amt'].reset_index().sort_values(
        by=['yr', 'sale_amt'], axis=0)

    df_temp['p0.6'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.60, interpolation='nearest'))
    df_temp['p0.65'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.65, interpolation='nearest'))
    df_temp['p0.7'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.70, interpolation='nearest'))
    df_temp['p0.75'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.75, interpolation='nearest'))
    df_temp['p0.8'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.80, interpolation='nearest'))
    df_temp['p0.85'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.85, interpolation='nearest'))
    df_temp['p0.9'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.90, interpolation='nearest'))
    df_temp['p0.95'] = df_temp.groupby(['yr'])['sale_amt'].transform(
        lambda x: x.quantile(q=0.95, interpolation='nearest'))
    df_temp = df_temp.assign(percentile=np.nan)

    for i, row in df_temp.iterrows():
        if row['sale_amt'] <= row['p0.6']:
            df_temp.loc[i, 'percentile'] = 0.6
        elif (row['sale_amt'] > row['p0.6']) & (row['sale_amt'] <= row['p0.65']):
            df_temp.loc[i, 'percentile'] = 0.65
        elif (row['sale_amt'] > row['p0.65']) & (row['sale_amt'] <= row['p0.7']):
            df_temp.loc[i, 'percentile'] = 0.7
        elif (row['sale_amt'] > row['p0.7']) & (row['sale_amt'] <= row['p0.75']):
            df_temp.loc[i, 'percentile'] = 0.75
        elif (row['sale_amt'] > row['p0.75']) & (row['sale_amt'] <= row['p0.8']):
            df_temp.loc[i, 'percentile'] = 0.8
        elif (row['sale_amt'] > row['p0.8']) & (row['sale_amt'] <= row['p0.85']):
            df_temp.loc[i, 'percentile'] = 0.85
        elif (row['sale_amt'] > row['p0.85']) & (row['sale_amt'] <= row['p0.9']):
            df_temp.loc[i, 'percentile'] = 0.9
        elif (row['sale_amt'] > row['p0.9']) & (row['sale_amt'] < row['p0.95']):
            df_temp.loc[i, 'percentile'] = 0.95
        elif row['sale_amt'] >= row['p0.95']:
            df_temp.loc[i, 'percentile'] = 1

    df_temp = pd.merge(df_temp, df_temp_com, on='prdt_cd', how='left')
    df = df_temp[['partcode', 'percentile', 'rolling', 'yr']]

    return df

#  div_style percentile 해당하는 스타일 매핑 함수
def div_style_yr(df, percentile) :
    df = df[df['percentile'] == percentile]
    if df.empty:
        df = pd.DataFrame(columns=['start_dt', 'sale_amt', 'sale_qty', 'sale_tag'])
    else:
        df = df.groupby(['start_dt']).median()[['sale_amt', 'sale_qty', 'sale_tag']].reset_index()
    return df

def last_row(df) :
    dt_last_week = dt.datetime.strftime(dt.datetime.now() - dt.timedelta(days=int(dt.datetime.today().weekday())), '%Y-%m-%d')
    if df.tail(1).iloc[0]['start_dt'] == dt_last_week:
        pass
    else:
        new_data = {'start_dt': dt_last_week, 'sale_amt': np.nan, 'sale_qty': np.nan, 'sale_tag': np.nan}
        df = df.append(new_data, ignore_index=True)
    return df

#  당해년도 해당 아이템과 Pecentile이 가장 유사한 과거 Percentile 자료 matching
def div_style(df, df_17, df_18, df_19):
    df = df.astype({'sale_qty': 'float64', 'sale_tag': 'float64'})
    percentile = round(df['percentile'].mean(),2)

    if df['yr'].apply(lambda item: int(item)).min() == 20:
        df_17 = div_style_yr(df_17, percentile)
        df_18 = div_style_yr(df_18, percentile)
        df_19 = div_style_yr(df_19, percentile)
        df = pd.concat([df[['start_dt', 'sale_amt', 'sale_qty', 'sale_tag']], df_17, df_18, df_19])
        df = df.drop_duplicates(['start_dt'], keep='last')
        df = df.sort_values(by=['start_dt'])
        df = last_row(df)
        return df

    if df['yr'].apply(lambda item: int(item)).min() == 19:
        df_17 = div_style_yr(df_17, percentile)
        df_18 = div_style_yr(df_18, percentile)
        df = pd.concat([df[['start_dt', 'sale_amt', 'sale_qty', 'sale_tag']], df_17, df_18])
        df = df.drop_duplicates(['start_dt'], keep='last')
        df = df.sort_values(by=['start_dt'])
        df = last_row(df)
        return df

    if df['yr'].apply(lambda item: int(item)).min() == 18:
        df_17 = div_style_yr(df_17, percentile)
        df = pd.concat([df[['start_dt', 'sale_amt', 'sale_qty', 'sale_tag']], df_17])
        df = df.drop_duplicates(['start_dt'], keep='last')
        df = df.sort_values(by=['start_dt'])
        df = last_row(df)
        return df

    if df['yr'].apply(lambda item: int(item)).min() == 17:
        df = df[['start_dt', 'sale_amt', 'sale_qty', 'sale_tag']]
        df = df.sort_values(by=['start_dt'])
        df = last_row(df)
        return df

def is_season(ds, lst):
    date = pd.to_datetime(ds)
    return date.month in lst

def item_season(ds, var_season):
    date = pd.to_datetime(ds)
    if var_season == 'S' :
        lst_season = [3,4,5,6,7,8]
    else :
        lst_season = [1,2,9,10,11,12]
    return date.month in lst_season

def prophet(df, var_season, item = np.nan, title = 'error') :
    print(df)
    # prophet 변수
    period = 32 # 예측기간
    changepoint_prior_scale = 0.07  # 유연성 조절 / default = 0.05, 늘리면 유연(=언더피팅 해결), 줄이면 경직(=오버피팅 해결)
    seasonality_mode = 'additive'  # 단순 Seasonality = additive, 점점 증가하는 Seasonality =  multiplicative

    df_temp = df.copy()
    df_temp['month'] = df_temp['ds'].apply(lambda item: dt.datetime.strptime(str(item).split(' ')[0], '%Y-%m-%d')).dt.month
    lst_season = sorted(list(df_temp['month'].unique()))

    if pd.isna(item) :
        df['on_season'] = df['ds'].apply(lambda item : is_season(item, lst_season))
        df['off_season'] = ~df['ds'].apply(lambda item : is_season(item, lst_season))
    else :
        df['on_season'] = df['ds'].apply(lambda item : item_season(item, var_season))
        df['off_season'] = ~df['ds'].apply(lambda item : item_season(item, var_season))

    m = Prophet(
        growth='linear',
        seasonality_mode=seasonality_mode,
        changepoint_prior_scale=changepoint_prior_scale,
        daily_seasonality=False,
        weekly_seasonality=False,
        yearly_seasonality=False,
    ).add_seasonality(
        name='monthly',
        period=30.5,
        fourier_order=12
    ).add_seasonality(
        name='yearly',
        period=365.25,
        fourier_order=10
    ).add_seasonality(
        name='quarterly',
        period=365.25 / 4,
        fourier_order=5,
        prior_scale=15
    ).add_seasonality(
        name='on_season',
        period=7,
        fourier_order=20
    ).add_seasonality(
        name='off_season',
        period=7,
        fourier_order=20
    )

    # prophet에 모델 적용
    m.fit(df)

    future = m.make_future_dataframe(periods=period, freq='W')
    if pd.isna(item) :
        future['on_season'] = future['ds'].apply(lambda item : is_season(item, lst_season))
        future['off_season'] = future['ds'].apply(lambda item : is_season(item, lst_season))
    else :
        future['on_season'] = future['ds'].apply(lambda item: item_season(item, var_season))
        future['off_season'] = future['ds'].apply(lambda item: item_season(item, var_season))
    forecast = m.predict(future)

    # prophet에 모델 보정 <-- off-season(과거 특정 월 판매 '0'인 경우, 일괄 0으로 조정)
    #                   <-- off-season(과거 특정 월 판매 'median'를 Cap으로 설정)
    #                   <--(-) 값 Handling(과거 데이터 min 값을 토대로, 그 이하로는 하락하지 않도록 구성)
    forecast['upper_gap'] = abs(forecast['yhat_upper'] - forecast['yhat'])
    forecast['lower_gap'] = abs(forecast['yhat'] - forecast['yhat_lower'])
    forecast['min'] = forecast[forecast['ds'] < df.tail(1).iloc[0]['ds']]['yhat'].min()
    forecast['off_season_max'] = df[df['off_season'] == True]['y'].median()

    lst_temp = list(df[df['off_season'] == True]['ds'].apply(lambda item: pd.to_datetime(item).month))

    for i, row in forecast.iterrows():
        if (row['ds'].month in lst_temp) & (row['ds'].year >= dt.datetime.today().year) :
            if row['yhat'] > row['off_season_max'] :
                forecast.loc[i, 'yhat'] = row['off_season_max']
                forecast.loc[i, 'yhat_upper'] = row['off_season_max'] + abs(row['upper_gap'])
                forecast.loc[i, 'yhat_lower'] = row['off_season_max'] - abs(row['lower_gap'])
        if (row['yhat'] < row['min']) & (row['ds'].year >= dt.datetime.today().year) :
            forecast.loc[i, 'yhat'] = 0
            forecast.loc[i, 'yhat_upper'] = abs(row['upper_gap'])
            forecast.loc[i, 'yhat_lower'] = -abs(row['lower_gap'])
        if (not(row['ds'].month in lst_season)) & (row['ds'].year >= dt.datetime.today().year):
            forecast.loc[i, 'yhat'] = 0
            forecast.loc[i, 'yhat_upper'] = abs(row['upper_gap'])
            forecast.loc[i, 'yhat_lower'] = -abs(row['lower_gap'])

    forecast_temp = forecast[['ds', 'yhat', 'yhat_upper', 'yhat_lower']]
    forecast_temp = forecast_temp.assign(prdt_cd = item)

    # 그래프 그리기
    fig1 = m.plot(forecast, uncertainty=True)
    plt.title(title)
    add_changepoints_to_plot(fig1.gca(), m, forecast)
    title = title + '.png'
    plt.savefig(title)
    plt.show()

    return forecast_temp


def def_excel_export(df):
    # EXCEL 출력
    filename = 'output_forecast.xlsx'
    if not os.path.exists(filename):
        with pd.ExcelWriter(filename, mode='w', engine='openpyxl') as writer:
            df.to_excel(writer, index=True)
    else:
        with pd.ExcelWriter(filename, mode='w', engine='openpyxl') as writer:
            df.to_excel(writer, index=True)