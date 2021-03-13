import os
import tempfile

import pytest

from typing import List, Dict

import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import index


@pytest.fixture
def client():
    index.app.config['TESTING'] = True

    with index.app.test_client() as client:
        yield client


@pytest.mark.mypy_testing
def test_basic_requests(client) -> None:
    rv = client.get("/firebase/register_new_account")
