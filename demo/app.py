from flask import Flask,render_template, Response
import sys
# Tornado web server
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="fb5a8d1d3b6b459e942a2b45ca0ba433",
                                                           client_secret="9924f4f104ee49249a23ee02f205dc58"))




#Debug logger
import logging 
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)




# Initialize Flask.
app = Flask(__name__)

#Route to stream music
@app.route('/<string:stream_id>')
def streammp3(stream_id):
    res = sp.episode(stream_id,market='US')
    print(res['audio_preview_url'])
    print(res['description'])
    print(res['images'][1]['url'])
                
    return render_template('player.html', image=res['images'][1]['url'], path=res['audio_preview_url'], name=res['name'], artist=res['show']['publisher'], des=res['description'])

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
    port = 5000
    http_server = HTTPServer(WSGIContainer(app))
    logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
    http_server.listen(port)
    IOLoop.instance().start()
    
