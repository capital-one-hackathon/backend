import config

from models.gae import GAEConfig


def _resolve_secrets(target, key_path=[]):
	"""Given a target dictionary or list of config properties, resolve
	any property with secret (e.g. None) values. Values for missing
	secrets are stored in the GAE datastore. 

	Since the datastore values are stored in a flat key=value structure, 
	while our target value may be deeply nested in several iterables, 
	there is an impedence mismatch in how to match keys from our target 
	to the datastore. We solve this by keeping track of the path we traversed
	in our target, then flatten to a single key which we use to look up 
	in the datastore.

	Example:
		the flatten key for client_secret in the following,
		target = {oauths: {github: {client_secret: None,..}}}
		will be `oauths_github_client_secret`

	Notes: 
		- this function is called after all the default and environment 
		specific config properties are loaded, thus overriding any 
		previously set
		- `target` is modified in the process of resolving the missing 
		values

	Parameters
	----------
	target: iterable
		The iterable to traverse through for missing values. `target` 
		will be modified
	key_path: list, optional
		List to keep track of traversal path
	"""
	if isinstance(target, dict):
		for k,v in target.items():
			# keep track of the path we use to get here
			key_path.append(''.join(['_', k]))
			if not v: 
				# a secret, since it's missing a value
				# flatten the path to a key, then use as lookup in datastore
				target[k] = GAEConfig.sget((''.join(key_path))[1:])
			elif hasattr(v, '__iter__'):
				# if value is another iter, traverse it for missing values
				_resolve_secrets(v, key_path)
			# remove the key we just traversed as we're done with it
			key_path.pop()
	elif isinstance(target, list):
		for item in target:
			_resolve_secrets(item, key_path)


def load(default_config=None, env_config=None):
	"""
	"""
	configs = config.load(
			default_config=default_config, 
			env_config=env_config)

	_resolve_secrets(target=configs)

	return configs
