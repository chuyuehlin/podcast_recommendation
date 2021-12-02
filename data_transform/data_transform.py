from elasticsearch import Elasticsearch, helpers
import csv
import glob
import json
from tqdm import tqdm
import spacy
from spacy.matcher import Matcher
from keybert import KeyBERT


##########################
# 將metadata跟逐字稿整合 #
##########################
all_transcript = {} #以每集的episodeID作為key值、內容為整集逐字稿 的dictionary
all_captions = {}
LEN = 0
for filename in tqdm(glob.iglob(r'/Users/chuyueh/課程/專題/spotify-podcasts-2020/*/7/*/*/*.json', recursive=True)):
	f = open(filename)
	f = json.load(f)
	
	#逐字稿的檔名就是episodeID
	Id = filename[-27:-5]
	
	#先設0，如果偵測到某字的時間超過此段上限，會先暫存此段文字再把starttime+60重新一個段落
	starttime=0
	
	tmp='' #每段逐字稿
	whole_trans='' #整集逐字稿
	transcript={} #整集跟每段的逐字稿
	
	captions = []
	cap_tmp=''
	start_of_sentence = -1
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
						
			#reset tmp + set starttime to another segment
			tmp=word['word']+' '
			starttime+=60
		
		if start_of_sentence == -1:
			start_of_sentence = word['startTime'][:-1]
		cap_tmp = cap_tmp+word['word']+' '
		if '.' in word['word'] or '?' in word['word'] or '!' in word['word'] or ',' in word['word']:
			captions.append([start_of_sentence,cap_tmp])
			start_of_sentence = -1
			cap_tmp=''
	#整集逐字稿放進dict裡，transcript["all"]是整集逐字稿，transcript[<某個秒數>]為分段逐字稿
	#transcript["all"] = whole_trans
	
	#把此集的逐字稿以episodeID為key值暫存起來
	all_transcript[Id] = transcript
	all_captions[Id] = captions
	
	
print('done')

##########################
# 格式調整後輸入es       #
##########################

# Create the elasticsearch client.
es = Elasticsearch(['https://s1uunigu33:w76fgn8dce@birch-68438726.us-east-1.bonsaisearch.net/'], timeout=60)

#因為要用bulk方式insert進去，因此會先把每集資料先放進list
insert = []

with open('/Users/chuyueh/課程/專題/json/recommend.json') as recon:
	recon = json.load(recon)

	with open('/Users/chuyueh/課程/專題/json/segmented_keywords.json') as seg_key:
		seg_key = json.load(seg_key)
		for k in seg_key:
			for T in seg_key[k]:
				seg_key[k][T] = [i[0]for i in seg_key[k][T]]

		with open('/Users/chuyueh/課程/專題/json/all_keywords.json') as key_f:
			key_f = json.load(key_f)
			for k in seg_key:
				seg_key[k]['all'] = key_f[k]

			#summarization 的 json file
			with open('/Users/chuyueh/課程/專題/json/abs_7.json') as abs_f:
				abs_f = json.load(abs_f)

				#metadata 的 json file
				with open('/Users/chuyueh/課程/專題/json/only7.json') as f:
					f = json.load(f)

					for row in f:
						
						#確認這筆episode有相對應的逐字稿
						if row['episode_uri'] in all_transcript and row['episode_uri'] in abs_f and row['episode_uri'] in key_f:
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
									#"captions":all_captions[row['episode_uri']],
									"keywords":seg_key[row['episode_uri']],
									"summarization":abs_f[row['episode_uri']],
									"recommendation":recon[row['episode_uri']],									
								}
							}	
							insert.append(tmp)
					print(len(insert))
					
					#insert進去es
					helpers.bulk(es, insert)
