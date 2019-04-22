import pytest
import os

ROTH_PATH = os.path.abspath('')


class TestListModels:
    def test_get(self, client, dir):
        dir_list = [element for element in dir.split(f'{ROTH_PATH}/')[1].split("/")]
        path = "/".join(dir_list[:-1]).replace('/', '_')
        response = client.get(f'/model/list/{path}')

        assert response.status_code == 200

        expected_result = {'model_0': dir_list[-1]}
        assert expected_result == response.json
