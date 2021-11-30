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

database_url="https://syndo6884b:dr0szlm9v7@ivy-475518791.us-east-1.bonsaisearch.net/"

@app.route('/')
def home():
	return render_template('index_copy_V3.html')

@app.route('/episode/<string:episodeID>')
def episode(episodeID):
	outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
	outcome = outcome.json()
	outcome = outcome["_source"]

	if outcome["poster"]=="null":
		outcome["poster"]=""
	message={"poster":outcome["poster"],"episode_audio":outcome["episode_audio"],"episode_name":outcome["episode_name"],"publisher":outcome["publisher"],"episode_description":outcome["episode_description"],"recommendation":outcome["recommendation"]}
	return render_template('demo3player.html', message=message)

@app.route('/recommend_image/<string:episodeID>/<string:time>/')
def recommend_image(episodeID,time):
	outcome = requests.get(database_url+'episodes/_doc/'+episodeID)
	outcome = outcome.json()
	outcome = outcome["_source"]

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
	app.run(debug=True)
