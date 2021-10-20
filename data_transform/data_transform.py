from elasticsearch import Elasticsearch, helpers
import csv
import glob
import json
from tqdm import tqdm

##########################
# 將metadata跟逐字稿整合 #
##########################
all_transcript = {} #以每集的episodeID作為key值、內容為整集逐字稿 的dictionary
all_keywords = {} #以每集的episodeID作為key值、內容為各段keywords 的dictionary
for filename in tqdm(glob.iglob(r'/path/to/spotify-podcasts-2020/*/*/*/*/*.json', recursive=True)):
	f = open(filename)
	f = json.load(f)
	
	#逐字稿的檔名就是episodeID
	Id = filename[-27:-5]
	
	#先設0，如果偵測到某字的時間超過此段上限，會先暫存此段文字再把starttime+60重新一個段落
	starttime=0
	
	keywords = {}
	tmp='' #每段逐字稿
	transcript='' #整集逐字稿
	for word in f['results'][-1]['alternatives'][0]['words']:
		
		#收集每60秒內的文字稿
		if float(word['startTime'][:-1]) < starttime+60:
			tmp=tmp+word['word']+' '
		
		#從每段逐字稿(tmp)中抓關鍵字，並把每段逐字稿(tmp)併入整集逐字稿中
		else:
			
			#把每段逐字稿併入整集逐字稿中
			transcript=transcript+tmp+' '
			
			#從每段的文字中抓關鍵字
			#keywords[starttime] = extract(tmp)
			#待晉毅補充

			#reset tmp + set starttime to another segment
			tmp=word['word']+' '
			starttime+=60
	
	#把此集的分段關鍵字、整個逐字稿以episodeID為key值暫存起來
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

with open('/path/to/only7.json') as f:
	f = json.load(f)
	for row in f:
		if row['episode_uri'] in all_transcript:
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
					"keywords":all_keywords[row['episode_uri']]
				}
			}	
			insert.append(tmp)
	print(len(insert))
	
	#insert進去es
	helpers.bulk(es, insert)

