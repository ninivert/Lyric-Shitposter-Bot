from .config import config
from .file import dump


def get_chat_vars(chat_id):
	res = {}

	for key in config['chats']['default'].keys():
		res[key] = get_chat_var(chat_id, key)

	return res


def get_chat_var(chat_id, var):
	import copy

	if str(chat_id) in config['chats'].keys() and var in config['chats'][str(chat_id)].keys():
		return config['chats'][str(chat_id)][var]
	else:
		return copy.deepcopy(config['chats']['default'][var])


def is_song_enabled(chat_id, artist, title):
	enabled_songs = get_chat_var(chat_id, 'enabled_songs')

	if artist in enabled_songs.keys():
		if type(enabled_songs[artist]) is list:
			if title in enabled_songs[artist]:
				return True

	return False


def get_songs_data(chat_id):
	datas = []

	for artist in config['lyrics'].keys():
		for title in config['lyrics'][artist].keys():
			enabled = is_song_enabled(chat_id, artist, title)
			song = config['song_format'].format(
				status_emoji='x' if enabled else ' ',
				artist=artist,
				title=title
			)
			datas.append({'artist': artist, 'title': title, 'enabled': enabled, 'song': song})

	return datas


def get_songs_buttons(chat_id):
	from telegram import InlineKeyboardButton
	import json

	songs_data = get_songs_data(chat_id)
	buttons = []

	for song_data in songs_data:
		callback_data = json.dumps([song_data['artist'], song_data['title'], song_data['enabled']])
		buttons.append(InlineKeyboardButton(song_data['song'], callback_data=callback_data))

	return buttons


def get_songs_markup(chat_id):
	from telegram import InlineKeyboardMarkup
	from .telegram_menu import build_menu

	return InlineKeyboardMarkup(
		build_menu(
			get_songs_buttons(chat_id),
			n_cols=config['songs_buttons_cols']
		)
	)


def set_chat_vars(chat_id, vars_dict):
	if str(chat_id) not in config['chats'].keys():
		config['chats'][str(chat_id)] = {}

	config['chats'][str(chat_id)].update(vars_dict)
	dump(config, 'config.json')


def set_chat_var(chat_id, var, val):
	if not str(chat_id) in config['chats'].keys():
		config['chats'][str(chat_id)] = {}

	config['chats'][str(chat_id)][var] = val
	dump(config, 'config.json')
