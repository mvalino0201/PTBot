import threading
import asyncio
import socket
import pycurl
import datetime
import requests
import re
import os
from lxml import html
from cloudbot import hook
import pytvmaze
from cloudbot.util import timeformat
from datetime import datetime
from datetime import timedelta
from cloudbot.util import timeformat, colors
from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats, get_color, get_format, _convert, strip_irc, strip_all, IRC_COLOUR_DICT
from io import BytesIO
import subprocess

ptfiles_re_Upload = re.compile(r'new (.*)\].* (https://ptfiles.net/details.php\?id=([0-9]+))', re.I)
ptfiles_re_s01e01 = re.compile(r'new.TV.*\].* (.*)\.S01E01\..*(https://ptfiles.net/details.php\?id=[0-9]+)', re.I)

@asyncio.coroutine
@hook.regex(ptfiles_re_Upload)
def ptfiles_url(match, bot, conn, chan):
	if chan == '#ptf-announce':
		type = match.group(1)
		url = match.group(2)
		tid = match.group(3)
		with open('/home/whocares/ssbot/whocares.cookie', 'r') as myfile:
			cookie=myfile.read().replace('\n', '')
		cookies = {'session_key': cookie}
		try:
			headers = {'Accept-language': 'en'}
			request = requests.get(url, headers=headers, cookies=cookies)
			request.raise_for_status()
		except requests.exceptions.HTTPError as e:
			print('Unable to fetch results: {}'.format(e))
		data = html.fromstring(request.text)
		output = data.xpath('//title')[0].text_content().strip()

		results = re.search("<a id=\"poster_details\" href=\"(.*)\" title", request.text, flags=re.IGNORECASE)
		results2 = re.search("<a id=\"poster_details\" href=\".*ptfiles\.net\/.*\" title", request.text, flags=re.IGNORECASE)
		results3 = re.search("<a id=\"poster_details\" href=\"\/image.php\/.*\" title", request.text, flags=re.IGNORECASE)
		if results is not None and results2 is None and results3 is None:
			'''External Image'''
			imgurl = results.group(1)
			imgrequest = requests.get(imgurl, headers=headers)
			imgtype = re.search("image/", imgrequest.headers.get('content-type'), flags=re.IGNORECASE)
			if len(imgrequest.content) < 2000000 and imgtype is not None:
				split = imgurl.rpartition('/')
				imgname = split[2]
				with open('/home/whocares/' + imgname, 'wb') as f:
					f.write(imgrequest.content)
				buffer = BytesIO()
				c = pycurl.Curl()
				c.setopt(c.URL, 'https://ptfiles.net/panel.php?tool=bitbucket')
				c.setopt(c.HTTPPOST, [
					('file', (
						c.FORM_FILE, '/home/whocares/' + imgname,
					)),
				])
				c.setopt(c.WRITEDATA, buffer)
				c.setopt(pycurl.COOKIE, 'session_key=' + cookie)
				c.perform()
				c.close()
				body = buffer.getvalue()
				imgout = body.decode('iso-8859-1')
				ptflink = re.search("<input .*id=\"direct\".*value=\"(.*)\" readonly='readonly'", imgout, flags=re.IGNORECASE)
				if ptflink is not None:
					posterlink = ptflink.group(1)
					try:
						posterup = "https://ptfiles.net/take_ajax.php?id={}&part=poster&val={}".format(tid,posterlink)
						headers = {'Accept-language': 'en'}
						imgrequest = requests.get(posterup, headers=headers, cookies=cookies)
						imgrequest.raise_for_status()
						conn.message('#phoenix/staff', colors.parse('Updated image on {} with {}'.format(url,posterlink)))
					except Exception as e:
						conn.message('#phoenix/staff', colors.parse('Failed to update image on {} with {}'.format(url,posterlink)))
				os.remove('/home/whocares/' + imgname)
		'''Large IMDB image'''
		poster = re.search("<a id=\"poster_details\" href=\".*\/.*imdb\/(\d+)_big.*\" title", request.text, flags=re.IGNORECASE)
		if poster is not None:
			imdbid = poster.group(1)
			imdbimg = "https://ptfiles.net/image.php/imdb/{}_big.jpg".format(imdbid)
			imdbimgrequest = requests.get(imdbimg, headers=headers, cookies=cookies)
			if len(imdbimgrequest.content) > 2000000:
				print(len(imdbimgrequest.content))
				shrinkurl = "https://ptfiles.net/imdb2/imgshrink.php?key=Qy7M3gMEJ3qcuDBb99Mn9Xo9l2JbnN3AF3Yc861kl2DLJMsE7ptAvD0urcxKaR3o&mid={}".format(imdbid)
				shrinkrequest = requests.get(shrinkurl, headers=headers, cookies=cookies)
				conn.message("#whocares", "Image shrunk for {} // Result: {}".format(url, shrinkrequest.text))

@asyncio.coroutine
@hook.regex(ptfiles_re_s01e01)
def ptfiles_pilot(match, bot, conn, chan):
	if chan == '#ptf-announce':
		name = match.group(1).replace(".", " ")
		url = match.group(2)
		tvm = pytvmaze.TVMaze()

		headers = {'User-Agent': bot.user_agent}
		strip = name.strip()
		params = {'t': strip, 'apikey': 'a7d6f6c'}

		try:
			request = requests.get("http://www.omdbapi.com/", params=params, headers=headers, timeout=5)
			if request.status_code == requests.codes.ok:
				content = request.json()
				if content['Response'] == 'True':
					imdb = '$(red)https://www.imdb.com/title/{}$(clear)'.format(content['imdbID'])
				else:
					imdb = '$(white, red)IMDB not found!$(clear)'
			else:
					imdb = '$(white, red)IMDB not found!$(clear)'
		except Exception:
			imdb = '$(white, red)IMDB not found!$(clear)'
			pass

		try:
			show = tvm.get_show(show_name=name)
			tvmaze = '$(red){}$(clear)'.format(show.url)
			pass
		except Exception as e:
			tvmaze = '$(white, red)TVMaze Not Found$(clear)'
			pass
		conn.message('#phoenix/staff', colors.parse('{} // {} // {} // {}'.format(name, url, tvmaze, imdb)))

@hook.irc_raw("JOIN", singlethread=True)
def voice(nick, action, message, chan, event, db, conn):
	try:
		chan = event.irc_raw.split(':')[2].lower()
	except:
		return
	if nick == "PTF":
		conn.send("MODE {} {} {}".format(chan, "+v", nick))
		pass


@asyncio.coroutine
@hook.command("addsquid")
def addsquid(text, reply, message, chan, nick):
	if chan == '#whocares':
		if nick == 'whocares':
			subprocess.call("sudo /home/whocares/addhost.sh '{}'".format(text), shell=True)
			message(colors.parse('{} has been added to the squid config file and squid is restarted'.format(text)))
