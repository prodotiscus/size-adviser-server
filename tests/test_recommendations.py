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


@pytest.mark.mypy_testing
@pytest.mark.rcm
def test_case_1b() -> None:
    rcm = recommend.Recommend(0, "test_data/sample_db_case1.sqlite3")
    assert rcm.alg1("aef1", "Adidas") is None
    assert rcm.alg1("aef2", "Adidas") is None
    assert rcm.alg1("aef5", "Adidas") is None
    assert rcm.alg2("aef1", 0, "Adidas") is None
    assert rcm.alg2("aef2", 0, "Adidas") is None
    assert rcm.alg2("aef5", 0, "Adidas") is None


@pytest.mark.mypy_testing
@pytest.mark.rcm
def test_case_2() -> None:
    """
    aef1: {Converse, 27 CM, 3} ; {Nike, 41 EU, 3}
    aef2: {Nike, 7 UK, 3}. alg1(Converse) = ? [Correct: 27 CM {-> 9 US}]
    aef3: {Nike, 8 UK, 3}. alg1(Converse) = ? [Correct: None]; alg2(Converse) = ? [Correct: 8 US];
    """
    rcm = recommend.Recommend(0, "test_data/sample_db_case2.sqlite3")
    assert rcm.get_E("Nike") == [(('Nike', '41 EU'), ('Converse', '27 CM'))]
    assert rcm.alg1("aef2", "Converse") in ["27 CM", "9 US"]
    assert rcm.alg2("aef5", 0, "Converse") == "10 US"
    assert [_ for _ in filter(lambda el: el[0] == ("Converse", "27 CM") and el[1] == ("Nike", "41 EU"), rcm.get_E("Converse"))]
    
  
