import os
from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard, json_field
from typing import List, Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

SONGS_DIR = Path(os.getenv('MICHELFOREVER_SONGS_DIR'))

@dataclass
class Song(JSONWizard):
	"""Handles song and loading from file as a unique `artist/title` identifier"""
	artist: str
	title: str
	lyrics: List[str] = json_field('lyrics', default_factory=list, dump=False)

	def __post_init__(self):
		path = SONGS_DIR / Path(self.artist) / Path(self.title)
		if not path.exists():
			raise RuntimeError(f'could not load song from path "{path}"')

		with open(path) as f:
			self.lyrics = [ line.strip() for line in f.readlines() ]

	def __eq__(self, other: 'Song') -> bool:
		return self.artist == other.artist and self.title == other.title

	def __len__(self) -> int:
		"""Number of lines in the song"""
		return len(self.lyrics)

	def format(self) -> str:
		return f'{self.artist} -- {self.title}'

	@classmethod
	def open_all(cls) -> List['Song']:
		return [ cls(*path.parts[-2:]) for path in SONGS_DIR.glob('*/*') ]


if __name__ == '__main__':
	print(Song('PeterChier', 'VenirSperme'))

	try:
		Song('thissong', 'doesnotexist')
	except RuntimeError as e:
		print('correctly caught exception:', e)

	print(Song.open_all())