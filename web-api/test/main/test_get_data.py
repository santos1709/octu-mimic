import os

import mock
import pytest
from flask import g

ROTH_PATH = os.path.abspath('')


class TestGetData:
    @mock.patch('main.requests.put')
    def test_post(self, mocked_put, data_directory, client):
        sent_json = {}

        response = client.post(f'/data/send', json=sent_json)

        assert response.status_code == 200

        with open(data_directory, 'r') as file:
            storaged_value = file.read()

        assert storaged_value == g.data_source.value + ','
