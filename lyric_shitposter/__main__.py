if __name__ == '__main__':
	import logging
	logging.basicConfig(format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', level=logging.INFO)

	from .bot import bot
	bot()
