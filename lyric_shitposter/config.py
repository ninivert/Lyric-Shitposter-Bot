import json
import os
import logging
from .dump import dump

_logger = logging.getLogger()
_logger.setLevel(logging.INFO)

# Load from existing config file
if os.path.exists('config.json'):
	with open('config.json') as file:
		config = json.load(file)

	_logger.info('Loaded config.')

# Generate new default config file
else:
	config = {
		'chats': {
			'default': {
				'threshold': 90,
				'index': 0,
			}
		},
		'ignored_regex': r'(?u)[^\w\d]',
		'lyrics': {
			'CaptainSparklez': {
				'Revenge': [
					'Creeper,',
					'aw man',
					'So we back in the mine,',
					'got our pick axe swinging from side to side',
					'Side, side to side',
					'This task a grueling one,',
					'hope to find some diamonds tonight, night, night',
					'Diamonds tonight',
					'Heads up,',
					'you hear a sound,',
					'turn around and look up,',
					'total shock fills your body',
					'Oh no it\'s you again',
					'I could never forget those eyes, eyes, eyes',
					'Eyes, eyes, eyes',
					'\'Cause baby tonight, the creeper\'s trying to steal all our stuff again',
					'\'Cause baby tonight, you grab your pick, shovel and bolt again',
					'And run, run',
					'until it\'s done, done,',
					'until the sun comes up in the morn\'',
					'\'Cause baby tonight, the creeper\'s trying to steal all our stuff again',
					'Just when you think you\'re safe,',
					'overhear some hissing from right behind',
					'Right, right behind',
					'That\'s a nice life you have,',
					'shame it\'s gotta end at this time, time, time',
					'Time, time, time, time',
					'Blows up,',
					'then your health bar drops,',
					'and you could use a 1-up,',
					'get inside don\'t be tardy',
					'So now you\'re stuck in there,',
					'half a heart is left but don\'t die, die, die',
					'Die, die, die, die',
					'\'Cause baby tonight, the creeper\'s trying to steal all your stuff again',
					'\'Cause baby tonight, you grab your pick, shovel and bolt again',
					'And run, run',
					'until it\'s done, done,',
					'until the sun comes up in the morn\'',
					'\'Cause baby tonight, the creeper\'s trying to steal all your stuff again',
					'Creepers, you\'re mine',
					'Dig up diamonds,',
					'and craft those diamonds',
					'and make some armor',
					'Get it baby,',
					'go and forge that like you so,',
					'MLG pro',
					'The sword\'s made of diamonds,',
					'so come at me bro',
					'Training in your room under the torch light',
					'Hone that form to get you ready for the big fight',
					'Every single day and the whole night',
					'Creeper\'s out prowlin\' - alright',
					'Look at me, look at you',
					'Take my revenge that\'s what I\'m gonna do',
					'I\'m a warrior baby, what else is new',
					'And my blade\'s gonna tear through you',
					'Bring it',
					'\'Cause baby tonight, the creeper\'s trying to steal all our stuff again',
					'Yeah baby tonight, grab your sword, armor and go, take your revenge',
					'So fight, fight',
					'like it\'s the last, last',
					'night of your life, life,',
					'show them your bite',
					'\'Cause baby tonight, the creeper\'s trying to steal all our stuff again',
					'\'Cause baby tonight, you grab your pick, shovel and bolt again',
					'And run, run',
					'until it\'s done, done,',
					'until the sun comes up in the morn\'',
					'\'Cause baby tonight, the creepers tried to steal all our stuff again'
				]
			}
		}
	}

	dump(config)

	_logger.info('Created new config file.')
