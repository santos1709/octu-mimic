import pytest
import os
from model import Model
import mock
from flask import g

ROTH_PATH = os.path.abspath('')


@pytest.mark.skip(reason="Under development")
class TestDataScanner:
    def test__get_path(self):
        assert True

    def test__get_full_path(self):
        assert True

    def iter_files(self):
        assert True

    def get_most_recents(self):
        assert True
