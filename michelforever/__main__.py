def main():
	import logging
	logging.basicConfig(format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s', level=logging.WARNING)

	from .bot import bot
	bot()


if __name__ == '__main__':
	main()
