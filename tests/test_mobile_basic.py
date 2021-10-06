import os
import tempfile
import pytest
import random
from typing import List, Dict, Tuple, Union
from collections import namedtuple

import sys

_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _path + '/../')

import index


@pytest.fixture
def client():
    index.app.config["TESTING"] = True

    with index.app.test_client() as client:
        yield client


def new_fid() -> int:
    return random.randrange(10**7, 10**8)


test_account = namedtuple("test_account", "uid email name gender_int")
TEDDY = test_account(
    "BlTshjeJc9hIUCyxDXLB2bPPzRo1",
    "sfedor2002@gmail.com",
    "Teddy+Tester",
    1
)
GENDER_SWITCH = range(0, 2)


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.core
def test_registration(client) -> None:
    for GINT in GENDER_SWITCH:
        r1 = client.get(f"/firebase/register_new_account?firebase_uid={TEDDY.uid}&user_email={TEDDY.email}&user_name={TEDDY.name}&user_gender={GINT}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.profile
def test_data4gender(client) -> None:
    for GINT in GENDER_SWITCH:
        r1 = client.get(f"/mobile/data_for_gender?user_id={TEDDY.uid}&gender_int={GINT}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
def test_get_brand_data(client) -> None:
    for GINT in GENDER_SWITCH:
        r1 = client.get(f"/mobile/get_brand_data?brand=Adidas&gender_int={GINT}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
def test_recommended_size(client) -> None:
    for GINT in GENDER_SWITCH:
        r1 = client.get(f"/mobile/recommended_size?brand=Adidas&gender_int={GINT}&user_id={TEDDY.uid}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
def test_brands_list(client) -> None:
    for GINT in GENDER_SWITCH:
        r1 = client.get(f"/mobile/get_brands?gender_int={GINT}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
@pytest.mark.my_collection
def test_result_submission_existing_brand(client) -> None:
    for GINT in GENDER_SWITCH:
        fid = new_fid()
        r1 = client.get(f"/mobile/try_with_size?user_id={TEDDY.uid}&fitting_id={fid}&brand=Asics&size=7.5&system=US&fit_value=4&date=12.23.48.15.03.2021")
        r_control = client.get(f"/mobile/data_for_gender?user_id={TEDDY.uid}&gender_int={GINT}")
        r2 = client.get(f"/mobile/remove_collection_item?user_id={TEDDY.uid}&fitting_id={fid}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
@pytest.mark.my_collection
def test_result_submission_new_brand(client) -> None:
    for GINT in GENDER_SWITCH:
        fid = new_fid()
        r1 = client.get(f"/mobile/try_with_size?user_id={TEDDY.uid}&fitting_id={fid}&brand=NonExistingBrand&size=7.5&system=US&fit_value=4&date=12.23.48.15.03.2021")
        r_control = client.get(f"/mobile/data_for_gender?user_id={TEDDY.uid}&gender_int={GINT}")
        r2 = client.get(f"/mobile/remove_collection_item?user_id={TEDDY.uid}&fitting_id={fid}")


@pytest.mark.mypy_testing
@pytest.mark.mobile
@pytest.mark.fitting_room
def test_bound_load(client) -> None:
    for GINT in GENDER_SWITCH:
        bound_load = client.get(f"/mobile/bound_load?user_gender={GINT}&brand=Adidas&user_id={TEDDY.uid}")

