"""
기본적인 기능 함수 모음

1. 이미지 관련
    스크린샷
    이미지 저장
    이미지 합치기
2. 파일 변환
3. 데이터 형변환
4. 랜덤 슬립
5. validate !
"""

import random
from functools import wraps
from time import sleep

def randomized_sleep(average=1):
    _min, _max = average * 1 / 2, average * 3 / 2
    sleep(random.uniform(_min, _max))

# 스크린샷 저장
def screenshot(browser, main_page=True):
    pass

# 이미지 합치기
def merge_image():
    pass

# 합치기 전 스크린샷 이미지 삭제
def del_file():
    pass

