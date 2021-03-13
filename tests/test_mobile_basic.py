import os
import tempfile
import pytest
import random
from typing import List, Dict

import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import index


@pytest.fixture
def client():
    index.app.config["TESTING"] = True

    with index.app.test_client() as client:
        yield client


@pytest.mark.mypy_testing
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
    g = client.get("/mobile/get_brand_data?brand=Asics&gender_int={gender_int}")
    h = client.get(f"/mobile/recommended_size?brand=Asics&gender_int={gender_int}&user_id={uid}")
    i = client.get(f"/mobile/try_with_size?user_id={uid}&fitting_id={rint}&brand=Asics&size=7.5&system=US&fit_value=4&date=13.03.2021")
    j = client.get(f"/mobile/get_collection_items?user_id={uid}")
    k = client.get(f"/mobile/remove_collection_item?user_id={uid}&fitting_id={rint}")
    l = client.get("/mobile/data_for_gender?user_id={uid}&gender_int=0")
