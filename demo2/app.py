from flask import Flask,render_template, Response, redirect, request
import requests
import sys
import urllib
import base64
import json
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

from googlesearch import search
import yake
import wikipediaapi

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

#Route to stream music
@app.route('/search/<string:query>')
def search(query):
	outcome = requests.get('http://54.168.215.20:9200/episodes/_search?q='+query)
	outcome = outcome.json()
	outcome = outcome["hits"]["hits"]
	if len(outcome)>10:
		outcome = outcome[:10]

	return outcome

@app.route('/episode/<string:episodeID>')
def episode(episodeID):
	outcome = requests.get('http://54.168.215.20:9200/episodes/_doc/'+episodeID)
	outcome = outcome.json()
	outcome = outcome["_source"]
	return outcome


@app.route('/recommend/<string:ID>/<string:time>/')
def recommend(ID,time):
	outcome = requests.get('http://54.168.215.20:9200/episodes/_doc/'+ID)
	outcome = outcome.json()
	text = outcome["_source"]["transcript"][time]
	
	kw_extractor = yake.KeywordExtractor(n=2, top=1)
	keywords = kw_extractor.extract_keywords(text)
	
	websites = []

	for kw in keywords:
		
		if len(search(kw[0], num_results=1))>0:
			websites.append(search(kw[0], num_results=1)[0])
		
		
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
		
		return {"result":websites}

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
	port = 5000
	http_server = HTTPServer(WSGIContainer(app))
	logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
	http_server.listen(port)
	IOLoop.instance().start()
	
