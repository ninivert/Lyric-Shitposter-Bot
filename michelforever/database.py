import logging
from collections import UserDict
from typing import Dict, Union

from .chat import Chat, ChatSong, CHATS_DIR

_logger = logging.getLogger('database')

class Database:
	def __init__(self) -> None:
		self.chats: Dict[str, Chat] = {}

		for path in CHATS_DIR.iterdir():
			self.chats[path.name] = Chat.load(path.name)

		_logger.debug(self.chats)

	def get(self, chatid: Union[str, int]) -> Chat:
		"""Gets the instance of ``Chat`` for ``chatid``, creating one as needed"""
		if isinstance(chatid, int): chatid = str(chatid)
		if chatid not in self.chats:
			self.chats[chatid] = Chat(chatid, songs=ChatSong.open_all())
		return self.chats[chatid]

	def dump(self):
		for chat in self.chats.values():
			chat.dump()

DATABASE = Database()


# def get_chat_vars(chat_id):
# 	res = {}

# 	for key in config['chats']['default'].keys():
# 		res[key] = get_chat_var(chat_id, key)

# 	return res


# def get_chat_var(chat_id, var):
# 	import copy

# 	if str(chat_id) in config['chats'].keys() and var in config['chats'][str(chat_id)].keys():
# 		return config['chats'][str(chat_id)][var]
# 	else:
# 		return copy.deepcopy(config['chats']['default'][var])


# def is_song_enabled(chat_id, artist, title):
# 	songs = get_chat_var(chat_id, 'songs')

# 	for song in songs:
# 		if song['artist'] == artist and song['title'] == title:
# 			return True

# 	return False


# def is_song_timed_out(chat_id, artist, title):
# 	import time

# 	songs = get_chat_var(chat_id, 'songs')
# 	timeout = get_chat_var(chat_id, 'timeout')

# 	for song in songs:
# 		if song['artist'] == artist and song['title'] == title:
# # 			return song['timestamp'] + timeout < time.time()


# def get_songs_data(chat_id):
# 	datas = []

# 	for artist in config['lyrics'].keys():
# 		for title in config['lyrics'][artist].keys():
# 			enabled = is_song_enabled(chat_id, artist, title)
# 			string = config['song_format'].format(
# 				status_emoji='x' if enabled else ' ',
# 				artist=artist,
# 				title=title
# 			)
# 			datas.append({'artist': artist, 'title': title, 'enabled': enabled, 'string': string})

# 	return datas


# def get_songs_buttons(chat_id):
# 	from telegram import InlineKeyboardButton
# 	import json

# 	songs_data = get_songs_data(chat_id)
# 	buttons = []

# 	for song_data in songs_data:
# 		callback_data = json.dumps([song_data['artist'], song_data['title'], song_data['enabled']])
# 		buttons.append(InlineKeyboardButton(song_data['string'], callback_data=callback_data))

# 	return buttons


# def get_songs_markup(chat_id):
# 	from telegram import InlineKeyboardMarkup
# 	from .telegram_menu import build_menu

# 	return InlineKeyboardMarkup(
# 		build_menu(
# 			get_songs_buttons(chat_id),
# 			n_cols=config['songs_buttons_cols']
# 		)
# 	)


# def set_chat_vars(chat_id, vars_dict):
# 	if str(chat_id) not in config['chats'].keys():
# 		config['chats'][str(chat_id)] = {}

# 	config['chats'][str(chat_id)].update(vars_dict)
# 	dump(config, 'config.json')


# def set_chat_var(chat_id, var, val):
# 	if not str(chat_id) in config['chats'].keys():
# 		config['chats'][str(chat_id)] = {}

# 	config['chats'][str(chat_id)][var] = val
# 	dump(config, 'config.json')
