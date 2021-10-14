import os
import tempfile
import pytest
import random
import recommend

import sys

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _path + '/../')

"""
import index


@pytest.fixture
def client():
    index.app.config["TESTING"] = True

    with index.app.test_client() as client:
        yield client
"""


@pytest.mark.mypy_testing
@pytest.mark.rcm
def test_case_1() -> None:
  """
  Case 1: each of users aef1, aef2 and aef5 (they all have gender_int=0) has exactly 1 fitting with same brand and different values.
  Moreover, aef5 had submitted fit_value=2. Test, whether alg1 and alg2 will suggest wrong sizes.
  """
  rcm = recommend.Recommend(0, "test_data/sample_db_case1.sqlite3")
  """alg1 and alg2 cannot say something useful to us now"""
  assert rcm.alg1("aef1", "Adidas") is None
  assert rcm.alg1("aef2", "Adidas") is None
  assert rcm.alg1("aef5", "Adidas") is None
  assert rcm.alg2("aef1", 0, "Adidas") is None
  assert rcm.alg2("aef2", 0, "Adidas") is None
  assert rcm.alg2("aef5", 0, "Adidas") is None
  
