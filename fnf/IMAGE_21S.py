import pandas as pd
from sqlalchemy import create_engine
import urllib
from PIL import Image
from os import listdir
from os.path import isfile, join



file_path = '//172.0.0.112/mlb/process_team/21F_CAD_STYLE_COL_previous'
file_path2 = '//172.0.0.112/mlb/process_team/21F_CAD_STYLE_COL'

png_files = [ f for f in listdir(file_path) if f.__contains__('png')]
png_files2 = [ f for f in listdir(file_path)if f.__contains__('jpg')]

print(len(png_files), len(png_files2))


base_path = '//172.0.0.112/mlb/process_team/21F_CAD_STYLE_COL/'


for img in png_files:
    new_name = img.split('.')[0] + '.jpg'
    im = Image.open(file_path + '/' +img)
    im.save(base_path+new_name)

for img in png_files2:
    im = Image.open(file_path + '/' +img)
    im.save(base_path+img)

#         urllib.request.urlretrieve(url, file_path)
#         image = Image.open(file_path)
#         # image = image.convert("RGBA")
#         size = (200, 200)
#         image.thumbnail(size, Image.ANTIALIAS)
#         pixdata = image.load()
#         width, height = image.size
#         for y in range(height):
#             for x in range(width):
#                 if pixdata[x, y] == (255, 255, 255, 255):
#                     pixdata[x, y] = (255, 255, 255, 0)
#         image.save(file_path, "PNG", quality=50)
#     except:
#         pass
#
