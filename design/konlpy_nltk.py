from konlpy.tag import Okt
import nltk

# nltk.download('stopwords')

okt = Okt()

print(okt.morphs(u'한글형태소분석기 테스트 중입니다'))
print(okt.nouns(u'한글형태소분석기 테스트 중입니다!'))
print(okt.pos(u'한글형태소분석기 테스트 중입니다.'))

def read_data(filename):
    with open(filename, 'r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
    return data

def tokenize(doc):
    return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]

def term_exist(doc): # selected_words 뭐지
    return {'exist({})'.format(word): (word in set(doc)) for word in selected_words}

# 데이터 읽어들이기
train_data = read_data('ratings_train.txt')
test_data = read_data('ratings_test.txt')

# 제대로 읽어왔는지 확인
print(len(train_data))
print(len(train_data[0]))
print(len(test_data))
print(len(test_data[0]))

#### 미리 의미없는 조사, 온점 등은 제거하고 돌려야겠으뮤

# 형태소 분류
train_docs = [(tokenize(row[1]), row[2]) for row in train_data[1:]]
test_docs = [(tokenize(row[1]), row[2]) for row in test_data[1:]]

# print(train_docs)
tokens = [t for d in train_docs for t in d[0]]
print(len(tokens))

text = nltk.Text(tokens, name='NMSC')
print(text.vocab().most_common(10))

text.collocations()

selected_words = [f[0] for f in text.vocab().most_common(2000)]
train_docs = train_docs[:10000]
train_xy = [(term_exist(d), c) for d,c in train_docs]
test_xy = [(term_exist(d), c) for d,c in train_docs]

classifier = nltk.NaiveBayesClassifier.train(train_xy)
print(nltk.classify.accuracy(classifier, test_xy))
# 결과 겁나 구림......ㅎ


classifier.show_most_informative_features(10)