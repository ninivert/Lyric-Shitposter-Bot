import re
import unicodedata
from fuzzywuzzy import fuzz
from .config import config


def normalize(s):
	s = s.lower()
	s = re.sub(config['ignored_regex'], '', s)
	s = unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8')
	return s


def same(s1, s2, threshold):
	return fuzz.ratio(normalize(s1), normalize(s2)) > threshold
