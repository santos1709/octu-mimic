from uuid import UUID


class TestGenerateToken:
    def test_put(self, client):
        """ Check if it generates a valid uuid4 string """

        json_data = {'user': 'pytest_user', 'device': 'pytest_device'}
        response = client.put(path='/token/generate', json=json_data)

        assert response.status_code == 200

        def expected_result(uuid):
            try:
                UUID(uuid, version=4)
                return True

            except ValueError:
                return False

        assert expected_result(response.json['generated_token'])
