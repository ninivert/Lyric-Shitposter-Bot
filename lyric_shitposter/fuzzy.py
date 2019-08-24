import re
from fuzzywuzzy import fuzz
from .config import config


def same(s1, s2, threshold):
	s1 = s1.lower()
	s2 = s2.lower()
	s1 = re.sub(config['ignored_regex'], '', s1)
	s2 = re.sub(config['ignored_regex'], '', s2)

	return fuzz.ratio(s1, s2) > threshold
