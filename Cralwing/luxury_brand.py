import os


"""
일의 순서
1. 브랜드별 진행
2. 홈페이지 접속
3. 캡춰 > 스크롤 다운 > 캡춰 (~마지막 페이지까지)
4. 이미지 하나로 합치기 (3에서 높이 연산 필요) 
ㄴ화면마다 위아래 제외해야 하는 높이 달라짐...ㅠ낑
5. 공유폴더 저장 (이미지명 : 브랜드+주차)

os.mkdir(path, exist_ok=True)

+ 추가로
다른 페이지들 수집도 가능해야 ...

_ 의미가 없는 것 ㄱ탕 ㅠㅠㅠㅠㅠ

"""
from browser import Browser



class LuxuryBrandCrawler(Browser):

    base_dir = '//172.0.0.112/mlb/process_team/luxury_brand/'
    brand_url = {'gucci': 'http://gucci.com',
                 'prada': 'https://www.prada.com/kr/ko.html',
                 'dior': 'https://www.dior.com/ko_kr',
                 'louisvuitton': 'https://kr.louisvuitton.com/',
                 'burberry': 'https://kr.burberry.com/'}

    def __init__(self, has_screen=False):
        super(LuxuryBrandCrawler, self).__init__()
        self.browser = Browser(has_screen)
        self.page_height = 0

