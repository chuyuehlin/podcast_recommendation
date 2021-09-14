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
from bing_image_downloader.downloader import download, get_all_link
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

client_id="fb5a8d1d3b6b459e942a2b45ca0ba433"
client_secret="9924f4f104ee49249a23ee02f205dc58"
redirect_uri = 'http://localhost:5000/callback'
scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control streaming user-library-read user-library-modify'

access_token = None
refresh_token = None

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

@app.route('/')
def get_token():
	f = { "response_type":"code",
			"client_id":client_id,
			"redirect_uri":redirect_uri,
			"scope":scope
		}
	url = 'https://accounts.spotify.com/authorize'
	return redirect(url + '?' + urllib.parse.urlencode(f))

@app.route('/callback')
def return_token():
	
	varify_code = request.args.get("code")
	url = 'https://accounts.spotify.com/api/token'
	grant_type = 'authorization_code'
	body = {"code": varify_code,
			"redirect_uri": redirect_uri,
			"grant_type":grant_type,
			"client_id":client_id,
			"client_secret":client_secret
			}
	
	res = requests.post(url,data = body)
	res = res.json()

	global access_token
	global refresh_token
	access_token = res["access_token"]
	refresh_token = res["refresh_token"]
	
	return 'input episode id to url'

@app.route('/refresh_token')
def refresh_token():
	
	url = 'https://accounts.spotify.com/api/token'
	grant_type = 'refresh_token'
	body = {"grant_type":grant_type,"refresh_token":refresh_token,"client_id":client_id, "client_secret":client_secret}
	
	res = requests.post(url,data = body)
	res = res.json()
	
	global access_token
	access_token = res['access_token']
	
	return 'token has refreshed'

# Initialize Flask.

#Route to stream music
@app.route('/<string:query>')
def streammp3(query):
    outcome = requests.get('http://localhost:9200/episodes/_search?q='+query)
    outcome = outcome.json()
    stream_id = outcome["hits"]["hits"][0]["_source"]["episode_uri"][16:]

    res = sp.episode(stream_id,market='US')
    print(res['audio_preview_url'])
    print(res['description'])
    print(res['images'][1]['url'])
                
    return render_template('player.html', image=res['images'][1]['url'], path=res['audio_preview_url'], name=res['name'], artist=res['show']['publisher'], des=res['description'], episode_id=stream_id, access_token=access_token)

@app.route('/recommend/<string:ID>/<string:time>/')
def recommend(ID,time):
	outcome = requests.get('http://localhost:9200/episodes/_doc/'+ID)
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

@app.route('/recommend_image/<string:ID>/<string:time>/')
def recommend_image(ID,time):
	time=str(int(time)-(int(time)%120))                         
	outcome = requests.get('http://localhost:9200/episodes/_doc/'+ID)
	outcome = outcome.json()
	text = outcome["_source"]["transcript"][time]
	language = "en"
	max_ngram_size = 5 #8
	deduplication_thresold = 0.5
	deduplication_algo = 'levs' #levs seqm jaro
	windowSize = 10
	numOfKeywords = 5
	
	

	custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
	keywords = custom_kw_extractor.extract_keywords(text)
	links=[]
	for i in keywords:
		tmp=[]
		print(i[0],i[1])

		query_string = i[0]
		tmp.append(i[0])
		# tmp.append(paths[0][i[0]])
		tmp.append(get_all_link(query_string, limit=2,  output_dir='dataset', adult_filter_off=True, force_replace=False, timeout=60, verbose=False))
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
    
