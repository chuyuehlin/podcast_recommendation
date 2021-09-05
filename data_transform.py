from elasticsearch import Elasticsearch, helpers
import csv
import glob
import json
from tqdm import tqdm

#逐字稿整理
All = {}
for filename in tqdm(glob.iglob(r'/Users/chuyueh/課程/專題/spotify-podcasts-2020/*/*/*/*/*.json', recursive=True)):
	Id = filename[-27:-5]
	f = open(filename)
	f = json.load(f)
	out = {}
	starttime=0
	tmp=''
	for word in f['results'][-1]['alternatives'][0]['words']:
		if float(word['startTime'][:-1]) < starttime+120:
			tmp=tmp+word['word']+' '
		else:
			out[str(starttime)]=tmp
			tmp=''
			starttime+=120
	All[Id] = out

print('done')


# Create the elasticsearch client.
es = Elasticsearch(host = "localhost", port = 9200)
insert = []
# Open csv file and bulk upload
with open('metadata.tsv') as f:
	reader = csv.reader(f, delimiter='\t')
	
	for row in tqdm(reader):
		if row[6][16:] in All:
			insert.append({
				"_index": "episodes",
				"_op_type": "index",
				"_id": row[6][16:],
				"_source": {
					"show_uri":row[0],
					"show_name":row[1],
					"show_description":row[2],
					"publisher":row[3],
					"language":row[4],
					"rss_link":row[5],	
					"episode_uri":row[6],	
					"episode_name":row[7],	
					"episode_description":row[8],	
					"duration":row[9],	
					"show_filename_prefix":row[10],	
					"episode_filename_prefix":row[11],
					"transcript":All[row[6][16:]]
				}
			})
	helpers.bulk(es, insert)
