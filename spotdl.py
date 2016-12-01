#!/bin/python

from bs4 import BeautifulSoup
import mechanize
import pafy
import os
import sys
import spotipy
import eyed3
#import spotipy.util as util

#print(sys.path[0])
os.chdir(sys.path[0] + '/')

if not os.path.exists("Music"):
	os.makedirs("Music")
open('Music/list.txt', 'a').close()

spotify = spotipy.Spotify()

print('')

def loadMechanize():
	global br
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [("User-agent","Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13")]

def searchYT(number):
	#print(URL)
	items = br.open(URL)
	#print(items)
	items = items.read()
	#print(items)
	zoom1 = items.find('yt-uix-tile-link')
	zoom2 = items.find('yt-uix-tile-link', zoom1+1)
	zoom3 = items.find('yt-uix-tile-link', zoom2+1)
	part = items[zoom1-100: zoom2]
	items_parse = BeautifulSoup(part, "html.parser")

	#items_parse = soup(items, "html.parser")
	first_result = items_parse.find(attrs={'class':'yt-uix-tile-link'})['href']

	full_link = "youtube.com" + first_result
	#print(full_link)
	global video
	video = pafy.new(full_link)
	global title
	title = ((video.title).replace("\\", "_").replace("/", "_").replace(":", "_").replace("*", "_").replace("?", "_").replace('"', "_").replace("<", "_").replace(">", "_").replace("|", "_").replace(" ", "_")).encode('utf-8')
	if not number == None:
		print(str(number) + '. ' + (video.title).encode("utf-8"))
	else:
		print(video.title).encode("utf-8")

def checkExists(islist):
	if os.path.exists("Music/" + title + ".m4a.temp"):
		os.remove("Music/" + title + ".m4a.temp")
	if os.path.exists("Music/" + title + ".mp3"):
		audiofile = eyed3.load("Music/" + title + '.mp3')
		if isSpotify() and not audiofile.tag.title == content['name']:
			os.remove("Music/" + title + '.mp3')
		elif islist:
			trimSong()
			return True
		else:
			prompt = raw_input('Song with same name has already been downloaded.. re-download? (y/n/play): ')
			if prompt == "y":
				os.remove("Music/" + title + ".mp3")
				download = 1
			elif prompt =="play":
				if not os.name == 'nt':
					os.system('mplayer "' + 'Music/' + title + '.mp3"')
				else:
					print('Playing ' + title + '.mp3')
					os.system('start ' + 'Music/' + title + '.mp3')
				return True
			else:
				return True
	return False

def getLyrics():
	if not title == '':
		if song == '':
			link = 'https://duckduckgo.com/html/?q=' + title.replace(' ', '+') + '+musixmatch'
		else:
			link = 'https://duckduckgo.com/html/?q=' + song.replace(' ', '+') + '+musixmatch'
		loadMechanize()
		page = br.open(link)
		page = page.read()
		soup = BeautifulSoup(page, 'html.parser')
		link = soup.find('a', {'class':'result__url'})['href']
		page = br.open(link).read()
		soup = BeautifulSoup(page, 'html.parser')
		for x in soup.find_all('p', {'class':'mxm-lyrics__content'}):
			print(x.get_text()).encode('utf-8')
		br.close()
	else:
		print('No log to read from..')

def fixSong():
	print 'Fixing meta-tags..'
	audiofile = eyed3.load("Music/" + title + '.mp3')
	audiofile.tag.artist = content['artists'][0]['name']
	audiofile.tag.album = content['album']['name']
	audiofile.tag.title = content['name']
	br.retrieve(content['album']['images'][0]['url'], 'Music/last_albumart.jpg')
	bla = open("Music/last_albumart.jpg","rb").read()
	audiofile.tag.images.set(3,bla,"image/jpeg")
	audiofile.tag.save()

def playSong():
	if not title == '':
		if not os.name == 'nt':
			os.system('mplayer "' + 'Music/' + title + '.mp3"')
		else:
			print('Playing ' + title + '.mp3')
			os.system('start ' + 'Music/' + title + '.mp3')


def convertSong():
	print('Converting ' + title + '.m4a to mp3..')
	if not os.name == 'nt':
		os.system('avconv -loglevel 0 -i "' + 'Music/' + title + '.m4a" -ab 192k "' + 'Music/' + title + '.mp3"')
	else:
		os.system('Scripts\\avconv.exe -loglevel 0 -i "' + 'Music/' + title + '.m4a" -ab 192k "' + 'Music/' + title + '.mp3"')
	os.remove('Music/' + title + '.m4a')

def downloadSong():
	a = video.getbestaudio(preftype="m4a")
	a.download(filepath="Music/" + title + ".m4a")

def isSpotify():
	if (len(raw_song) == 22 and raw_song.replace(" ", "%20") == raw_song) or (raw_song.find('spotify') > -1):
		return True
	else:
		return False

def trimSong():
	with open('Music/list.txt', 'r') as fin:
		data = fin.read().splitlines(True)
	with open('Music/list.txt', 'w') as fout:
		fout.writelines(data[1:])

def trackPredict():
	global URL
	if isSpotify():
		global content
		content = spotify.track(raw_song)
		song = (content['artists'][0]['name'] + ' - ' + content['name']).replace(" ", "%20").encode('utf-8')
		URL = "https://www.youtube.com/results?sp=EgIQAQ%253D%253D&q=" + song
	else:
		song = raw_song.replace(" ", "%20")
		URL = "https://www.youtube.com/results?sp=EgIQAQ%253D%253D&q=" + song
		song = ''

def graceQuit():
		print('')
		print('')
		print('Exitting..')
		exit()

title = ''
song = ''

while True:
	x = 0
	y = 0
	try:
		for m in os.listdir('Music/'):
			if m.endswith('.temp') or m.endswith('.m4a'):
				os.remove('Music/' + m)
		print('')
		print('')
		raw_song = raw_input('>> Enter a song/cmd: ').decode('utf-8').encode('utf-8')
		print('')
		if raw_song == 'exit':
			exit()
		elif raw_song == 'play':
			playSong()

		elif raw_song == 'lyrics':
			loadMechanize()
			getLyrics()

		elif raw_song == 'list':
			loadMechanize()
			f = open('Music/list.txt', 'r').read()
			lines = f.splitlines()
			for raw_song in lines:
				if not len(raw_song) == 0:
					x = x + 1
			print('Total songs in list = ' + str(x) + ' songs')
			for raw_song in lines:
				try:
					if not len(raw_song) == 0:
						trackPredict()
						print('')
						y = y + 1
						searchYT(y)
						if not checkExists(True):
							downloadSong()
							trimSong()
							print('')
							convertSong()
							if isSpotify():
								fixSong()
					else:
						trimSong()
				except KeyboardInterrupt:
					graceQuit()
				except:
					lines.append(raw_song)
					trimSong()
					with open('Music/list.txt', 'a') as myfile:
						myfile.write(raw_song)
					print('Could not complete a Song download, will try later..')

		else:
			try:
				loadMechanize()
				trackPredict()
				searchYT(None)
				if not checkExists(False):
					downloadSong()
					print('')
					convertSong()
					if isSpotify():
						fixSong()
			except KeyboardInterrupt:
				graceQuit()
		br.close()

	except KeyboardInterrupt:
		graceQuit()
