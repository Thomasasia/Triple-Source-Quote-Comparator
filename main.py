import gensim
import numpy as np
from statistics import mean
def avg_sentence_vector(words, model, num_features, index2word_set):
    #function to average all words vectors in a given paragraph
    featureVec = np.zeros((num_features,), dtype="float32")
    nwords = 0

    for word in words:
        if word in index2word_set:
            nwords = nwords+1
            featureVec = np.add(featureVec, model[word])

    if nwords>0:
        featureVec = np.divide(featureVec, nwords)
    return featureVec

cullwords = ["and","the","an","on","so","for","our"]

import csv
from sklearn.metrics.pairwise import cosine_similarity
from gensim.test.utils import common_texts
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim import corpora, models, similarities

sentences = []
initial = True
with open("hatespeech.csv") as file:
    reader = csv.reader(file,delimiter=',')
    for row in reader:
        if(initial):
            initial = False
            continue
        if(int(row[2]) + int(row[3]) >= int(row[4])):
            sentences.append(row[6])


sentences = [text.split() for text in sentences]

dictionary = corpora.Dictionary(sentences)

feat_c=len(dictionary.token2id)
corpus=[dictionary.doc2bow(text) for text in sentences]

model = models.TfidfModel(corpus)


tweet = "Arizona hearings on live right now on @OANN. Such total corruption. So sad for our country!".split()
tweet2 = []
cull = 0
for i in tweet:
    if i in cullwords:
        cull+=1
    else:
        tweet2.append(i)


vec = dictionary.doc2bow(tweet)
index = similarities.SparseMatrixSimilarity(model[corpus],num_features=feat_c)

sim = index[model[vec]]

print(mean(sim))
