import os

import pytest

ROTH_PATH = os.path.abspath('')


@pytest.mark.skip(reason="Under development")
class TestAlert:
    def test_get(self, client):
        assert True
