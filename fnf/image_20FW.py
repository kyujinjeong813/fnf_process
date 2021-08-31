import pandas as pd
from sqlalchemy import create_engine
import urllib
from PIL import Image

engine = create_engine('postgresql+psycopg2://postgres:1111@172.0.2.93:5432/postgres')
conn = engine.connect()

strSQL_1 = """
select partcode || '_' || color as nm ,url
from di_image a
where brand in ('M','I') and season = '20F'
and image_from = 'ONLINE' and default_image = '0'
order by 1
;"""

strSQL_2 = """
select partcode || '_po' as nm, image_nm_po
from di_prdt
where brand in ('M','I') and season = '20F'
and image_nm_po is not null
"""


df = pd.read_sql(strSQL_2, conn)

for row in range(df.shape[0]):
    partcode = df.loc[row][0]
    url_root = df.loc[row][1]
    print('Beginning file download with urllib2...')
    url = url_root
    try:
        file_path = 'C:/Users/kyujin/Desktop/PROCESS/china/' + partcode + '.png'
        urllib.request.urlretrieve(url, file_path)
        image = Image.open(file_path)
        # image = image.convert("RGBA")
        size = (800, 800)
        image.thumbnail(size, Image.ANTIALIAS)
        pixdata = image.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                if pixdata[x, y] == (255, 255, 255, 255):
                    pixdata[x, y] = (255, 255, 255, 0)
        image.save(file_path, "PNG", quality=50)
    except:
        pass
