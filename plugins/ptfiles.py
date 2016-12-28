import pycurl
import datetime
import requests
import re
from lxml import html
from cloudbot import hook
import pytvmaze
from cloudbot.util import timeformat
from datetime import datetime
from datetime import timedelta
from cloudbot.util import timeformat, colors
from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats, get_color, get_format, _convert, strip_irc, strip_all, IRC_COLOUR_DICT
from io import BytesIO

ptfiles_re_Movies = re.compile(r'(https://ptfiles.net/details.php\?id=([0-9]+))', re.I)
ptfiles_re_s01e01 = re.compile(r'new.TV.*\].* (.*)\.S01E01\..*(https://ptfiles.net/details.php\?id=[0-9]+)', re.I)

@hook.regex(ptfiles_re_Movies)
def ptfiles_url(match, bot, conn):
	url = match.group(1)
	tid = match.group(2)
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
	if results is not None:
		results2 = re.search("<a id=\"poster_details\" href=\".*ptfiles\.net\/.*\" title", request.text, flags=re.IGNORECASE)
		if results2 is None:
			imgurl = results.group(1)
			imgrequest = requests.get(imgurl, headers=headers, cookies=cookies)
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
						request = requests.get(posterup, headers=headers, cookies=cookies)
						request.raise_for_status()
						conn.message('#phoenix/staff', colors.parse('Updated image on {} with {}'.format(url,posterlink)))
					except Exception as e:
						conn.message('#phoenix/staff', colors.parse('Failed to update image on {} with {}'.format(url,posterlink)))
				os.remove('/home/whocares/' + imgname)
			

@hook.regex(ptfiles_re_s01e01)
def ptfiles_pilot(match, bot, conn):
	name = match.group(1).replace(".", " ")
	url = match.group(2)
	tvm = pytvmaze.TVMaze()

	headers = {'User-Agent': bot.user_agent}
	strip = name.strip()
	params = {'t': strip}

	request = requests.get("http://www.omdbapi.com/", params=params, headers=headers)
	content = request.json()

	if content.get('Error', None) == 'Movie not found!':
		imdb = '$(white, red)IMDB not found!$(clear)'
	elif content['Response'] == 'True':
		imdb = '$(red)https://www.imdb.com/title/{}$(clear)'.format(content['imdbID'])
	try:
		show = tvm.get_show(show_name=name)
		tvmaze = '$(red){}$(clear)'.format(show.url)
		pass
	except Exception as e:
		tvmaze = '$(white, red)TVMaze Not Found$(clear)'
		raise e
	conn.message('#phoenix/staff', colors.parse('{} // {} // {} // {}'.format(name, url, tvmaze, imdb)))