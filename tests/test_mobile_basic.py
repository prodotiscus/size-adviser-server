import os
import tempfile
import pytest
import random
from typing import List, Dict, Tuple, Union

import sys

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _path + '/../')

import index


@pytest.fixture
def client():
    index.app.config["TESTING"] = True

    with index.app.test_client() as client:
        yield client


stuff_bot: Tuple[str, str, str, int, int] = (
    f"123456789xtt",
    f"tester.populate@size-adviser.com",
    "Tester+Populate",
    1,
    123456789
)


@pytest.mark.mypy_testing
@pytest.mark.general
def test_basic_requests_android(client) -> None:
    uid = f"{random.randrange(10**7, 10**8)}xxx"
    eml = f"tester{random.randrange(10**7, 10**8)}@size-adviser.com"
    name = "Foo+Bar"
    gender_int = 1
    rint = random.randrange(10**7, 10**8)
    a = client.get(f"/firebase/register_new_account?firebase_uid={uid}&user_email={eml}&user_name={name}&user_gender=0")
    b = client.get(f"/mobile/data_for_gender?user_id={uid}&gender_int={gender_int}")
    c = client.get(f"/mobile/get_brand_data?brand=Adidas&gender_int={gender_int}")
    d = client.get(f"/mobile/recommended_size?brand=Adidas&gender_int={gender_int}&user_id={uid}")
    e = client.get(f"/mobile/get_brands?gender_int={gender_int}")
    f = client.get(f"/mobile/get_brand_data?brand=Adidas&gender_int={gender_int}")
    g = client.get(f"/mobile/get_brand_data?brand=Asics&gender_int={gender_int}")
    h = client.get(f"/mobile/recommended_size?brand=Asics&gender_int={gender_int}&user_id={uid}")
    i = client.get(f"/mobile/try_with_size?user_id={uid}&fitting_id={rint}&brand=Asics&size=7.5&system=US&fit_value=4&date=13.03.2021")
    j = client.get(f"/mobile/get_collection_items?user_id={uid}")
    l0 = client.get(f"/mobile/data_for_gender?user_id={uid}&gender_int={gender_int}")
    k = client.get(f"/mobile/remove_collection_item?user_id={uid}&fitting_id={rint}")
    l = client.get(f"/mobile/data_for_gender?user_id={uid}&gender_int={gender_int}")


@pytest.mark.mypy_testing
@pytest.mark.adding_stuff
def test_as_unknown_brand(client) -> None:
    uid, eml, name, gender_int, rint = stuff_bot
    a = client.get(f"/mobile/try_with_size?user_id={uid}&fitting_id={rint}&brand=UnknownBrand&size=7.5&system=US&fit_value=4&date=13.03.2021")
    b = client.get(f"/mobile/data_for_gender?user_id={uid}&gender_int={gender_int}")


@pytest.mark.mypy_testing
@pytest.mark.removing_stuff
def test_rs_unknown_brand(client) -> None:
    uid, eml, name, gender_int, rint = stuff_bot
    a = client.get(f"/mobile/remove_collection_item?user_id={uid}&fitting_id={rint}")
