import gensim
import numpy
from numpy import dot
from numpy.linalg import norm
import json
import string
from tqdm import tqdm
import operator
import copy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
model = gensim.models.KeyedVectors.load_word2vec_format('/Users/chuyueh/Downloads/lexvec.enwiki+newscrawl.300d.W+C.pos.vectors', binary=False)

#把一大段文字，先抓出每個字的vector後加總，最後回傳整段文字的vector
def text_vec(txt):
	vectors = [model[w] for w in txt if w in model]
	if(len(vectors)>1):
		vector = vectors[0]
		for v in vectors[1:]:
			vector=vector + v
	elif(len(vectors)>0):
		vector = vectors[0]
	else:
		vector = numpy.array([0]*300)
	return vector

#計算一段文字的字數
def word_count(text):
	word_list = text.split()
	return len(word_list)

#抓出episode的description，在呼叫text_vec生出vector，在把vector放進episode的資訊裡
def append_vec(D):
	word_tokens = word_tokenize(D['episode_description'])
	#filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
	filtered_sentence = [w for w in word_tokens]
	D['vector'] = text_vec(filtered_sentence)
	return D

#開檔
a = open('only7.json','r')
a = json.load(a)

#建一個dictionary暫存，讓之後輸出檔案的時候查找比較快
a_dict = dict()
for i in a:
	a_dict[ i['episode_uri'] ] = copy.deepcopy(i)

#把標點符號去除
for d in a:
	for punc in string.punctuation:
		d['episode_description'] = d['episode_description'].replace(punc, '')

#先計算每個字出現在各集的頻率，再把最常出現的字加進stop words
D = dict()
for d in a:
	word = d['episode_description'].split()
	
	#看這集出現哪些字
	tmp = []
	for w in word:
		#print(w)
		w = w.lower()
		if w not in tmp:
			tmp.append(w)
	
	#把這些字出現的次數+1
	for w in tmp:
		if w in D:
			D[w]+=1
		else:
			D[w]=1

#D存每個字出現在幾集裡面，如果常常出現的話把該字視為stopword
stop_words = set([d for d in D if D[d]>len(a)*0.01]+['instagram','facebook','twitter','email','youtube'])
#print(stop_words)

#build up vector for each episode
a = list(map(append_vec, a))

#計算各集之間的相似度
output = dict()
for i in tqdm(a):
	score = dict()
	for j in a:
		#如果是同show則不會被推薦，不計算相似度
		if(i['show_uri']!=j['show_uri'] and i['episode_uri']!=j['episode_uri']):
			score[j['episode_uri']] = dot(i['vector'],j['vector'])/(norm(i['vector'])*norm(j['vector']))
	
	#前五相關的會輸出
	output[i['episode_uri']]=[]
	for k in range(5):
		key = max(score.items(), key=operator.itemgetter(1))[0]
		score.pop(key)
		output[i['episode_uri']].append(a_dict[key])

#輸出
with open('recommend.json','w') as o:
	json.dump(output,o)
