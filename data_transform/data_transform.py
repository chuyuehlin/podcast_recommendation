from elasticsearch import Elasticsearch, helpers
import csv
import glob
import json
from tqdm import tqdm
import spacy
from spacy.matcher import Matcher
from keybert import KeyBERT

#下載pretrained model指令 >> python -m spacy download en_core_web_trf 

##########################
#   載入並設定model參數   #
##########################
nlp = spacy.load('en_core_web_trf') #load spacy pretrained model 
patterns = [
    [{"DEP": "compound","OP": "*"}, {"POS": "NOUN"}],
    [{"DEP": "compound","OP": "*"}, {"POS": "PROPN"}],

    ]
matcher = Matcher(nlp.vocab)
matcher.add("NOUN", [patterns[0]])
matcher.add("PROPN", [patterns[1]])
model = KeyBERT(model='paraphrase-MiniLM-L6-v2') #load keybert pretrained model 


##########################
# 將metadata跟逐字稿整合 #
##########################
all_transcript = {} #以每集的episodeID作為key值、內容為整集逐字稿 的dictionary
all_keywords = {} #以每集的episodeID作為key值、內容為各段keywords 的dictionary
for filename in tqdm(glob.iglob(r'/path/to/spotify-podcasts-2020/*/7/*/*/*.json', recursive=True)):
	f = open(filename)
	f = json.load(f)
	
	#逐字稿的檔名就是episodeID
	Id = filename[-27:-5]
	
	#先設0，如果偵測到某字的時間超過此段上限，會先暫存此段文字再把starttime+60重新一個段落
	starttime=0
	
	keywords = {}
	tmp='' #每段逐字稿
	whole_trans='' #整集逐字稿
	transcript={} #整集跟每段的逐字稿
	for word in f['results'][-1]['alternatives'][0]['words']:
		
		#收集每60秒內的文字稿
		if float(word['startTime'][:-1]) < starttime+60:
			tmp=tmp+word['word']+' '
		
		#從每段逐字稿(tmp)中抓關鍵字，並把每段逐字稿(tmp)併入整集逐字稿中
		else:
			
			#把每段逐字稿併入整集逐字稿中
			whole_trans=whole_trans+tmp+' '

			#每段逐字稿放進dict裡
			transcript[starttime] = tmp
					
			#從每段的文字中抓關鍵字
			doc = nlp(tmp)
			matches = matcher(doc) 
			extracted_keywords=[]  #此段文字稿抓到的所有關鍵字(keyBERT extraction + spaCy NER)
	
			result=[]
			for match_id, start, end in matches:
			    span = doc[start:end]
			    result.append(span.text.lower())
			result=list(set(result))  #用PoS 取得複合名詞/名詞片語...
			extracted_keywords = extracted_keywords + model.extract_keywords(tmp, candidates=result, top_n=10)  #用bert抓關鍵字
			extracted_keywords = extracted_keywords + list(set([(ee.text.lower(),0) for ee in doc.ents if ee.label_ == 'PERSON' or ee.label_ == 'ORG' or ee.label_ == 'GPE'])) #用spacy NER抓命名實體 

			keywords[starttime] = extracted_keywords
			
			
			#reset tmp + set starttime to another segment
			tmp=word['word']+' '
			starttime+=60
	
	#整集逐字稿放進dict裡，transcript["all"]是整集逐字稿，transcript[<某個秒數>]為分段逐字稿
	transcript["all"] = whole_trans
	
	#把此集的分段關鍵字、逐字稿以episodeID為key值暫存起來
	all_keywords[Id] = keywords
	all_transcript[Id] = transcript

print('done')

##########################
# 格式調整後輸入es       #
##########################

# Create the elasticsearch client.
es = Elasticsearch(host = "127.0.0.1", port = 9200, timeout=60)

#因為要用bulk方式insert進去，因此會先把每集資料先放進list
insert = []

#summarization 的 json file
with open('/path/to/abs_7.json') as abs_f:
	abs_f = json.load(abs_f)

	#metadata 的 json file
	with open('/path/to/only7.json') as f:
		f = json.load(f)

		for row in f:
			
			#確認這筆episode有相對應的逐字稿
			if row['episode_uri'] in all_transcript and row['episode_uri'] in abs_f:
				tmp={
					"_index": "episodes",
					"_op_type": "index",
					"_id": row['episode_uri'],
					"_source": {
						"show_uri":row["show_uri"],
						"show_name":row["show_name"],
						"show_description":row["show_description"],
						"publisher":row["publisher"],
						"language":row["language"],
						"episode_uri":row["episode_uri"],	
						"episode_name":row["episode_name"],
						"episode_audio":row['episode_audio'],
						"episode_description":row["episode_description"],
						"poster":row["poster"],
						"duration":row["duration"],	
						"transcript":all_transcript[row['episode_uri']],
						"keywords":all_keywords[row['episode_uri']],
						"summarization":abs_f[row['episode_uri']]
					}
				}	
				insert.append(tmp)
		print(len(insert))
		
		#insert進去es
		helpers.bulk(es, insert)
