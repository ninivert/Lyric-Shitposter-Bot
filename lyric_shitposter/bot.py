import logging
from .config import config
from .lyrics import get_next_index
from .database import *


def bot():
	from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

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
	stat_handler = CommandHandler('stats', cmd_stats)
	unknown_handler = MessageHandler(cmd_filter, cmd_unknown)
	dispatcher.add_handler(message_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(next_handler)
	dispatcher.add_handler(stat_handler)
	dispatcher.add_handler(unknown_handler)

	# Run bot
	updater.start_polling()
	updater.idle()


def message(update, context):
	chat = get_chat_vars(update.message.chat_id)
	lyrics = config['lyrics']['CaptainSparklez']['Revenge']

	next_index = get_next_index(
		update.message.text,
		lyrics,
		start_index=chat['index'],
		threshold=chat['threshold']
	)

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
			next_index = config['chats']['default']['index']

		set_chat_vars(update.message.chat_id, {
			'index': next_index,
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
	set_chat_var(update.message.chat_id, 'index', config['chats']['default']['index'])
	cmd_next(update, context)


def cmd_next(update, context):
	lyrics = config['lyrics']['CaptainSparklez']['Revenge']

	index = get_chat_var(update.message.chat_id, 'index')
	index = (index + 1) % len(lyrics)
	set_chat_var(update.message.chat_id, 'index', index)

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=lyrics[index]
	)


def cmd_stats(update, context):
	from telegram import ParseMode

	chat = get_chat_vars(update.message.chat_id)

	stats = f'Here are some stats for chat {update.message.chat_id}:'

	for key, item in chat.items():
		stats += f'\n`{key}: {item}`'

	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text=stats,
		parse_mode=ParseMode.MARKDOWN
	)


def cmd_unknown(update, context):
	context.bot.send_message(
		chat_id=update.message.chat_id,
		reply_to_message_id=update.message.message_id,
		text='Unknown command. /help'
	)
