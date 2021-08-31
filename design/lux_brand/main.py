import os
import pandas as pd
import urllib
from PIL import Image

path_dir = '//172.0.0.112/mlb/process_team/luxury_brand/gucci/2020-08-31/main/'
file_list = os.listdir(path_dir)
file_list = sorted(file_list)
print(file_list)
base_width = 1920
base_height = 1080
f_count = len(file_list)
header_nav = 65
crop_height = base_height - 65
height = crop_height * f_count + header_nav
merged = Image.new('RGBA', (base_width, height), (255, 255, 255, 255))

h = 0
for i, f in enumerate(file_list):
    if 'png' in f:
        image = Image.open(path_dir + f)
        if '0' in f:
            crop_img = image
            merged.paste(crop_img, (0, h))
            h += base_height
            print(h)
        else:
            crop_img = image.crop((0, header_nav, 1920, crop_height))
            merged.paste(crop_img, (0, h))
            h += crop_height
            print(h)

merged.save(path_dir + 'mainpage.png')

# luxury_brand_main db 만들어서 이미지 업로드
# 컬럼은 : 브랜드, 주차, 이미지경로