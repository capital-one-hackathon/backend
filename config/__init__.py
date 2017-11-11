import os
import yaml


def merge_configs(target, overrides):
	"""Merges the two given dictionaries, overriding any target values with
	optional values with the same key. Merging is semi-deep in that it will
	continue to traverse the values if they are themselves dictionaries.

	Note: 'target' is modified in the merging process, unless there was nothing
	to merge.

	Parameters
	----------
	target : 
		Dictionary of properties we will be merging into
	overrides : 
		Dictionary or value we want to merge into `target`

	Returns
	-------
	dict or value
		The modified target dictionary or value
	"""
	if isinstance(target, dict) and isinstance(overrides, dict):
		# TODO: add support for lists, tuples
		for k,v in overrides.items():
			target[k] = merge_configs(target[k], v) if k in target else v
	elif overrides:
		target = overrides
	return target


def _load_config(path):
	"""Loads a yaml config at the given path, otherwise nothing
	if there was an error, failing silently.
	"""
	if path:
		try:
			# We'll assume 'path' points to an OS environment variable--that holds 
			# the path of a config file--if it doesn't look like a file path.
			if path and not path.endswith('.yml'):
				path = os.getenv(path)
			# load the config file
			with open(path) as f:
				return yaml.load(f)
		except(IOError, yaml.YAMLError) as err:
			#print(err)
			pass
	return None


def load(default_config='config/default.yml', 
		env_config=None,
		secret_config='instance/secrets.yml'):
	"""Loads up to three levels of configurations, based on the given parameters.

	Parameters
	----------
	default_config : str, optional 
		Path to file containing properties common in all environments,
		defaults to './config/default.yml'
	env_config : str, optional 
		Path to file with environment specific properties.
	secret_config: str, optional 
		Path to file with properties that are too sensitive for source
		control, defaults to './instance/secrets.yml'

	Returns
	-------
	dict
		Dictionary containing the properties loaded
	"""

	configs = merge_configs(merge_configs(merge_configs({},
		_load_config(default_config)),
		_load_config(env_config)),
		_load_config(secret_config))

	return configs

