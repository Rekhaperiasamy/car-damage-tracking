# test_app.py

import pytest
from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def test_client():
    yield TestClient(app)
