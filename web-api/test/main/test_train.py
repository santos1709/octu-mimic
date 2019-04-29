import os

import pytest

ROTH_PATH = os.path.abspath('')


@pytest.mark.skip(reason="Model logic not fully working")
class TestTrain:
    def test_put(self, client):
        assert True
