import os
import pytest

@pytest.fixture
def paths():
	data_dir = os.path.dirname(os.path.realpath(__file__))
	return {
		'default': os.path.join(data_dir, 'default.yml'),
		'test': os.path.join(data_dir, 'test.yml')
	}

