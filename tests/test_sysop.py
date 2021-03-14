import os
import tempfile
import pytest
import random
from typing import List, Dict

import sys

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _path + '/../')

import index


@pytest.fixture
def client():
    index.app.config["TESTING"] = True

    with index.app.test_client() as client:
        yield client


@pytest.mark.mypy_testing
@pytest.mark.general
def test_xlsx_downloader(client) -> None:
    dl = client.get("/sysop/sheet_acquire/000001.xlsx")
    result: str = str(dl.data)
    assert "No file holding the given number found" not in result
