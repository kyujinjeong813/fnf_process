from inscrawler import crawler
from datetime import date
import pandas as pd
import numpy as np
from datetime import date

logging = crawler.Logging()
Crawler = crawler.InsCrawler(logging)
Crawler.login()
Crawler._dismiss_login_prompt()
Crawler._dismiss_alarm_prompt()
# Crawler.get_hashtag_results()

dic = Crawler.get_hashtag('https://www.instagram.com/p/CEQbx-Dlcbi/')
print(dic)

# 아악 더보기가 계속 안된다!!!!!!!!!!!!!! 풔기