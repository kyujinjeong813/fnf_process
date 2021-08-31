from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd
from sqlalchemy.dialects.postgresql import psycopg2
import psycopg2.extras

#################################################################################
"""화면설정"""
################################################################################

# 최대 줄 수 설정
pd.set_option('display.max_rows', 3207)
# 최대 열 수 설정
pd.set_option('display.max_column', 100)
# 표시할 가로의 길이
pd.set_option('display.width', 1000)


def postfetch(sql) -> pd.DataFrame():
    """
    postsql DB에서 fetch해오는 function
    """
    try:
        conn_string = "host='172.0.2.93' dbname ='postgres' user='postgres' password='1111'"
        conn = psycopg2.connect(conn_string)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute(sql + ";")
        result = cur.fetchall()

        postfetch_df = pd.DataFrame(result)
        postfetch_df.columns = [desc[0] for desc in cur.description]

    except:
        print("DB연결 이슈 또는 SQL에 이슈가 있음")

    finally:
        cur.close()
        conn.close()

    return postfetch_df

def postfetch_data(search_keyword) -> pd.DataFrame():
    """
    postsql DB에서 특정 sql fetch 해오는 function
    """
    sql = """select *
             from db_mkt_naver_cafe_review
             where gn_keyword = '"""+ str(search_keyword) + """'"""

    df = postfetch(sql)

    return df

if __name__ == '__main__':
    search_keyword = '캉골 버킷백'
    df = postfetch_data(search_keyword)

    lst_title = df['title'].to_list()
    lst_text = df['review_text'].to_list()

    result_lst_text = []
    for item in lst_text :
        item = item.replace('{', "")
        item = item.replace('}', "")
        item = item.replace('\"', "")
        item = item.replace('cafe', "")
        item = item.replace('naver', "")
        item = item.replace('https', "")
        item = item.replace('seller', "")
        item = item.replace('com', "")
        item = item.replace('co', "")
        item = item.replace('kr', "")
        for text in item.split(','):
            result_lst_text.append(text)

    result = ""
    for item in result_lst_text :
        result = result + " " + item

    for item in lst_title :
        result = result + " "+ item


    stopwords = set(STOPWORDS)
    stopwords.add('저도')
    stopwords.add('저두')
    stopwords.add('저도')
    stopwords.add('저도')
    stopwords.add('감사합니다')
    stopwords.add('이뻐요')
    stopwords.add('예뻐요')
    stopwords.add('진짜')
    stopwords.add('ㅎㅎ')
    stopwords.add('같아요')
    stopwords.add('저는')
    stopwords.add('제가')
    stopwords.add('진짜')
    stopwords.add('cafe naver')
    stopwords.add(' cafe naver')
    stopwords.add('cafe naver ')
    stopwords.add('co kr')
    stopwords.add('co kr')
    stopwords.add('https seller')
    stopwords.add('근데')
    stopwords.add('ㅎㅎㅎ')
    stopwords.add('ㅜㅜ')
    stopwords.add('ㅋㅋ')
    stopwords.add('너무')
    stopwords.add('지금')
    stopwords.add('작성부탁드리고')
    stopwords.add('완료시')
    stopwords.add('있어요')
    stopwords.add('이거')
    stopwords.add('혹시')
    stopwords.add('감사해요')
    stopwords.add('감사해용')
    stopwords.add('좋아요')
    stopwords.add('감사합니당')
    stopwords.add('버킷백')
    stopwords.add('주문서')
    stopwords.add('링크')
    stopwords.add('버킷')
    stopwords.add('오늘')
    stopwords.add('그쵸')
    stopwords.add('buyer')
    stopwords.add('안녕하세요')
    stopwords.add('ㅠㅠㅠ')
    stopwords.add('ㅠㅠ')
    stopwords.add('ㅋㅋㅋ')
    stopwords.add('ㅋㅋㅋㅋ')
    stopwords.add('ㅋㅋㅋㅋㅋ')
    stopwords.add('엄청')
    stopwords.add('맞아요')
    stopwords.add('네네')
    stopwords.add('이제')
    stopwords.add('있는데')
    stopwords.add('그래도')
    stopwords.add('부탁드려요')
    stopwords.add('다른')
    stopwords.add('그래서')
    stopwords.add('했는데')
    stopwords.add('가방')
    stopwords.add('다시')
    stopwords.add('계속')
    stopwords.add('요거')
    stopwords.add('이쁘네요')
    stopwords.add('예쁘네요')
    stopwords.add('완전')
    stopwords.add('많이')
    stopwords.add('그냥')
    stopwords.add('우와')
    stopwords.add('넘나')
    stopwords.add('이렇게')
    stopwords.add('정말')
    stopwords.add('역시')
    stopwords.add('후기')
    stopwords.add('가능한가요')
    stopwords.add('왔어요')
    stopwords.add('해요')
    stopwords.add('order Form')
    stopwords.add('orderForm')
    stopwords.add('지금은')
    stopwords.add('어떻게')
    stopwords.add('얼른')
    stopwords.add('가방이')
    stopwords.add('샀는데')
    stopwords.add('같이')
    stopwords.add('아직')
    stopwords.add('샀어요')


    wordcloud = WordCloud(font_path='./NanumGothic.ttf', stopwords=stopwords,background_color='white').generate(result)

    plt.figure(figsize=(22, 22))  # 이미지 사이즈 지정
    plt.imshow(wordcloud, interpolation='lanczos')  # 이미지의 부드럽기 정도
    plt.axis('off')  # x y 축 숫자 제거
    plt.show()
    plt.savefig(search_keyword)
