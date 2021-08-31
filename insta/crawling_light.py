from inscrawler import crawler
import pandas as pd
import time
from datetime import date, datetime

# 해시태그 검색어 기반 인플루언서 글 수집
workout_hashtags = ['운동', '운동하는여자', '운동하는남자', '운동하는직장인', '운동', '운동스타그램', '운동영상', '헬스타그램',
            '홈트', '홈트레이닝','홈트하는여자', '피트니스', '피트니스모델']

logging = crawler.Logging()
Crawler = crawler.InsCrawler(logging)

for tag in workout_hashtags:
    dict = Crawler.get_postsnum_by_tag(tag)
    print(dict)
