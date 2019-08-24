from .config import config
from .fuzzy import same


def get_next_index(
	guess: str,
	lyrics: list,
	start_index=None,
	threshold=None
):
	"""Try to find the next exact match, line by line"""

	start_index = config['chats']['default']['index'] if start_index is None else start_index
	threshold = config['chats']['default']['threshold'] if threshold is None else threshold

	for index in range(start_index, len(lyrics)):
		lyric = lyrics[index]
		if same(guess, lyric, threshold):
			return index + 1

	return -1
