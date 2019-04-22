import os
import tempfile
from contextlib import contextmanager

import mock
import pytest
from flask import appcontext_pushed, g

from main import create_app


@contextmanager
def objects_set(app, mocked_data_source, mocked_db):
    """ This allows to set (simulate) session objects with arbitrary ones """

    def handler(sender, **kwargs):
        g.data_source = mocked_data_source
        g.db = mocked_db

    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""

    app = create_app()
    app.testing = True

    with objects_set(app, get_mocked_data_source(), get_mocked_db()):
        with app.test_client() as client:
            yield client


@pytest.fixture
def dir():
    """Create and close new fake directory/file for each test that it needs"""

    fd, path = tempfile.mkstemp(suffix='.h5', prefix='test_model_', dir='test/models')

    yield path

    os.close(fd)
    os.unlink(path)


@mock.patch('db.database.Database')
def get_mocked_db(db):
    db.update.return_value = True

    return db


@mock.patch('main.Data')
def get_mocked_data_source(data_source):
    data_source.user = 'pytest_user'
    data_source.device = 'pytest_device'

    return data_source
