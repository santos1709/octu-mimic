import os
import tempfile

import mock
import pytest

from main import create_app, objects_set


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""

    app = create_app()
    app.testing = True

    with objects_set(app, get_mocked_data_source(), get_mocked_db(), get_mocked_model()):
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


@mock.patch('model.Model')
def get_mocked_model(model):
    model.train_data_size = 20

    return model


@mock.patch('db.database.Database')
def get_mocked_db(db):
    db.update.return_value = True
    db.copy_to_db.return_value = True
    db.get_from_db.return_value = {'data': [[1]]}

    return db


@mock.patch('main.DataSource')
def get_mocked_data_source(data_source):
    data_source.user = 'pytest_user'
    data_source.device = 'pytest_device'
    data_source.key = 'pytest_quantity'
    data_source.value = '1000'
    data_source.token = _parse_token()
    data_source.timestamp = 'pytest_timestamp'
    data_source.get_most_recents.return_value = [0*i for i in range(21)]
    data_source.data_full_path = f'data/{data_source.timestamp}_{data_source.key}_{data_source.token}.csv'

    return data_source


def _parse_token():
    token = [t for t in os.listdir(f"{os.getcwd()}/data/") if 'pytest_timestamp_pytest_quantity_' in t]
    try:
        token = token[0].split('_')[-1].split('.')[0]
    except IndexError:
        return None
    return token
