from function import *
import datetime

def function_set(brand, startDate, endDate, timeUnit, df_keyword_set, last_row=False, i=0):
    keyword_list = df_to_dict(df_keyword_set, last_row, i)
    json_obj = api_con(keyword_list, startDate, endDate, timeUnit)
    search_df = json_to_df(json_obj, brand)
    db_insert(search_df, brand)


def get_search_count(brand, startDate, endDate, timeUnit):
    df = get_keywords_from_db(brand)
    df_keyword_set = make_keyword_list(df)
    num, rem = get_iteration_number(df)

    for i in range(num):
        function_set(brand, startDate, endDate, timeUnit, df_keyword_set, i=i)

    last_row = rem
    function_set(brand, startDate, endDate, timeUnit, df_keyword_set, last_row=last_row)

    print("----------{}'s data update completed------------".format(brand))

if __name__ == '__main__':

    print("----------- start ", datetime.datetime.now(), " ----------")

    brands = ['DK', 'DX', 'MLB']
    # brands = ['DX']
    # brands = ['MLB KIDS']
    startDate = '2018-01-01'
    endDate = str(datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"))
    timeUnit = 'date'

    for brand in brands:
        print(":::::: {} start :::::: ".format(brand))
        print(datetime.datetime.now())
        db_refresh(brand)
        get_search_count(brand, startDate, endDate, timeUnit)
        db_week_update(brand)

    print("----------- end ", datetime.datetime.now(), " ----------")

