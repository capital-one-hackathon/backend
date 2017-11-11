import pytest
import config
import yaml

from helpers import paths

def test_load_default_config(paths):
	# see default.yml for configs
	c1 = config.load(default_config=paths.get('default'))
	c2 = yaml.load(file(paths.get('default'),'r'))
	assert c1 == c2
	assert c1.get('debug') == False
	assert c1.get('secret') == None
	assert (c1.get('oauths', {})
		.get('github',{})
		.get('callback') == 'http://localhost:8080/oauth/github/callback')

def test_overriding_default_config(paths):
	c1 = config.load(default_config=paths.get('default'),
					env_config=paths.get('test'))
	assert c1.get('debug') == True
	assert (c1.get('oauths', {})
		.get('github',{})
		.get('callback') == 'http://testing.acme.com/oauth/github/callback')

