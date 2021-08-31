import xlsxwriter
import pandas as pd
from sqlalchemy import create_engine
from urllib import request
from PIL import Image
import time
from io import BytesIO

# DB 정보 가져와서 데이터프레임화
engine = create_engine('postgresql://postgres:fnf##)^2020!@fnf-process.ch4iazthcd1k.ap-northeast-2.rds.amazonaws.com:5432/postgres')
conn = engine.connect()

strSQL = """
select *
from mlb.gtm20f_lp_raw
;"""

df = pd.read_sql(strSQL, conn)
cols = df.columns
new_cols = cols.insert(4, 'sample_info')
new_cols = new_cols.insert(5, 'image')
df['sample_info'] = ''
df['image'] = ''
df_new = df[new_cols]
df_new['sample_info'] = df_new['sample_no'] + '_' + df_new['color']
file_info = df_new['sample_info'].tolist()

row_count = df.shape[0] #머리글 제외한 열 수
column_count = df.shape[1]

base = "https://static-dashff.fnf.co.kr/dashff/static/gtm/sketch/"
# URL_LIST = []
# for p in file_info:
#     url = base + p + '.jpg'
#     URL_LIST.append(url)
#
# for url in URL_LIST:
#     try:
#         start=time.time()
#         res = request.urlopen(url).read()
#         print(time.time() - start)
#         img = Image.open(BytesIO(res))
#     except:
#         pass

writer = pd.ExcelWriter('exel_image.xlsx', engine='xlsxwriter')
df_new.to_excel(writer, sheet_name='Sheet1')
workbook = writer.book
worksheet = writer.sheets['Sheet1']
worksheet.set_default_row(50)
image_col = 4

# p = 'M21FHD002_50CRS'
# url = base + p + '.jpg'

from io import BytesIO

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

p = 'M21FJP011_43BGS'
url = base + p + '.jpg'
print(url)
try:
    image_data = BytesIO(urlopen(url).read())
    pil_image = Image.open(image_data)
    pil_image = pil_image.resize((20,20))
    pil_image.save('sample.jpg', format='JPEG')
    # image_data.resize(50,50)
    # image = image_data.resize((200, 200), Image.ANTIALIAS)
    worksheet.insert_image('A1', pil_image)
    # worksheet.insert_image('A1', url, {'image_data' :img})
    # worksheet.insert_image('A1', url, {'image_data' :image_data})
except:
    print("집에가고싶엉")
# for i in range(row_count):
#     start = time.time()
#     p = df_new.iloc[i,image_col]
#     url = base + p + '.jpg'
#     print(url)
#     try:
#         image_data = BytesIO(urlopen(url).read())
#         image = image_data.resize((200, 200), Image.ANTIALIAS)
#         worksheet.insert_image('G'+str(i+1), url, {'image_data': image_data})
# #         worksheet.insert_image(i+1, image_col+2, url, {'image_data':image_data}, {'x_scale': 0.12, 'y_scale': 0.12})
#         print(p + "이미지가 업로드되었습니다.")
#     except:
#         print(p + "이미지가 없습니다.")

#         start = time.time()
#         res = request.urlopen(url).read()
#         img = Image.open(BytesIO(res))
#         worksheet.insert_image(i+1, image_col+2, img,{'x_scale':0.12,'y_scale':0.12})
#         print(time.time() - start)
#     except:
#         pass
workbook.close()


