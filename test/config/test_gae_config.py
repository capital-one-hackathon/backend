import os
import pytest
import yaml
import sys
import mock

sys.modules['models'] = mock.MagicMock()
sys.modules['models.gae'] = mock.MagicMock()
sys.modules['models.gae.GAEConfig'] = mock.MagicMock()

from helpers import paths
from config import gae
from models.gae import GAEConfig

def test_loading_from_gae_datastore(paths):
	place_holder = '__REPLACE_ME__'
	with mock.patch.object(GAEConfig, 'sget', return_value=place_holder):
		configs = gae.load(default_config=paths.get('default'),
				env_config=paths.get('test'))
		assert configs.get('debug') == True
		assert (configs.get('oauths', {})
			.get('github',{})
			.get('callback') == 'http://testing.acme.com/oauth/github/callback')
		assert configs.get('secret_key') == place_holder
