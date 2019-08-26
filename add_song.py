import json

with open('config.json') as file:
	config = json.load(file)


import sys

lines = []

with open(sys.argv[1]) as file:
	for line in file:
		line = line.strip()
		if line:
			lines.append(line)

if not sys.argv[2] in config['lyrics']:
	config['lyrics'][sys.argv[2]] = {}

config['lyrics'][sys.argv[2]][sys.argv[3]] = lines

with open('config.json', 'w') as file:
	json.dump(config, file, indent='\t')
