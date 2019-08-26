import json


def dump(config, file_path):
	with open(file_path, 'w') as file:
		json.dump(config, file, indent='\t')


def load(file_path):
	with open(file_path) as file:
		content = json.load(file)

	return content
