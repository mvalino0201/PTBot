"""

"""
from pytz import timezone
import pytvmaze
from cloudbot import hook
from datetime import datetime
import re
from datetime import timedelta
from cloudbot.util import timeformat, colors
from cloudbot.util.colors import parse, strip, get_available_colours, get_available_formats, get_color, get_format, _convert, strip_irc, strip_all, IRC_COLOUR_DICT

@hook.command("today")
def today(reply, message):
	tvm = pytvmaze.TVMaze()
	schedule = pytvmaze.get_schedule(primetime='yes')
	networks = ["NBC", "ABC", "CBS", "FOX", "Discovery Channel", "Food Network", "TNT", "Comedy Central", "HBO", "USA Network", "The CW", "tbs", "Bravo", "History", "FX", "Showtime"]
	lines = []
	times =[]
	for episode in schedule:
		if episode.show.network.name in networks:
			time = episode.airtime
			if time != '':
				if time > '19:30' or time < '03:15':
					if time not in times:
						lines.append([])
						times.append(time)
					index = times.index(time)
					lines[index].append('$(bold){}$(clear): $(orange){} (S{}E{})$(clear)'.format(episode.show.network.name, episode.show.name, episode.season_number, episode.episode_number))

	for time in times:
		index = times.index(time)
		line = ' && '.join([str(i) for i in lines[index]])
		message(colors.parse('$(bold)$(red, white)[{}]$(clear) - {}'.format(time, line)))
	'''return '{} - {} - {} - {} - {} ({} ago)'.format(section, name, size, files, date_string, since)'''

@hook.command('show', 's')
def show(text, reply, message):
	tvm = pytvmaze.TVMaze()
	try:
		show = tvm.get_show(show_name=text)
		message(colors.parse('$(bold)$(orange, white){}$(clear)').format(show))
		lines = []
		if show.type is not None:
			lines.append('$(red)Type:$(clear) {}'.format(show.type))
			pass
		if len(show.genres) > 0:
			lines.append('$(red)Genres:$(clear) {}'.format(', '.join([str(i) for i in show.genres])))
			pass
		if show.status is not None:
			lines.append('$(red)Status:$(clear) {}'.format(show.status))
			pass
		if show.runtime is not None:
			lines.append('$(red)Runtime:$(clear) {}'.format(show.runtime))
			pass
		if len(show.schedule['days']) > 0 and len(show.schedule['time']) > 0:
			lines.append('$(red)Airing:$(clear) {} @ {} on $(bold){}$(clear)'.format(show.schedule['days'][0], show.schedule['time'], show.network.name))
			pass
		message(colors.parse('$(red) // $(clear)'.join([str(i) for i in lines])))
		message(colors.parse('$(red)Summary:$(clear) {}'). format(show.summary))
		message(colors.parse('$(red)More at:$(clear) {}'). format(show.url))
		if show.next_episode is not None:
			message(colors.parse('$(red)Next Episode:$(clear) {} (S{}E{}) $(red)// Airing on:$(clear) {} $(red)//$(clear) {}').format(show.next_episode.title, show.next_episode.season_number, show.next_episode.episode_number, show.next_episode.airdate, show.next_episode.summary))
		pass
	except Exception as e:
		message(colors.parse('$(white, red)Show Not Found$(clear)'))
		raise e
	

@hook.command('next', 'n')
def next(text, reply, message):
	tvm = pytvmaze.TVMaze()
	try:
		show = tvm.get_show(show_name=text)
		if show.next_episode is not None:
			message(colors.parse('$(red)Next Episode:$(clear) {} (S{}E{}) $(red)// Airing on:$(clear) {} $(red)//$(clear) {}').format(show.next_episode.title, show.next_episode.season_number, show.next_episode.episode_number, show.next_episode.airdate, show.next_episode.summary))
			message(colors.parse('$(red)More at:$(clear) {}'). format(show.next_episode.url))
		else:
			message(colors.parse('$(white, red){} does not have a next episode$(clear)').format(show))
		pass
	except Exception as e:
		message(colors.parse('$(white, red)Show Not Found$(clear)'))
		raise e

@hook.command('prev', 'previous', 'p')
def prev(text, reply, message):
	tvm = pytvmaze.TVMaze()
	try:
		show = tvm.get_show(show_name=text)
		if show.previous_episode is not None:
			message(colors.parse('$(red)Previous Episode:$(clear) {} (S{}E{}) $(red)// Airing on:$(clear) {} $(red)//$(clear) {}').format(show.previous_episode.title, show.previous_episode.season_number, show.previous_episode.episode_number, show.previous_episode.airdate, show.previous_episode.summary))
			message(colors.parse('$(red)More at:$(clear) {}'). format(show.previous_episode.url))
		else:
			message(colors.parse('$(white, red){} does not have a previous episode$(clear)').format(show))
		pass
	except Exception as e:
		message(colors.parse('$(white, red)Show Not Found$(clear)'))
		raise e
@hook.command("tomorrow")
def tomorrow(reply, message):
	tvm = pytvmaze.TVMaze()
	schedule = pytvmaze.get_schedule(date=str((datetime.now(timezone('US/Eastern')) + timedelta(days=1)).strftime('%Y-%m-%d')))
	networks = ["NBC", "ABC", "CBS", "FOX", "Discovery Channel", "Food Network", "TNT", "Comedy Central", "HBO", "USA Network", "The CW", "tbs", "Bravo", "History", "FX", "Showtime"]
	lines = []
	times =[]
	for episode in schedule:
		if episode.show.network.name in networks:
			time = episode.airtime
			if time != '':
				if time > '19:30' or time < '03:15':
					if time not in times:
						lines.append([])
						times.append(time)
					index = times.index(time)
					lines[index].append('$(bold){}$(clear): $(orange){} (S{}E{})$(clear)'.format(episode.show.network.name, episode.show.name, episode.season_number, episode.episode_number))

	for time in times:
		index = times.index(time)
		line = ' && '.join([str(i) for i in lines[index]])
		message(colors.parse('$(bold)$(red, white)[{}]$(clear) - {}'.format(time, line)))