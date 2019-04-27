import os
import tempfile
from contextlib import contextmanager

import mock
import pytest
from flask import appcontext_pushed, g
from uuid import uuid4

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
        # with app.app_context():
        #     try:
        #         print([t for t in os.listdir(os.getcwd() + '/test/data/') if 'timestamp_quantity_' in t][0])
        #         g.data_source.token = \
        #             [t for t in os.listdir(os.getcwd() + '/test/data/') if 'timestamp_quantity_' in t][0]
        #     except IndexError:
        #         pass
        with app.test_client() as client:
            yield client


@pytest.fixture
def models_directory():
    """Create and close a models fake directory/file for each test that it needs"""

    fd, path = tempfile.mkstemp(suffix='.h5', prefix='test_model_', dir='test/models')

    yield path

    os.close(fd)
    os.unlink(path)


@pytest.fixture
def data_directory():
    """Create and close a data fake directory/file for each test that it needs"""

    fd, path = tempfile.mkstemp(suffix='.csv', prefix='pytest_timestamp_pytest_quantity_', dir='data')

    yield path

    os.close(fd)
    os.unlink(path)


@mock.patch('db.database.Database')
def get_mocked_db(db):
    db.update.return_value = True
    db.copy_to_db.return_value = True
    db.get_from_db.return_value = {'data': [[100]]}

    return db


@mock.patch('main.DataSource')
def get_mocked_data_source(data_source):
    data_source.user = 'pytest_user'
    data_source.device = 'pytest_device'
    data_source.key = 'pytest_quantity'
    data_source.value = '1000'
    try:
        data_source.token = [t for t in os.listdir(f"{os.getcwd()}/data/") if 'pytest_timestamp_pytest_quantity_' in t]
        data_source.token = data_source.token[0].split('_')[-1].split('.')[0]
    except IndexError:
        pass
    data_source.timestamp = 'pytest_timestamp'

    return data_source
