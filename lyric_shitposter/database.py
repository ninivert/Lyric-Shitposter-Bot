from .config import config
from .dump import dump


def get_chat_vars(chat_id):
	res = {}

	for key in config['chats']['default'].keys():
		res[key] = get_chat_var(chat_id, key)

	return res


def get_chat_var(chat_id, var):
	if str(chat_id) in config['chats'].keys() and var in config['chats'][str(chat_id)].keys():
		return config['chats'][str(chat_id)][var]
	else:
		return config['chats']['default'][var]


def set_chat_vars(chat_id, vars_dict):
	config['chats'][str(chat_id)].update(vars_dict)
	dump(config)


def set_chat_var(chat_id, var, val):
	if not str(chat_id) in config['chats'].keys():
		config['chats'][str(chat_id)] = {}

	config['chats'][str(chat_id)][var] = val
	dump(config)
