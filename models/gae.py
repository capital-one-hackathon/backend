from google.appengine.ext import ndb

class GAEConfig(ndb.Model):
	"""Class representing application config in the form of key/value pairs,
	for use with Google App Engine Datastore. Model's id will serve as the 
	configuration key name.
	"""
	# value of this config
	value = ndb.StringProperty()

	@classmethod
	def get(cls, key):
		"""Returns the value for Config with given key. Creating 
		placeholder entry in datastore if key/value does not exists."""
		PLACEHOLDER = '__REPLACE_ME__'
		config = ndb.Key(GAEConfig, key).get()
		if not config or config.value == PLACEHOLDER:
			# add placeholder, then alert developer
			config = GAEConfig(id=key, value=PLACEHOLDER)
			config.put()
			raise Exception('Config {} not found! Please use the Developers Console to enter missing config!'.format(key))
		return config.value


	@classmethod
	def sget(cls, key):
		"""Wrapper for get() that fails silently."""
		try:
			return cls.get(key)
		except Exception as e:
			print(e)
			pass
		return None 
