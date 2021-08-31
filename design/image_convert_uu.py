import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import os
from PIL import Image

# 변수 설정
engine_info = 'postgresql+psycopg2://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:35430/postgres'
sql = """
    select distinct partcode, sample_no, color
    from gtm20f_lp_raw
    union all
    select distinct partcode, sample_no, color
    from gtm20f_lp_raw_kids

    """
# original_dir = os.getcwd()+'/original/'
# convert_dir = os.getcwd()+'/convert/'

original_dir = 'C:/Users/kyujin/PycharmProjects/design/test/original/'
convert_dir = 'C:/Users/kyujin/PycharmProjects/design/test/convert/'



# DB에서 sample_no, partcode, color_code 받아와서 dictionary화 (key:sample_no)
def read_db_contents(engine_info, sql):
    engine = create_engine(engine_info)
    conn = engine.connect()

    strSQL = sql

    df = pd.read_sql(strSQL, conn)
    dict = df.set_index('sample_no').T.to_dict()
    return dict


def convert_file_name(file_name, dictionary):
    file_name = file_name.replace('-', '_')
    sample_number, color_code = file_name.split('_')
    sample_number = sample_number.replace('_', '')
    color_code = color_code.replace('_', '')
    not_converted_file = []
    print('원래 파일명 : ', file_name)

    try:
        if dictionary[sample_number]:
            partcode = dictionary[sample_number]['partcode']
            new_name = partcode + '_' + color_code.split('.')[0]
            print('수정된 이름: ', new_name)

            resize_and_retype(file_name, new_name)

        else:
            print("sample number is not exited in lp : {}".format(file_name))
    except KeyError:
        print("sample_number {} not exists in DB.".format(sample_number))
        not_converted_file.append(sample_number)

    return not_converted_file

#    file_type = file_name[-3:]
def resize_and_retype(file_name, new_name):
    new_file_name = convert_dir + new_name + '.jpg'
    if "png" in file_name:
        image = Image.open(original_dir + file_name)
        pixdata = image.load()
        width, height = image.size
        ratio = get_ratio(width)
        for y in range(height):
            for x in range(width):
                if pixdata[x, y] == (255, 255, 255, 255):
                    pixdata[x, y] = (255, 255, 255, 0)

        resize_image = image.resize((int(ratio * width), int(ratio * height)))
        resize_image = resize_image.convert('RGB')
        if os.path.isfile(new_file_name):
            pass
        else:
            resize_image.save(new_file_name, quality=95)

    if "jpg" in file_name:
        image = Image.open(original_dir + file_name)
        width, height = image.size
        ratio = get_ratio(width)
        resize_image = image.resize((int(ratio * width), int(ratio * height)))
        if os.path.isfile(new_file_name):
            pass
        else:
            resize_image.save(new_file_name, quality=95)


def get_ratio(width):
    if width < 500:
        ratio = 1
    elif width < 1000:
        ratio = 0.5
    elif width < 2000:
        ratio = 0.2
    else:
        ratio = 0.1

    return ratio



if __name__ == "__main__":
    dict = read_db_contents(engine_info, sql)
    original_lst = os.listdir(original_dir)
    for file in original_lst:
        convert_file_name(file, dict)

    # convert_lst = [convert_file_name(file, dict) for file in original_lst]
