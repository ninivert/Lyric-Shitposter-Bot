import os, logging, time
from dataclasses import dataclass, field
from dataclass_wizard import JSONWizard
from result import Ok, Err, Result
from typing import List, Tuple, Optional
from pathlib import Path
from .song import Song
from .compare import same

from dotenv import load_dotenv
load_dotenv()

CHATS_DIR = Path(os.getenv('MICHELFOREVER_CHATS_DIR'))

_logger = logging.getLogger('chat')

@dataclass
class ChatSong(Song, JSONWizard):
	"""Handles a song as a member of a chat"""
	index: int = -1
	timestamp: float = 0

	def find_next_index(self, message: str, threshold: float) -> int:
		"""Finds the next index given a message, returning `-1` if not found"""
		for index in range(max(self.index, 0), len(self.lyrics)):
			lyric = self.lyrics[index]
			if same(message, lyric, threshold):
				return index + 1

		return -1

	def next_line(self) -> str:
		"""Returns next line in song, incrementing state and updating timestamp"""
		self.index = (self.index + 1) % len(self.lyrics)
		self.timestamp = time.time()
		return self.lyrics[self.index]

	def goto_lineidx(self, lineidx: str):
		"""Go to the line, updating timestamp"""
		self.index = lineidx % len(self.lyrics)
		self.timestamp = time.time()

	def restart(self, update_timestamp: bool = True):
		"""Restarts song from beginning"""
		self.index = -1
		if update_timestamp:
			self.timestamp = time.time()

	def timed_out(self, timeout: float) -> bool:
		return self.timestamp + timeout < time.time()

	@classmethod
	def open_all(cls) -> List['ChatSong']:
		return super().open_all()
		


@dataclass
class Chat(JSONWizard):
	"""Handles chat data and its component songs"""
	chatid: str
	songs: List[ChatSong] = field(default_factory=list)
	threshold: float = 85.0
	timeout: int = 300  # seconds
	uses: int = 0

	@staticmethod
	def load(chatid: str) -> Optional['Chat']:
		path = CHATS_DIR / Path(chatid)
		if not path.exists(): return None
		
		with open(path) as f:
			return Chat.from_json(f.read())

	def dump(self):
		_logger.info(f'dumping chatid={self.chatid}')
		path = CHATS_DIR / Path(self.chatid)
		with open(path, 'w') as f:
			f.write(self.to_json())

	@property
	def current_song(self) -> Result[ChatSong, str]:
		if len(self.songs) == 0: return Err('no songs activated')
		return Ok(self.songs[0])

	def update_on_message(self, message: str) -> Result[Tuple[str, bool], str]:
		# timeout the songs
		for song in self.songs:
			if song.timed_out(self.timeout):
				song.restart(update_timestamp=False)

		# find first match in the list of songs
		gen = filter(
			lambda song_idx: song_idx[1] > -1,
			((song, song.find_next_index(message, self.threshold))
			for song in self.songs)
		)
		song_idx = next(gen, None)
		if song_idx is None: return Err('not found')
		song, lineidx = song_idx
		
		# update song and move it to front
		song.goto_lineidx(lineidx-1)
		self.songs.insert(0, self.songs.pop(self.songs.index(song)))
		line = song.next_line()
		lastline = lineidx == len(song)
		self.uses += 1

		return Ok((line, lastline))

	def reload(self):
		self.songs = ChatSong.open_all()

	def restart(self) -> Result[None, str]:
		res = self.current_song
		if isinstance(self.current_song, Err): return res
		res.unwrap().restart()

	def next_line(self) -> Result[str, str]:
		res = self.current_song
		if isinstance(self.current_song, Err): return res
		return Ok(res.unwrap().next_line())
		

if __name__ == '__main__':
	c = Chat('debug', songs=[ChatSong('PeterChier', 'VenirSperme')])
	c = Chat('debug', songs=ChatSong.open_all())
	print(c.to_json())
	c.dump()  # creates chats/debug
	print(Chat.load('debug'))