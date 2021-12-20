from urllib.request import urlopen

import requests
from deepdiff import DeepDiff  # For Deep Difference of 2 objects
from deepdiff import DeepHash  # For hashing objects based on their contents
from deepdiff import DeepSearch, grep  # For finding if item exists in an object

from server.utils.json import json_dumps
from tests.acceptance_tests.acceptance_settings import acceptance_settings

PRD_BACKEND_URI = acceptance_settings.PRD_BACKEND_URI
ACC_BACKEND_URI = acceptance_settings.ACC_BACKEND_URI
test_shop_id = "a08a13e2-a31b-4b6d-b2b4-0491cb3d2227"
test_shop_id_2 = "19149768-691c-40d8-a08e-fe900fd23bc0"


def test_shops_get_multi():
    response_prd = requests.get(PRD_BACKEND_URI + "shops").json()
    response_acc = requests.get(ACC_BACKEND_URI + "shops").json()
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}


def test_shops_full():
    response_prd = requests.get(PRD_BACKEND_URI + "shops").json()
    response_acc = requests.get(ACC_BACKEND_URI + "shops").json()
    assert len(response_prd) == len(response_acc)
    shops_ids = []
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}
    for shop in response_prd:
        shops_ids.append(shop["id"])

    for shop_id in shops_ids:
        response_prd = requests.get(PRD_BACKEND_URI + f"shops/{shop_id}").json()
        response_acc = requests.get(ACC_BACKEND_URI + f"shops/{shop_id}").json()
        acc_prices = response_acc["prices"]
        prd_prices = response_prd["prices"]

        assert len(acc_prices) == len(prd_prices)
        prices_differences = []
        for prd_price in prd_prices:
            for acc_price in acc_prices:
                if prd_price["id"] == acc_price["id"]:
                    price_diff = DeepDiff(prd_price, acc_price, ignore_order=True)
                    if price_diff != {}:
                        prices_differences.append(price_diff.tree)

        assert len(prices_differences) == 0


def test_shops_get_by_id():
    response_prd = requests.get(PRD_BACKEND_URI + f"shops/{test_shop_id}").json()
    response_acc = requests.get(ACC_BACKEND_URI + f"shops/{test_shop_id}").json()
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}
