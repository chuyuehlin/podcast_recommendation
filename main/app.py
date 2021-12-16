from flask import Flask,render_template, Response, redirect, request
import requests
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
from keybert import KeyBERT
import spacy
from spacy.matcher import Matcher
import pke
#Debug logger
import logging
import os
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter( '%(asctime)s - %(name)s - %(levelname)s - %(message)s' )
ch.setFormatter(formatter)
root.addHandler(ch)


app = Flask(__name__)
model = KeyBERT(model=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','paraphrase-MiniLM-L6-v2'))
nlp = spacy.load('en_core_web_trf')
patterns = [
	[{"DEP": "compound","OP": "*"}, {"POS": "NOUN"}],
	[{"DEP": "compound","OP": "*"}, {"POS": "PROPN"}],

	]
matcher = Matcher(nlp.vocab)
matcher.add("NOUN", [patterns[0]])
matcher.add("PROPN", [patterns[1]])
episodes_cache=dict()

database_url='https://s1uunigu33:w76fgn8dce@birch-68438726.us-east-1.bonsaisearch.net/'
database_url_captions="https://syndo6884b:dr0szlm9v7@ivy-475518791.us-east-1.bonsaisearch.net/"

@app.route('/')
def home():
	return render_template('index_copy_V3.html')

@app.route('/episode/<string:episodeID>/caption/<int:num>')
def episode_caption(episodeID,num):
	try:
		outcome = episodes_cache[episodeID]
	except:
		outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
		outcome = outcome.json()
		outcome = outcome["_source"]
		episodes_cache.update({episodeID:outcome})

	captions = requests.get(database_url_captions+'captions/_doc/'+episodeID)
	captions = captions.json()
	captions = captions["_source"]
	captions = captions["captions"]

	tmp = dict()
	for i in captions:
		if(float(i[0])/60>=num and float(i[0])/60<num+1):
			tmp.update({i[0]:i[1]})

	return tmp

@app.route('/episode/<string:episodeID>')
def episode(episodeID):
	try:
		outcome = episodes_cache[episodeID]
	except:
		outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
		outcome = outcome.json()
		outcome = outcome["_source"]
		episodes_cache.update({episodeID:outcome})

	captions = requests.get(database_url_captions+'captions/_doc/'+episodeID)
	captions = captions.json()
	captions = captions["_source"]

	if outcome["poster"]=="null":
		outcome["poster"]=""
		
	message = { "poster":outcome["poster"],
				"episode_audio":outcome["episode_audio"],
				"episode_name":outcome["episode_name"],
				"publisher":outcome["publisher"],
				"episode_description":outcome["episode_description"],
				"recommendation":outcome["recommendation"],
				"captions":captions["captions"]
			}
	return render_template('demo3player.html', message=message)

@app.route('/recommend_image/<string:episodeID>/<string:time>/')
def recommend_image(episodeID,time):
	outcome=episodes_cache[episodeID]
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
	keywords=[]
	extractor = pke.unsupervised.SingleRank()
	extractor.load_document(text, language='en')
	extractor.candidate_selection()
	extractor.candidate_weighting(window=5)
	doc = nlp(text)
	keywords = keywords+ list(set([(ee.text.lower(),0) for ee in doc.ents if ee.label_ == 'PERSON' or ee.label_ == 'ORG' or ee.label_ == 'GPE']))
	keywords = keywords+ extractor.get_n_best(n=4)
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
	app.run(debug=True)
