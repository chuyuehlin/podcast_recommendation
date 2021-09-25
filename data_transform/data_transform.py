from elasticsearch import Elasticsearch, helpers
import csv
import glob
import json
from tqdm import tqdm
All = {}
for filename in tqdm(glob.iglob(r'/Users/chuyueh/課程/專題/spotify-podcasts-2020/*/*/*/*/*.json', recursive=True)):
	f = open(filename)
	Id = filename[-27:-5]
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
es = Elasticsearch(host = "127.0.0.1", port = 9200, timeout=60)
insert = []


with open('all.json') as f:
	f = json.load(f)
	for row in f:
		if row['episode_uri'] in All:
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
					"transcript":All[row['episode_uri']]
				}
			}	
			insert.append(tmp)
	print(len(insert))
	helpers.bulk(es, insert)


'''

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
'''
