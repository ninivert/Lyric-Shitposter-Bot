import logging
import time
from .config import config
from .lyrics import get_next_index
from .database import *


def bot():
	from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler

	# Setup logger
	global _logger
	_logger = logging.getLogger()

	# Get API token
	with open('token.txt') as file:
		token = file.read().strip()

	# Init bot
	updater = Updater(token=token, use_context=True)
	dispatcher = updater.dispatcher

	# Handlers
	cmd_filter = (Filters.command & (~Filters.update.edited_message))
	message_handler = MessageHandler(Filters.text, message)
	dispatcher.add_handler(message_handler)
	# Usage
	start_handler = CommandHandler('start', cmd_start)
	next_handler = CommandHandler('next', cmd_next)
	lyrics_handler = CommandHandler('lyrics', cmd_lyrics)
	current_handler = CommandHandler('current', cmd_current)
	uses_handler = CommandHandler('uses', cmd_uses)
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(next_handler)
	dispatcher.add_handler(lyrics_handler)
	dispatcher.add_handler(current_handler)
	dispatcher.add_handler(uses_handler)
	# Settings
	songs_handler = CommandHandler('songs', cmd_songs)
	songs_inline_handler = CallbackQueryHandler(cmd_songs_inline)
	reset_handler = CommandHandler('reset', cmd_reset)
	set_threshold_handler = CommandHandler('set_threshold', cmd_set_threshold)
	set_timeout_handler = CommandHandler('set_timeout', cmd_set_timeout)
	dispatcher.add_handler(songs_handler)
	dispatcher.add_handler(songs_inline_handler)
	dispatcher.add_handler(reset_handler)
	dispatcher.add_handler(set_threshold_handler)
	dispatcher.add_handler(set_timeout_handler)
	# Help and debug
	help_handler = CommandHandler('help', cmd_help)
	debug_handler = CommandHandler('debug', cmd_debug)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(debug_handler)
	# Unkowon
	unknown_handler = MessageHandler(cmd_filter, cmd_unknown)
	dispatcher.add_handler(unknown_handler)

	# Run bot
	updater.start_polling()
	updater.idle()


def cmd_start(update, context):
	songs = get_chat_var(update.message.chat_id, 'songs')

	if len(songs) == 0:
		throw_no_songs_exception(update, context)
		return

	songs[0]['index'] = -1
	set_chat_var(update.message.chat_id, 'songs', songs)
	cmd_next(update, context)


def cmd_next(update, context):
	songs = get_chat_var(update.message.chat_id, 'songs')

	if len(songs) == 0:
		throw_no_songs_exception(update, context)
		return

	lyrics = config['lyrics'][songs[0]['artist']][songs[0]['title']]

	if is_song_timed_out(update.message.chat_id, songs[0]['artist'], songs[0]['title']):
		songs[0]['index'] = -1

	songs[0]['index'] = (songs[0]['index'] + 1) % len(lyrics)
	songs[0]['timestamp'] = time.time()

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=lyrics[songs[0]['index']]
	)


def cmd_lyrics(update, context):
	songs = get_chat_var(update.message.chat_id, 'songs')

	if len(songs) == 0:
		throw_no_songs_exception(update, context)
		return

	lyrics = config['lyrics'][songs[0]['artist']][songs[0]['title']]

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text="\n".join(lyrics)
	)


def cmd_current(update, context):
	songs = get_chat_var(update.message.chat_id, 'songs')
	text = 'Currently playing, in decreasing order of priority:'

	for song_index in range(len(songs)):
		song = songs[song_index]
		text += f'\n[{song_index+1}] {song["title"]} by {song["artist"]} (at pos {song["index"]}, last seen {time.ctime(song["timestamp"])})'

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=text
	)


def cmd_uses(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=f'I have replied {get_chat_var(update.message.chat_id, "uses")} times !',
	)


def cmd_songs(update, context):
	reply_markup = get_songs_markup(update.message.chat_id)

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		reply_markup=reply_markup,
		text='Tap a song to enable or disable it.'
	)


def cmd_songs_inline(update, context):
	message_id = update.callback_query.message.message_id
	chat_id = update.callback_query.message.chat.id

	import json
	artist, title, enabled = json.loads(update.callback_query.data)
	songs = get_chat_var(chat_id, 'songs')

	# Disable song
	if enabled:
		for data_index in reversed(range(len(songs))):
			song = songs[data_index]
			if is_song_enabled(chat_id, song['artist'], song['title']):
				del songs[data_index]

	# Enable song
	else:
		if not is_song_enabled(chat_id, artist, title):
			songs.append({
				'artist': artist,
				'title': title,
				'index': -1,
				'timestamp': 0
			})

	enabled = not enabled

	set_chat_var(chat_id, 'songs', songs)

	reply_markup = get_songs_markup(chat_id)
	update_text = f'{title} from {artist} is now {"enabled" if enabled else "disabled"}.'

	context.bot.edit_message_text(
		chat_id=chat_id,
		message_id=message_id,
		text=update_text,
		reply_markup=reply_markup
	)


def cmd_reset(update, context):
	songs = get_chat_var(update.message.chat_id, 'songs')

	for song in songs:
		song['index'] = -1

	set_chat_var(update.message.chat_id, 'songs', songs)

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=f'Reset all songs for chat {update.message.chat_id}',
	)


def cmd_set_threshold(update, context):
	try:
		threshold = float(context.args[0])

	except IndexError:
		throw_no_args_exception(update, context)
	except ValueError:
		throw_expected_float_exception(update, context)

	else:
		chat = get_chat_vars(update.message.chat_id)
		chat['threshold'] = threshold
		set_chat_vars(update.message.chat_id, chat)

		context.bot.send_message(
			chat_id=update.message.chat_id,
			reply_to_message_id=update.message.message_id,
			text=f'Set threshold to {threshold}%',
		)


def cmd_set_timeout(update, context):
	try:
		timeout = float(context.args[0])

	except IndexError:
		throw_no_args_exception(update, context)
	except ValueError:
		throw_expected_float_exception(update, context)

	else:
		chat = get_chat_vars(update.message.chat_id)
		chat['timeout'] = timeout * 60
		set_chat_vars(update.message.chat_id, chat)

		context.bot.send_message(
			chat_id=update.message.chat_id,
			reply_to_message_id=update.message.message_id,
			text=f'Set timeout to {timeout} minute(s)',
		)


def message(update, context):
	chat = get_chat_vars(update.message.chat_id)
	next_index = -1

	for song_index in range(len(chat['songs'])):
		song = chat['songs'][song_index]

		# Check timeout
		if is_song_timed_out(update.message.chat_id, song['artist'], song['title']):
			song['index'] = -1

		lyrics = config['lyrics'][song['artist']][song['title']]

		next_index = get_next_index(
			update.message.text,
			lyrics,
			start_index=song['index'],
			threshold=chat['threshold']
		)

		if next_index > -1:
			break

	_logger.info(f'Message: "{update.message.text}", next index: {next_index}')

	if next_index > -1:
		if next_index < len(lyrics):
			context.bot.send_message(
				chat_id=update.message.chat_id,
				reply_to_message_id=update.message.message_id,
				text=lyrics[next_index]
			)
		else:
			context.bot.send_sticker(
				chat_id=update.message.chat_id,
				reply_to_message_id=update.message.message_id,
				sticker='CAADAQADfkQAAq8ZYgeMKpo3QZgHKRYE'
			)
			next_index = -1

		# Move song front
		chat['songs'].insert(0, chat['songs'].pop(song_index))
		chat['songs'][0]['index'] = next_index
		chat['songs'][0]['timestamp'] = time.time()

		set_chat_vars(update.message.chat_id, {
			'songs': chat['songs'],
			'uses': chat['uses'] + 1
		})


def cmd_help(update, context):
	with open('help.txt') as file:
		help_text = file.read()

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=help_text
	)


def cmd_debug(update, context):
	import json
	from telegram import ParseMode

	chat = get_chat_vars(update.message.chat_id)
	stats = f'Here are some stats for chat {update.message.chat_id}:\n'
	stats += '<code>'
	stats += json.dumps(chat, indent='\t')
	stats += '</code>'

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=stats,
		parse_mode=ParseMode.HTML
	)


def cmd_unknown(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='Unknown command. /help'
	)


def throw_no_songs_exception(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='[Error] No songs active ! /songs'
	)


def throw_expected_float_exception(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='[Error] Expected a number'
	)


def throw_no_args_exception(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='[Error] Expected an argument, none provided'
	)
