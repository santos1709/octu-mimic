import pytest
import tempfile

from main import *


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""

    app.testing = True
    # app.config = {"TESTING": True,
    #               "DATABASE": Database(),
    #               "DATA_OBJECT": Data()
    #               }

    client = app.test_client()

    yield client


@pytest.fixture
def dir():
    """Create and configure a new app instance for each test."""

    fd, path = tempfile.mkstemp(suffix='.h5', prefix='test_model_', dir='test/models')

    yield path

    os.close(fd)
    os.unlink(path)
