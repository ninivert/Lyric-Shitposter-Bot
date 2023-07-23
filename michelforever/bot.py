import logging, time, json, os
from typing import Optional

from .database import DATABASE

from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler, Application, CallbackContext
from telegram.ext import filters as Filters
from result import Ok, Err, Result

from dotenv import load_dotenv
load_dotenv()

ADMIN_USER_IDS = [
	763391143  # stupidfkingcat
]

def bot():
	# Setup logger
	global _logger
	_logger = logging.getLogger()

	# Get API token
	# with open('token.txt') as file:
	# 	token = file.read().strip()
	token = os.getenv('MICHELFOREVER_TOKEN')

	# Init bot
	application = Application.builder().token(token).post_shutdown(stop).build()

	# Usage
	start_handler = CommandHandler('start', cmd_start)
	next_handler = CommandHandler('next', cmd_next)
	lyrics_handler = CommandHandler('lyrics', cmd_lyrics)
	list_handler = CommandHandler('list', cmd_list)
	uses_handler = CommandHandler('uses', cmd_uses)
	application.add_handler(start_handler)
	application.add_handler(next_handler)
	application.add_handler(lyrics_handler)
	application.add_handler(list_handler)
	application.add_handler(uses_handler)
	# Settings
	# songs_handler = CommandHandler('songs', cmd_songs)
	# songs_inline_handler = CallbackQueryHandler(cmd_songs_inline)
	# application.add_handler(songs_handler)
	# application.add_handler(songs_inline_handler)
	reload_handler = CommandHandler('reload', cmd_reload)
	set_threshold_handler = CommandHandler('set_threshold', cmd_set_threshold)
	set_timeout_handler = CommandHandler('set_timeout', cmd_set_timeout)
	application.add_handler(reload_handler)
	application.add_handler(set_threshold_handler)
	application.add_handler(set_timeout_handler)
	# Help and debug
	help_handler = CommandHandler('help', cmd_help)
	debug_handler = CommandHandler('debug', cmd_debug)
	application.add_handler(help_handler)
	application.add_handler(debug_handler)

	# Handlers
	message_handler = MessageHandler(Filters.TEXT, message)
	application.add_handler(message_handler)
	# Unkowon
	unknown_handler = MessageHandler(Filters.COMMAND, cmd_unknown)
	application.add_handler(unknown_handler)

	# Run bot
	application.run_polling(poll_interval=2.0, timeout=20)


async def cmd_start(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	res = chat.restart()
	if isinstance(res, Err):
		await send_err(update, context, res.err())
		return
	await send_info(update, context, f'starting song {chat.current_song.unwrap()}')
	await cmd_next(update, context)


async def cmd_next(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	res = chat.next_line()
	if isinstance(res, Err):
		await send_err(update, context, res.err())
		return
	await send_msg(update, context, res.unwrap())


async def cmd_lyrics(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	res = chat.current_song
	if isinstance(res, Err):
		await send_err(update, context, res.err())
		return
	await send_msg(update, context, f'{chat.current_song.unwrap().artist} -- {chat.current_song.unwrap().title}' + '\n'.join(res.unwrap().lyrics))


async def cmd_list(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	await send_msg(update, context, '\n'.join(f'{song.artist} -- {song.title}' for song in chat.songs))


async def cmd_debug(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	await send_msg(update, context, str(chat))


async def cmd_uses(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	await send_msg(update, context, f'I have replied {chat.uses} times !')


async def cmd_reload(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	if not update.message.from_user.id in ADMIN_USER_IDS:
		# check if stupidfkingcat sent the message
		await send_err(update, context, 'you are not permitted to do this operation')
		return
	chat.reload()
	await send_info(update, context, f'reset all songs for chatid {chat.chatid}')


async def cmd_set_threshold(update: Optional[object], context: CallbackContext):
	try:
		threshold = float(context.args[0])
	except IndexError:
		await send_err(update, context, 'no value provided')
		return
	except ValueError:
		await send_err(update, context, 'value is not a number')
		return

	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	chat.threshold = threshold
	await send_info(update, context, f'set threshold to {threshold}%')


async def cmd_set_timeout(update: Optional[object], context: CallbackContext):
	try:
		timeout = int(context.args[0])
	except IndexError:
		await send_err(update, context, 'no value provided')
		return
	except ValueError:
		await send_err(update, context, 'value is not a number')
		return

	else:
		if update is None: return
		chat = DATABASE.get(update.message.chat_id)
		chat.timeout = timeout
		await send_info(update, context, f'set timeout to {timeout} seconds')


async def message(update: Optional[object], context: CallbackContext):
	if update is None: return
	chat = DATABASE.get(update.message.chat_id)
	res = chat.update_on_message(update.message.text)
	if isinstance(res, Err):
		return
	line, lastline = res.unwrap()
	print(line, lastline)
	if not lastline:
		await send_msg(update, context, line)
	else:
		await context.bot.send_sticker(
			chat_id=update.message.chat_id,
			reply_to_message_id=update.message.message_id,
			sticker='CAADAQADfkQAAq8ZYgeMKpo3QZgHKRYE'
		)


async def cmd_help(update: Optional[object], context: CallbackContext):
	with open('help.txt') as file:
		help_text = file.read()

	await send_msg(update, context, help_text)

async def cmd_unknown(update: Optional[object], context: CallbackContext):
	await send_err(update, context, 'no such command')


async def send_err(update: Optional[object], context: CallbackContext, errstr: str):
	await send_msg(update, context, f'[Err] {errstr}')

async def send_info(update: Optional[object], context: CallbackContext, errstr: str):
	await send_msg(update, context, f'[Info] {errstr}')

async def send_msg(update: Optional[object], context: CallbackContext, text: str):
	await context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=text
	)

async def stop(app: Application):
	DATABASE.dump()



# TODO
# async def cmd_songs(update: Optional[object], context: CallbackContext):
# 	reply_markup = get_songs_markup(update.message.chat_id)

# 	await context.bot.send_message(
# 		chat_id=update.message.chat_id,
# 		reply_to_message_id=update.message.message_id,
# 		reply_markup=reply_markup,
# 		text='Tap a song to enable or disable it.'
# 	)
# async def cmd_songs_inline(update: Optional[object], context: CallbackContext):
# 	message_id = update.callback_query.message.message_id
# 	chat_id = update.callback_query.message.chat.id
# 	artist, title, enabled = json.loads(update.callback_query.data)
# 	songs = get_chat_var(chat_id, 'songs')
# 	# Disable song
# 	if enabled:
# 		for data_index in reversed(range(len(songs))):
# 			song = songs[data_index]
# 			if is_song_enabled(chat_id, song['artist'], song['title']):
# 				del songs[data_index]
# 	# Enable song
# 	else:
# 		if not is_song_enabled(chat_id, artist, title):
# 			songs.append({
# 				'artist': artist,
# 				'title': title,
# 				'index': -1,
# 				'timestamp': 0
# 			})
# 	enabled = not enabled
# 	set_chat_var(chat_id, 'songs', songs)
# 	reply_markup = get_songs_markup(chat_id)
# 	update_text = f'{title} from {artist} is now {"enabled" if enabled else "disabled"}.'
# 	await context.bot.edit_message_text(
# 		chat_id=chat_id,
# 		message_id=message_id,
# 		text=update_text,
# 		reply_markup=reply_markup
# 	)
