import pytest
import os

ROTH_PATH = os.path.abspath('')


@pytest.mark.skip(reason="Model logic not working properly yet")
class TestSelectModels:
    def test_post(self, client):
        json_data = {'model_name': 'test_model',
                     'model_version': '0000-00-00_00-00-00'}
        response = client.post('/model/select', data=json_data)

        assert response.status_code == 200

        expected_result = {'new_model': json_data}
        assert expected_result == response.json
