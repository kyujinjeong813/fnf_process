from collections import namedtuple
from gensim.models import doc2vec
from konlpy.tag import Okt
import multiprocessing
from pprint import pprint

okt = Okt()

def read_data(filename):
    with open(filename, 'r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
    return data

def tokenize(doc):
    return ['/'.join(t) for t in okt.pos(doc, norm=True, stem=True)]

# doc2vec parameters
cores = multiprocessing.cpu_count()

vector_size = 300
window_size= 15
word_min_count = 2
sampling_threashold = 1e-5
negative_size = 5
train_epoch = 100
dm = 1
worker_count = cores

train_data = read_data('data/ratings_train.txt')

train_docs = [(tokenize(row[1]), row[2]) for row in train_data[1:]]

TaggedDocument = namedtuple('TaggedDocument', 'words tags')
tagged_train_docs = [TaggedDocument(d, [c]) for d,c in train_docs]

doc_vectorizer = doc2vec.Doc2Vec(size=300, alpha=0.025, min_alpha=0.025, seed=1234)
doc_vectorizer.build_vocal(tagged_train_docs)

for epoch in range(10):
    doc_vectorizer.train(tagged_train_docs, total_examples=doc_vectorizer.corpus_count, epochs=doc_vectorizer.iter)
    doc_vectorizer.alpha -= 0.002
    doc_vectorizer.min_alpha = doc_vectorizer.alpha

doc_vectorizer.save('model/doc2vec.model')

pprint(doc_vectorizer.most_similar('공포/Noun'))
pprint(doc_vectorizer.similarity('공포/Noun', 'ㅋㅋ/KoreanParticle'))
