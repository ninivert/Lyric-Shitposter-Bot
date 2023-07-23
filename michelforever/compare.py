import re
import unicodedata
from fuzzywuzzy import fuzz

IGNORED_REGEX = '(?u)[^\\w\\d]'

def normalize(s: str) -> str:
	s = s.lower()
	s = re.sub(IGNORED_REGEX, '', s)  # TODO : precompile regex
	s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')
	return s


def same(s1: str, s2: str, threshold: float) -> bool:
	return fuzz.ratio(normalize(s1), normalize(s2)) > threshold


# TODO : remove this
# def get_next_index(
# 	guess: str,
# 	lyrics: list,
# 	start_index=None,
# 	threshold=None
# ) -> int:
# 	"""Try to find the next exact match, line by line"""

# 	start_index = config['chats']['default']['index'] if start_index is None else start_index
# 	threshold = config['chats']['default']['threshold'] if threshold is None else threshold

# 	for index in range(start_index, len(lyrics)):
# 		lyric = lyrics[index]
# 		if same(guess, lyric, threshold):
# 			return index + 1

# 	return -1
