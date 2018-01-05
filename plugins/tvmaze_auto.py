"""

"""
from pytz import timezone
import pytvmaze
from cloudbot import hook
from cloudbot.util import timeformat
from datetime import datetime
import re
from datetime import timedelta
from cloudbot.util import timeformat, colors
from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats, get_color, get_format, _convert, strip_irc, strip_all, IRC_COLOUR_DICT
import asyncio

@asyncio.coroutine
@hook.periodic(60, initial_interval=0)
def upcoming(message, bot, conn):
	high_time = (datetime.now(timezone('US/Eastern')) + timedelta(minutes=10)).strftime('%H:%M')
	current_hour = int(datetime.now(timezone('US/Eastern')).strftime('%H'))
	conn = bot.connections['P2PNET']
	if current_hour >= 18 or current_hour <= 3:
		tvm = pytvmaze.TVMaze()
		schedule = pytvmaze.get_schedule(primetime='yes')
		networks = ["NBC", "ABC", "CBS", "FOX", "Discovery Channel", "Food Network", "TNT", "Comedy Central", "HBO", "USA Network", "The CW", "tbs", "Bravo", "History", "FX", "Showtime", "Science", "AMC", "CBS All Access"]
		lines = []
		for episode in schedule:
			time = episode.airtime
			if time != '':
				if time == high_time:
					if episode.show.network is not None:
						if episode.show.network.name in networks:
							lines.append('$(bold){}$(clear): $(orange){} (S{}E{})$(clear)'.format(episode.show.network.name, episode.show.name, episode.season_number, episode.episode_number))
					elif episode.show.web_channel is not None:
						if episode.show.web_channel.name in networks:
							lines.append('$(bold){}$(clear): $(orange){} (S{}E{})$(clear)'.format(episode.show.web_channel.name, episode.show.name, episode.season_number, episode.episode_number))
					else:
						lines.append('$(bold){}$(clear): $(orange){} (S{}E{})$(clear)'.format("Unknown", episode.show.name, episode.season_number, episode.episode_number))
		if len(lines) > 0:
			line = ' && '.join([str(i) for i in lines])
			conn.message('#phoenix-torrents', colors.parse('Airing in 10 minutes - {}'.format(line)))
		pass
