import json


def dump(config):
	# Write edited config
	with open('config.json', 'w') as file:
		json.dump(config, file, indent='\t')
