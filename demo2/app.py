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
	f = { "response_type":"code","client_id":client_id,"redirect_uri":redirect_uri,"scope":scope}
	url = 'https://accounts.spotify.com/authorize'
	return redirect(url + '?' + urllib.parse.urlencode(f))

@app.route('/callback')
def return_token():
	
	varify_code = request.args.get("code")
	url = 'https://accounts.spotify.com/api/token'
	grant_type = 'authorization_code'
	body = {"code": varify_code,"redirect_uri": redirect_uri,"grant_type":grant_type,"client_id":client_id, "client_secret":client_secret}
	
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
@app.route('/<string:stream_id>')
def streammp3(stream_id):
    res = sp.episode(stream_id,market='US')
    print(res['audio_preview_url'])
    print(res['description'])
    print(res['images'][1]['url'])
                
    return render_template('player.html', image=res['images'][1]['url'], path=res['audio_preview_url'], name=res['name'], artist=res['show']['publisher'], des=res['description'], episode_id=stream_id, access_token=access_token)

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
    
