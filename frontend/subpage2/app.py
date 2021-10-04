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
episodes_cache={"2XL2UdYBBhTy6AvkItjVRO":{'show_uri': '38XNk5T3KoIbNKxQMKaMY0', 'show_name': 'Sport talks', 'show_description': 'Talks with various guests and experts about sports and life', 'publisher': 'Alex', 'language': "['en']", 'rss_link': 'https://anchor.fm/s/f98a0e4/podcast/rss', 'episode_uri': '2XL2UdYBBhTy6AvkItjVRO', 'episode_name': 'Sport Talks S01E02', 'episode_audio': 'https://anchor.fm/s/f98a0e4/podcast/play/7557830/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net%2Fstaging%2F2020-02-26%2Ff134ec2379b6d653b76c15dd9a1e82ff.m4a', 'episode_description': 'Sport talks s01e02 ', 'poster': 'https://d3t3ozftmdmh3i.cloudfront.net/production/podcast_uploaded/2516609/2516609-1571602331890-3ab1c71d8a03b.jpg', 'duration': '10.858816666666666', 'transcript': {'0': "Hey guys, welcome to my podcast today. My guest is Thomas. Thomas is reduces of I'm Thomas glad to be here. Okay. So in this podcast for gonna both be answering a couple questions just some random questions. So the first question is, what are your top three basketball players of all time you could question. Where do you say all time or just current? Yeah, well time that goes even deeper. I would have to say Michael Jordan because he's the go he's like six four nine six six wins three losses in the finals LeBron James and then Kareem Abdul-Jabbar. Hello. So sorry my mic kinda ditched shall I say so yeah. Yeah. I respect those choices. I top three would be Michael Jordan. Mmm. Second would probably be shocked. You know, Shaq. Okay insane. I got you in player. And then ", '120': "just have to go with you know King James of course. Yeah King James very very good player. Yeah guys. So yeah guys, so yeah guys. Yeah. Yeah, so next question guys. your three most favorite foods All right, so I would have to say pizza. Number one. It offers a very variety variety of choices. Ha ha that's funny. Okay. Yeah, you know pepperoni pizzas out there and it gives you may doze it gives you cheese that's vegetables Dairy protein. Ins carbohydrates? It's got it all second. I would have to go for a good old hamburger hamburger is just tastes good not much explanation for that. And then third I'm will have to say. Imma have to say vanilla ice cream So basically America's favorites so very good food. So my top three would probably be in no specific order. I'd have to say sushi. smoothies, you know nice smoothie from McDonald's pretty nice and Yeah, ", '240': "cream vanilla ice creams free nice. So yeah, I just go with that very hard choice. So I next question top three YouTubers. Wow, very good question, you know one year ago, maybe two years ago. The top of the list would be T 1 Alpha Lowell Tyler one, but he's kind of boring now. I'm sure you still doing fine through. Yeah. I just can't watch League of Legends all day Taiwan. So at the top of the list I would have to go. Huh, you know, I'm binging the seidman right now. I guess I could put them up there and then Number two. Yeah, I mean, I've been really popping off lately. So yeah sure as of October 21st, they got a video on trending very very good another actually honestly nearly tied for first. I would have to say Bros first. There are two dudes that are like bodybuilders provide very Funny content and third I would have to dedicate that slot to my boy. I be salty. He's an underrated YouTube really plays Minecraft. I be salty. He's insane. Yeah, how about you so I have to go with number one. Where's I'd residing in P. He's insane. Number two, ", '360': "not really a YouTuber but xq cow, he's he has some pretty funny content. I carried number 3 probably. Advisor advisors go and yeah. Alright, very good. So next question. top three classes at school Very good question. I would have to say in terms of in terms of academic. Like academic grades and stuff or just like how much fun you have? You can choose either one. All right, in terms of grades. I would have to go Social Justice Academy history and then Social Justice Academy English and then I would have to say AP Psychology very easy classes if you guys want to take them in terms of One would have to go. history shoe physical education, you know, that's up there and no shoot calculus Okay. Yeah, calculus super fun. I love it so much. So my top three for grade probably Social Justice Academy history. ", '480': "probably. AP human geography and cvps and number three all God Probably biomed pretty free. Yeah. I got you there most fun. Calculus. I mean, it's so much fun. I like you so much. I love doing through do so much. It's just awesome. I could honestly just do derivatives all day. Yep. Number two, probably. I'd have to say I mean, you just can't talk calculus pretty hard. I think of another one. I'd have to go with a 3pc blow another very fun class enjoyed that class and much probably. Study hall. Yeah pretty hard. But I mean respectable choices. Yep. Okay. Next question is if you could have a superpower, what would it be? I would have to go with the semi mainstream. I would want to be able to read somebody's mind or if the if the if it is a superpower, I'd like to always be right because in on these Cal quizzes and tests, I just know the right answer grades are all you need to succeed in life. Everybody knows that boom go to do. Duke boom go to Harvard boom get a scholarship to Harvard boom make trillions of dollars. "}}}

database_url="http://54.168.198.194:9200/"
#Route to stream music
# @app.route('/<string:stream_id>')
# def streammp3(stream_id):
#     res = sp.episode(stream_id,market='US')
#     print(res['audio_preview_url'])
#     print(res['description'])
#     print(res['images'][1]['url'])
                
#     return render_template('player.html', image=res['images'][1]['url'], path=res['audio_preview_url'], name=res['name'], artist=res['show']['publisher'], des=res['description'], episode_id=stream_id)

#Route to stream music
@app.route('/search/<string:query>')
def search(query):
	outcome = requests.get(database_url+'episodes/_search?q='+query)
	outcome = outcome.json()
	outcome = outcome["hits"]["hits"]
	if len(outcome)>10:
		outcome = outcome[:10]

	return outcome

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
		outcome["poster"]="data:image/jpeg;base64,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"
	message={"poster":outcome["poster"],"episode_audio":outcome["episode_audio"],"episode_name":outcome["episode_name"],"publisher":outcome["publisher"],"episode_description":outcome["episode_description"]}
	return render_template('demo3player.html', message=message)


@app.route('/recommend/<string:ID>/<string:time>/')
def recommend(ID,time):
	outcome=episodes_cache[ID]
	text = outcome["transcript"][time]

	kw_extractor = yake.KeywordExtractor(n=2, top=1)
	keywords = kw_extractor.extract_keywords(text)
	
	websites = []

	for kw in keywords:
		
		# if len(search(kw[0], num_results=1))>0:
		# 	websites.append(search(kw[0], num_results=1)[0])
		
		
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
	#前後30秒
	# outcome = requests.get('http://54.178.59.171:9200/episodes/_doc/'+ID)
	# outcome = outcome.json()
	outcome=episodes_cache[ID]
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


@app.route('/recommend_summary/<string:ID>/<string:time>/')
def recommend_summary(ID,time):
	time=str(int(time)-(int(time)%120))                         
	outcome = requests.get(database_url+'episodes/_doc/'+ID)
	outcome = outcome.json()
	text = outcome["_source"]["transcript"][time]
	# language = "en"
	# max_ngram_size = 5 #5 #8
	# deduplication_thresold = 0.5
	# deduplication_algo = 'levs' #levs seqm jaro
	# windowSize = 10
	# numOfKeywords = 5
	
	

	# custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold, dedupFunc=deduplication_algo, windowsSize=windowSize, top=numOfKeywords, features=None)
	# keywords = custom_kw_extractor.extract_keywords(text)
	keywords = model.extract_keywords(text, keyphrase_ngram_range=(1, 10), top_n=1)
	
	return {"result":keywords[0][0]} 

#launch a Tornado server with HTTPServer.
if __name__ == "__main__":
	port = 5000
	http_server = HTTPServer(WSGIContainer(app))
	logging.debug("Started Server, Kindly visit http://localhost:" + str(port))
	http_server.listen(port)
	IOLoop.instance().start()