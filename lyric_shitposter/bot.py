import logging
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
	message_handler = MessageHandler(Filters.text, message)
	cmd_filter = (Filters.command & (~Filters.update.edited_message))
	help_handler = CommandHandler('help', cmd_help)
	start_handler = CommandHandler('start', cmd_start)
	next_handler = CommandHandler('next', cmd_next)
	debug_handler = CommandHandler('debug', cmd_debug)
	uses_handler = CommandHandler('uses', cmd_uses)
	current_handler = CommandHandler('current', cmd_current)
	songs_handler = CommandHandler('songs', cmd_songs)
	songs_inline_handler = CallbackQueryHandler(cmd_songs_inline)
	unknown_handler = MessageHandler(cmd_filter, cmd_unknown)
	dispatcher.add_handler(message_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(next_handler)
	dispatcher.add_handler(debug_handler)
	dispatcher.add_handler(uses_handler)
	dispatcher.add_handler(current_handler)
	dispatcher.add_handler(songs_handler)
	dispatcher.add_handler(songs_inline_handler)
	dispatcher.add_handler(unknown_handler)

	# Run bot
	updater.start_polling()
	updater.idle()


def message(update, context):
	chat = get_chat_vars(update.message.chat_id)

	for data_index in range(len(chat['indexes'])):
		artist, title, index = chat['indexes'][data_index]

		lyrics = config['lyrics'][artist][title]

		next_index = get_next_index(
			update.message.text,
			lyrics,
			start_index=index,
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

		# Move index front
		chat['indexes'].insert(0, chat['indexes'].pop(data_index))
		chat['indexes'][0][2] = next_index

		set_chat_vars(update.message.chat_id, {
			'indexes': chat['indexes'],
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


def cmd_start(update, context):
	indexes = get_chat_var(update.message.chat_id, 'indexes')
	indexes[0][2] = -1
	set_chat_var(update.message.chat_id, 'indexes', indexes)
	cmd_next(update, context)


def cmd_next(update, context):
	indexes = get_chat_var(update.message.chat_id, 'indexes')
	artist, title, index = indexes[0]
	lyrics = config['lyrics'][artist][title]
	index = (index + 1) % len(lyrics)
	indexes[0][2] = index

	set_chat_var(update.message.chat_id, 'indexes', indexes)

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=lyrics[index]
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


def cmd_uses(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=f'I have replied {get_chat_var(update.message.chat_id, "uses")} times !',
	)


def cmd_current(update, context):
	indexes = get_chat_var(update.message.chat_id, 'indexes')
	text = 'Currently playing, in decreasing order of priority:'

	for i in range(len(indexes)):
		artist, title, index = indexes[i]
		text += f'\n[{i+1}] {title} by {artist} (at pos {index})'

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=text
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
	enabled_songs = get_chat_var(chat_id, 'enabled_songs')
	indexes = get_chat_var(chat_id, 'indexes')

	if enabled:
		for data_index in range(len(indexes)):
			_artist, _title, _index = indexes[data_index]
			if _artist == artist and _title == title:
				del indexes[data_index]

		enabled_songs[artist].remove(title)
		if len(enabled_songs[artist]) == 0:
			del enabled_songs[artist]

	else:
		if artist not in enabled_songs.keys():
			enabled_songs[artist] = []
		enabled_songs[artist].append(title)

		indexes.append([artist, title, -1])

	enabled = not enabled

	set_chat_var(chat_id, 'enabled_songs', enabled_songs)
	set_chat_var(chat_id, 'indexes', indexes)

	reply_markup = get_songs_markup(chat_id)
	update_text = f'{title} from {artist} is now {"enabled" if enabled else "disabled"}.'

	context.bot.edit_message_text(
		chat_id=chat_id,
		message_id=message_id,
		text=update_text,
		reply_markup=reply_markup
	)


def cmd_unknown(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='Unknown command. /help'
	)
