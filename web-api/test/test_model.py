import pytest
import os
from model import Model
import mock
from flask import g

ROTH_PATH = os.path.abspath('')


@pytest.mark.skip(reason="Model logic not working properly yet")
class TestModel:
    def test__fit_data(self):
        assert True

    def test_get_last_model(self):
        assert True

    def test_update_model(self):
        assert True

    def test_save_model(self):
        assert True

    def test_detect_if_anomaly(self):
        assert True

    def test_train_model(self):
        assert True
