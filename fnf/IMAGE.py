# -*- coding: utf-8 -*-
import urllib.request
from PIL import Image

import pandas as pd
import pandas as pd
from sqlalchemy import create_engine
import cx_Oracle as co
import os
import datetime
import time
import random
import settings

download_image_root = settings.IMAGE_DOWN_ROOT


def run():
    engine = settings.postgres_engine_use()

    strSQL = """
    select *
    from {schema}.di_image
    where (brand, season, partcode, color) not in (select distinct brand, season, partcode, color
    from (select brand, season, partcode, case when color = '' then '?' else color end as color from {schema}.di_image_thumbnail)a)
    and seq = '1' and default_image = '0' and season > '16S' and brand = 'M'
    """.format(schema=settings.TO_POSTGRES_SCHEMA)

    df = pd.read_sql(strSQL, engine)
    total_cnt = df.shape[0]
    cnt = 0

    for row in range(df.shape[0]):
        brand = df.loc[row][0]
        season = df.loc[row][1]
        partcode = df.loc[row][2]
        color = df.loc[row][3]
        seq = df.loc[row][4]
        url_root = df.loc[row][6]
        url = url_root

        try:
            if color == '':
                image_new_name = brand + season + partcode + '.png'
            else:
                image_new_name = brand + season + partcode + '_' + color + '_' + str(seq) + '.png'

            urllib.request.urlretrieve(url, download_image_root + image_new_name)
            image = Image.open(download_image_root + image_new_name)
            image.thumbnail((400, 400), Image.ANTIALIAS)

            pixdata = image.load()
            width, height = image.size
            for y in range(height):
                for x in range(width):
                    if pixdata[x, y] == (255, 255, 255, 255):
                        pixdata[x, y] = (255, 255, 255, 0)

            image.save(download_image_root + image_new_name, "PNG", quality=5)

            cnt = cnt + 1
            print(cnt, '/', total_cnt)

        except:
            print('error , resume next')

    print(' *********   download image complete, start update di_image_thumbnail ***********')
    # 이미지썸네일 업데이트
    filenames = os.listdir(download_image_root)

    engine.execute("truncate table {schema}.di_image_thumbnail  ".format(schema=settings.TO_POSTGRES_SCHEMA))
    engine.execute('commit;')

    for filename in filenames:
        if len(filename) == 17:
            # full_filename = os.path.join(dirname, filename)
            brand = filename[0]
            season = filename[1:4]
            partcode = filename[4:13]
            color = ''
        else:
            brand = filename[0]
            season = filename[1:4]
            partcode = filename[4:13]
            color = filename[14:17]

        # data insert
        sql = """
            insert into {schema}.di_image_thumbnail values('{brand}','{season}','{partcode}','{color}','{filename}')
        """.format(schema=settings.TO_POSTGRES_SCHEMA, brand=brand, season=season, partcode=partcode, color=color, filename=filename)

        engine.execute(sql)
        engine.execute('commit;')

    del engine


if __name__ == '__main__':
    run()