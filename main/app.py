from flask import Flask,render_template, Response, redirect, request
import requests
from bs4 import BeautifulSoup
import sys
import urllib
from urllib.parse import urlparse
import base64
import json
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from bing_image_downloader.downloader import download, get_all_link
from googlesearch import search
import yake
import wikipediaapi
from keybert import KeyBERT

#Debug logger
import logging 
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
ch.setFormatter(formatter)
root.addHandler(ch)


app = Flask(__name__)
model = KeyBERT(model='paraphrase-MiniLM-L6-v2')
episodes_cache=dict()

database_url="http://127.0.0.1:9200/"

@app.route('/')
def home():
	return render_template('index_copy_V3.html')


@app.route('/episode/<string:episodeID>')
def episode(episodeID):
	try:
		outcome = episodes_cache[episodeID]
	except:
		outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
		outcome = outcome.json()
		outcome = outcome["_source"]
		episodes_cache.update({episodeID:outcome})

	if outcome["poster"]=="null":
		outcome["poster"]=""
	message={"poster":outcome["poster"],"episode_audio":outcome["episode_audio"],"episode_name":outcome["episode_name"],"publisher":outcome["publisher"],"episode_description":outcome["episode_description"]}
	return render_template('demo3player.html', message=message)


@app.route('/recommend/<string:episodeID>/<string:time>/')
def recommend(episodeID,time):
	try:
		outcome = episodes_cache[episodeID]
	except:
		outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
		outcome = outcome.json()
		outcome = outcome["_source"]
		episodes_cache.update({episodeID:outcome})
	
	time = int(time/60) * 60
	text = outcome["transcript"][time]

	kw_extractor = yake.KeywordExtractor(n=3, top=1)
	keywords = kw_extractor.extract_keywords(text)
	
	websites = []

	for kw in keywords:
			
		wiki_wiki = wikipediaapi.Wikipedia('en')
		wiki_page = wiki_wiki.page(kw[0])
		if wiki_page.exists():
			websites.append(wiki_page.fullurl)
		
		
		key_word = kw[0].replace(" ", "&")	
		url = 'https://api.currentsapi.services/v1/search?keywords=' + key_word + '&apiKey=jwq2zz6rcBmPByF_neecIR9GM0joS4KKfzZdYf_Oj-326HQR'
		r = requests.get(url)
		r = r.json()
		if r['status']=="ok" and len(r['news'])>0:
			websites.append(r['news'][0]['url'])
	
	result = []
	for w in websites:
		u = urlparse(w)
		domain_name = u.netloc

		reqs = requests.get(w)
		soup = BeautifulSoup(reqs.text, 'html.parser')
		title = soup.find_all('title')[0].get_text()

		result.append({"url":w,"domain_name":domain_name,"title":title})

	return {"result":result}

@app.route('/recommend_image/<string:episodeID>/<string:time>/')
def recommend_image(episodeID,time):
	#前後30秒
	# outcome = requests.get('http://54.178.59.171:9200/episodes/_doc/'+ID)
	# outcome = outcome.json()
	try:
		outcome = episodes_cache[episodeID]
	except:
		outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
		outcome = outcome.json()
		outcome = outcome["_source"]
		episodes_cache.update({episodeID:outcome})

	interval=30  #可調整
	start = int(float(time))-interval
	end = int(float(time))+interval
	if start<0:
		start=0
		end=interval*2
	start_t = str(start-(start%120))
	end_t = str(end-(end%120))
	start_fragment = outcome["transcript"][start_t]
	try:
		end_fragment = outcome["transcript"][end_t]
	except:
		end_fragment = ""
	start_fragment = start_fragment.split(" ")
	end_fragment = end_fragment.split(" ")
	text = start_fragment[int(len(start_fragment)*(start%120)/120):] + end_fragment[:int(len(end_fragment)*(end%120)/120)]
	text = " ".join(text)



    #2分鐘(fixed)
	# time=str(int(time)-(int(time)%120))
	# outcome = requests.get('http://54.178.59.171:9200/episodes/_doc/'+ID)
	# outcome = outcome.json()
	# text = outcome["_source"]["transcript"][time]


	# language = "en"
	# max_ngram_size = 5 #5 #8
	# deduplication_thresold = 0.5
	# deduplication_algo = 'levs' #levs seqm jaro
	# windowSize = 10
	# numOfKeywords = 5
	
	

	# custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
	# keywords = custom_kw_extractor.extract_keywords(text)
	keywords = model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=4) #ngram影響速度 
	links=[]
	for i in keywords:
		tmp=[]
		print(i[0],i[1])

		query_string = i[0]
		tmp.append(i[0])
		# tmp.append(paths[0][i[0]])
		tmp.append(get_all_link(query_string, limit=4,  output_dir='dataset', adult_filter_off=False, force_replace=False, timeout=60, verbose=False))  #adult可改
		print(tmp)
		links.append(tmp)
	return {"result":links} 

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
	port = 5000
	http_server = HTTPServer(WSGIContainer(app))
	logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
	http_server.listen(port)
	IOLoop.instance().start()
	app.run(host='0.0.0.0',debug=True)
