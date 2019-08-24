def bot():
	from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

	# Get API token
	with open('token.txt') as file:
		token = file.read().strip()

	# Init bot
	updater = Updater(token=token, use_context=True)
	dispatcher = updater.dispatcher
