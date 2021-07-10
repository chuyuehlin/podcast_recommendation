from flask import Flask, redirect
import json
import requests
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)

@app.route('/')
def index():
	return 'y'

@app.route('/<string:episode_id>')
def listen(episode_id):
	
	headers = CaseInsensitiveDict()
	headers["Authorization"] = "Bearer "+'BQAoczi19eyQJ3gnNnhWZeOWHiQ2BQJumS5wH_edyqQtJ3nFaQD1214ai8H6PUk5noCuK-73bUCODX6Rg4bTEu7NLDvQI6A7FEZ9rhKFGPiikwBQb9deW4KtvRZDXGWJNQ4sgpXWvvr3Sj0sBg'
	result = requests.get('https://api.spotify.com/v1/episodes/'+episode_id, headers = headers)
	result=result.json()

	return '<video controls="" autoplay="" name="media"><source src="'+result["audio_preview_url"]+'" type="audio/mpeg"></video>'
		

if __name__ == '__main__':
	app.run(debug=True)
