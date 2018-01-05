import asyncio
import httplib2
import os
import subprocess
import datetime
import oauth2client
from oauth2client import client, tools
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from apiclient import errors, discovery
from cloudbot import hook
from cloudbot.util import timeformat
import feedparser
import pickle
import ssl
if hasattr(ssl, '_create_unverified_context'):
	ssl._create_default_https_context = ssl._create_unverified_context

@asyncio.coroutine
@hook.periodic(60, initial_interval=0)
def upcoming(message, bot):
	conn = bot.connections['P2PNET']
	with open ('/home/whocares/PTBot/plugins/rssfeed', 'rb') as fp:
		itemlist = pickle.load(fp)
	EMAIL = ''

	AUTHORS = ['Dual Writer', 'Jay Cantrell', 'SmokinDriver', 'Refusenik', 'Cold Creek', 'Argon', 'EzzyB', 'Don Lockwood', 'Harddaysknight', "Svengali's Ghost", 'Banzai Ben', 'aubie56', 'Invid Fan', 'Sage Mullins', 'JeremyDCP', 'Charlie Foxtrot', 'Openbook', 'Kingkey', 'Lazlo Zalezac', 'Bastion Grammar Jr', 'Ernest Bywater', 'Mindmeld', 'Lloyd Sampsel', 'Banadin', 'Lumpy', 'DeeBee', 'rlfj', 'Pars001', 'Reluctant_Sir', 'The Outsider', 'Anthill Mob', 'ShadowWriter']
	u232feed = feedparser.parse( "https://forum-u-232.servebeer.com/index.php?action=.xml;type=atom", request_headers={"Cookie": "SMFCookie11=a%3A4%3A%7Bi%3A0%3Bs%3A3%3A%22303%22%3Bi%3A1%3Bs%3A40%3A%22afce925440651b17b686ad3b29cc5c1fcb35b82c%22%3Bi%3A2%3Bi%3A1644698039%3Bi%3A3%3Bi%3A0%3B%7D; expires=Sun, 13 Feb 2022 11:57:06 GMT; path=/; domain=forum-u-232.servebeer.com"} )
	githubfeed = feedparser.parse( "https://github.com/Bigjoos/U-232-V5/commits/master.atom")
	mylibraryfeed = feedparser.parse("http://storiesonline.net/feed/HTcmoeA6%252BWFH1Jfz4yuQaA%253D%253D.xml")
	blogsfeed = feedparser.parse("http://storiesonline.net/feed/fMGM1Ttdw8FqtCiL%252Bgb%252FMQ%253D%253D.xml")
	newfeed = feedparser.parse("https://storiesonline.net/feed/FLZlnGxXlNwD0NDs1ZTf5g%253D%253D.xml")
	finefeed = feedparser.parse("http://finestories.com/feed/dxfFCYJ3EB0Eg2oRHlQ%252FEw%253D%253D.xml")
	for entry in u232feed.entries:
		if entry.link not in itemlist:
			conn.message("#09source", "New Support Forum Post - {} in {} by {} // {}".format(entry.title, entry.label, entry.author_detail.name, entry.link))
			itemlist.append(entry.link)
	for entry in githubfeed.entries:
		if entry.link not in itemlist:
			conn.message("#09source", "New Github Commit - {} // {}".format(entry.title, entry.link))
			itemlist.append(entry.link)
	for entry in mylibraryfeed.entries:
		if entry.id not in itemlist:
			conn.message("whocares", "{} updated // {}".format(entry.title, entry.link))
			EMAIL = EMAIL + "{} updated // {}\n".format(entry.title, entry.link)
			itemlist.append(entry.id)
	for entry in blogsfeed.entries:
		if entry.id not in itemlist and entry.author in AUTHORS:
			conn.message("whocares", "{} - {}".format(entry.title, entry.id))
			itemlist.append(entry.id)
	for entry in newfeed.entries:
		if entry.id not in itemlist and entry.author in AUTHORS:
			conn.message("whocares", "{} - {}".format(entry.title, entry.id))
			EMAIL = EMAIL + "{} - {}\n".format(entry.title, entry.id)
			itemlist.append(entry.id)
	for entry in finefeed.entries:
		if entry.id not in itemlist:
			conn.message("whocares", "{} updated // {}".format(entry.title, entry.link))
			EMAIL = EMAIL + "{} updated // {}\n".format(entry.title, entry.link)
			itemlist.append(entry.id)

	with open('/home/whocares/PTBot/plugins/rssfeed', 'wb') as fp:
		pickle.dump(itemlist, fp)

	if len(EMAIL) > 0:
		today = datetime.date.today()
		to = "joel.norton@gmail.com"
		sender = "whocares@open-scene.net"
		subject = 'SOL/FS Updates'
		SendMessage(sender, to, subject, EMAIL)
		pass


SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Quickstart'

def get_credentials():
	home_dir = os.path.expanduser('~')
	credential_dir = os.path.join(home_dir, '.credentials')
	if not os.path.exists(credential_dir):
		os.makedirs(credential_dir)
	credential_path = os.path.join(credential_dir, 'gmail-python-send.json')
	store = oauth2client.file.Storage(credential_path)
	credentials = store.get()
	if not credentials or credentials.invalid:
		flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
		flow.user_agent = APPLICATION_NAME
		credentials = tools.run_flow(flow, store)
		print('Storing credentials to ' + credential_path)
	return credentials

def SendMessage(sender, to, subject, msgPlain):
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)
	message1 = CreateMessage(sender, to, subject,  msgPlain)
	SendMessageInternal(service, "whocares@open-scene.net", message1)

def SendMessageInternal(service, user_id, message):
	try:
		message = (service.users().messages().send(userId=user_id, body=message).execute())
		return message
	except errors.HttpError as error:
		print('An error occurred: %s' % error)

def CreateMessage(sender, to, subject, message_text):
	msg = MIMEText(message_text)
	msg['To'] = to
	msg['From'] = sender
	msg['Subject'] = subject
	return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('UTF-8')).decode('ascii')}